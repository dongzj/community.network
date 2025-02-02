"""Operation for Configuration comparison in COM7 devices.
"""
from lxml import etree
from ncclient.xml_ import qualify
from ansible_collections.community.network.plugins.module_utils.network.pycw7.utils.xml.namespaces import NCDATA, NCDATA_C, NCACTION
from ansible_collections.community.network.plugins.module_utils.network.pycw7.utils.xml.lib import *
import os

class Compare(object):
    """This class is used to get data and configure a specific File.

    Args:
        device (COM7): connected instance of a ``pycw7.comware.COM7``
            object.
        cmd: command to excute
        result: result file path

    Attributes:
        device (COM7): connected instance of a ``pycw7.comware.COM7``
            object.

    """
    def __init__(self, device, cmd, result):
        self.device = device
        if cmd:
            self.cmd = cmd
        if result:
            self.result=result

    def get_result(self):
        commands = '{0}'.format(self.cmd)
        res = self.device.cli_display(commands)
        ele = res.split('\n')
        element = ele[1:-1]

        alist = []
        blist = []

        for line in element:
            line = line.rstrip()
            if line:
                alist.append(line)
        for line in open(self.result, 'r'):
            line = line.rstrip()
            if line:
                blist.append(line)
        if set(alist) == set(blist):
            return True
        else:
            return False



