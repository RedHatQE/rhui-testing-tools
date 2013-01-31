RHUI testing tools
==================

Contents:
--------
Scipts (scripts/, placed under /usr/bin in rpm):
    create-cf-stack.py: creates CloudForamtion stack of resources (cnf/ contains examples)
    remote-rhui-installer.sh: run remote RHUI installer
    rhui-installer.py: RHUI installer (must be run on 'Master' node)

RHUI tests (rhui-tests/, placed under /usr/share/rhui-testing-tools/rhui-tests in rpm):
    test-rhui-workflow-simple.py: simple workflow (basic test)


Basic usage:
-----------
1) Create cloudformation stack for testing:
    without rpm:
        scripts/create-cf-stack.py  --region eu-west-1
    with rpm installed:
        create-cf-stack.py --region eu-west-1

    use --rhel5, --rhel6, --cds, --proxy parameters to specify required configuration

    /etc/validation.yaml is used as config file. An example:
    ec2: {ec2-key: AAAAAAAAAAAAAAAAAAAA, ec2-secret-key: B0B0B0B0B0B0B0B0B0B0a1a1a1a1a1a1a1a1a1a1}
    ssh:
      ap-northeast-1: [user-ap-northeast-1, /home/user/.pem/ap-northeast-1-iam.pem]
      ap-southeast-1: [user-ap-southeast-1, /home/user/.pem/ap-southeast-1-iam.pem]
      ap-southeast-2: [user-ap-southeast-2, /home/user/.pem/ap-southeast-2-iam.pem]
      eu-west-1: [user-eu-west-1, /home/user/.pem/eu-west-1-iam.pem]
      sa-east-1: [user-sa-east-1, /home/user/.pem/sa-east-1-iam.pem]
      us-east-1: [user-us-east-1, /home/user/.pem/us-east-1-iam.pem]
      us-west-1: [user-us-west-1, /home/user/.pem/us-west-1-iam.pem]
      us-west-2: [user-us-west-2, /home/user/.pem/us-west-2-iam.pem]

2) Build actual rhui-testing-tools package (if you have no) using 'tito' tool:
    tito build --rpm --test

3) Run remote rhui installer:
    without rpm:
        scripts/remote-rhui-installer.sh &lt;master ip&gt; &lt;your-region-ssh-key&gt; &lt;RHUI iso&gt; &lt;rhui-testing-tools.rpm&gt;
    with rpm installed:
        remote-rhui-installer.sh &lt;master ip&gt; &lt;your-region-ssh-key&gt; &lt;RHUI iso&gt; &lt;rhui-testing-tools.rpm&gt;
    You can get rhui-testing-tools RPM here: https://rhuiqerpm.s3.amazonaws.com/index.html

4) Go to master
    ssh -i &lt;your-region-ssh-key&gt; &lt;master ip&gt;

5) Run simple workflow
    /usr/share/rhui-testing-tools/rhui-tests/test-rhui-workflow-simple.py [--cert your-rh-entitlement-certificate]
