Deploying splice
================

####Prerequisites
```
/tmp/satellite.iso
/tmp/satellite-cert.xml
/tmp/sam.iso
```

####Stack and Master node
```
../scripts/create-cf-stack.py --sam --satellite
# save the master ip address in your inventory
ansible-playbook -i inventory.cfg master-installer.yml --private-key <your ssh private key>  -e \
  "rhn_user=<rhn user> rhn_password=<rhn password> rhn_system_name=<system name>"
ssh -i <your ssh private key> root@<master ip>
```

####Splice deployment; on master node
```
cd /usr/src/rhui-testing-tools/deploy
ansible-playbook -i common/modules/rhui_inventory.py installer.yml
```
