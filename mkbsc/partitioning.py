from typing import Iterable, Iterator

from mkbsc import observation
from mkbsc import state


class Partitioning:
	"""Represents a partitioning of observations"""

	def __init__(self, *observations: observation.Observation):
		"""Create a new partitioning

        ex. p = Partitioning(o1, o2, o3)
        """
		self.observations = tuple(observations)

	def __iter__(self) -> Iterator[observation.Observation]:
		"""Iterate over the observations"""
		for observation in self.observations:
			yield observation

	def valid(self, states: Iterable[state.State]) -> bool:
		"""Test if the partitioning contains all states"""
		s = set()
		for observation in self.observations:
			for state in observation:
				if state in s:
					return False
				else:
					s.add(state)

		return frozenset(s) == frozenset(states)
