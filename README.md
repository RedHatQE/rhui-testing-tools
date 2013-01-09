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
        scripts/create-cf-stack.py --cloudformation cfn/rhui_with_1cds_1cli.json --region eu-west-1
    with rpm installed:
        create-cf-stack.py --cloudformation /usr/share/rhui-testing-tools/cfn/rhui_with_1cds_1cli.json --region eu-west-1

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
