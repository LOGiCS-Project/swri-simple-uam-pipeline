from .corpus.abstract import *
from attrs import define, field, frozen
from typing import List, Dict, Any, Iterator, Tuple, Optional
import json
from pathlib import Path
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
        for from_comp, lib_comp in self.design_to_corpus.items():
            cad_prt = self.corpus[lib_comp].cad_part

            new_entry = {
                'FROM_COMP': from_comp,
                'LIB_COMPONENT': lib_comp,
                'CAD_PRT': cad_prt
            }

            if any_none(from_comp, lib_comp, cad_prt):
                log.warning(
                    'Skipping entry in component_maps due to null values',
                    **new_entry,
                )
            else:
                cmp_maps.append(new_entry)
        return cmp_maps

    connection_maps : List[dict] = field(
        init=False,
    )
    """ List of connections in the design. """

    connection_maps_file = 'info_connectionMap6.json'

    @connection_maps.default
    def _conn_maps_def(self):
        conn_maps = list()
        for conn_entry in self.design['connections']:
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
            if any_none(from_comp, from_conn, to_comp, to_conn):
                log.warning(
                    'Skipping entry in connectionMap due to null values',
                    comp_entry=conn_entry,
                    **new_entry,
                )
            else:
                conn_maps.append(new_entry)
        return conn_maps

    param_maps : List[dict] = field(
        init = False,
    )

    param_maps_file = "info_paramMap4.json"

    @param_maps.default
    def _param_maps_default(self):
        param_maps = list()
        for param_entry in self.design['parameters']:
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
                if any_none(design_param,
                            design_param_val,
                            component_name,
                            component_param):
                    log.warning(
                        'Skipping entry in paramMap due to null values',
                        comp_entry=comp_entry,
                        **new_entry,
                    )
                else:
                    param_maps.append(new_entry)
        return param_maps

    cad_properties : List[dict] = field(
        init = False,
    )

    cad_properties_file = "info_componentCadProp2.json"

    @cad_properties.default
    def _cad_props_default(self):
        cad_props = list()
        for entry in self.component_maps: # NOTE : needs component map list
            comp_name = entry['FROM_COMP']
            lib_name = entry['LIB_COMPONENT']
            cad_part = entry['CAD_PRT']
            prop_vals = self.corpus[lib_name].cad_properties
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
                if any_none(prop_name, prop_value):
                    log.warning(
                        'Skipping entry in paramMap due to null values',
                        entry=entry,
                        prop_val=prop_val,
                        **new_entry,
                    )
                else:
                    cad_props.append(new_entry)
        return cad_props

    cad_connections : List[dict] = field(
        init=False,
    )

    cad_connections_file = "info_connectionCADMap3.json"

    @cad_connections.default
    def _cad_conn_default(self):
        cad_conns = list()
        for entry in self.connection_maps: ## NOTE: need connmap
            from_comp = entry['FROM_COMP']
            to_comp = entry['TO_COMP']
            from_conn = entry['FROM_CONN']
            to_conn = entry['TO_CONN']
            from_comp_type = self.design_to_corpus[from_comp] ## NOTE: needs ci_to_comp
            to_comp_type = self.design_to_corpus[to_comp]
            from_conn_cs = self.corpus[from_comp_type].cad_connection(from_conn)
            to_conn_cs = self.corpus[to_comp_type].cad_connection(to_conn)
            new_entry = {
                'FROM_COMP': from_comp,
                'FROM_CONN_CS': from_conn_cs,
                'TO_COMP': to_comp,
                'TO_CONN_CS': to_conn_cs
            }
            if any_none(from_conn_cs and to_conn_cs):
                log.warning(
                    'Skipping entry in connectionCadMap due to null values',
                    entry=entry,
                    **new_entry,
                )
            else:
                cad_conns.append(new_entry)
        return cad_conns

    component_props : List[dict] = field(
        init=False,
    )

    component_props_file = "info_componentProps7.json"

    @component_props.default
    def _comp_props_default(self):
        comp_props = list()
        for entry in self.component_maps:
            comp_name = entry['FROM_COMP']
            lib_name = entry['LIB_COMPONENT']
            prop_vals = self.corpus[lib_name].properties
            for prop_val in prop_vals:
                prop_name = prop_val['PROP_NAME']
                prop_value = prop_val['PROP_VALUE']
                new_entry = {
                    'COMP_NAME': comp_name,
                    'LIB_NAME': lib_name,
                    'PROP_NAME': prop_name,
                    'PROP_VALUE': prop_value
                }
                if any_none(prop_name, prop_val):
                    log.warning(
                        'Skipping entry in componentProps due to null values',
                        entry=entry,
                        prop_val=prop_val,
                        **new_entry,
                    )
                else:
                    comp_props.append(new_entry)
        return comp_props


    component_params : List[dict] = field(
        init=False,
    )

    component_params_file = 'info_componentParams8.json'

    @component_params.default
    def _comp_params_default(self):
        comp_params = list()
        for entry in self.component_maps:
            comp_name = entry['FROM_COMP']
            lib_name = entry['LIB_COMPONENT']
            prop_vals = self.corpus[lib_name].params
            for prop_val in prop_vals:
                prop_name = prop_val['PROP_NAME']
                prop_value = prop_val['PROP_VALUE']
                new_entry = {
                    'COMP_NAME': comp_name,
                    'LIB_NAME': lib_name,
                    'PROP_NAME': prop_name,
                    'PROP_VALUE': prop_value
                }
                if any_none(prop_name, prop_value):
                    log.warning(
                        'Skipping entry in componentParams due to null values',
                        entry=entry,
                        prop_val=prop_val,
                        **new_entry,
                    )
                else:
                    comp_params.append(new_entry)
        return comp_params

    cad_params : List[dict] = field(
        init=False,
    )

    cad_params_file = 'info_componentCADParams5.json'

    @cad_params.default
    def _cad_params(self):
        cad_params = list()
        for entry in self.component_maps: ## NOTE: ComponentMapList
            comp_name = entry['FROM_COMP']
            lib_name = entry['LIB_COMPONENT']
            cad_part = entry['CAD_PRT']
            prop_vals = self.corpus[lib_name].cad_params
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
                if any_none(prop_name, prop_value):
                    log.warning(
                        'Skipping entry in componentCadParams due to null values',
                        entry=entry,
                        prop_val=prop_val,
                        **new_entry,
                    )
                else:
                    cad_params.append(new_entry)
        return cad_params

    @property
    def info_file_map(self):
        """
        Map from filename to file data.
        """

        return {
            self.component_maps_file: self.component_maps,
            self.connection_maps_file: self.connection_maps,
            self.param_maps_file: self.param_maps,
            self.cad_properties_file: self.cad_properties,
            self.cad_connections_file: self.cad_connections,
            self.component_props_file: self.component_props,
            self.component_params_file: self.component_params,
            self.cad_params_file: self.cad_params,
        }

    def write_files(self, out_dir):
        """
        Write all the info files to the output directory.
        """

        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        for filename, content in self.info_file_map.items():
            filepath = out_dir / filename

            with filepath.open('w') as fp:
                json.dump(content, fp, indent="  ")
