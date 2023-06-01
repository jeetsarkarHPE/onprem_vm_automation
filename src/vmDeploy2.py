import ssl
from pyVmomi import vim, vmodl
from pyvim.connect import SmartConnect, Disconnect
import atexit

def deploy_vm_from_ova(url, name, datastore, cluster):
    # Disable SSL certificate verification (only for testing purposes)
    # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    # context.verify_mode = ssl.CERT_NONE
    context = ssl._create_unverified_context()

    # Connect to vCenter Server
    try:
        si = SmartConnect(host="16.182.25.237",
                                        user="administrator@vsphere.local",
                                        pwd="Nim123Boli#",
                                        
                                        sslContext=context)
        atexit.register(Disconnect, si)
    except vmodl.MethodFault as error:
        print("Failed to connect to vCenter Server: %s" % error.msg)
        return

    # Find the datastore and cluster objects
    content = si.RetrieveContent()
    datacenter = content.rootFolder.childEntity[0]
    datastore = get_datastore(datacenter, datastore)
    cluster = get_cluster(datacenter, cluster)

    if not datastore or not cluster:
        print("Datastore or cluster not found.")
        return

    # Deploy the virtual machine from OVA
    try:
        ovf_manager = content.ovfManager
        ovf_deployer = ovf_manager.CreateDeployOVFTask(ovf_url=url,
                                                       name=name,
                                                       vmFolder=datacenter.vmFolder,
                                                       diskProvisioning="thin",
                                                       datastore=datastore,
                                                       networkMapping=None,
                                                       cisp=True,
                                                       cluster=cluster)
        while ovf_deployer.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            pass

        if ovf_deployer.info.state == vim.TaskInfo.State.success:
            print("Virtual machine deployed successfully.")
        else:
            print("Failed to deploy virtual machine: %s" % ovf_deployer.info.error.localizedMessage)
    except vmodl.MethodFault as error:
        print("Failed to deploy virtual machine: %s" % error.msg)

def get_datastore(datacenter, datastore_name):
    for datastore in datacenter.datastore:
        if datastore.name == datastore_name:
            return datastore
    return None

def get_cluster(datacenter, cluster_name):
    for cluster in datacenter.hostFolder.childEntity:
        if cluster.name == cluster_name:
            return cluster
    return None

# Usage example
ova_url = "~/golden-image/glcp-onprem-combined-1.0.0-10.ova"
vm_name = "jeet_144.79_1.0.0-10_testing"
datastore_name = "datastore1 (4)"
cluster_name = "cluster-5"

deploy_vm_from_ova(ova_url, vm_name, datastore_name, cluster_name)
