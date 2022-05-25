from .alphabet import Alphabet
from .state import State, StateContent
from .observation import Observation
from .partitioning import Partitioning
from .transition import Transition
from .helper_functions import _permute, _lookup, _lookup_by_base, _reachable, consistent, powerset

#import threading
#import time
from itertools import chain, combinations, permutations
from collections import deque
from typing import Any, Callable, Dict, FrozenSet, Generic, Iterable, List, Literal, Optional, Sequence, Set, Tuple, TypeVar, Union

import networkx as nx  # type: ignore
from networkx.algorithms.isomorphism import is_isomorphic  # type: ignore
from networkx.drawing.nx_pydot import to_pydot  # type: ignore

try:
	from types import EllipsisType  # type: ignore
except ImportError:
	EllipsisType = Any

T = TypeVar("T")
# Used in MultiplayerGame.create()
_EdgesSpecification = Iterable[Tuple[StateContent, Union[T, EllipsisType],
                                     Union[StateContent, Set[StateContent]]]]
_ExpandedEdges = List[Tuple[StateContent, Union[T, EllipsisType], StateContent]]
_GroupingSpecification = Iterable[Iterable[Union[Iterable[StateContent],
                                                 EllipsisType]]]


class MultiplayerGame(Generic[StateContent, T]):
	"""Represents a game of one or more players

    The easiest way to create a new game is to call MultiplayerGame.create() with the
    appropriate parameters. Among other things, the game has methods to apply the (M)KBSC,
    to project the game onto a certain player, to check for isomorphism and to export the
    game as a dot string."""

	def __init__(self,
	             states: Tuple[State[StateContent], ...],
	             initial_state: State[StateContent],
	             alphabet: Alphabet[T],
	             transitions: Tuple[Transition[StateContent, T], ...],
	             partitionings: Tuple[Partitioning[StateContent], ...],
	             remove_unreachable: bool = False,
	             validate: bool = False,
	             **attributes: Any):
		"""Create a new game and optionally validate and remove unreachable states."""

		self.states: Tuple[State[StateContent], ...] = states
		self.initial_state: State[StateContent] = initial_state
		self.alphabet: Alphabet[T] = alphabet
		self.transitions: Tuple[Transition[StateContent, T], ...] = transitions
		self.partitionings: Tuple[Partitioning[StateContent], ...] = partitionings

		self.graph = nx.MultiDiGraph()
		self.graph.graph["graph"] = attributes
		default_attributes = {
		    #"rankdir": "LR",
		    "nodesep": 0.5,
		    "ranksep": 0.5,
		    "concentrate": False,
		    "splines": "True"
		}
		for key in default_attributes:
			if key not in self.graph.graph["graph"]:
				self.graph.graph["graph"][key] = default_attributes[key]

		self.player_count = len(alphabet)

		assert len(partitionings) == self.player_count

		if validate:
			for partitioning in partitionings:
				assert partitioning.valid(states)

		for state in states:
			self.graph.add_node(state)
		for transition in transitions:
			if validate:
				assert transition.start in states and transition.end in states
				for i, action in enumerate(transition.joint_action):
					assert action in self.alphabet[i]

			self.graph.add_edge(transition.start,
			                    transition.end,
			                    label=transition.label(),
			                    key=transition.joint_action,
			                    action=transition.joint_action)

		if remove_unreachable:
			to_remove = (set(self.states) - _reachable(
			    self.graph, self.initial_state)) - {self.initial_state}
			#print("Removing " + str(to_remove))
			self.graph.remove_nodes_from(to_remove)

	@classmethod
	def create(
	    cls,
	    content: Iterable[StateContent],
	    initial: StateContent,
	    alphabet: Union[Alphabet[T], Iterable[Iterable[T]]],
	    transition_edges: _EdgesSpecification,
	    state_groupings: _GroupingSpecification,
	    **attributes: Any,
	) -> "MultiplayerGame[StateContent, T]":
		"""Create a new game and validate it

        content -- the knowledge of the states, ex. [1, 2, 3] or range(5)
        initial -- the knowledge in the initial state, ex. 1
        alphabet -- the alphabet of actions, ex. (['a', 'b'], ['1', '2']) or ('ab', '12')
        transition_edges -- the edges in the game graph, ex. [(1, ('a', '1'), 2), (2, 'b1', 3)]
        state_groupings -- the observation partitionings, ex. ([[1, 2], [3]], [[1], [2, 3]])"""

		states = tuple(set(map(lambda x: State(x), content)))
		initial_state = _lookup(states, initial)

		if not isinstance(alphabet, Alphabet):
			alphabet = Alphabet(*alphabet)

		transitions = []
		expanded_edges: _ExpandedEdges = []
		for edge_iterable in [transition_edges, expanded_edges]:
			for from_, label, to in edge_iterable:
				if isinstance(to, set):
					for edge_end in to:
						expanded_edges.append((from_, label, edge_end))
					continue

				start = _lookup(states, from_)
				end = _lookup(states, to)
				if label == Ellipsis:
					for joint_action in alphabet.permute():
						transitions.append(Transition(start, joint_action, end))
				else:
					transitions.append(Transition(start, label, end))

		partitionings = []
		for grouping in state_groupings:
			observations = []
			ellipsis = False
			for group in grouping:
				if group == Ellipsis:
					ellipsis = True
					continue
				observations.append(
				    Observation(*[_lookup(states, s) for s in group]))
			if ellipsis:
				covered_states: Set[State[StateContent]] = set()
				for observation in observations:
					covered_states.update(observation)

				for state in states:
					if state not in covered_states:
						observations.append(Observation(state))

			partitionings.append(Partitioning(*observations))

		return cls(
		    states,
		    initial_state,
		    alphabet,
		    tuple(transitions),
		    tuple(partitionings),
		    remove_unreachable=False,
		    validate=True,
		    **attributes,
		)

	@classmethod
	def _create_from_serialized(cls,
	                            states,
	                            initial_state,
	                            alphabet,
	                            transitions,
	                            state_groupings,
	                            validate=True,
	                            **attributes):
		"""Create a new game from serialized data and validate it"""

		states = tuple(states)

		if type(alphabet) is not Alphabet:
			alphabet = Alphabet(*alphabet)

		transitions = tuple(map(lambda edge: Transition(*edge), transitions))

		partitionings = tuple(
		    map(
		        lambda grouping: Partitioning(
		            *[Observation(*group) for group in grouping]),
		        state_groupings))

		return cls(states, initial_state, alphabet, transitions, partitionings,
		           False, validate, **attributes)

	def state(self, knowledge):
		"""Get the state object with the specified knowledge"""
		return _lookup(self.states, knowledge,
		               len(self.states[0].knowledges) == 1)

	def states_by_consistent_base(self, base):
		"""Get the state objects which represent the specified base states"""
		return _lookup_by_base(self.states, base)

	def post(self, action, states) -> Set[State]:
		"""Get the states that are possible after taking a certain action in one of the specified states"""

		res = set()
		if self.player_count == 1:
			action = (action,)
		if not hasattr(states, "__iter__"):
			states = (states,)

		for state in states:
			neighbors = self.graph.neighbors(state)
			for neighbor in neighbors:
				edges = self.graph[state][neighbor]
				for key in edges:
					if edges[key]["action"] == action:
						res.add(neighbor)
						break

		return res

	def reachable(self, initial: Optional[State] = None) -> Set[State]:
		"""Get the reachable states in a game, optionally given a certain initial state"""

		res = set()
		if not initial:
			initial = self.initial_state
			res.add(self.initial_state)
		return res.union(_reachable(self.graph, initial))

	def to_dot(self,
	           group_observations: Optional[bool] = None,
	           group_by_base: bool = False,
	           group_edges: bool = True,
	           epistemic: Union[str, Literal[False]] = False,
	           supress_edges: bool = False,
	           color_scheme: str = "set19",
	           colorfunc: Callable[[int], int] = lambda x: x + 1,
	           observations_constrain: bool = True,
	           target_states: Optional[Sequence[Union[State,
	                                                  Set[State]]]] = None,
	           **kwargs) -> str:
		"""Generate a dot representation of the game

        group_observations -- if true, places the nodes in an observation within a subgraph cluster. Only works well for some singleplayer games.
        group_by_base -- if true, places nodes which represent the same states in separate subgraph clusters. Currently yields rather ugly results.
        group_edges -- if true, collects all edges between two nodes into a single edge with all the labels from the original edges. Keeping this true is strongly recommended.
        epistemic -- 'verbose', 'nice' or 'isocheck'. Specifies different ways to label the nodes. The default is similar to 'nice' for few iterations of the KBSC. 'nice' is recommended for checking state contents, 'isocheck' for edges and observation groups.
        supress_edges -- if true, removes the labels from the edges.
        color_scheme -- see https://www.graphviz.org/doc/info/colors.html#brewer for options. defines the coloring for observation equivalence relations for each of the players
        colorfunc -- a function which numbers the players from 1 to be used with the color scheme, or provides the color directly
        observations_constrain -- if false, ignores the observation equivalence relations when generating the graph layout
        target_states -- the states (or singleton knowledge in states) which should be marked in the rendered graph"""

		G = self.graph.copy()

		all_joint_actions = set(self.alphabet.permute())

		if group_edges:
			for node in G:
				for neighbor in list(G.neighbors(node)):
					edges = [
					    edge for edge in G.edges(node, data=True)
					    if edge[1] == neighbor
					]
					if len(edges) == 1:
						continue

					label = ", ".join(map(lambda edge: edge[2]["label"], edges))
					superaction = tuple(edge[2]["action"] for edge in edges)

					if len(set(superaction)) == len(all_joint_actions):
						label = "(-)"

					total_attributes = {}

					for edge in edges:
						if edge[2]["action"]:
							current_attributes = G[edge[0]][edge[1]][edge[2]
							                                         ["action"]]
							for key in current_attributes:
								if key not in ["label", "action", "key"]:
									total_attributes[key] = current_attributes[
									    key]

							G.remove_edge(edge[0], edge[1], edge[2]["action"])

					G.add_edge(node,
					           neighbor,
					           label=label,
					           key=superaction,
					           action=superaction,
					           **total_attributes)

		for edge in G.edges(data="action"):
			if edge[0] == edge[1]:
				G[edge[0]][edge[1]][edge[2]]["dir"] = "back"

		if supress_edges:
			for edge in G.edges(data="action"):
				G[edge[0]][edge[1]][edge[2]]["label"] = ""

		epistemic_functions: Dict[str, Callable[[State], str]] = {
		    "verbose": State.epistemic_verbose,
		    "nice": State.epistemic_nice,
		    "isocheck": State.epistemic_isocheck,
		}
		if epistemic:
			func = epistemic_functions[epistemic.lower()]
			for state in G.nodes():
				G.nodes[state]["label"] = func(state)

		G.add_node("hidden", shape="none", label="")
		G.add_edge("hidden", self.initial_state)

		if target_states:
			for target_state in target_states:
				if not isinstance(target_state, State):
					[target_state] = _lookup_by_base(self.states, target_state)
				G.nodes[target_state]["shape"] = "doublecircle"

		#if group_observations is None:
		#    group_observations = (self.player_count == 1)

		if group_observations:
			State.compact_representation = True
			arr = to_pydot(G).to_string().split("\n")
			for player, partitioning in enumerate(self.partitionings):
				arr[-2:-2] = [
				    observation.to_dot({
				        "style":
                                                                                        "dashed",
				        "label":
                                                                                        "~" + str(player) if self.player_count > 1 else ""
				    }) for observation in partitioning
				]

			State.compact_representation = False
			return "\n".join(arr)
		else:
			for player, partitioning in enumerate(self.partitionings):
				for observation in partitioning:
					if len(observation) > 1:
						for start, end in combinations(observation, 2):
							G.add_edge(
							    start,
							    end,
							    style="dashed",
							    label="~" +
							    str(player) if self.player_count > 1 else "",
							    arrowhead="none",
							    colorscheme=color_scheme,
							    color=colorfunc(player),
							    constraint=observations_constrain)

			State.compact_representation = True
			arr = to_pydot(G).to_string().split("\n")
			if group_by_base:
				groups: Dict[Any, Set[State[StateContent]]] = {}
				for state in self.states:
					fs = frozenset(state.consistent_base())
					if fs not in groups:
						groups[fs] = set()
					groups[fs].add(state)

				#print(groups.keys())

				for i, group in enumerate(groups):
					subgraph = nx.Graph()
					subgraph.graph["graph"] = {"style": "invis"}
					subgraph.add_nodes_from(groups[group])
					s = to_pydot(subgraph).to_string()
					s = "subgraph cluster" + str(i) + " {" + s[s.index("\n"):]
					arr[-2:-2] = [s]

			State.compact_representation = False
			return "\n".join(arr)

	def project(self, player: int) -> "MultiplayerGame":
		"""Project the game onto a player"""

		assert player < self.player_count

		states = self.states
		initial_state = self.initial_state
		alphabet = Alphabet(self.alphabet[player])

		transitions = [
		    Transition(t.start, (t.joint_action[player],), t.end)
		    for t in self.transitions
		]
		partitionings = (self.partitionings[player],)

		attributes = self.graph.graph["graph"]

		return MultiplayerGame(states, initial_state, alphabet,
		                       tuple(transitions), partitionings, **attributes)

	def _synchronous_product(
	        self, games: Sequence["MultiplayerGame"]) -> "MultiplayerGame":
		"""Combine singleplayer knowledge-based games into a single knowledge-based multiplayer game"""

		initial_states = tuple(game.initial_state for game in games)
		initial_knowledges = tuple(
		    state.knowledges[0] for state in initial_states)
		transitions = []

		states = {initial_knowledges: State(*initial_knowledges)}

		tested = set()
		queue = deque([(initial_states, consistent(initial_states))])

		while len(queue):
			state_tuple, possible = queue.pop()

			if state_tuple in tested:
				continue
			else:
				tested.add(state_tuple)

			for joint_action in self.alphabet.permute():
				possible_post = self.post(joint_action, possible)
				players_post = [
				    games[i].post(joint_action[i], state_tuple[i])
				    for i in range(self.player_count)
				]

				for i in range(self.player_count):
					players_post[i] = set(
					    filter(
					        lambda state: not state.knowledges[0].isdisjoint(
					            possible_post), players_post[i]))

				for possible_knowledge in _permute(players_post):
					knowledge_tuple = tuple(
					    state.knowledges[0] for state in possible_knowledge)
					consistent_to = consistent(possible_knowledge)
					if not consistent_to:
						continue
					if knowledge_tuple not in states:
						states[knowledge_tuple] = State(*knowledge_tuple)
						queue.appendleft((possible_knowledge, consistent_to))

					consistent_from = consistent(state_tuple)
					for t in self.transitions:
						if t.joint_action == joint_action and t.start in consistent_from and t.end in consistent_to:
							break
					else:
						# Prune inconsistent transitions.
						continue

					k = tuple(state.knowledges[0] for state in state_tuple)
					fromstate = states[k]
					tostate = states[knowledge_tuple]
					transition = Transition(fromstate, joint_action, tostate)
					transitions.append(transition)

		initial_state = states[initial_knowledges]
		states_list = list(states.values())
		attributes = self.graph.graph["graph"]

		observation_dicts: List[Dict[StateContent, Set[State[StateContent]]]] = [
		    {} for _ in range(self.player_count)
		]
		for state in states_list:
			for i in range(self.player_count):
				if state[i] in observation_dicts[i]:
					observation_dicts[i][state[i]].add(state)
				else:
					observation_dicts[i][state[i]] = {state}

		partitionings = tuple(
		    Partitioning(*[
		        Observation(*observation_dicts[i][knowledge])
		        for knowledge in observation_dicts[i]
		    ])
		    for i in range(self.player_count))

		return MultiplayerGame(tuple(states_list), initial_state, self.alphabet,
		                       tuple(transitions), partitionings, **attributes)

	def KBSC(self) -> "MultiplayerGame[Any, T]":
		"""Apply the KBSC to the game (or MKBSC in the multiplayer case)"""

		if self.player_count > 1:
			games = [
			    self.project(player).KBSC()
			    for player in range(self.player_count)
			]
			game = self._synchronous_product(games)
			return game

		else:
			#print("Singleplayer KBSC")
			partitioning = self.partitionings[0]

			initial_state = State(frozenset({self.initial_state}))
			states = {initial_state[0]: initial_state}

			transitions = []
			queue = deque([initial_state])
			tested = set()

			while len(queue):
				fromstate = queue.pop()
				if fromstate in tested:
					continue
				else:
					tested.add(fromstate)

				for action in self.alphabet[0]:
					post_states = self.post(action, fromstate.knowledges[0])
					for obs in partitioning:
						knowledge = frozenset(post_states.intersection(obs.states))
						if knowledge:
							tostate = states.get(knowledge)
							if not tostate:
								tostate = State(knowledge)
								states[knowledge] = tostate
								queue.appendleft(tostate)

							transitions.append(
							    Transition(fromstate, (action,), tostate))

			states_tuple = tuple(states.values())

			partitionings = (Partitioning(
			    *[Observation(state) for state in states_tuple]),)
			attributes = self.graph.graph["graph"]

			#print("KBSC game creation")
			return MultiplayerGame(states_tuple,
			                       initial_state,
			                       self.alphabet,
			                       tuple(transitions),
			                       partitionings,
			                       remove_unreachable=True,
			                       **attributes)

	def isomorphic(self,
	               other: "MultiplayerGame[Any, T]",
	               consider_observations: bool = False):
		"""Check if two games have isomorphic graphs with regards to nodes and edges
        
        other -- the other game
        consider_observations -- if true, the equivalence relations from the observations must be the same in both graphs as well"""

		if len(self.states) != len(other.states):
			return False

		a = self.graph.copy()
		b = other.graph.copy()

		for g in ((a, self), (b, other)):
			if consider_observations:
				for player, partitioning in enumerate(g[1].partitionings):
					for observation in partitioning:
						if len(observation) > 1:
							for start, end in permutations(observation, 2):
								g[0].add_edge(start, end, player=str(player))

			g[0].add_node("hidden")
			g[0].add_edge("hidden", g[1].initial_state)

		State.orderable = True
		iso = is_isomorphic(a, b, edge_match=lambda x, y: x == y)
		State.orderable = False
		return iso

	def partitioning_profile(self):
		"""Return a list of each player's pratitioning of observations larger than a single state

        Useful for checking the equivalence relations for large games with complex states"""

		s = ""
		for player, partitioning in enumerate(self.partitionings):
			s += "Player " + str(player) + ": " + ", ".join([
			    str(tuple(sorted([s.epistemic_isocheck()
			                      for s in o])))
			    for o in sorted(partitioning.observations, key=len)
			    if len(o) > 1
			])
			s += "\n"
		return s
