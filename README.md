RHUI testing tools
==================

Contents:
--------
Scipts (scripts/, placed under /usr/bin in rpm):
    create-cf-stack.py: creates CloudForamtion stack of resources (cnf/ contains examples)
    remote-rhui-installer.sh: run remote RHUI installer
    rhui-installer.py: RHUI installer (must be run on 'Master' node)

RHUI tests (rhui-tests/, placed under /usr/share/rhui-testing-tools/rhui-tests in rpm):
    rhui-workflow-simple.py: simple workflow (basic test)


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
        scripts/remote-rhui-installer.sh <master ip> <your-region-ssh-key> <RHUI iso> <rhui-testing-tools.rpm>
    with rpm installed:
        remote-rhui-installer.sh <master ip> <your-region-ssh-key> <RHUI iso> <rhui-testing-tools.rpm>

4) Go to master
    ssh -i <your-region-ssh-key> <master ip>

5) Run simple workflow
    /usr/share/rhui-testing-tools/rhui-tests/rhui-workflow-simple.py
