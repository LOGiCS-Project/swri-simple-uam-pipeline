from .corpus.abstract import *
from attrs import define, field
from typing import List, Dict, Any, Iterator, Tuple, Optional

from simple_uam.util.logging import get_logger

log = get_logger(__name__)

def any_none(*vargs):
    return any(map(lambda x: x is None, vargs))

@frozen
class DesignInfoFiles():

    corpus : CorpusReader = field()
    """ Corpus being used during generation. """

    design : dict = field()
    """ Design rep we're generating info files for. """

    design_to_corpus : dict = field(
        init=False,
    )
    """ Map from design component instances to corpus component classes. """

    @design_to_corpus.default
    def _cdcm_default(self):
        cdcm = dict()
        for comp_entry in self.design['components']:
            from_comp = comp_entry['component_instance']
            lib_component = comp_entry['component_choice']
            cdcm[from_comp] = lib_component
        return cdcm

    component_maps : List[dict] = field(
        init = False,
    )
    """ Map of components and cad files. """

    component_maps_file = 'info_componentMapList1.json'

    @component_maps.default
    def _cmp_maps_default(self):
        cmp_maps = list()
        for (from_comp, lib_comp) in self.design_to_corpus:
            cad_prt = self.corpus[lib_comp].cad_part

            new_entry = {
                'FROM_COMP': from_comp,
                'LIB_COMPONENT': lib_component,
                'CAD_PRT': cad_prt
            }

            if any_none(from_comp, lib_comp, car_prt):
                log.warning(
                    'Skipping entry in component_maps due to null values',
                    **new_entry,
                )
            else:
                cmp_maps.append(new_entry)
        return cmp_maps


@define
class ComponentMapList():

    ci_to_comp = field(factory=list)

    filename = 'info_componentMapList1.json'

    def gen_rep(self, corpus, design):
        rep = list()
        for comp_entry in design['components']:
            from_comp = comp_entry['component_instance']
            lib_component = comp_entry['component_choice']
            self.ci_to_comp[from_comp] = lib_component
            cad_prt = corpus[lib_component].cad_part
            new_entry = {
                'FROM_COMP': from_comp,
                'LIB_COMPONENT': lib_component,
                'CAD_PRT': cad_prt
            }

            if from_comp and lib_component and cad_prt:
                rep.append(new_entry)
            else:
                log.warning(
                    'Skipping entry in componentMapList due to null values',
                    comp_entry=comp_entry,
                    **new_entry,
                )
        return rep

@define
class ConnectionMap():

    filename = 'info_connectionMap6.json'

    def gen_rep(self, corpus, design):
        rep = list()
        for conn_entry in design['connections']:
            from_comp = conn_entry['from_ci']
            from_conn = conn_entry['from_conn']
            to_comp = conn_entry['to_ci']
            to_conn = conn_entry['to_conn']
            new_entry = {
                'FROM_COMP': from_comp,
                'FROM_CONN': from_conn,
                'TO_COMP': to_comp,
                'TO_CONN': to_conn
            }
            if from_comp and from_conn and to_comp and to_conn:
                rep.append(new_entry)
            else:
                log.warning(
                    'Skipping entry in connectionMap due to null values',
                    comp_entry=comp_entry,
                    **new_entry,
                )
        return rep

@define
class ParamMap():

    filename = "info_paramMap4.json"

    def gen_rep(self, corpus, design):
        rep = list()
        for param_entry in design['parameters']:
            design_param = param_entry['parameter_name']
            design_param_val = param_entry['value']
            for target in param_entry['component_properties']:
                component_name = target['component_name']
                component_param = target['component_property']
                new_entry = {
                    'DESIGN_PARAM': design_param,
                    'DESIGN_PARAM_VAL': design_param_val,
                    'COMPONENT_NAME': component_name,
                    'COMPONENT_PARAM': component_param
                }
                if design_param and design_param_val \
                   and component_name and component_param:
                    rep.append(new_entry)
                else:
                    log.warning(
                        'Skipping entry in paramMap due to null values',
                        comp_entry=comp_entry,
                        **new_entry,
                    )
        return rep


@define
class ComponentCadProps():

    filename = "info_componentCadProp2.json"

    def gen_rep(self, corpus, design):
        rep = list()
        for entry in componentMapList: # NOTE : needs component map list
            comp_name = entry['FROM_COMP']
            lib_name = entry['LIB_COMPONENT']
            cad_part = entry['CAD_PRT']
            prop_vals = corpus[lib_name].cad_properties
            for prop_val in prop_vals:
                prop_name = prop_val['PROP_NAME']
                prop_value = prop_val['PROP_VALUE']
                new_entry = {
                    'COMP_NAME': comp_name,
                    'LIB_NAME': lib_name,
                    'CAD_PART': cad_part,
                    'PROP_NAME': prop_name,
                    'PROP_VALUE': prop_value
                }
                if prop_name and prop_value is not None:
                    rep.append(new_entry)
                else:
                    log.warning(
                        'Skipping entry in paramMap due to null values',
                        entry=entry,
                        prop_val=prop_val,
                        **new_entry,
                    )
        return rep

@define
class ConnectionCadMap():

    filename = "info_connectionCADMap3.json"

    def gen_rep(self, corpus, design):
        rep = list()
        for entry in connectionMap: ## NOTE: need connmap
            from_comp = entry['FROM_COMP']
            to_comp = entry['TO_COMP']
            from_conn = entry['FROM_CONN']
            to_conn = entry['TO_CONN']
            from_comp_type = ci_to_comp[from_comp] ## NOTE: needs ci_to_comp
            to_comp_type = ci_to_comp[to_comp]
            from_conn_cs = corpus[from_comp_type].cad_connection(from_conn)
            to_conn_cs = corpus[to_comp_type].cad_connection(to_conn)
            new_entry = {
                'FROM_COMP': from_comp,
                'FROM_CONN_CS': from_conn_cs,
                'TO_COMP': to_comp,
                'TO_CONN_CS': to_conn_cs
            }
            if from_conn_cs and to_conn_cs:
                rep.append(new_entry)
            else:
                log.warning(
                    'Skipping entry in connectionCadMap due to null values',
                    entry=entry,
                    **new_entry,
                    )
        return rep

@define
class ComponentProps():

    filename = "info_componentProps7.json"

    def gen_rep(self, corpus, design):
        rep = list()

        for entry in componentMapList: ## NOTE: componentMapList
            comp_name = entry['FROM_COMP']
            lib_name = entry['LIB_COMPONENT']
            prop_vals = corpus[lib_name].properties
            for prop_val in prop_vals:
                prop_name = prop_val['PROP_NAME']
                prop_value = prop_val['PROP_VALUE']
                new_entry = {
                    'COMP_NAME': comp_name,
                    'LIB_NAME': lib_name,
                    'PROP_NAME': prop_name,
                    'PROP_VALUE': prop_value
                }
                if prop_name and prop_value:
                    rep.append(new_entry)
                else:
                    log.warning(
                        'Skipping entry in componentProps due to null values',
                        entry=entry,
                        prop_val=prop_val,
                        **new_entry,
                    )
        return rep

@define
class ComponentParams():

    filename = 'info_componentParams8.json'

    def gen_rep(self, corpus, design):
        rep = list()
        for entry in componentMapList: ## NOTE: ComponentMapList
            comp_name = entry['FROM_COMP']
            lib_name = entry['LIB_COMPONENT']
            prop_vals = corpus[lib_name].params
            for prop_val in prop_vals:
                prop_name = prop_val['PROP_NAME']
                prop_value = prop_val['PROP_VALUE']
                new_entry = {
                    'COMP_NAME': comp_name,
                    'LIB_NAME': lib_name,
                    'PROP_NAME': prop_name,
                    'PROP_VALUE': prop_value
                }
                if prop_name and prop_value:
                    rep.append(new_entry)
                else:
                    log.warning(
                        'Skipping entry in componentParams due to null values',
                        entry=entry,
                        prop_val=prop_val,
                        **new_entry,
                    )
        return rep

@define
class ComponentCadParams():

    filename = 'info_componentCADParams5.json'

    def gen_rep(self, corpus, design):
        rep = list()
        for entry in componentMapList: ## NOTE: ComponentMapList
            comp_name = entry['FROM_COMP']
            lib_name = entry['LIB_COMPONENT']
            cad_part = entry['CAD_PRT']
            prop_vals = corpus[lib_name].cad_params
            for prop_val in prop_vals:
                prop_name = prop_val['PROP_NAME']
                prop_value = prop_val['PROP_VALUE']
                new_entry = {
                    'COMP_NAME': comp_name,
                    'LIB_NAME': lib_name,
                    'CAD_PART': cad_part,
                    'PROP_NAME': prop_name,
                    'PROP_VALUE': prop_value
                }
                if prop_name and prop_value:
                    rep.append(new_entry)
                else:
                    log.warning(
                        'Skipping entry in componentCADParams due to null values',
                        entry=entry,
                        prop_val=prop_val,
                        **new_entry,
                    )
        return rep
