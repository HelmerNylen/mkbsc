from json import dumps, loads
import os
from queue import LifoQueue
from subprocess import call
from typing import Any, Dict, Iterable, List, Literal, Union

from mkbsc.state import State
from mkbsc.multiplayer_game import MultiplayerGame


def export(game: MultiplayerGame,
           filename: str,
           view: bool = True,
           folder: str = "pictures",
           epistemic: Union[str, Literal[False]] = "nice",
           supress_edges: bool = False,
           group_observations=None,
           target_states=None,
           **kwargs):
	"""Exports the game as a picture
	
	view -- if true, opens the file when done
	folder -- the subfolder to save the picture in
	epistemic -- how to render the states in the graph. Can be 'verbose', 'nice' or 'isocheck'
	supress_edges -- if true, does not draw labels for the transitions
	group_observations -- if true, the observations will be arranged in marked subgraphs. Only works for singleplayer games
	target_states -- the states (or singleton knowledge in states) which should be marked in the rendered graph"""

	dot_path = os.path.join(folder, filename + ".dot")
	png_path = os.path.join(folder, filename + ".png")
	with open(dot_path, "w") as dotfile:
		dotfile.write(
		    game.to_dot(epistemic=epistemic,
		                supress_edges=supress_edges,
		                group_observations=group_observations,
		                target_states=target_states,
		                **kwargs))

	call(["dot", "-Tpng", dot_path, "-o", png_path])
	if view:
		call(("start " if os.name == "nt" else "xdg-open ") + png_path,
		     shell=True)


def from_file(
    filename: str,
    folder: str = "games",
    fileext: str = ".game",
    validate: bool = True,
) -> MultiplayerGame:
	"""Import a game from a file

	validate -- if false, skips the computationally expensive validation when creating the game"""
	if folder and len(folder) != 0:
		folder += "/"
	else:
		folder = ""
	with open(folder + filename + fileext, encoding="utf8", newline="\n") as f:
		try:
			return _parse(f, validate)
		except StopIteration as e:
			raise EOFError from e


def from_string(string: str, validate: bool = True) -> MultiplayerGame:
	"""Import a game from a string

	validate -- if false, skips the computationally expensive validation when creating the game"""
	try:
		return _parse(string.split('\n'), validate)
	except StopIteration as e:
		raise ValueError from e


def to_file(game: MultiplayerGame,
            filename: str,
            folder: str = "games",
            fileext: str = ".game"):
	"""Export a game to a file"""
	if folder and len(folder) != 0:
		folder += "/"
	else:
		folder = ""
	with open(folder + filename + fileext,
	          mode="w",
	          encoding="utf8",
	          newline="\n") as f:
		for line in _serialize(game):
			f.write(line + "\n")


def to_string(game: MultiplayerGame) -> str:
	"""Export a game to a string"""
	return "\n".join(_serialize(game))


def _serialize(game: MultiplayerGame) -> Iterable[str]:
	#Alphabet
	yield "Alphabet:"

	action_id = 0
	alphabet_dicts: List[Dict[Any,
	                          int]] = [{} for player in range(game.player_count)
	                                  ]
	for i, playeralphabet in enumerate(game.alphabet):
		for action in playeralphabet:
			alphabet_dicts[i][action] = action_id
			action_id += 1
		yield ",".join([repr(action) for action in playeralphabet])

	yield ""

	#States
	def _pick(_set):
		for x in _set:
			return x
		raise None

	state_id = 0
	state_dict = {}
	states = game.states
	state_stack: LifoQueue[State] = LifoQueue()

	while type(_pick(states)[0]) is frozenset:
		newstates = set()
		for state in states:
			state_dict[state] = state_id
			state_stack.put(state)

			for player in range(game.player_count):
				newstates.update(state[player])

			state_id -= 1
		states = tuple(newstates)

	id_add = abs(state_id) + len(states) - 1
	yield "Base States:"

	state_id -= len(states)
	for state in states:
		state_id += 1
		state_dict[state] = state_id
		yield "{0}={1}".format(state_id + id_add, repr(state[0]))

	yield ""
	yield "Knowledge States:"

	while state_stack.qsize() != 0:
		state = state_stack.get()
		yield "{0}={1}".format(
		    state_dict[state] + id_add, "|".join(
		        map(
		            lambda knowledge: ",".join(
		                [str(state_dict[s] + id_add) for s in knowledge]),
		            state.knowledges)))

	yield ""

	yield "Initial State: " + str(state_dict[game.initial_state] + id_add)
	yield ""

	#Observations
	yield "Observations:"

	for partitioning in game.partitionings:
		yield "|".join([
		    ",".join(str(state_dict[state] + id_add)
		             for state in observation)
		    for observation in partitioning
		])

	yield ""

	#Transitions
	yield "Transitions:"

	for transition in game.transitions:
		yield "{0} {1} {2}".format(
		    state_dict[transition.start] + id_add, ",".join([
		        str(alphabet_dicts[player][action])
		        for player, action in enumerate(transition.joint_action)
		    ]), state_dict[transition.end] + id_add)

	yield ""

	yield "Attributes: " + dumps(game.graph.graph["graph"])


def _parse(iterable: Iterable[str], validate: bool = True) -> MultiplayerGame:
	iterator = iter(iterable)

	iterator.__next__()

	#Alphabet
	alphabet_dict = {}
	alphabet = []

	line = iterator.__next__().strip()
	action_id = 0
	while line != "" and not line.isspace():
		currentalphabet = []

		i = 0
		while i < len(line):
			if line[i] in "\'\"":
				nextquote = line.index(line[i], i + 1)
				value: Union[int, str] = line[i + 1:nextquote]
				i = nextquote + 2

				currentalphabet.append(value)
				alphabet_dict[action_id] = value

			elif line[i].isdigit():
				nextcomma = line.find(',', i)
				if nextcomma == -1:
					nextcomma = len(line)
				value = int(line[i:nextcomma])
				i = nextcomma + 1

				currentalphabet.append(value)
				alphabet_dict[action_id] = value

			else:
				raise TypeError(line, "Index: " + str(i))

			action_id += 1

		alphabet.append(currentalphabet)
		line = iterator.__next__().strip()

	iterator.__next__()

	#Base States
	state_dict = {}
	top_states = set()

	line = iterator.__next__()
	while line != "" and not line.isspace():
		id = int(line[:line.index("=")])
		value = line[line.index("=") + 1:]

		if value[0] in "\'\"":
			value = value[1:-2]

		elif value[0].isdigit():
			value = int(value)

		else:
			raise TypeError(line, value)

		state = State(value)
		state_dict[id] = state
		top_states.add(state)

		line = iterator.__next__()

	iterator.__next__()

	#Knowledge States
	line = iterator.__next__()
	while line != "" and not line.isspace():
		id = int(line[:line.index("=")])
		linepart = line[line.index("=") + 1:]

		knowledge = [
		    frozenset(state_dict[int(i)]
		              for i in playerknowledge.split(","))
		    for playerknowledge in linepart.split("|")
		]

		state = State(*knowledge)
		state_dict[id] = state
		top_states.add(state)
		for playerknowledge in knowledge:
			top_states.difference_update(playerknowledge)

		line = iterator.__next__()

	line = iterator.__next__()
	initial_state = state_dict[int(line[line.index(": ") + 2:])]

	iterator.__next__()
	iterator.__next__()

	#Observations
	state_groupings = []

	line = iterator.__next__()
	while line != "" and not line.isspace():
		grouping = [[state_dict[int(s)]
		             for s in observation.split(",")]
		            for observation in line.split("|")]
		state_groupings.append(grouping)

		line = iterator.__next__()

	iterator.__next__()

	#Transitions
	transitions = []

	line = iterator.__next__()
	while line != "" and not line.isspace():
		state_from, joint_action, state_to = line.split(" ")
		transition = [
		    state_dict[int(state_from)],
		    [alphabet_dict[int(action)] for action in joint_action.split(",")],
		    state_dict[int(state_to)],
		]
		transitions.append(transition)

		line = iterator.__next__()

	line = iterator.__next__()
	attributes = loads(line[line.index(": ") + 2:])

	return MultiplayerGame._create_from_serialized(top_states,
	                                               initial_state,
	                                               alphabet,
	                                               transitions,
	                                               state_groupings,
	                                               validate=validate,
	                                               **attributes)
