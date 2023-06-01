from VMConnect import VMConnect
from create_ova import CreateOVA
vmconnect= VMConnect()
vmconnect.readYaml()
vmconnect.VCenterConnect()
container_view = vmconnect.get_container_view()

ova = CreateOVA(
    ova_url='~/golden-image/glcp-onprem-combined-1.0.0-10.ova',
    datacenter_name='op360-g10s06.hstlabs.glcp.hpecorp.net', 
    cluster_name='cluster-5', 
    datastore_name='datastore1 (4)', 
    network_name='VM Network',
    vm_name='jeet_144.79_1.0.0-10_testing',
    content = vmconnect.get_content()
)

try:
    ova.deploying_ova()
except Exception as e:
    print(e)
# esxi_hosts =[]
# for host in container_view.view:
#     esxi_hosts.append(host)
#     print(host)

# class getDetails:
#        init(self, host):
#         self.host
       


# for host in esxi_hosts:
#             print(f"ESXi Host: {host.name}")
#             print(f"ESXi Host-datastore: {host.datastore}")
#             print(f"IP Address: {host.summary.managementServerIp}")
#             print(f"Product Version: {host.summary.config.product.fullName}")
#             print("--- VMs ---")
#             for vm in host.vm:
#                 print(f"VM Name: {vm.name}")
#             print("------------")
#             print(f"---------------------------------------------------")