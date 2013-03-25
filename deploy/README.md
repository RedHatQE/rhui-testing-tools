Deploying with Ansible
=================

Dependencies to be able to install ansible from git:
* git
* make
* python-paramiko
* python-jinja2
* PyYAML

Deploying RHUI; assuming one stands in the directory _rhui-testing-tools/deploy_ on the _master node_
* make sure to copy a RHUI Iso file into _/tmp/rhui.iso_
* ansible-playbook -i common/modules/rhui_inventory.py rhui-installer.yml 

Debugging
* export ANSIBLE_KEEP_REMOTE_FILES=1
* ansible-playbook -i common/modules/rhui_inventory.py --list-tasks --list-hosts rhui-installer.py
* ansible-playbook -i common/modules/rhui_inventory.py -vvv rhui-installer.yml 
