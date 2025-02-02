"""Manage telemetry stream collector on COM7 devices.
"""
from ansible_collections.community.network.plugins.module_utils.network.pycw7.features.interface import Interface

from ansible_collections.community.network.plugins.module_utils.network.pycw7.utils.xml.lib import *


class Telemetry(object):
    """This class is used to get and build telemetry stream collector
    configurations on ``COM7`` devices.

    Args:
        device (COM7): connected instance of a ``pycw7.comware.COM7``
            object.

    Attributes:
        device (COM7): connected instance of a ``pycw7.comware.COM7``
            object.
    """
    def __init__(self, device, sourceID=None, destinID=None, sourcePort=None, destinPort=None):
#    def __init__(self, device):
        self.device = device
        self.sourceID = sourceID
        self.destinID = destinID
        self.sourcePort = sourcePort
        self.destinPort = destinPort

        self.telemetry_key_map = {
            'sourceID': 'SrcIP',
            'destinID': 'DstIP',
            'sourcePort': 'SrcPort',
            'destinPort': 'DstPort'
        }

    def gen_top(self):
        E = data_element_maker()
        top = E.top(
            E.TelemetryFlowTrace(
                E.MOD(
                    E.Encap()
                )
            )
        )
        return top

    def get_config(self):
        """Return the current layer 2 settings on the switchport.

        Returns:
            A dictionary of current configuration parameters.

            For example::

                {
                    'pvid': '2',
                    'link_type': 'trunk',
                    'permitted_vlans': '1-5'
                }
        """
        top = self.gen_top()
        telemetry_id_ele = find_in_data('Encap', top)
        telemetry_id_ele.append(data_element_maker().SrcIP(self.sourceID))
        telemetry_id_ele.append(data_element_maker().DstIP(self.destinID))
        telemetry_id_ele.append(data_element_maker().SrcPort(self.sourcePort))
        telemetry_id_ele.append(data_element_maker().DstPort(self.destinPort))

        nc_get_reply = self.device.get(('subtree', top))
        telemetry_config = data_elem_to_dict(nc_get_reply.data_ele, self.telemetry_key_map)

        return telemetry_config

    def remove(self, stage=False):
        """Stage or execute telemetry stream collector configuration.

        Args:
            stage (bool): whether to stage the command or execute immediately

        Returns:
            True if stage=True and successfully staged
            etree.Element XML response if immediate execution
        """
        config = self._build_config(state='absent')
        if stage:
            return self.device.stage_config(config, 'edit_config')
        else:
            return self.device.edit_config(config)


    def build(self, stage=False, **telemetry):
        """Stage telemetry stream collectorconfiguration with given parameters.

        Args:
            stage (bool): whether to stage the command or execute immediately

        Returns:
            True if stage=True and successfully staged
            etree.Element XML response if immediate execution
        """
        config = self._build_config(state='present', **telemetry)
        if stage:
            return self.device.stage_config(config, 'edit_config')
        else:
            return self.device.edit_config(config)

    def _build_config(self, state, **telemetry):
        if state == 'present':
            operation = 'merge'
            telemetry['sourceID'] = self.sourceID
            telemetry['destinID'] = self.destinID
            telemetry['sourcePort'] = self.sourcePort
            telemetry['destinPort'] = self.destinPort
        elif state == 'absent':
            operation = 'delete'
            self.sourceID = ''
            self.destinID = ''
            self.sourcePort = ''
            self.sourcePort = ''
            telemetry['sourceID'] = self.sourceID
            telemetry['destinID'] = self.destinID
            telemetry['sourcePort'] = self.sourcePort
            telemetry['destinPort'] = self.sourcePort

        EC = nc_element_maker()
        E = config_element_maker()
        config = EC.config(
            E.top(
                E.TelemetryFlowTrace(
                    E.MOD(
                        E.Encap(
                            *config_params(telemetry, self.telemetry_key_map)
                        )
                    ),
                    **operation_kwarg(operation)
                )
            )
        )

        return config