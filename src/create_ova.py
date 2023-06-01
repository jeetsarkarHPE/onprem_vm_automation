from pyVmomi import vim
class CreateOVA:
    def __init__(self,ova_url, datacenter_name, cluster_name, datastore_name, network_name,vm_name,content ):
        self.ova_url = ova_url
        self.datacenter_name = datacenter_name
        self.cluster_name = cluster_name
        self.datastore_name = datastore_name
        self.network_name = network_name
        self.vm_name = vm_name
        self.content = content
       
        self.datacenter = self.content.rootFolder.childEntity[0]
        self.cluster = self.datacenter.hostFolder.childEntity[0]
        self.datastore = self.datacenter.datastore[0]

        # Create the deployment specification
        self.deployment_spec = vim.OvfManager.DeploymentOption()
        # self.deployment_spec.powerOn = False
        # self.deployment_spec.name = self.vm_name

        # Retrieve the OVF descriptor from the URL
        self.ovf_manager = self.content.ovfManager
        self.ovf_descriptor = self.ovf_manager.ParseDescriptor(self.ova_url)

        # Create the import spec
        self.import_spec_params = vim.OvfManager.CreateImportSpecParams()
        self.import_spec_params.ovfDescriptor = self.ovf_descriptor
        self.import_spec_params.entityName = self.vm_name
        self.import_spec_params.deploymentSpec = self.deployment_spec
        self.import_spec_params.networkMapping = []

        # Deploy the OVA
    def deploying_ova(self):
        self.resource_pool = self.cluster.resourcePool
        folder = self.datacenter.vmFolder
        task = self.import_spec.importSpec.importVApp(self.resource_pool, folder)
        #Wait for the task to complete
        # i=0
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            pass
            # if i%10 == 0:
                # print(i)
                # i+=1

            #Check if the task completed successfully
        if task.info.state == vim.TaskInfo.State.success:
            print('Virtual machine created successfully!')
        else:
            print('Error deploying virtual machine:', task.info.error)

            # Disconnect from vCenter server
        self.connect.Disconnect(self.service_instance)

