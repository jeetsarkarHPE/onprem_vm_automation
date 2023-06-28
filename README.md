## Automation of the OVA deployment

This repository consists of code base that can be used for automating the deployment of the Virtual Machines from an OVA file. 
It consists of 3 main directories - Test, ova_deploy and vm_config.
#### Test Directory
1. The test directories consist of codes that are developed during the experimental phase of the project. 
2. These codebases are to be referred only to take some help or get an idea of the code. 

#### delete_vm 
1. The destroy.py is the main code to run the delete function. The VM name (case sensitive) needs to be mentioned. 
2. The tasks.py is imported in the destroy. It is a helper module for the task operations and needs to be included.
   
#### ova_deploy Directory
1. The ova_deploy directory consist of the codes that are able to execute the deployment of Virtual Machine from an OVA file. 
2. The directory has 2 main codes - newOnpremCode.py and service_instance.py
3. The service_instance.py determines the most preferred API version supported by the specified server, then connect to the specified server, which is the vsphere client, using that API version, login and return the service instance object.
4. The newOnpremCode.py is used for the deployment purposes.
