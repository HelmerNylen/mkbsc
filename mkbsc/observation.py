from typing import Any, Dict, Iterator, Optional

import networkx as nx  # type: ignore
from networkx.drawing.nx_pydot import to_pydot  # type: ignore

from mkbsc import state


class Observation:
	"""Represents an observation of several states in a game"""
	_idcounter = 0

	def __init__(self, *states: state.State):
		"""Create a new observation

        ex. o = Observation(s0, s2, s3)
        """
		self.states = tuple(states)
		self.id = Observation._idcounter
		Observation._idcounter += 1

	def __len__(self) -> int:
		"""Return the number of states in the observation"""
		return len(self.states)

	def __iter__(self) -> Iterator[state.State]:
		"""Iterate over the states"""
		for state in self.states:
			yield state

	def _subgraph(self,
	              attributes: Optional[Dict[str, Any]] = None) -> nx.Graph:
		"""Generates a networkx subgraph of the states"""
		subgraph = nx.Graph()
		subgraph.add_nodes_from(self.states)

		if not attributes:
			attributes = {"style": "dashed"}
		subgraph.graph["graph"] = attributes

		return subgraph

	def to_dot(self, attributes: Optional[Dict[str, Any]] = None) -> str:
		"""Returns the dot representation of the states in the observation"""
		s = to_pydot(self._subgraph(attributes)).to_string()
		s = "subgraph cluster" + str(self.id) + " {" + s[s.index("\n"):]
		return s
