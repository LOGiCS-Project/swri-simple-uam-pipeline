from attrs import define, frozen, field
from typing import List, Dict, Any, Iterator, Tuple, Optional
from abc import ABC, abstractmethod
from simple_uam.craidl.corpus.abstract import CorpusReader

@define
class DesignParameterProperty():
    instance_name : str = field()
    property_name : str = field()

    def rendered(self) -> object:
        """
        This parameter as a JSON serializable object.
        """
        return dict(
            component_name = self.instance_name,
            component_property = self.property_name,
        )

class AbstractDesignParameter(ABC):
    """
    Abstract interface representing a single parameter in a design
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The parameter name.
        """
        ...

    @property
    @abstractmethod
    def value(self) -> str:
        """
        The parameter vanlue.
        """
        ...

    @property
    @abstractmethod
    def properties(self) -> List[DesignParameterProperty]:
        """
        A map from component name to property name with this parameter.
        """
        ...

    @property
    def component_properties(self) -> List[Dict[str,str]]:
        """
        The rendered component properties with members as tuples
        """
        return [prop.rendered() for prop in self.properties]

    @component_properties.setter
    def component_properties(self, props : List[Dict[str,str]]):
        self.properties = [
            DesignParameterProperty(
                instance_name = prop['component_name'],
                property_name = prop['component_property']
            )
            for prop in props
        ]

    @abstractmethod
    def add_property(self, prop: DesignParameterProperty):
        """
        Adds a single property to the list of component properties.
        """
        ...

    def rendered(self) -> object:
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

class AbstractDesignComponent(ABC):
    """
    Abstract interface representing a single component in a design.
    """

    @property
    @abstractmethod
    def instance(self) -> str:
        """
        The name of the component instance
        """
        ...

    @property
    @abstractmethod
    def type(self) -> Optional[str]:
        """
        The type of the component instance
        """
        ...

    @property
    @abstractmethod
    def choice(self) -> str:
        """
        The choice of the component instance
        """
        ...

    def rendered(self) -> object:
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

@frozen
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

class AbstractDesignConnection(ABC):
    """
    A connection between two connectors in the abstract
    """

    @property
    @abstractmethod
    def from_side(self) -> DesignConnector:
        """
        Connector on the from side of the connection.
        """
        ...

    @property
    @abstractmethod
    def to_side(self) -> DesignConnector:
        """
        Connector on the to side of the connection.
        """
        ...

    def rendered(self) -> object:
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
    def parameter_dict(self) -> Dict[str,AbstractDesignParameter]:
        """
        A dict of  all the parameters in the design
        """
        ...

    @property
    def parameters(self) -> Iterator[AbstractDesignParameter]:
        """
        An iterator of all the parameters in the design
        """
        return self.parameter_dict.values()

    def parameter(self, name : str) -> AbstractDesignParameter:
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
    def component_dict(self) -> Dict[str,AbstractDesignComponent]:
        """
        A dict of  all the components in the design
        """
        ...

    @property
    def components(self) -> Iterator[AbstractDesignComponent]:
        """
        An iterator of all the components in the design
        """
        return self.component_dict.values()

    def component(self, name : str) -> AbstractDesignComponent:
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
    def connection_dict(self) -> Dict[DesignConnector, AbstractDesignConnection]:
        """
        A dictionary of connectors to abstract connections, only connections
        where the connector is the front connector are printed.
        """

    @property
    def connections(self) -> Iterator[AbstractDesignConnection]:
        """
        De-duplicated list of connections in this component
        """
        for from_side, conn in self.connection_dict.items():
            if conn.from_side == from_side:
                yield conn

    def connection(self, side: DesignConnector) -> AbstractDesignConnection:
        """
        Accessor for a specific connection.
        """
        return self.connection_dict[side]

    def has_connection(self, side: DesignConnector) -> AbstractDesignConnection:
        """
        Does a specific connection exist?
        """
        return side in self.connection_dict

    def add_connection(self, conn: AbstractDesignConnection):
        """
        Adds a connection to this component properly.
        """

        # Defer write so you can catch errors w/o leaving things in an
        # invalid state.
        f_conn = None
        t_conn = None

        if conn.from_side not in self.connection_dict:
            f_conn = conn
        else:
            other = self.connection_dict[conn.from_side]
            if not (conn == other or conn.is_flipped(other)):
                raise RuntimeError(f"Connection already exists at: {conn.from_side}")

        if conn.to_side not in self.connection_dict:
            t_conn = conn
        else:
            other = self.connection_dict[conn.to_side]
            if not (conn == other or conn.is_flipped(other)):
                raise RuntimeError(f"Connection already exists at: {conn.to_side}")

        if f_conn:
            self.connection_dict[conn.from_side] = f_conn

        if t_conn:
            self.connection_dict[conn.to_side] = t_conn

    def rendered(self) -> object:
        """
        Render the design into a JSON serialazable object.
        """

        return dict(
            name = self.name,
            extra = self.extra,
            parameters  = [param.rendered() for param in self.parameters ],
            components  = [comp.rendered()  for comp  in self.components ],
            connections = [conn.rendered()  for conn  in self.connections],
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

    def rendered(self) -> object:
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
