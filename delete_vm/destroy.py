
from __future__ import print_function
import atexit
import requests
from pyvim import connect
from pyVmomi import vim
import tasks
requests.packages.urllib3.disable_warnings()
import sys
import os

__author__="jeetsarkarHPE"
si = connect.SmartConnect(host="m2-dl380g10-74-vm01.mip.storage.hpecorp.net",
                                            user="administrator@vsphere.local",
                                            pwd="Nim123Boli#",
                                            disableSslCertValidation=True)
atexit.register(connect.Disconnect, si)

def main():
    datacenter = si.content.rootFolder
    datacenter_choice = int(input("enter 1 for houston 2 for milpitas: "))
    if(datacenter_choice==1):
        datacenter = si.content.rootFolder.childEntity[0]
    else:
        datacenter = si.content.rootFolder.childEntity[1]

    
    obj = deleteVM(si)
    obj.vm_deletion(si,datacenter,si.content.viewManager)


class deleteVM:
    __author__ = "jeetsarkarHPE"
    # datacenter = si.content.rootFolder.childEntity[0]
    view_manager = si.content.viewManager
    def __init__(self,si):
        self.vmname = str
        self.VM = None
    
    def vm_deletion(self,si,datacenter,view_manager):
        self.vmname = input("Enter the name of the VM to be deleted : ")
        try:
            container_viewComputeResource = view_manager.CreateContainerView(datacenter, [vim.ComputeResource], True)
            for cluster in container_viewComputeResource.view:
                container_viewHostSystem = view_manager.CreateContainerView(cluster,[vim.HostSystem],True)
                for host in container_viewHostSystem.view:  
                    container_viewVM = view_manager.CreateContainerView(host,[vim.VirtualMachine],True)
                    for vm in container_viewVM.view:
                        if(vm.name==self.vmname):
                            self.VM = vm
            
            print(f"Found: {self.VM.name}")
            print(f"The current powerState is: {self.VM.runtime.powerState}")
            print(f"Attempting to power off {self.VM.name}")
            TASK = self.VM.PowerOffVM_Task()
            tasks.wait_for_tasks(si, [TASK])
            print(f"{TASK.info.state}")
            print("Destroying VM from vSphere.")
            TASK = self.VM.Destroy_Task()
            tasks.wait_for_tasks(si, [TASK])
            print("Done.")
            
        except:
            raise SystemExit("Unable to locate VirtualMachine.")

if __name__ == "__main__":
    sys.exit(main())