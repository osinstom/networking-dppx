from networking_p4.services.common import constants
from neutron_lib import constants as n_constants

DEVICE_OWNER_P4 = constants.DEVICE_OWNER_P4


def prepare_port_data(p4_module, name=None):
    return {'project_id': p4_module['project_id'],
            'network_id': p4_module['network_id'],
            'fixed_ips': n_constants.ATTR_NOT_SPECIFIED,
            'device_id': p4_module['id'],
            'device_owner': DEVICE_OWNER_P4,
            'admin_state_up': True,
            'name': name if name is not None else '',
            'binding:host_id': 'p4-test'}


def prepare_port_pair_data(name, port):
    return {
        'name': 'PP_' + name,
        'project_id': port['tenant_id'],
        'description': '',
        'ingress': port['id'],
        'egress': port['id'],
        'service_function_parameters': {'correlation': None,
                                        'weight': 1}
    }


def prepare_port_pair_group_data(port_pair):
    return {
        "name": "PG_" + port_pair['name'],
        "project_id": port_pair['project_id'],
        "description": "",
        "port_pairs": [
            port_pair['id']
        ],
        "port_pair_group_parameters": {
            "lb_fields": [],
            "ppg_n_tuple_mapping": {
                "ingress_n_tuple": {},
                "egress_n_tuple": {}
            }
        }
    }


def prepare_port_chain_data(module_id, flow_classifier, port_chain_groups, type):
    return {
        "name": "PC_FOR_" + module_id,
        "project_id": flow_classifier['project_id'],
        "description": "",
        "flow_classifiers": [flow_classifier['id']],
        "port_pair_groups": [ppg['id'] for ppg in port_chain_groups],
        "chain_id": "1",
        "chain_parameters": {
            "symmetric": False,
            "correlation": 'mpls'
        }
    }
