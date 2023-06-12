import yaml
from yaml.loader import SafeLoader
from pyVim import connect
from pyVmomi import vim
import atexit
import ssl

# vSphere connection parameters
vcenter_ip = ''
username = ''
password = ''
context = ssl._create_unverified_context()

with open('details.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)
    vcenter_ip=data['vcenter_ip']
    username=data['username']
    password=data['password']

# Connect to vCenter
try:
    si = connect.SmartConnect(
        host=vcenter_ip,
        user=username,
        pwd=password,
        sslContext=context
    )
    atexit.register(connect.Disconnect, si)
    content = si.RetrieveContent()
except Exception as e:
    print(f"Error connecting to vCenter: {str(e)}")
    exit(1)

root_folder = content.rootFolder
# Traverse the inventory tree and find ESXi hosts
esxi_hosts = []
container_view = content.viewManager.CreateContainerView(
    container=root_folder,
    type=[vim.HostSystem],
    recursive=True
)
for host in container_view.view:
    esxi_hosts.append(host)

# Print ESXi host details
for host in esxi_hosts:
    print(f"ESXi Host: {host.name}")
    print(f"IP Address: {host.summary.managementServerIp}")
    print(f"Product Version: {host.summary.config.product.fullName}")
    print("--- VMs ---")
    for vm in host.vm:
        print(f"VM Name: {vm.name}")
    print("------------")
    print(f"---------------------------------------------------")
