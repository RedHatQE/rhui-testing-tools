#! /usr/bin/python -tt

""" Create CloudFormation stack """

from paramiko import SSHClient
from boto import cloudformation
from boto import regioninfo
from boto import ec2
import argparse
import time
import logging
import sys
import random
import string
import json
import tempfile
import paramiko
import yaml

# pylint: disable=W0621


class SyncSSHClient(SSHClient):
    '''
    Special class for sync'ed commands execution over ssh
    '''
    def run_sync(self, command):
        """ Run sync """
        logging.debug("RUN_SYNC '%s'", command)
        stdin, stdout, stderr = self.exec_command(command)
        status = stdout.channel.recv_exit_status()
        if status:
            logging.debug("RUN_SYNC status: %i", status)
        else:
            logging.debug("RUN_SYNC failed!")
        return stdin, stdout, stderr

    def run_with_pty(self, command):
        """ Run with PTY """
        logging.debug("RUN_WITH_PTY '%s'", command)
        chan = self.get_transport().open_session()
        chan.get_pty()
        chan.exec_command(command)
        status = chan.recv_exit_status()
        logging.debug("RUN_WITH_PTY recv: %s", chan.recv(16384))
        logging.debug("RUN_WITH_PTY status: %i", status)
        chan.close()
        return status


def setup_host_ssh(hostname, key):
    '''
    Setup ssh connection to host.
    If necessary allow root ssh connections
    '''
    ntries = 20
    sftp = None
    client = SyncSSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    while ntries > 0:
        try:
            logging.debug("Trying to connect to %s as root", hostname)
            client.connect(hostname=hostname,
                           username="root",
                           key_filename=key,
                           look_for_keys=False)
            _, stdout, _ = client.run_sync("whoami")
            output = stdout.read()
            logging.debug("OUTPUT for 'whoami': " + output)
            if output != "root\n":
                #It's forbidden to login under 'root', switching this off
                # randomly selecting login ('ec2-user' or 'fedora')
                login = random.choice(['ec2-user', 'fedora'])
                client = SyncSSHClient()
                client.load_system_host_keys()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname=hostname,
                               username=login,
                               key_filename=key,
                               look_for_keys=False)
                client.run_with_pty("sudo su -c 'cp -af /home/" + login + "/.ssh/authorized_keys /root/.ssh/authorized_keys; chown root.root /root/.ssh/authorized_keys'")
                client.run_with_pty("sudo su -c \"sed -i 's,disable_root: 1,disable_root: 0,' /etc/cloud/cloud.cfg\"")
                client.connect(hostname=hostname,
                               username="root",
                               key_filename=key,
                               look_for_keys=False)
            sftp = client.open_sftp()
            break
        except Exception, e:
            logging.debug('Caught exception in setup_host_ssh: ' + str(e.__class__) + ': ' + str(e))
            ntries -= 1
        time.sleep(10)
    if ntries == 0:
        logging.error("Failed to setup ssh to " + hostname + " using " + key + " key")
    client.get_transport().set_keepalive(10)
    sftp.get_channel().get_transport().set_keepalive(10)
    return (client, sftp)


def setup_main(client):
    '''
    Create ssh key on main node.
    '''
    logging.info('setting up main: %s', client._transport.sock.getpeername())
    try:
        logging.info('generating main ssh keypair')
        client.run_sync("rm -f /root/.ssh/id_rsa{,.pub}; ssh-keygen -t rsa -b 2048 -N '' -f /root/.ssh/id_rsa")
        _, stdout, _ = client.run_sync("cat /root/.ssh/id_rsa.pub")
        output = stdout.read()
        logging.debug("Generated ssh main key: " + output)
        return output
    except Exception, e:
        logging.error('Caught exception in setup_main: ' + str(e.__class__) + ': ' + str(e))
        return None
    finally:
        logging.info('setting up main %s: all done', client._transport.sock.getpeername())


def setup_subordinate(client, sftp, hostname, hostsfile, yamlfile, main_keys, setup_script):
    '''
    Setup subordinate node.
    - Allow connections from mains
    - Set hostname
    - Write /etc/hosts
    - Write /etc/rhui-testing.yaml
    '''
    logging.info('setting up subordinate: %s', hostname)
    try:
        logging.info('configuring hosts file')
        client.run_sync("touch /tmp/hosts")
        sftp.put(hostsfile, "/tmp/hosts")
        client.run_sync("cat /etc/hosts >> /tmp/hosts")
        client.run_sync("sort -u /tmp/hosts > /etc/hosts")
        logging.info('dumping rhui-testing.yaml')
        client.run_sync("touch /etc/rhui-testing.yaml")
        sftp.put(yamlfile, "/etc/rhui-testing.yaml")
        if hostname:
            logging.info('setting hostname to %s', hostname)
            client.run_sync("hostname " + hostname)
            client.run_sync("sed -i 's,^HOSTNAME=.*$,HOSTNAME=" + hostname + ",' /etc/sysconfig/network")
        for key in main_keys:
            if key:
                logging.info('allowing ssh key: %s', key.split()[-1])
                client.run_sync("cat /root/.ssh/authorized_keys > /root/.ssh/authorized_keys.new")
                client.run_sync("echo '" + key + "' >> /root/.ssh/authorized_keys.new")
                client.run_sync("sort -u /root/.ssh/authorized_keys.new | grep -v '^$' > /root/.ssh/authorized_keys")
        if setup_script:
            logging.info('running setup script')
            sftp.put(setup_script, "/root/instance_setup_script")
            client.run_sync("chmod 755 /root/instance_setup_script")
            client.run_sync("/root/instance_setup_script")
    except Exception, e:
        logging.error('Caught exception in setup_subordinate: ' + str(e.__class__) + ': ' + str(e))
    finally:
        logging.info('subordinate setup done: %s', hostname)


argparser = argparse.ArgumentParser(description='Create CloudFormation stack and run the testing')
argparser.add_argument('--rhuirhelversion', help='RHEL version for RHUI setup (RHEL6, RHEL6)', default="RHEL6")

argparser.add_argument('--rhel5', help='number of RHEL5 clients', type=int, default=0)
argparser.add_argument('--rhel6', help='number of RHEL6 clients', type=int, default=1)
argparser.add_argument('--rhel7', help='number of RHEL7 clients', type=int, default=0)
argparser.add_argument('--cds', help='number of CDSes instances', type=int, default=1)
argparser.add_argument('--proxy', help='create RHUA<->CDN proxy', action='store_const', const=True, default=False)
argparser.add_argument('--config',
                       default="/etc/rhui_ec2.yaml", help='use supplied yaml config file')
argparser.add_argument('--debug', action='store_const', const=True,
                       default=False, help='debug mode')
argparser.add_argument('--fakecf', action='store_const', const=True,
                       default=False, help='use fakecf creator')
argparser.add_argument('--dry-run', action='store_const', const=True,
                       default=False, help='do not run stack creation, validate only')
argparser.add_argument('--parameters', metavar='<expr>', nargs="*",
                       help="space-separated NAME=VALUE list of parametars")
argparser.add_argument('--region',
                       default="eu-west-1", help='use specified region')
argparser.add_argument('--timeout', type=int,
                       default=10, help='stack creation timeout')

argparser.add_argument('--vpcid', help='VPCid')
argparser.add_argument('--subnetid', help='Subnet id (for VPC)')

argparser.add_argument('--instancesetup', help='Instance setup script for all instances except main node')
argparser.add_argument('--mainsetup', help='Instance setup script for main node')
argparser.add_argument('--r3', action='store_const', const=True, default=False,
                        help='use r3.xlarge instances to squeeze out more network and cpu performance (requires vpcid and subnetid)')

args = argparser.parse_args()

if args.debug:
    loglevel = logging.DEBUG
else:
    loglevel = logging.INFO

REGION = args.region

logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

if args.debug:
    logging.getLogger("paramiko").setLevel(logging.DEBUG)
else:
    logging.getLogger("paramiko").setLevel(logging.WARNING)

if (args.vpcid and not args.subnetid) or (args.subnetid and not args.vpcid):
    logging.error("vpcid and subnetid parameters should be set together!")
    sys.exit(1)
if (args.r3 and not args.vpcid):
    logging.error("r3 requires setting vpcid and subnetid")
    sys.exit(1)

if args.instancesetup:
    fd = open(args.instancesetup, 'r')
    instancesetup = fd.read()
    fd.close()

if args.mainsetup:
    fd = open(args.mainsetup, 'r')
    mainsetup = fd.read()
    fd.close()

try:
    with open(args.config, 'r') as confd:
        valid_config = yaml.load(confd)

    (ssh_key_name, ssh_key) = valid_config["ssh"][REGION]
    ec2_key = valid_config["ec2"]["ec2-key"]
    ec2_secret_key = valid_config["ec2"]["ec2-secret-key"]

except Exception as e:
    logging.error("got '%s' error processing: %s", e, args.config)
    logging.error("Please, check your config or and try again")
    sys.exit(1)

json_dict = {}

json_dict['AWSTemplateFormatVersion'] = '2010-09-09'

json_dict['Description'] = 'RHUI with %s CDSes' % args.cds
if args.rhel5 > 0:
    json_dict['Description'] += " %s RHEL5 clients" % args.rhel5
if args.rhel6 > 0:
    json_dict['Description'] += " %s RHEL6 clients" % args.rhel6
if args.rhel7 > 0:
    json_dict['Description'] += " %s RHEL7 clients" % args.rhel7
if args.proxy:
    json_dict['Description'] += " PROXY"

json_dict['Mappings'] = \
  {u'Fedora': {
                u'ap-northeast-1': {u'AMI': u'ami-20d6cd21'},
                u'ap-southeast-1': {u'AMI': u'ami-06edc754'},
                u'ap-southeast-2': {u'AMI': u'ami-ddf480e7'},
                u'eu-west-1': {u'AMI': u'ami-030f2174'},
                u'eu-central-1': {u'AMI': u'ami-5cd9ea41'},
                u'sa-east-1': {u'AMI': u'ami-650cb078'},
                u'us-east-1': {u'AMI': u'ami-acd999c4'},
                u'us-west-1': {u'AMI': u'ami-15326925'},
                u'us-west-2': {u'AMI': u'ami-dce3fb99'}},
   u'RHEL7': {
                u'us-east-1': {u'AMI': u'ami-10663b78'},
                u'eu-central-1': {u'AMI': u'ami-defdcfc3'},
                u'us-west-1': {u'AMI': u'ami-9b40a5df'},
                u'eu-west-1': {u'AMI': u'ami-25158352'},
                u'ap-northeast-1': {u'AMI': u'ami-adb458ad'},
                u'us-west-2': {u'AMI': u'ami-4bbf9e7b'},
                u'ap-southeast-2': {u'AMI': u'ami-dddaace7'},
                u'sa-east-1': {u'AMI': u'ami-0fe25b12'},
                u'ap-southeast-1': {u'AMI': u'ami-d81c2b8a'},},
    u'RHEL6': {
                u'us-east-1': {u'AMI': u'ami-d2d06aba'},
                u'ap-southeast-2': {u'AMI': u'ami-57e38e6d'},
                u'eu-west-1': {u'AMI': u'ami-1fa6ca68'},
                u'us-west-1': {u'AMI': u'ami-6dccd928'},
                u'ap-northeast-1': {u'AMI': u'ami-9f56669e'},
                u'ap-southeast-1': {u'AMI': u'ami-34133266'},
                u'sa-east-1': {u'AMI': u'ami-9f5ce882'},
                u'us-west-2': {u'AMI': u'ami-5bbcf36b'},
                u'eu-central-1': {u'AMI': u'ami-84f7c199'},},
    u'RHEL5': {
                u'us-east-1': {u'AMI': u'ami-3068da58'},
                u'eu-west-1': {u'AMI': u'ami-ec94369b'},
                u'us-west-1': {u'AMI': u'ami-995953dc'},
                u'sa-east-1': {u'AMI': u'ami-834efb9e'},
                u'ap-northeast-1': {u'AMI': u'ami-fdc8fdfc'},
                u'ap-southeast-2': {u'AMI': u'ami-45ee8c7f'},
                u'ap-southeast-1': {u'AMI': u'ami-5a567008'},
                u'us-west-2': {u'AMI': u'ami-c599d4f5'},
                u'eu-central-1': {u'AMI': u'ami-c4d9efd9'},},

   }

json_dict['Parameters'] = \
{u'KeyName': {u'Description': u'Name of an existing EC2 KeyPair to enable SSH access to the instances',
              u'Type': u'String'}}

json_dict['Resources'] = \
{u'CLIsecuritygroup': {u'Properties': {u'GroupDescription': u'CLI security group',
                                       u'SecurityGroupIngress': [{u'CidrIp': u'0.0.0.0/0',
                                                                  u'FromPort': u'22',
                                                                  u'IpProtocol': u'tcp',
                                                                  u'ToPort': u'22'}]},
                       u'Type': u'AWS::EC2::SecurityGroup'},
 u'MAINsecuritygroup': {u'Properties': {u'GroupDescription': u'MAIN security group',
                                          u'SecurityGroupIngress': [{u'CidrIp': u'0.0.0.0/0',
                                                                     u'FromPort': u'22',
                                                                     u'IpProtocol': u'tcp',
                                                                     u'ToPort': u'22'},
                                                                    {u'CidrIp': u'0.0.0.0/0',
                                                                     u'FromPort': u'6379',
                                                                     u'IpProtocol': u'tcp',
                                                                     u'ToPort': u'6379'}]},
                          u'Type': u'AWS::EC2::SecurityGroup'},
 u'PROXYsecuritygroup': {u'Properties': {u'GroupDescription': u'PROXY security group',
                                         u'SecurityGroupIngress': [{u'CidrIp': u'0.0.0.0/0',
                                                                    u'FromPort': u'22',
                                                                    u'IpProtocol': u'tcp',
                                                                    u'ToPort': u'22'},
                                                                   {u'CidrIp': u'0.0.0.0/0',
                                                                    u'FromPort': u'3128',
                                                                    u'IpProtocol': u'tcp',
                                                                    u'ToPort': u'3128'}]},
                         u'Type': u'AWS::EC2::SecurityGroup'},
 u'RHUIsecuritygroup': {u'Properties': {u'GroupDescription': u'RHUI security group',
                                        u'SecurityGroupIngress': [{u'CidrIp': u'0.0.0.0/0',
                                                                   u'FromPort': u'22',
                                                                   u'IpProtocol': u'tcp',
                                                                   u'ToPort': u'22'},
                                                                  {u'CidrIp': u'0.0.0.0/0',
                                                                   u'FromPort': u'443',
                                                                   u'IpProtocol': u'tcp',
                                                                   u'ToPort': u'443'},
                                                                  {u'CidrIp': u'0.0.0.0/0',
                                                                   u'FromPort': u'5674',
                                                                   u'IpProtocol': u'tcp',
                                                                   u'ToPort': u'5674'}]},
                        u'Type': u'AWS::EC2::SecurityGroup'}}

json_dict['Resources']["main"] = \
{u'Properties': {u'ImageId': {u'Fn::FindInMap': [u'Fedora',
                                                             {u'Ref': u'AWS::Region'},
                                                             u'AMI']},
                             u'InstanceType': args.r3 and u'r3.xlarge' or u'm3.large',
                             u'KeyName': {u'Ref': u'KeyName'},
                             u'SecurityGroups': [{u'Ref': u'MAINsecuritygroup'}],
                             u'BlockDeviceMappings' : [
                                      {
                                        "DeviceName" : "/dev/sda1",
                                        "Ebs" : { "VolumeSize" : "16" }
                                      },
                             ],
                             u'Tags': [{u'Key': u'Name',
                                        u'Value': {u'Fn::Join': [u'_',
                                                                 [u'RHUI_Main',
                                                                  {u'Ref': u'KeyName'}]]}},
                                       {u'Key': u'Role',
                                        u'Value': u'Main'},
                                       {u'Key': u'PrivateHostname',
                                        u'Value': u'main.example.com'},
                                       {u'Key': u'PublicHostname',
                                        u'Value': u'main_pub.example.com'}]},
             u'Type': u'AWS::EC2::Instance'}

json_dict['Resources']["rhua"] = \
 {u'Properties': {u'ImageId': {u'Fn::FindInMap': [args.rhuirhelversion,
                                                           {u'Ref': u'AWS::Region'},
                                                           u'AMI']},
                           u'InstanceType': args.r3 and u'r3.xlarge' or u'm3.large',
                           u'KeyName': {u'Ref': u'KeyName'},
                           u'SecurityGroups': [{u'Ref': u'RHUIsecuritygroup'}],
                           u'BlockDeviceMappings' : [
                                      {
                                        "DeviceName" : "/dev/sdb",
                                        "Ebs" : { "VolumeSize" : "300" }
                                      },
                             ],
                           u'Tags': [{u'Key': u'Name',
                                      u'Value': {u'Fn::Join': [u'_',
                                                               [u'RHUA',
                                                                {u'Ref': u'KeyName'}]]}},
                                     {u'Key': u'Role', u'Value': u'RHUA'},
                                     {u'Key': u'PrivateHostname',
                                      u'Value': u'rhua.example.com'},
                                     {u'Key': u'PublicHostname',
                                      u'Value': u'rhua_pub.example.com'}]},
           u'Type': u'AWS::EC2::Instance'}

if args.proxy:
    json_dict['Resources']["proxy"] = \
     {u'Properties': {u'ImageId': {u'Fn::FindInMap': [u"Fedora",
                                                            {u'Ref': u'AWS::Region'},
                                                            u'AMI']},
                            u'InstanceType': u'm3.large',
                            u'KeyName': {u'Ref': u'KeyName'},
                            u'SecurityGroups': [{u'Ref': u'PROXYsecuritygroup'}],
                            u'BlockDeviceMappings' : [
                                      {
                                        "DeviceName" : "/dev/sda1",
                                        "Ebs" : { "VolumeSize" : "16" }
                                      },
                            ],
                            u'Tags': [{u'Key': u'Name',
                                       u'Value': {u'Fn::Join': [u'_',
                                                                [u'PROXY',
                                                                 {u'Ref': u'KeyName'}]]}},
                                      {u'Key': u'Role', u'Value': u'PROXY'},
                                      {u'Key': u'PrivateHostname',
                                       u'Value': u'proxy.example.com'},
                                      {u'Key': u'PublicHostname',
                                       u'Value': u'proxy_pub.example.com'}]},
            u'Type': u'AWS::EC2::Instance'}

for i in range(1, args.cds + 1):
    json_dict['Resources']["cds%i" % i] = \
        {u'Properties': {u'ImageId': {u'Fn::FindInMap': [args.rhuirhelversion,
                                                           {u'Ref': u'AWS::Region'},
                                                           u'AMI']},
                           u'InstanceType': args.r3 and u'r3.xlarge' or u'm3.large',
                           u'BlockDeviceMappings' : [
                                      {
                                        "DeviceName" : "/dev/sdb",
                                        "Ebs" : { "VolumeSize" : "300" }
                                      },
                             ],
                           u'KeyName': {u'Ref': u'KeyName'},
                           u'SecurityGroups': [{u'Ref': u'RHUIsecuritygroup'}],
                           u'Tags': [{u'Key': u'Name',
                                      u'Value': {u'Fn::Join': [u'_',
                                                               [u'CDS%i' % i,
                                                                {u'Ref': u'KeyName'}]]}},
                                     {u'Key': u'Role', u'Value': u'CDS'},
                                     {u'Key': u'PrivateHostname',
                                      u'Value': u'cds%i.example.com' % i},
                                     {u'Key': u'PublicHostname',
                                      u'Value': u'cds%i_pub.example.com' % i}]},
           u'Type': u'AWS::EC2::Instance'}

os_dict = {5: "RHEL5", 6: "RHEL6", 7: "RHEL7"}
for i in (5,6,7):
    num_cli_ver = args.__getattribute__("rhel%i" % i)
    if num_cli_ver:
        for j in range(1, num_cli_ver + 1):
            os = os_dict[i]
            json_dict['Resources']["cli%inr%i" % (i, j)] = \
                {u'Properties': {u'ImageId': {u'Fn::FindInMap': [os,
                                                                   {u'Ref': u'AWS::Region'},
                                                                   u'AMI']},
                                   u'InstanceType': u'm3.large' if os == "RHEL5"  else u'm3.large',
                                   u'KeyName': {u'Ref': u'KeyName'},
                                   u'SecurityGroups': [{u'Ref': u'CLIsecuritygroup'}],
                                   u'Tags': [{u'Key': u'Name',
                                              u'Value': {u'Fn::Join': [u'_',
                                                                       [u'RHUI_CLI%i_%i' % (i, j),
                                                                        {u'Ref': u'KeyName'}]]}},
                                             {u'Key': u'Role', u'Value': u'CLI'},
                                             {u'Key': u'PrivateHostname',
                                              u'Value': u'cli%i_%i.example.com' % (i, j)},
                                             {u'Key': u'PublicHostname',
                                              u'Value': u'cli%i_%ipub.example.com' % (i, j)},
                                             {u'Key': u'OS', u'Value': u'%s' % os[:5]}]},
                   u'Type': u'AWS::EC2::Instance'}

if args.vpcid and args.subnetid:
    # Setting VpcId and SubnetId
    json_dict['Outputs'] = {}
    for key in json_dict['Resources'].keys():
        # We'll be changing dictionary so .keys() is required here!
        if json_dict['Resources'][key]['Type'] == 'AWS::EC2::SecurityGroup':
            json_dict['Resources'][key]['Properties']['VpcId'] = args.vpcid
        elif json_dict['Resources'][key]['Type'] == 'AWS::EC2::Instance':
            json_dict['Resources'][key]['Properties']['SubnetId'] = args.subnetid
            json_dict['Resources'][key]['Properties']['SecurityGroupIds'] = json_dict['Resources'][key]['Properties'].pop('SecurityGroups')
            json_dict['Resources']["%sEIP" % key] = \
            {
                "Type" : "AWS::EC2::EIP",
                "Properties" : {"Domain" : "vpc",
                                "InstanceId" : { "Ref" : key }
                               }
            }
else:
#    json_dict['Outputs'] = \
#    {u'IPMain': {u'Description': u'main.example.com IP',
#               u'Value': {u'Fn::GetAtt': [u'main', u'PublicIP']}}}
    pass
json_dict['Outputs'] = {}

json_body =  json.dumps(json_dict, indent=4)

region = regioninfo.RegionInfo(name=args.region,
                               endpoint="cloudformation." + args.region + ".amazonaws.com")

if not region:
    logging.error("Unable to connect to region: " + args.region)
    sys.exit(1)

if args.fakecf:
    from fakecf.fakecf import FakeCF
    con_cf = FakeCF(aws_access_key_id=ec2_key,
                    aws_secret_access_key=ec2_secret_key,
                    region=args.region)
else:
    con_cf = cloudformation.connection.CloudFormationConnection(aws_access_key_id=ec2_key,
                                                                aws_secret_access_key=ec2_secret_key,
                                                                region=region)

con_ec2 = ec2.connect_to_region(args.region,
                                aws_access_key_id=ec2_key,
                                aws_secret_access_key=ec2_secret_key)

if not con_cf or not con_ec2:
    logging.error("Create CF/EC2 connections: " + args.region)
    sys.exit(1)

STACK_ID = "STACK" + ''.join(random.choice(string.ascii_lowercase) for x in range(10))
logging.info("Creating stack with ID " + STACK_ID)

parameters = []
try:
    if args.parameters:
        for param in args.parameters:
            parameters.append(tuple(param.split('=')))
except:
    logging.error("Wrong parameters format")
    sys.exit(1)

parameters.append(("KeyName", ssh_key_name))

if args.dry_run:
    sys.exit(0)

con_cf.create_stack(STACK_ID, template_body=json_body,
                    parameters=parameters, timeout_in_minutes=args.timeout)

is_complete = False
result = False
while not is_complete:
    time.sleep(10)
    try:
        for event in con_cf.describe_stack_events(STACK_ID):
            if event.resource_type == "AWS::CloudFormation::Stack" and event.resource_status == "CREATE_COMPLETE":
                logging.info("Stack creation completed")
                is_complete = True
                result = True
                break
            if event.resource_type == "AWS::CloudFormation::Stack" and event.resource_status == "ROLLBACK_COMPLETE":
                logging.info("Stack creation failed")
                is_complete = True
                break
    except:
        # Sometimes 'Rate exceeded' happens
        pass

if not result:
    sys.exit(1)

instances = []
for res in con_cf.describe_stack_resources(STACK_ID):
    # we do care about instances only
    if res.resource_type == 'AWS::EC2::Instance' and res.physical_resource_id:
        logging.debug("Instance " + res.physical_resource_id + " created")
        instances.append(res.physical_resource_id)

instances_detail = []
hostsfile = tempfile.NamedTemporaryFile(delete=False)
logging.debug("Created temporary file for /etc/hosts " + hostsfile.name)
yamlfile = tempfile.NamedTemporaryFile(delete=False)
logging.debug("Created temporary YAML config " + yamlfile.name)
for i in con_ec2.get_all_instances():
    for ii in  i.instances:
        if ii.id in instances:
            try:
                public_hostname = ii.tags["PublicHostname"]
            except KeyError:
                public_hostname = None
            try:
                private_hostname = ii.tags["PrivateHostname"]
            except KeyError:
                private_hostname = None
            try:
                role = ii.tags["Role"]
            except KeyError:
                role = None

            if ii.ip_address:
                public_ip = ii.ip_address
            else:
                public_ip = ii.private_ip_address
            private_ip = ii.private_ip_address

            details_dict = {"id": ii.id,
                            "public_hostname": public_hostname,
                            "private_hostname": private_hostname,
                            "role": role,
                            "public_ip": public_ip,
                            "private_ip": private_ip}

            for tag_key in ii.tags.keys():
                if tag_key not in ["PublicHostname", "PrivateHostname", "Role"]:
                    details_dict[tag_key] = ii.tags[tag_key]

            instances_detail.append(details_dict)

            if private_hostname and private_ip:
                hostsfile.write(private_ip + "\t" + private_hostname + "\n")
            if public_hostname and public_ip:
                hostsfile.write(public_ip + "\t" + public_hostname + "\n")
yamlconfig = {'Instances': sorted(instances_detail[:], lambda x, y: cmp(str(x['Name']), str(y['Name'])), reverse=True)}
yamlfile.write(yaml.safe_dump(yamlconfig))
yamlfile.close()
hostsfile.close()
logging.debug(instances_detail)
main_keys = []
result = []
for instance in instances_detail:
    if instance["public_ip"]:
        ip = instance["public_ip"]
        result_item = dict(role=str(instance['role']), hostname=str(instance['public_hostname']), ip=str(ip))
        logging.info("Instance with public ip created: %s", result_item)
    else:
        ip = instance["private_ip"]
        result_item = dict(role=str(instance['role']), hostname=str(instance['private_hostname']), ip=str(ip))
        logging.info("Instance with private ip created: %s", result_item)
    result.append(result_item)
    (instance["client"], instance["sftp"]) = setup_host_ssh(ip, ssh_key)
    if instance["role"] == "Main":
        main_keys.append(setup_main(instance["client"]))

for instance in instances_detail:
    if instance["private_hostname"]:
        hostname = instance["private_hostname"]
    else:
        hostname = instance["public_hostname"]
    instance['hostname'] = hostname
    setup_script = None
    if instance["role"] == "Main" and args.mainsetup:
        setup_script = args.mainsetup
    if instance["role"] != "Main" and args.instancesetup:
        setup_script = args.instancesetup

    setup_subordinate(instance["client"], instance["sftp"], hostname,
                hostsfile.name, yamlfile.name, main_keys, setup_script)

# --- close the channels
for instance in instances_detail:
    logging.debug('closing instance %s channel', instance['hostname'])
    try:
        instance['client'].close()
    except Exception as e:
        logging.warning('closing %s client channel: %s', instance['hostname'], e)
    finally:
        logging.debug('client %s channel closed', instance['hostname'])
    logging.debug('closing client %s sftp channel', instance['hostname'])
    try:
        instance['sftp'].close()
    except Exception as e:
        logging.warning('closing %s sftp channel: %s', instance['hostname'], e)
    finally:
        logging.debug('client %s sftp channel closed', instance['hostname'])

# --- dump the result
print '# --- instances created ---'
yaml.dump(result, sys.stdout)
# miserable hack --- cannot make paramiko not hang upon exit
import os
os.system('kill %d' % os.getpid())
