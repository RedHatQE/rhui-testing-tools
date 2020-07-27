#! /bin/bash -ex

# logging setup
exec > /tmp/main_setup.log
exec 2>&1

# prerequisities
yum install -y git make PyYAML python-paramiko python-jinja2

# fetch and install required source code
pushd /usr/src

# ansible
git clone https://github.com/ansible/ansible.git
pushd ansible
make install
popd # ansible

# rhui-testing-tools
git clone https://github.com/RedHatQE/rhui-testing-tools.git
pushd rhui-testing-tools
git checkout with_ansible

# conduct the orchestration
pushd deploy
ansible-playbook -i common/modules/rhui_inventory.py -vvv rhui-installer.yml

popd # deploy
popd # rhui-testing-tools
popd # /usr/src
