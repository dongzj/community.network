"""Manage interfaces on COM7 devices.
"""

from ansible_collections.community.network.plugins.module_utils.network.pycw7.utils.xml.lib import reverse_value_map
from ansible_collections.community.network.plugins.module_utils.network.pycw7.features.errors import InterfaceCreateError, InterfaceTypeError,\
    InterfaceAbsentError, InterfaceParamsError, InterfaceVlanMustExist, StpParamsError
from ansible_collections.community.network.plugins.module_utils.network.pycw7.features.interface import Interface
from ansible_collections.community.network.plugins.module_utils.network.pycw7.utils.xml.lib import *


class Radius(object):
    """This class is used to get and handle radius config
    """
    def __init__(self,device,radius_scheme):
        self.device = device
        self.radius_scheme = radius_scheme
        self._key_map = {
            'radius_scheme':'SchemeName',
        }
        self._value_map = {}
        self._r_key_map = dict(reversed(item) for item in self._key_map.items())
        self._r_value_map = reverse_value_map(self._r_key_map, self._value_map)

    def get_radius_info(self):
        E = data_element_maker()
        top = E.top(
            E.Radius(
                E.Client(
                    E.Schemes(
                        E.Scheme()
                    )
                )
            )
        )
        nc_get_reply = self.device.get(('subtree', top))
        reply_data = findall_in_data('SchemeName', nc_get_reply.data_ele)
        radiuses = [radius.text for radius in reply_data]
        return radiuses

    def get_config(self):
        E = data_element_maker()
        top = E.top(
            E.Radius(
                E.Client(
                    E.Schemes(
                        E.Scheme()
                    )
                )
            )
        )
        nc_get_reply = self.device.get(('subtree', top))
        reply_data = find_in_data('Scheme', nc_get_reply.data_ele)
        if reply_data is None:
            return {}
        return data_elem_to_dict(reply_data, self._key_map)

    def build(self, stage=False, **params):
        return self._build_config(state='present',stage=stage,**params)

    def build_aaa(self,stage=False, **params):
        return self.build_aaa_scheme(state='present', stage=stage, **params)

    def default(self, stage=False, **params):
        return self._build_config(state='default', stage=stage,**params)

    def _build_config(self, state, stage=False, **params):
        if state == 'present':
            EN = nc_element_maker()
            EC = config_element_maker()
            config = EN.config(
                EC.top(
                    EC.Radius(
                        EC.Client(
                            EC.Schemes(
                                EC.Scheme(*config_params(params, self._key_map))
                            )
                        )
                    )
                )
            )
            if stage:
                return self.device.stage_config(config, 'edit_config')
            else:
                return self.device.edit_config(config)

        if state == 'default':
            EN = nc_element_maker()
            EC = config_element_maker()
            operation = 'delete'
            config = EN.config(
                EC.top(
                    EC.Radius(
                        EC.Client(
                            EC.Schemes(
                                EC.Scheme(*config_params(params, self._key_map))
                            )
                        ),
                        **operation_kwarg(operation)
                    )
                )
            )
            if stage:
                return self.device.stage_config(config, 'edit_config')
            else:
                return self.device.edit_config(config)
        return False
