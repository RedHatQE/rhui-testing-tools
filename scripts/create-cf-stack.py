#! /usr/bin/python -tt

from paramiko import SSHClient
from boto import cloudformation
from boto import regioninfo
from boto import ec2
import argparse
import ConfigParser
import time
import logging
import sys
import random
import string
import json
import tempfile
import paramiko
import yaml


class SyncSSHClient(SSHClient):
    '''
    Special class for sync'ed commands execution over ssh
    '''
    def run_sync(self, command):
        stdin, stdout, stderr = self.exec_command(command)
        stdout.channel.recv_exit_status()
        return stdin, stdout, stderr


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
            client.connect(hostname=hostname,
                           username="root",
                           key_filename=key)
            stdin, stdout, stderr = client.run_sync("whoami")
            output = stdout.read()
            logging.debug("OUTPUT for 'whoami': " + output)
            if output != "root\n":
                #It's forbidden to login under 'root', switching this off
                client.connect(hostname=hostname,
                               username="ec2-user",
                               key_filename=key)
                stdin, stdout, stderr = client.run_sync("su -c 'cp -af /home/ec2-user/.ssh/authorized_keys /root/.ssh/authorized_keys; chown root.root /root/.ssh/authorized_keys'")
                output = stdout.read()
                logging.debug("OUTPUT (ssh keys setup): " + output)
                stdin, stdout, stderr = client.run_sync("su -c \"sed -i 's,disable_root: 1,disable_root: 0,' /etc/cloud/cloud.cfg\"")
                output = stdout.read()
                logging.debug("OUTPUT (cloud.cfg): " + output)
                client.connect(hostname=hostname, username="root", key_filename=key)
            sftp = client.open_sftp()
            break
        except Exception, e:
            logging.debug('Caught exception in setup_host_ssh: ' + str(e.__class__) + ': ' + str(e))
            ntries -= 1
        time.sleep(10)
    if ntries == 0:
        logging.error("Failed to setup ssh to " + hostaname + " using " + key + " key")
    return (client, sftp)


def setup_master(client):
    '''
    Create ssh key on master node.
    '''
    try:
        client.run_sync("rm -f /root/.ssh/id_rsa{,.pub}; ssh-keygen -t rsa -b 2048 -N '' -f /root/.ssh/id_rsa")
        stdin, stdout, stderr = client.run_sync("cat /root/.ssh/id_rsa.pub")
        output = stdout.read()
        logging.debug("Generated ssh master key: " + output)
        return output
    except Exception, e:
        logging.error('Caught exception in setup_master: ' + str(e.__class__) + ': ' + str(e))
        return None


def setup_slave(client, sftp, hostname, hostsfile, yamlfile, master_keys):
    '''
    Setup slave node.
    - Allow connections from masters
    - Set hostname
    - Write /etc/hosts
    - Write /etc/rhui-testing.yaml
    '''
    try:
        client.run_sync("touch /tmp/hosts")
        sftp.put(hostsfile, "/tmp/hosts")
        client.run_sync("cat /etc/hosts >> /tmp/hosts")
        client.run_sync("sort -u /tmp/hosts > /etc/hosts")
        sftp.put(yamlfile, "/etc/rhui-testing.yaml")
        client.run_sync("touch /etc/rhui-testing.yaml")
        if hostname:
            client.run_sync("hostname " + hostname)
            client.run_sync("sed -i 's,^HOSTNAME=.*$,HOSTNAME=" + hostname + ",' /etc/sysconfig/network")
        for key in master_keys:
            if key:
                client.run_sync("cat /root/.ssh/authorized_keys > /root/.ssh/authorized_keys.new")
                client.run_sync("echo '" + key + "' >> /root/.ssh/authorized_keys.new")
                client.run_sync("sort -u /root/.ssh/authorized_keys.new | grep -v '^$' > /root/.ssh/authorized_keys")
    except Exception, e:
        logging.error('Caught exception in setup_slave: ' + str(e.__class__) + ': ' + str(e))


argparser = argparse.ArgumentParser(description='Create CloudFormation stack and run the testing')
argparser.add_argument('--cloudformation', required=True,
                       help='use supplied JSON file to setup CloudFormation stack')
argparser.add_argument('--config',
                       default="/etc/rhui-testing.cfg", help='use supplied config file')
argparser.add_argument('--debug', action='store_const', const=True,
                       default=False, help='debug mode')
argparser.add_argument('--dry-run', action='store_const', const=True,
                       default=False, help='do not run stack creation, validate only')
argparser.add_argument('--parameters', metavar='<expr>', nargs="*",
                       help="space-separated NAME=VALUE list of parametars")
argparser.add_argument('--region',
                       default="us-east-1", help='use specified region')
argparser.add_argument('--timeout', type=int,
                       default=10, help='stack creation timeout')
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

config = ConfigParser.ConfigParser()
# Try all possible configs
config_read = False
for possible_config in [args.config, "rhui-testing.cfg", "/etc/validation.cfg"]:
    if config.read(possible_config) != []:
        logging.debug("reading config values from " + possible_config)
        config_read = True
        break
    else:
        logging.debug("unable to read config values from " + possible_config)

if not config_read:
    logging.error("You should create rhui-testing.cfg in /etc or current directory or use --config option!")
    sys.exit(1)

AWS_ACCESS_KEY_ID = config.get('EC2-Keys', 'ec2-key')
AWS_SECRET_ACCESS_KEY = config.get('EC2-Keys', 'ec2-secret-key')
if None in [AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY]:
    logging.error("You must specify ec2 credentials in configfile!")
    sys.exit(1)
SSHKEY_NAME_AP_S = config.get('SSH-Info', 'ssh-key-name_apsouth')
SSHKEY_AP_S = config.get('SSH-Info', 'ssh-key-path_apsouth')
SSHKEY_NAME_AP_N = config.get('SSH-Info', 'ssh-key-name_apnorth')
SSHKEY_AP_N = config.get('SSH-Info', 'ssh-key-path_apnorth')
SSHKEY_NAME_EU_W = config.get('SSH-Info', 'ssh-key-name_euwest')
SSHKEY_EU_W = config.get('SSH-Info', 'ssh-key-path_euwest')
SSHKEY_NAME_US_W = config.get('SSH-Info', 'ssh-key-name_uswest')
SSHKEY_US_W = config.get('SSH-Info', 'ssh-key-path_uswest')
SSHKEY_NAME_US_E = config.get('SSH-Info', 'ssh-key-name_useast')
SSHKEY_US_E = config.get('SSH-Info', 'ssh-key-path_useast')
SSHKEY_NAME_US_O = config.get('SSH-Info', 'ssh-key-name_uswest-oregon')
SSHKEY_US_O = config.get('SSH-Info', 'ssh-key-path_uswest-oregon')
SSHKEY_SA_E = config.get('SSH-Info', 'ssh-key-path_saeast')
SSHKEY_NAME_SA_E = config.get('SSH-Info', 'ssh-key-name_saeast')

if REGION == "us-east-1":
    SSHKEY = SSHKEY_US_E
    SSHKEYNAME = SSHKEY_NAME_US_E
elif REGION == "us-west-2":
    SSHKEY = SSHKEY_US_O
    SSHKEYNAME = SSHKEY_NAME_US_O
elif REGION == "us-west-1":
    SSHKEY = SSHKEY_US_W
    SSHKEYNAME = SSHKEY_NAME_US_W
elif REGION == "eu-west-1":
    SSHKEY = SSHKEY_EU_W
    SSHKEYNAME = SSHKEY_NAME_EU_W
elif REGION == "ap-southeast-1":
    SSHKEY = SSHKEY_AP_S
    SSHKEYNAME = SSHKEY_NAME_AP_S
elif REGION == "ap-northeast-1":
    SSHKEY = SSHKEY_AP_N
    SSHKEYNAME = SSHKEY_NAME_AP_N
elif REGION == "sa-east-1":
    SSHKEY = SSHKEY_SA_E
    SSHKEYNAME = SSHKEY_NAME_SA_E
else:
    logging.error("Unknown region " + REGION)
    sys.exit(1)

try:
    json_file = open(args.cloudformation, "r")
    json_body = json_file.read()
    json_file.close()
    #do simple json validation
    json.loads(json_body)
except IOError as e:
    logging.error("I/O error({0}): {1}".format(e.errno, e.strerror))
    sys.exit(1)
except ValueError as e:
    logging.error("Invalid JSON file " + args.cloudformation)
    sys.exit(1)
except:
    logging.error("Unexpected error: " + str(sys.exc_info()[0]))
    sys.exit(1)

region = regioninfo.RegionInfo(name=args.region,
                               endpoint="cloudformation." + args.region + ".amazonaws.com")

if not region:
    logging.error("Unable to connect to region: " + args.region)
    sys.exit(1)

con_cf = cloudformation.connection.CloudFormationConnection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                                            region=region)

con_ec2 = ec2.connect_to_region(args.region,
                                aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

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

parameters.append(("KeyName", SSHKEYNAME))

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

            public_ip = ii.ip_address
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
yamlconfig = {'Instances': instances_detail[:]}
yamlfile.write(yaml.safe_dump(yamlconfig))
yamlfile.close()
hostsfile.close()
logging.debug(instances_detail)
master_keys = []
for instance in instances_detail:
    if instance["public_ip"]:
        ip = instance["public_ip"]
        logging.info("Instance with public ip created: " + instance["role"] + ":" + instance["public_hostname"] + ":" + ip)
    else:
        ip = instance["private_ip"]
        logging.info("Instance with private ip created: " + instance["role"] + ":" + instance["private_hostname"] + ":" + ip)
    (instance["client"], instance["sftp"]) = setup_host_ssh(ip, SSHKEY)
    if instance["role"] == "Master":
        master_keys.append(setup_master(instance["client"]))

for instance in instances_detail:
    if instance["private_hostname"]:
        hostname = instance["private_hostname"]
    else:
        hostname = instance["public_hostname"]
    setup_slave(instance["client"], instance["sftp"], hostname,
                hostsfile.name, yamlfile.name, master_keys)
