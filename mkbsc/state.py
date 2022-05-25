from typing import Any, FrozenSet, Generic, Set, Tuple, TypeVar

StateContent = TypeVar("StateContent", Any, FrozenSet)


class State(Generic[StateContent]):
	"""Represents a game state, with separate knowledge for each player

	The knowledge is stored as a tuple, and can be accessed by State().knowledges[playerindex]
	or simply State()[playerindex]. The players are zero-indexed. In the base game, the states'
	knowledge should be an integer or short string, the same for all players. This case is
	treated separately and the tuple State().knowledges is a singleton. When applying the KBSC, the new
	states' knowledge are sets of states from the previous iteration. For example, after two
	iterations the states' knowledge are sets of states, whose knowledge are sets of states,
	whose knowledge could be integers.
	"""

	def __init__(self, *knowledges: StateContent):
		"""Create a new state

		ex. s = State(1)
		"""

		self.knowledges: Tuple[StateContent, ...] = tuple(knowledges)

	def __getitem__(self, index: int) -> StateContent:
		"""Get the knowledge of the specified player

		Will work as expected even if knowledges is a singleton"""

		if self.is_singleplayer:
			return self.knowledges[0]
		else:
			return self.knowledges[index]

	# TODO: Use a separate SingleplayerState class.
	@property
	def is_singleplayer(self) -> bool:
		"""Whether there is only one element in the knowledge tuple.

		The knowledge tuple of states in a singleplayer game have only
		one element. This may also be the case for base states.
		"""
		return len(self.knowledges) == 1

	# TODO: this could probably be done in a less hacky way
	@property
	def is_base_state(self) -> bool:
		"""Whether this is a state belonging to the original game.
		
		The elements of knowledge tuples in states that have had the KBSC
		applied are frozen sets.
		"""
		return not isinstance(self.knowledges[0], frozenset)

	def __str__(self) -> str:
		return repr(self)

	compact_representation = False

	def __repr__(self) -> str:
		"""Return a compact string representation of the knowledge"""

		#if we are writing to a dot file we only need a unique string, not the full representation
		if State.compact_representation:
			return str(id(self))


#        return "s" + str(self.knowledges)
		if self.is_singleplayer:
			if self.is_base_state:
				return str(self.knowledges[0])
			else:
				return str(set(self.knowledges[0]))
		else:
			return str(
			    tuple(
			        set(self.knowledges[i])
			        for i in range(len(self.knowledges))))

	__indent = "\t"

	def epistemic_verbose(self, level: int = 0) -> str:
		"""Return a verbose representation of the knowledge. Not recommended for overly iterated games."""
		if self.is_singleplayer:
			return State.__indent * level + "We are in " + str(
			    self.knowledges[0]) + "\n"

		s = ""
		for player, knowledge in enumerate(self.knowledges):
			s += State.__indent * level + "Player " + str(player) + " knows:\n"
			s += (State.__indent * (level + 1) + "or\n").join(
			    [state.epistemic(level + 1) for state in knowledge])

		return s

	def epistemic_nice(self, level: int = 0) -> str:
		"""Return a compact but still quite readable representation of the knowledge"""

		def __wrap(state: "State", l: int) -> str:
			if self.is_singleplayer:
				return str(state.knowledges[0])
			else:
				return "(" + state.epistemic_nice(l + 1) + ")"

		if level == 0:
			if not self.is_singleplayer:
				return "\n".join([
				    "{" + ", ".join([
				        state.epistemic_nice(level + 1) for state in knowledge
				    ]) + "}" for knowledge in self.knowledges
				])
			else:
				if type(self.knowledges[0]) is frozenset:
					return "{" + ", ".join([
					    state.epistemic_nice(level + 1)
					    for state in self.knowledges[0]
					]) + "}"
				else:
					return str(self.knowledges[0])
		else:
			if not self.is_singleplayer:
				return "-".join([
				    "".join([__wrap(state, level)
				             for state in knowledge])
				    for knowledge in self.knowledges
				])
			else:
				if type(self.knowledges[0]) is frozenset:
					return "{" + ", ".join([
					    state.epistemic_nice(level + 1)
					    for state in self.knowledges[0]
					]) + "}"
				else:
					return str(self.knowledges[0])

	def epistemic_isocheck(self) -> str:
		"""Return the most compact representation, only containing which states in the base game are possible in this state"""
		return ", ".join(
		    [str(state.knowledges[0]) for state in self.consistent_base()])

	def consistent_base(self) -> Set["State[Any]"]:
		"""Return the states in the base game that are possible in this state

		This assumes that the knowledges in the base game are singletons"""

		def _pick(_set):
			for x in _set:
				return x
			raise ValueError("Set was empty")

		states: Any = {self}
		if len(self.knowledges) == 1 and not self.is_base_state:
			states = {self.knowledges[0]}

		while len(_pick(states).knowledges) > 1:
			states = set.intersection(*[
			    set.intersection(*[
			        set(state[player]) for player in range(len(self.knowledges))
			    ]) for state in states
			])

		return states

	#workaround to make sure the networkx isomorphism check works
	orderable = False

	def __gt__(self, other: "State[Any]"):
		if not isinstance(other, State):
			return NotImplemented
		assert State.orderable
		return id(self) > id(other)

	def __lt__(self, other: "State[Any]"):
		if not isinstance(other, State):
			return NotImplemented
		assert State.orderable
		return id(self) < id(other)
