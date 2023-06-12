from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import atexit
import ssl

context = ssl._create_unverified_context()
# Configuration variables
vcenter_server = '16.182.25.237'
vcenter_user = 'administrator@vsphere.local'
vcenter_password = 'Nim123Boli#'
datacenter_name = 'op360-g10s06.hstlabs.glcp.hpecorp.net'
cluster_name = 'cluster-5'
vm_name = 'sachin_144.79'
vm_folder = 'houston'
datastore_name = 'datastore1 (4)'
ova_path = 'http://10.14.144.19/golden-image/glcp-onprem-combined-1.0.0-10.ova'

# Connect to vCenter Server
si = SmartConnectNoSSL(
    host=vcenter_server,
    user=vcenter_user,
    pwd=vcenter_password,
    sslContext=context
)
atexit.register(Disconnect, si)

# Retrieve necessary objects
content = si.RetrieveContent()
datacenter = content.rootFolder.childEntity[0]
cluster = datacenter.hostFolder.childEntity[0]
datastore = None

for ds in cluster.datastore:
    if ds.name == datastore_name:
        datastore = ds
        break

# Load OVA file as a VM template
spec_params = vim.OvfManager.CreateImportSpecParams()
ovf_manager = content.ovfManager
ovf_import_spec = ovf_manager.CreateImportSpec(
    ovfDescriptor=None,
    resourcePool=cluster.resourcePool,
    datastore=datastore,
    cisp=spec_params
)

# Get the OVA file content
with open(ova_path, 'rb') as f:
    ova_content = f.read()

# Create the VM from the OVA
vm_folder_obj = datacenter.vmFolder
ovf_import_spec.importSpec.configSpec.name = vm_name
ovf_import_spec.importSpec.configSpec.vmPathName = vm_folder

task = ovf_manager.ImportVApp(
    folder=vm_folder_obj,
    spec=ovf_import_spec.importSpec,
    vappImportSpec=ovf_import_spec.importSpec,
    encryptionKey=None,
    host=cluster.host[0]
)

# Monitor the task for completion
while task.info.state == vim.TaskInfo.State.running:
    continue

# Check for errors
if task.info.state == vim.TaskInfo.State.success:
    print("VM created successfully.")
else:
    print("Error creating VM:", task.info.error.msg)