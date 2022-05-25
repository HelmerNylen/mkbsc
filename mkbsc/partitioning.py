from typing import Generic, Iterable, Iterator, Tuple

from mkbsc import observation
from mkbsc import state

_Observations = Tuple[observation.Observation[state.StateContent], ...]


class Partitioning(Generic[state.StateContent]):
	"""Represents a partitioning of observations"""

	def __init__(self,
	             *observations: observation.Observation[state.StateContent]):
		"""Create a new partitioning

        ex. p = Partitioning(o1, o2, o3)
        """
		self.observations: _Observations = tuple(observations)

	def __iter__(self) -> Iterator[observation.Observation[state.StateContent]]:
		"""Iterate over the observations"""
		yield from self.observations

	def valid(self, states: Iterable[state.State[state.StateContent]]) -> bool:
		"""Test if the partitioning contains all states"""
		collected = set()
		for obs in self.observations:
			for st in obs:
				if st in collected:
					return False
				else:
					collected.add(st)

		return frozenset(collected) == frozenset(states)
