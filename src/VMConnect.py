# Import statemennts
import yaml
from yaml.loader import SafeLoader
from pyvim import connect
from pyVmomi import vim
import atexit
import ssl

class VMConnect:
    flag = 0
    def __init__(self):
        self.vcenter_ip = None
        self.username = None
        self.password = None
        self.context = ssl._create_unverified_context()
        self.container_view = None
        self.content = None

    # Function to read the 
    def readYaml(self):
        with open('details.yaml') as file_yaml:
            self.data_yaml = yaml.load(file_yaml, Loader=SafeLoader)
            self.vcenter_ip = self.data_yaml['vcenter_ip']
            self.username = self.data_yaml['username']
            self.password = self.data_yaml['password']
            
    def VCenterConnect(self):
        try:
            si=connect.SmartConnect(
                host = self.vcenter_ip,
                user = self.username,
                pwd = self.password,
                sslContext = self.context
            )
            atexit.register(connect.Disconnect, si)
            self.content = si.RetrieveContent()
        except Exception as e:
            print(f"Error connecting to vCenter: {str(e)}")
            exit(1)
        finally:    
            root_folder = self.content.rootFolder
            self.container_view = self.content.viewManager.CreateContainerView(
                container=root_folder,
                type=[vim.HostSystem],
                recursive=True
            )  
    def get_content(self):
        return self.content
    
    def get_container_view(self):
        return self.container_view
   







