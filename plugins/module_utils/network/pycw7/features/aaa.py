"""Manage interfaces on COM7 devices.
"""

from ansible_collections.community.network.plugins.module_utils.network.pycw7.utils.xml.lib import reverse_value_map
from ansible_collections.community.network.plugins.module_utils.network.pycw7.features.errors import InterfaceCreateError, InterfaceTypeError,\
    InterfaceAbsentError, InterfaceParamsError, InterfaceVlanMustExist, StpParamsError,\
    AaaConfigAbsentError, AaaSuperError
from ansible_collections.community.network.plugins.module_utils.network.pycw7.features.interface import Interface
from ansible_collections.community.network.plugins.module_utils.network.pycw7.utils.xml.lib import *


class Aaa(object):
    """This class is used to get and handle aaa config
    """
    def __init__(self,device,domain_name):
        self.device = device
        self.domain_name = domain_name
        self._key_map = {
            'domain_name':'DomainName',
            'aaa_type': 'AaaType',
            'access_type':'AccessType',
            'scheme_list':'SchemeList',
            'scheme_name_list':'SchemeNameList',
        }
        self._value_map = {
            'AaaType':{'0':'authentication',
                       '4':'authorization',
                       '5':'accounting'},

            'AccessType':{'3':'LAN access',
                          '0':'login',
                          '1':'super',
                          '4':'PPP',
                          '5':'default',
                          '6':'portal'},

            'SchemeList':{'2':'radius',
                          '1':'hwtacacs',
                          '4':'local'}
        }
        self._r_key_map = dict(reversed(item) for item in self._key_map.items())
        self._r_value_map = reverse_value_map(self._r_key_map, self._value_map)

    def get_domain_info(self):
        E = data_element_maker()
        top = E.top(
            E.Domain(
                E.Domains(
                    E.Domain()
                )
            )
        )
        nc_get_reply = self.device.get(('subtree', top))
        reply_data = findall_in_data('DomainName', nc_get_reply.data_ele)
        domains = [domain.text for domain in reply_data]
        return domains

    def get_config(self):
        E = data_element_maker()
        key_map = {
            'domain_name': 'DomainName',
        }
        top = E.top(
            E.Domain(
                E.Domains(
                    E.Domain()
                )
            )
        )
        nc_get_reply = self.device.get(('subtree', top))
        reply_data = find_in_data('Domain', nc_get_reply.data_ele)
        if reply_data is None:
            return {}
        return data_elem_to_dict(reply_data, key_map)

    def build(self, stage=False, **params):
        return self._build_config(state='present',stage=stage,**params)

    def build_aaa(self,stage=False, **params):
        return self.build_aaa_scheme(state='present', stage=stage, **params)

    def default(self, stage=False, **params):
        return self._build_config(state='default', stage=stage,**params)

    def _build_config(self, state, stage=False, **params):
        key_map = {
            'domain_name': 'DomainName',
        }
        if state == 'present':
            EN = nc_element_maker()
            EC = config_element_maker()
            config = EN.config(
                EC.top(
                    EC.Domain(
                        EC.Domains(
                            EC.Domain(
                                *config_params(params, key_map)
                            )
                        )
                    )
                )
            )
            if stage:
                return self.device.stage_config(config, 'edit_config')
            else:
                return self.device.edit_config(config)

        if state == 'default' or 'absent':
            EN = nc_element_maker()
            EC = config_element_maker()
            operation = 'delete'
            config = EN.config(
                EC.top(
                    EC.Domain(
                        EC.Domains(
                            EC.Domain(
                                *config_params(params, key_map)
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

    def build_aaa_scheme(self,state, stage=False,**params):
        if state == 'present':
            EN = nc_element_maker()
            EC = config_element_maker()
            config = EN.config(
                EC.top(
                    EC.Domain(
                        EC.Schemes(
                            EC.Scheme(
                                *config_params(params, self._key_map, value_map=self._r_value_map)
                            )
                        )
                    )
                )
            )
            if stage:
                return self.device.stage_config(config, 'edit_config')
            else:
                return self.device.edit_config(config)

    def param_check(self,**params):
        if params.get('scheme_list'):
            if not params.get('scheme_name_list'):
                raise AaaConfigAbsentError('scheme_name_list')

        if params.get('aaa_type') != 'authentication':
            if params.get('access_type') == 'super':
                raise AaaSuperError('super')

        if params.get('access_type') == 'super':
            if params.get('scheme_list') == 'local':
                raise AaaSuperError('super')