from itertools import combinations, chain
from collections import deque
from typing import Iterable, Set

from mkbsc import state


def _permute(iterables):
	"""Generate every permutation taking one item from each iterable

    ex. _permute('ab', [1, 2]) -> ('a', 1), ('a', 2), ('b', 1), ('b', 2) in some order"""

	iterables = tuple(
	    iterable if hasattr(iterable, '__getitem__') else tuple(iterable)
	    for iterable in iterables)
	indexes = [0] * len(iterables)
	for iterable in iterables:
		if len(iterable) == 0:
			return

	while indexes[-1] < len(iterables[-1]):
		yield tuple(iterables[i][indexes[i]] for i in range(len(iterables)))
		i = 0
		indexes[i] += 1
		while indexes[i] >= len(iterables[i]) and i + 1 < len(iterables):
			indexes[i] = 0
			i += 1
			indexes[i] += 1


def _lookup(states, knowledge, single_knowledge=True):
	"""Find the state with the specified knowledge"""
	if single_knowledge:
		knowledge = (knowledge,)
	for state in states:
		if state.knowledges == knowledge:
			return state

	raise KeyError("Could not find a matching state. Searching for "
	               f"{knowledge!r} in {states!r}")


def _lookup_by_base(states: Iterable[state.State],
                    base: Set[state.State]) -> Set[state.State]:
	"""Find the state with the specified consistent base (see state.py)"""

	res = set()
	for state in states:
		b = state.consistent_base()
		if len(b) != len(base):
			continue

		base_to_check = base.copy()

		include = True
		for basestate in b:
			for valid in base_to_check:
				if basestate is valid or basestate.knowledges == (valid,):
					base_to_check.remove(valid)
					continue
				include = False
				break
			if not include:
				break

		if include and len(base_to_check) == 0:
			res.add(state)

	return res


def _reachable(graph, initial):
	"""Return all reachable nodes in a networkx graph reachable from a node"""
	res = set()
	to_check = deque([initial])

	while len(to_check):
		neighbors = graph.neighbors(to_check.pop())
		for neighbor in neighbors:
			if neighbor not in res:
				to_check.appendleft(neighbor)
				res.add(neighbor)
	return res


def powerset(iterable):
	"""Generate the powerset of an iterable"""
	s = list(iterable)
	return chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))


def consistent(states):
	"""Return the states in the previous multiplayer game which are consistent, given a set of transformed singleplayer states"""
	if not len(states) or len(states[0].knowledges) != 1:
		return set()

	res = set(states[0][0])
	for state in states:
		res = res.intersection(state[0])
	return res


def iterate_until_isomorphic(G, limit=-1, print_size=False, verbose=True):
	"""Iterate the MKBSC until the graph stabilizes or the limit is reached. Returns a log of graph sizes, the final game and whether the final game is stabilized
    
    G -- the game to begin with
    limit -- the maximum number of iterations. Use -1 (default) to remove the limit
    print_size -- if true, continuously prints the size of the graph
    verbose -- if false, logs only the number of nodes in the graph"""

	current = G
	currentK = None
	i = 0
	last_iso = 0

	log = []

	def p(index, size, iso=0):
		if verbose:
			s = "G" + str(index) + "K:\t" + str(size) + " nodes"

			if iso == 1:
				s += " (isomorphic)"
			elif iso == 2:
				s += " (isomorphic with equivalent observations)"
		else:
			s = size

		if print_size:
			print(s)

		log.append(s)

	p(0, len(G.states))

	while limit == -1 or i < limit:
		currentK = current.KBSC()
		i += 1

		if len(current.states) == len(
		    currentK.states) and current.isomorphic(currentK):
			if current.isomorphic(currentK, consider_observations=True):
				last_iso = 2
				p(i, len(currentK.states), 2)
				break
			else:
				last_iso = 1
				p(i, len(currentK.states), 1)
		else:
			last_iso = 0
			p(i, len(currentK.states))

		current = currentK

	return log, current, last_iso
