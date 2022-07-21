from attrs import define, frozen, field
from typing import List, Dict, Any, Iterator, Tuple, Union, Optional

import shutil
from .abstract import *

from simple_uam.util.logging import get_logger
import json
from pathlib import Path

log = get_logger(__name__)

@frozen
class StaticComponent(ComponentReader):
    """
    A static component defined an an immutable object.
    """

    rep : dict = field(
    )
    """ Internal object representation of a component. """

    @property
    def name(self) -> str:
        return self.rep['name']

    @property
    def connections(self) -> List[str]:
        return list(self.rep.get('conns',dict()).keys())

    @property
    def cad_part(self) -> Optional[str]:
        return self.rep.get('cad_part')

    @property
    def cad_properties(self) -> List[Dict[str,Any]]:
        return self.to_prop_list(
            self.rep.get('cad_props',dict())
        )

    @property
    def cad_params(self) -> List[Dict[str,Any]]:
        return self.to_prop_list(
            self.rep.get('cad_params',dict())
        )

    def cad_connection(self, conn : str) -> Optional[str]:
        return self.rep.get('conns',dict()).get(conn,dict()).get('cad')

    @property
    def properties(self) -> List[Dict[str,Any]]:
        return self.to_prop_list(
            self.rep.get('props',dict())
        )

    @property
    def params(self) -> List[Dict[str,Any]]:
        return self.to_prop_list(
            self.rep.get('params',dict())
        )

    @staticmethod
    def from_prop_list(prop_list : List[Dict[str,str]]) -> Dict[str,str]:
        prop_dict = dict()
        for item in prop_list:
            prop_dict[item['PROP_NAME']] = item['PROP_VALUE']
        return prop_dict

    @staticmethod
    def to_prop_list(prop_dict : Dict[str,str]) -> List[Dict[str,str]]:
        prop_list = list()
        for name, val in prop_dict.items():
            prop_list.append({'PROP_NAME': name, 'PROP_VALUE': val})
        return prop_list

    @classmethod
    def from_rep(cls, rep) -> 'StaticComponent':
        """ Load from serializable rep. """
        return cls(rep)

    def to_rep(self):
        """ Return the rep. """
        return self.rep

    @classmethod
    def load_json(cls, fp, **kwargs):
        """ Same arguments as json.load. """
        return cls.from_rep(json.load(fp,**kwargs))

    @classmethod
    def load_json_str(cls, s, **kwargs):
        """ Same arguments as json.loads. """
        return cls.from_rep(json.loads(s, **kwargs))

    def dump_json(self, fp, indent="  ", **kwargs):
        """ Same arguments as json.dump less the first. """
        return json.dump(self.rep, fp, indent=indent, **kwargs)

    def dump_json_str(indent="  ", **kwargs):
        """ Same arguments as json.dumps less the first. """
        return json.dumps(self.rep, indent=indent, **kwargs)

    @classmethod
    def component_rep(cls,comp : ComponentReader) -> dict:
        """ Extract the rep from a component. """

        rep = dict()

        log.info("Getting component name.")
        name = comp.name
        rep['name'] = name

        log.info("Getting Connection List.")
        conns = dict()
        conn_list = list(comp.connections)
        num = len(conn_list)
        for ind, conn in enumerate(conn_list):
            log.info(
                f"Getting connection data ({ind+1}/{num})",
                comp=name,
                conn=conn,
            )
            conns[conn] = dict()
            if cad_conn := comp.cad_connection(conn):
                log.info(
                    f"Found connection data.",
                    comp=name,
                    conn=conn,
                    cad_conn=cad_conn,
                )
                conns[conn]['cad'] = cad_conn
        rep['conns'] = conns

        if cad_part := comp.cad_part:
            log.info(
                "Getting cad part data.",
                comp=name,
                cad_part=cad_part,
            )
            rep['cad_part'] = cad_part

        cad_props = cls.from_prop_list(comp.cad_properties)
        log.info(
            "Getting cad properties",
            comp=name,
            cad_props=cad_props,
        )
        if len(cad_props) > 0:
            rep['cad_props'] = cad_props

        cad_params = cls.from_prop_list(comp.cad_params)
        log.info(
            "Getting cad parameters",
            comp=name,
            cad_params=cad_params,
        )
        if len(cad_params) > 0:
            rep['cad_params'] = cad_params

        props = cls.from_prop_list(comp.properties)
        log.info(
            "Getting properties.",
            comp=name,
            props=props,
        )
        if len(props) > 0:
            rep['props'] = props

        params = cls.from_prop_list(comp.params)
        log.info(
            "Getting parameters",
            comp=name,
            params=params,
        )
        if len(params) > 0:
            rep['params'] = params

        return rep

    @classmethod
    def from_component(cls, comp : ComponentReader) -> 'StaticComponent':
        return cls.from_rep(cls.component_rep(comp))


@frozen
class StaticCorpus(CorpusReader):
    """
    A corpus that is backed by a static representation.
    """

    rep : dict = field(
    )

    def __getitem__(self, comp : str) -> ComponentReader:
        return StaticComponent.from_rep(self.rep[comp])

    def __contains__(self, comp : str) -> bool:
        return comp in self.rep[comp]

    @property
    def components(self) -> Iterator[ComponentReader]:
        return self.rep.keys()

    @classmethod
    def from_rep(cls, rep) -> 'StaticCorpus':
        """ Load from serializable rep. """
        return cls(rep)

    def to_rep(self):
        """ Return the rep. """
        return self.rep

    @classmethod
    def load_json(cls, fp, **kwargs):
        """ Same arguments as json.load. """
        return cls.from_rep(json.load(fp,**kwargs))

    @classmethod
    def load_json_str(cls, s, **kwargs):
        """ Same arguments as json.loads. """
        return cls.from_rep(json.loads(s, **kwargs))

    def dump_json(self, fp, indent="  ", **kwargs):
        """ Same arguments as json.dump less the first. """
        return json.dump(self.rep, fp, indent=indent, **kwargs)

    def dump_json_str(indent="  ", **kwargs):
        """ Same arguments as json.dumps less the first. """
        return json.dumps(self.rep, indent=indent, **kwargs)

    @staticmethod
    def corpus_rep(corp : CorpusReader,
                   cache_dir : Union[Path, str, None] = None,
                   cluster_size : int = 100) -> dict:
        """
        Generates a representation of a corpus.

        Argument:
           corp: The corpus we are reading from.
           cache_dir: The directory we are reading cached items from.
           cluster_size: The size of each cluster of files we write to size.
        """
        if cache_dir:
            cache_dir = Path(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)

        log.info("Getting component list.")
        cmp_list = sorted(list(corp.components))
        cmp_num = len(cmp_list)

        # split into clusters
        clusters = list()
        cluster_filename = lambda x: f"corpus_cache_{x}.json"
        if cache_dir:
            clusters = [cmp_list[x:x+cluster_size] for x in range(0, cmp_num, cluster_size)]
        else:
            clusters = [cmp_list]
        cluster_num = len(clusters)

        rep = dict()
        for cluster_ind, cluster in enumerate(clusters):
            # check if cluster file exists
            cluster_file = cache_dir / cluster_filename(cluster_ind)
            cluster_str =  f"({cluster_ind + 1}/{cluster_num})"
            if cache_dir and cluster_file.exists():
                log.info(
                    f"Found cached cluster of components, skipping read. {cluster_str}",
                    cache_dir=str(cache_dir),
                    cluster_file=str(cluster_file),
                )
                continue
            elif cache_dir:
                log.info(
                    f"Reading cluster from source corpus. {cluster_str}",
                    cache_dir=str(cache_dir),
                    cluster_file=str(cluster_file),
                )

            # get components in cluster
            for comp_num, comp in enumerate(cluster):
                ind = (cluster_ind * cluster_size) + comp_num
                log.info(f"Getting component data ({ind+1}/{cmp_num})",
                         component=comp)
                rep[comp] = StaticComponent.component_rep(corp[comp])

            # write cluster file
            if cache_dir:
                log.info(
                    f"Writing cluster to file. {cluster_str}",
                    cache_dir=str(cache_dir),
                    cluster_file=str(cluster_file),
                )
                with cluster_file.open('w') as cf:
                    json.dump(rep,cf,indent="  ")
                rep = dict()

        if cache_dir:
            rep = dict()
            for cluster_ind, cluster in enumerate(clusters):
                cluster_file = cache_dir / cluster_filename(cluster_ind)
                cluster_str =  f"({cluster_ind + 1}/{cluster_num})"
                log.info(
                    f"Reading cluster from cache. {cluster_str}",
                    cache_dir=str(cache_dir),
                    cluster_file=str(cluster_file),
                )
                with cluster_file.open('r') as cf:
                    rep.update(json.load(cf))

            log.info(
                "Generated complete dump, deleting cache dir.",
                cache_dir=str(cache_dir)
            )
            shutil.rmtree(cache_dir, ignore_errors=True)

        return rep

    @classmethod
    def from_corpus(cls,
                    corp : CorpusReader,
                    cache_dir : Union[Path, str, None] = None,
                    cluster_size : int = 100) -> 'StaticCorpus':
        """ Extract the rep from a component. see corpus_rep for args. """

        return cls.from_rep(cls.corpus_rep(
            corp,
            cache_dir=cache_dir,
            cluster_size=cluster_size,
        ))
