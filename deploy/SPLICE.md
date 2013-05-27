Deploying splice
* save satellite iso as _/tmp/satellite.iso_
* save satellite cert as _/tmp/satellite-cert.xml_
* save sam iso as _/tmp/sam.iso_
* ../scripts/create-cf-stack.py --sam --satellite                                                                                                                                                                                            
* save the master node ip address:                                                                                                                                                                                                           
  cat \> inventory.cfg                                                                                                                                                                                                                        
  [MASTER]                                                                                                                                                                                                                                   
  \<the IP address of master\>                                                                                                                                                                                                                 
  ^D                                                                                                                                                                                                                                         
* ansible-playbook -i inventory.cfg master-installer.yml --private-key <your ssh private key>  -e "rhn_user=\<rhn user\> rhn_password=\<rhn_password\> rhn_system_name=\<system name\>"                                                            
* ssh -i \<your ssh private key\> root@\<master ip\>                                                                                                                                                                                             
* cd /usr/src/rhui-testing-tools/deploy                                                                                                                                                                                                      
* ansible-playbook -i common/modules/rhui_inventory.py installer.yml
