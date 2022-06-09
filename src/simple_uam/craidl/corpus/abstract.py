from attrs import define, field
from typing import List, Dict, Any, Iterator, Tuple, Optional
from abc import ABC, abstractmethod

class ComponentReader(ABC):
    """
    Abstract interface representing a single component in a corpus.
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
    def connections(self) -> Iterator[str]:
        """
        The list of connections this component type can have.
        """
        ...

    @property
    @abstractmethod
    def cad_part(self) -> Optional[str]:
        """
        Get a string with the name of the cad file for this component.
        """
        ...

    @property
    @abstractmethod
    def cad_properties(self) -> List[Dict[str,Any]]:
        """
        Cad Properties for this component.

        Returns:
          A list of dictionaries with 'PROP_NAME' and 'PROP_VALUE' entries.
        """
        ...

    @property
    @abstractmethod
    def cad_params(self) -> List[Dict[str,Any]]:
        """
        Cad parameters for this component.

        Returns:
          A list of dictionaries with 'PROP_NAME' and 'PROP_VALUE' entries.
        """
        ...

    @abstractmethod
    def cad_connection(self, conn : str) -> Optional[str]:
        """
        Get the connection specifier as used in this component's cad file.

        Arguments:
          conn: Name of connection as string.

        Returns: String name of connection specifier.
        """
        ...


    @property
    @abstractmethod
    def properties(self) -> List[Dict[str,Any]]:
        """
        Properties for this component.

        Returns:
          A list of dictionaries with 'PROP_NAME' and 'PROP_VALUE' entries.
        """
        ...

    @property
    @abstractmethod
    def params(self) -> List[Dict[str,Any]]:
        """
        Parameters for this component.

        Returns:
          A list of dictionaries with 'PROP_NAME' and 'PROP_VALUE' entries.
        """
        ...

class CorpusReader(ABC):
    """
    Represents a corpus that can be read and queried.
    """

    @abstractmethod
    def __getitem__(self, comp :str) -> ComponentReader:
        """
        Allows you to get a component by providing its name.

        Implementations may error on call or defer errors till compoent
        is used.
        """
        ...

    @property
    @abstractmethod
    def components(self) -> Iterator[ComponentReader]:
        """
        Iterates over a list of all components.
        """
        ...
