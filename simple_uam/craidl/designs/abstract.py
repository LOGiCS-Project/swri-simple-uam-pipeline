from attrs import define, frozen, field, setters
from typing import List, Dict, Set, Any, Iterator, Tuple, Optional
from abc import ABC, abstractmethod
from simple_uam.craidl.corpus.abstract import CorpusReader

@define
class DesignProperty():
    instance_name : str = field()
    property_name : str = field()

    @staticmethod
    def from_rep(rep : object) -> 'DesignProperty':
        return DesignProperty(
            instance_name = rep['component_name'],
            property_name = rep['component_property'],
        )

    @property
    def rep(self) -> object:
        """
        This parameter as a JSON serializable object.
        """
        return dict(
            component_name = self.instance_name,
            component_property = self.property_name,
        )

@define
class DesignParameter():
    """
    Abstract interface representing a single parameter in a design
    """

    name : str = field(
        on_setattr = setters.frozen,
    )
    """
    The parameter name.
    """

    value : str = field(
        on_setattr = setters.frozen,
    )
    """
    The parameter value.
    """

    properties : Set[DesignProperty] = field(
        factory = set,
    )
    """
    A set of properties bound to this parameter.
    """

    @property
    def component_properties(self) -> List[Dict[str,str]]:
        """
        The rendered component properties with members as tuples
        """
        return [prop.rep for prop in self.properties]

    @component_properties.setter
    def component_properties(self, props : List[Dict[str,str]]):
        self.properties = {
            DesignProperty.from_rep(prop)
            for prop in props
        }

    def add_property(self, prop: DesignProperty):
        """
        Adds a single property to the list of component properties.
        """
        self.properties.add(prop)

    def add_property_rep(self, prop_rep : object):
        """
        Adds a single property to the list of component properties.
        """
        self.add_property(DesignProperty.from_rep(prop_rep))

    @staticmethod
    def from_rep(rep: object) -> 'DesignParameter':
        out = DesignParameter(
            name = rep['parameter_name'],
            value = rep['value'],
        )

        out.component_properties = rep['component_properties']
        return out

    @property
    def rep(self) -> object:
        """
        This parameter as a JSON serializable object.
        """
        return dict(
            parameter_name = self.name,
            value = self.value,
            component_properties = self.component_properties
        )

    def validate(self,
                 design : 'AbstractDesign',
                 corpus : Optional[CorpusReader] = None):
        """
        Checks whether this property is valid in the context of this design
        and/or corpus.
        """

        for prop in self.properties:

            if not design.has_component(prop.instance_name):
                raise RuntimeError(f"Component {prop.instance_name} not found in Design {design.name}")

            if corpus:
                comp_name = design.component(prop.instance_name).choice

                if comp_name not in corpus:
                    raise RuntimeError(f"Component {comp_name} does not exist in corpus")

                if not corpus[comp_name].has_param(prop.property_name):
                    raise RuntimeError(f"Component {comp_name} does not have parameter {prop.property_name}")

@frozen
class DesignComponent():
    """
    A single component in a design.
    """


    instance : str = field()
    """
    The name of the component instance
    """

    type : Optional[str] = field(default = None)
    """
    The type of the component instance
    """

    choice : str = field()
    """
    The choice of the component instance
    """

    @staticmethod
    def from_rep(rep : object) -> 'DesignComponent':
        return DesignComponent(
            instance = rep['component_instance'],
            choice = rep['component_choice'],
            type = rep.get('component_type',None),
        )

    @property
    def rep(self) -> object:
        """
        This component as a JSON serializable object.
        """
        output = dict(
            component_instance = self.instance,
            component_choice = self.choice,
        )
        if self.type:
            output['component_type'] = self.type,
        return output

    def validate(self,
                 design : 'AbstractDesign',
                 corpus : Optional[CorpusReader] = None):
        """
        Checks whether this component instance is valid in the context of this
        design and/or corpus.
        """

        if corpus and self.choice not in corpus:
            raise RuntimeError(f"Component Type {self.choice} not found in corpus.")

@frozen(order=True)
class DesignConnector():
    """
    A single connector in a connection
    """

    instance : str = field()
    """
    Instance connector is part of
    """

    conn_type : str = field()
    """
    Type of connector
    """

    def validate(self,
                 design : 'AbstractDesign',
                 corpus : Optional[CorpusReader] = None):
        """
        Checks whether this connector is valid in the context of this
        design and/or corpus.
        """

        if not design.has_component(self.instance):
            raise RuntimeError(f"Could not find component {self.instance} in design")

        if corpus:
            comp_name = design.component(self.instance).choice

            if comp_name not in corpus:
                raise RuntimeError(f"Component {comp_name} does not exist in corpus")

            if self.conn_type not in corpus[comp_name].connections:
                raise RuntimeError(f"Component {comp_name} does not have connection {self.conn_type}")

@frozen
class DesignConnection():
    """
    A connection between two connectors in the abstract
    """

    _side_a : DesignConnector = field(
    )

    _side_b : DesignConnector = field(
    )

    _flipped : bool = field(
        eq=False,
        order=False,
        hash=False,
    )

    def __init__(self, from_side, to_side):

        side_a = from_side
        side_b = to_side
        flipped = False
        if side_b < side_a:
            side_a = to_side
            side_b = from_side
            flipped = True

        return self.__attrs_init__(
            side_a=side_a,
            side_b=side_b,
            flipped=flipped,
        )

    @property
    def from_side(self) -> DesignConnector:
        """
        Connector on the from side of the connection.
        """
        return self._side_b if self._flipped else self._side_a

    @property
    def to_side(self) -> DesignConnector:
        """
        Connector on the to side of the connection.
        """
        return self._side_b if self._flipped else self._side_a

    @staticmethod
    def from_rep(rep : object) -> 'DesignConnection':
        return DesignConnection(
            from_side=DesignConnector(
                instance=rep['from_ci'],
                conn_type=rep['from_conn'],
            ),
            to_side=DesignConnector(
                instance=rep['to_ci'],
                conn_type=rep['to_conn'],
            ),
        )

    @property
    def rep(self) -> object:
        """
        This connection as a JSON serializable object.
        """

        return dict(
            from_ci = self.from_side.instance,
            from_conn = self.from_side.conn_type,
            to_ci = self.to_side.instance,
            to_conn = self.to_side.conn_type,
        )

    def is_flipped(self, other : DesignConnector) -> bool:
        return (self.from_side == other.to_side) and (self.to_side == other.from_side)

    def validate(self,
                 design : 'AbstractDesign',
                 corpus : Optional[CorpusReader] = None):
        """
        Checks whether this connector is valid in the context of this
        design and/or corpus.
        """

        self.from_side.validate(design, corpus)
        self.to_side.validate(design, corpus)

        if design.connection(self.from_side) != self:
            raise RuntimeError(
                f"Connection not properly initialized in design."
            )

        if design.connection(self.to_side) != self:
            raise RuntimeError(
                f"Connection not properly initialized in design."
            )

class AbstractDesign(ABC):
    """
    Abstract interface representing a single design in a corpus.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The component name.
        """
        ...

    @property
    @abstractmethod
    def extra(self) -> object:
        """
        Extra info about design.
        """
        ...

    @property
    @abstractmethod
    def parameter_dict(self) -> Dict[str,DesignParameter]:
        """
        A dict of  all the parameters in the design
        """
        ...

    @property
    def parameters(self) -> Iterator[DesignParameter]:
        """
        An iterator of all the parameters in the design
        """
        return self.parameter_dict.values()

    def parameter(self, name : str) -> DesignParameter:
        """
        Accessor for a specific parameter.
        """
        return self.parameter_dict[name]

    def has_parameter(self, name : str) -> bool:
        """
        Does a given parameter exist?
        """
        return name in self.parameter_dict

    @property
    @abstractmethod
    def component_dict(self) -> Dict[str,DesignComponent]:
        """
        A dict of  all the components in the design
        """
        ...

    @property
    def components(self) -> Iterator[DesignComponent]:
        """
        An iterator of all the components in the design
        """
        return self.component_dict.values()

    def component(self, name : str) -> DesignComponent:
        """
        Accessor for a specific component.
        """
        return self.component_dict[name]

    def has_component(self, name : str) -> bool:
        """
        Is there a component with a given name?
        """
        return name in self.component_dict

    @property
    @abstractmethod
    def connections(self) -> Iterator[DesignConnection]:
        """
        De-duplicated list of connections in this component
        """
        ...

    @abstractmethod
    def add_connection(self, conn: DesignConnection):
        """
        Adds a connection to this component properly.
        """
        ...

    @property
    def rep(self) -> object:
        """
        Render the design into a JSON serialazable object.
        """

        return dict(
            name = self.name,
            extra = self.extra,
            parameters  = [param.rep for param in self.parameters ],
            components  = [comp.rep  for comp  in self.components ],
            connections = [conn.rep  for conn  in self.connections],
        )

    def validate(self, corpus : Optional[CorpusReader] = None):
        """
        Checks whether this design is valid w/ a possible corpus.
        """

        for param in self.parameters:
            param.validate(self, corpus)

        for comp in self.components:
            comp.validate(self, corpus)

        for _, conn in self.connection_dict.items():
            conn.validate(self, corpus)


class AbstractDesignCorpus(ABC):
    """
    Represents a corpus that can be read and queried.
    """

    @abstractmethod
    def __getitem__(self, comp :str) -> AbstractDesign:
        """
        Allows you to get a design by providing its name.

        Implementations may error on call or defer errors till compoent
        is used.
        """
        ...

    @abstractmethod
    def __contains__(self, comp :str) -> bool:
        """
        Eagerly test whether a design is in this corpus.
        """
        ...

    @property
    @abstractmethod
    def designs(self) -> Iterator[str]:
        """
        Iterates over a list of all designs.
        """
        ...

    @property
    def rep(self) -> object:
        """
        Produce a json serializable version of the corpus.
        """
        return {design : self[design].rendered() for design in self.designs()}

    def validate(self, corpus : Optional[CorpusReader] = None):
        """
        Checks whether this design is valid w/ a possible corpus.
        """

        for design in self.designs:
            design.validate(corpus)
