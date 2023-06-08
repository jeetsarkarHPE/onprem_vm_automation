python3 deploy_ope_vm.py
        -oU "http://16.182.31.122:9000/golden-image/glcp-onprem-combined-1.0.0-10.ova"
        -oH "op360-g10s04-vm01.hstlabs.glcp.hpecorp.net"
        -vcenter "m2-dl380g10-74-vm01.mip.storage.hpecorp.net"
        -u "administrator@vsphere.local"
        -p "Nim123Boli#"
        -ds "datastore_1_3"
        -dc "cluster-5"



ovftool --skipManifestCheck --noSSLVerify --acceptAllEulas --powerOn --X:logToConsole --net:Network="VM Network" --prop:sys_:_hostname=op360-g10s04-vm01.hstlabs.glcp.hpecorp.net -ds=datastore_1_3 --name=test_automation /home/esroot/sachinthra/automation-test/glcp-onprem-combined-1.0.0-10.ova vi://administrator%40vsphere.local:Nim123Boli%23@m2-dl380g10-74-vm01.mip.storage.hpecorp.net/Datacenter/host/cluster-5/