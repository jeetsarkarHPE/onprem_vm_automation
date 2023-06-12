#!/usr/bin/env python
"""
Written by Nathan Prziborowski
Github: https://github.com/prziborowski

This code is released under the terms of the Apache 2
http://www.apache.org/licenses/LICENSE-2.0.html

Deploy an ova file either from a local path or a URL.
Most of the functionality is similar to ovf except that
that an OVA file is a "tarball" so tarfile module is leveraged.

"""
import os
import os.path
import ssl
import sys
import tarfile
import time

from threading import Timer
from six.moves.urllib.request import Request, urlopen

from tools import cli, service_instance

from pyVmomi import vim, vmodl

__author__ = 'prziborowski'


def main():
    parser = cli.Parser()
    parser.add_optional_arguments(cli.Argument.OVA_PATH, cli.Argument.DATACENTER_NAME,
                                  cli.Argument.RESOURCE_POOL, cli.Argument.DATASTORE_NAME)
    args = parser.get_args()
    si = service_instance.connect(args)

    if args.datacenter_name:
        datacenter = get_dc(si, args.datacenter_name)
    else:
        datacenter = si.content.rootFolder.childEntity[0]

    if args.resource_pool:
        resource_pool = get_rp(si, datacenter, args.resource_pool)
    else:
        resource_pool = get_largest_free_rp(si, datacenter)

    if args.datastore_name:
        datastore = get_ds(datacenter, args.datastore_name)
    else:
        datastore = get_largest_free_ds(datacenter)

    ovf_handle = OvfHandler(args.ova_path)

    ovf_manager = si.content.ovfManager
    # CreateImportSpecParams can specify many useful things such as
    # diskProvisioning (thin/thick/sparse/etc)
    # networkMapping (to map to networks)
    # propertyMapping (descriptor specific properties)
    cisp = vim.OvfManager.CreateImportSpecParams()
    cisr = ovf_manager.CreateImportSpec(
        ovf_handle.get_descriptor(), resource_pool, datastore, cisp)

    # These errors might be handleable by supporting the parameters in
    # CreateImportSpecParams
    if cisr.error:
        print("The following errors will prevent import of this OVA:")
        for error in cisr.error:
            print("%s" % error)
        return 1

    ovf_handle.set_spec(cisr)

    lease = resource_pool.ImportVApp(cisr.importSpec, datacenter.vmFolder)
    while lease.state == vim.HttpNfcLease.State.initializing:
        print("Waiting for lease to be ready...")
        time.sleep(1)

    if lease.state == vim.HttpNfcLease.State.error:
        print("Lease error: %s" % lease.error)
        return 1
    if lease.state == vim.HttpNfcLease.State.done:
        return 0

    print("Starting deploy...")
    return ovf_handle.upload_disks(lease, args.host)


def get_dc(si, name):
    """
    Get a datacenter by its name.
    """
    for datacenter in si.content.rootFolder.childEntity:
        if datacenter.name == name:
            return datacenter
    raise Exception('Failed to find datacenter named %s' % name)


def get_rp(si, datacenter, name):
    """
    Get a resource pool in the datacenter by its names.
    """
    view_manager = si.content.viewManager
    container_view = view_manager.CreateContainerView(datacenter, [vim.ResourcePool], True)
    for rp in container_view.view:
        if rp.name == name:
            return rp
    raise Exception('Failed to find resource pool named %s' % name)


def get_largest_free_rp(si, datacenter):
    """
    Get the largest free resource pool in the datacenter.
    """
    view_manager = si.content.viewManager
    container_view = view_manager.CreateContainerView(datacenter, [vim.ResourcePool], True)
    largest_rp = None
    largest_rp_free_memory = 0
    for rp in container_view.view:
        if rp.runtime.memory.freeMemory > largest_rp_free_memory:
            largest_rp_free_memory = rp.runtime.memory.freeMemory
            largest_rp = rp
    if largest_rp is None:
        raise Exception('Failed to find a resource pool with free memory')
    return largest_rp


def get_ds(datacenter, name):
    """
    Get a datastore in the datacenter by its name.
    """
    for datastore in datacenter.datastore:
        if datastore.name == name:
            return datastore
    raise Exception('Failed to find datastore named %s' % name)


def get_largest_free_ds(datacenter):
    """
    Get the largest free datastore in the datacenter.
    """
    largest_ds = None
    largest_ds_free_space = 0
    for datastore in datacenter.datastore:
        free_space = datastore.summary.freeSpace
        if free_space > largest_ds_free_space:
            largest_ds_free_space = free_space
            largest_ds = datastore
    if largest_ds is None:
        raise Exception('Failed to find a datastore with free space')
    return largest_ds


class OvfHandler(object):
    def __init__(self, path):
        self.path = path
        self.__spec = None
        self.__descriptor = None
        self.__disks = None
        self.__upload_file_paths = None

    def __read_descriptor(self):
        with tarfile.open(self.path, 'r') as tar:
            try:
                return tar.extractfile(self.path.split("/")[-1].split(".")[0] + ".ovf").read()
            except KeyError:
                raise Exception('Failed to find OVF descriptor in OVA')

    def get_descriptor(self):
        if self.__descriptor is None:
            self.__descriptor = self.__read_descriptor()
        return self.__descriptor

    def get_disks(self):
        if self.__disks is None:
            self.__disks = self.__get_disks()
        return self.__disks

    def __get_disks(self):
        descriptor = self.get_descriptor()
        disks = []
        for line in descriptor.split('\n'):
            if "<File ovf:href=" in line:
                file_path = line.split('"')[1]
                disks.append(file_path)
        return disks

    def set_spec(self, spec):
        self.__spec = spec

    def upload_disks(self, lease, host):
        if self.__upload_file_paths is None:
            self.__upload_file_paths = self.__get_upload_file_paths(lease)

        total_files = len(self.__upload_file_paths)
        for index, file_path in enumerate(self.__upload_file_paths, start=1):
            print("Uploading disk %d of %d" % (index, total_files))
            self.__upload_disk(lease, file_path, host)
            print("Upload completed for disk %d of %d" % (index, total_files))

        lease.Complete()

    def __get_upload_file_paths(self, lease):
        file_paths = []
        for device_url in lease.info.deviceUrl:
            file_paths.append(device_url.url.replace('*', host))
        return file_paths

    def __upload_disk(self, lease, file_path, host):
        session = lease.info.deviceUrl[0].key
        url = lease.info.deviceUrl[0].url.replace('*', host)
        if not url.startswith("https"):
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            context.verify_mode = ssl.CERT_NONE
            try:
                resp = urlopen(url, context=context)
                file_data = resp.read()
            except Exception as e:
                print("Error occurred while downloading disk: %s" % e)
                raise
        else:
            try:
                req = Request(url)
                req.add_header('Authorization', 'Bearer %s' % session)
                resp = urlopen(req, context=ssl._create_unverified_context())
                file_data = resp.read()
            except Exception as e:
                print("Error occurred while downloading disk: %s" % e)
                raise

        with open(file_path, "wb") as fout:
            fout.write(file_data)

        lease.HttpNfcLeaseProgress(50)
        lease.HttpNfcLeaseProgress(100)

        try:
            os.remove(file_path)
        except OSError as e:
            print("Failed to remove temp disk file %s: %s" % (file_path, e))

    def deploy(self):
        print("Deploying OVA from path: %s" % self.path)
        spec = self.__spec
        print("Deploying OVF %s on %s" % (self.get_descriptor(), spec.entityName))
        print("Datastore: %s" % spec.entityName.datastore.name)
        print("Resource Pool: %s" % spec.entityName.resourcePool.name)
        task = spec.ImportVApp()
        print("Deploy task submitted: %s" % task.info.descriptionId)
        wait_for_task(task, si)


def wait_for_task(task, si):
    """Given a task, wait for it to complete, print result and return
    task info."""
    while task.info.state == vim.TaskInfo.State.running:
        time.sleep(2)

    if task.info.state == vim.TaskInfo.State.success:
        print("Task completed successfully.")
        return task.info.result
    elif task.info.state == vim.TaskInfo.State.error:
        print("Error occurred.")
        print("Task error message: %s" % task.info.error.localizedMessage)
        raise task.info.error
    return None


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("Error: %s" % e)
        sys.exit(1)
