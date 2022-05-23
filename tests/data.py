"""Data used in unit tests."""

from typing import FrozenSet, Iterable, List, TypeVar

from mkbsc import multiplayer_game

T = TypeVar("T")


def _frozen(sets: Iterable[Iterable[T]]) -> List[FrozenSet[T]]:
	return [frozenset(s) for s in sets]


def wagon() -> multiplayer_game.MultiplayerGame:
	states = [0, 1, 2]
	initial = 0
	alphabet = (("wait", "push"), ("wait", "push"))
	transitions = [
	    (0, ("push", "push"), 0),
	    (0, ("wait", "wait"), 0),
	    (0, ("wait", "push"), 1),
	    (0, ("push", "wait"), 2),
	    (1, ("push", "push"), 1),
	    (1, ("wait", "wait"), 1),
	    (1, ("wait", "push"), 2),
	    (1, ("push", "wait"), 0),
	    (2, ("push", "push"), 2),
	    (2, ("wait", "wait"), 2),
	    (2, ("wait", "push"), 0),
	    (2, ("push", "wait"), 1),
	]
	observations = [
	    [[0, 1], [2]],
	    [[0, 2], [1]],
	]
	return multiplayer_game.MultiplayerGame.create(states, initial, alphabet,
	                                               transitions, observations)


def wagon_projected_0() -> multiplayer_game.MultiplayerGame:
	states = [0, 1, 2]
	initial = 0
	alphabet = (("wait", "push"),)
	transitions = [
	    (0, ("wait",), 0),
	    (0, ("wait",), 1),
	    (0, ("push",), 0),
	    (0, ("push",), 2),
	    (1, ("wait",), 1),
	    (1, ("wait",), 2),
	    (1, ("push",), 1),
	    (1, ("push",), 0),
	    (2, ("wait",), 2),
	    (2, ("wait",), 0),
	    (2, ("push",), 2),
	    (2, ("push",), 1),
	]
	observations = [
	    [[0, 1], [2]],
	]
	return multiplayer_game.MultiplayerGame.create(states, initial, alphabet,
	                                               transitions, observations)


def wagon_projected_0_transformed() -> multiplayer_game.MultiplayerGame:
	states = _frozen([
	    {0},
	    {1},
	    {2},
	    {0, 1},
	])
	initial = states[0]
	alphabet = (("wait", "push"),)
	transitions = [
	    (states[0], ("wait",), states[3]),
	    (states[0], ("push",), states[0]),
	    (states[0], ("push",), states[2]),
	    (states[1], ("wait",), states[1]),
	    (states[1], ("wait",), states[2]),
	    (states[1], ("push",), states[3]),
	    (states[2], ("wait",), states[2]),
	    (states[2], ("wait",), states[0]),
	    (states[2], ("push",), states[2]),
	    (states[2], ("push",), states[1]),
	    (states[3], ("wait",), states[3]),
	    (states[3], ("wait",), states[2]),
	    (states[3], ("push",), states[3]),
	    (states[3], ("push",), states[2]),
	]
	observations = [
	    [
	        [states[0]],
	        [states[1]],
	        [states[2]],
	        [states[3]],
	    ],
	]
	return multiplayer_game.MultiplayerGame.create(states, initial, alphabet,
	                                               transitions, observations)


def wagon_projected_1_transformed() -> multiplayer_game.MultiplayerGame:
	states = _frozen([
	    {0},
	    {1},
	    {2},
	    {0, 2},
	])
	initial = states[0]
	alphabet = (("wait", "push"),)
	transitions = [
	    (states[0], ("wait",), states[3]),
	    (states[0], ("push",), states[0]),
	    (states[0], ("push",), states[1]),
	    (states[1], ("wait",), states[1]),
	    (states[1], ("wait",), states[0]),
	    (states[1], ("push",), states[1]),
	    (states[1], ("push",), states[2]),
	    (states[2], ("wait",), states[2]),
	    (states[2], ("wait",), states[1]),
	    (states[2], ("push",), states[3]),
	    (states[3], ("wait",), states[3]),
	    (states[3], ("wait",), states[1]),
	    (states[3], ("push",), states[3]),
	    (states[3], ("push",), states[1]),
	]
	observations = [
	    [
	        [states[0]],
	        [states[1]],
	        [states[2]],
	        [states[3]],
	    ],
	]
	return multiplayer_game.MultiplayerGame.create(states, initial, alphabet,
	                                               transitions, observations)


def wagon_kbsc() -> multiplayer_game.MultiplayerGame:
	states = _frozen([
	    (frozenset({0}), frozenset({0})),
	    (frozenset({1}), frozenset({1})),
	    (frozenset({2}), frozenset({2})),
	    (frozenset({0}), frozenset({0, 2})),
	    (frozenset({2}), frozenset({0, 2})),
	    (frozenset({0, 1}), frozenset({0})),
	    (frozenset({0, 1}), frozenset({1})),
	    (frozenset({0, 1}), frozenset({0, 2})),
	])
	initial = states[0]
	alphabet = (("wait", "push"), ("wait", "push"))
	transitions = [
	    (states[0], ("wait", "wait"), states[7]),
	    (states[0], ("wait", "push"), states[6]),
	    (states[0], ("push", "wait"), states[4]),
	    (states[0], ("push", "push"), states[0]),
	    (states[1], ("wait", "wait"), states[1]),
	    (states[1], ("wait", "push"), states[2]),
	    (states[1], ("push", "wait"), states[5]),
	    (states[1], ("push", "push"), states[6]),
	    (states[2], ("wait", "wait"), states[2]),
	    (states[2], ("wait", "push"), states[3]),
	    (states[2], ("push", "wait"), states[1]),
	    (states[2], ("push", "push"), states[4]),
	    (states[3], ("wait", "wait"), states[7]),
	    (states[3], ("wait", "push"), states[6]),
	    (states[3], ("push", "wait"), states[4]),
	    (states[3], ("push", "push"), states[3]),
	    (states[4], ("wait", "wait"), states[4]),
	    (states[4], ("wait", "push"), states[3]),
	    (states[4], ("push", "wait"), states[1]),
	    (states[4], ("push", "push"), states[4]),
	    (states[5], ("wait", "wait"), states[7]),
	    (states[5], ("wait", "push"), states[6]),
	    (states[5], ("push", "wait"), states[4]),
	    (states[5], ("push", "push"), states[5]),
	    (states[6], ("wait", "wait"), states[6]),
	    (states[6], ("wait", "push"), states[2]),
	    (states[6], ("push", "wait"), states[5]),
	    (states[6], ("push", "push"), states[6]),
	    (states[7], ("wait", "wait"), states[7]),
	    (states[7], ("wait", "push"), states[6]),
	    (states[7], ("push", "wait"), states[4]),
	    (states[7], ("push", "push"), states[7]),
	]
	observations = [
	    [
	        [states[0], states[3]],
	        [states[1]],
	        [states[2], states[4]],
	        [states[5], states[6], states[7]],
	    ],
	    [[states[0], states[5]], [states[1], states[6]], [states[2]],
	     [states[3], states[4], states[7]]],
	]
	return multiplayer_game.MultiplayerGame.create(states, initial, alphabet,
	                                               transitions, observations)


def magiian22() -> multiplayer_game.MultiplayerGame:
	states = [0, 1, 2]
	initial = 1
	alphabet = (("a",), ("a",))
	transitions = [
	    (0, ("a", "a"), 1),
	    (0, ("a", "a"), 2),
	    (1, ("a", "a"), 0),
	    (1, ("a", "a"), 2),
	    (2, ("a", "a"), 0),
	    (2, ("a", "a"), 1),
	]
	observations = [
	    [[0, 1], [2]],
	    [[0, 2], [1]],
	]
	return multiplayer_game.MultiplayerGame.create(states, initial, alphabet,
	                                               transitions, observations)


def magiian22_kbsc() -> multiplayer_game.MultiplayerGame:
	states = [
	    (frozenset({1}), frozenset({1})),
	    (frozenset({0}), frozenset({0, 2})),
	    (frozenset({2}), frozenset({0, 2})),
	    (frozenset({0, 1}), frozenset({1})),
	    (frozenset({0, 1}), frozenset({0, 2})),
	]
	initial = states[0]
	alphabet = (("a",), ("a",))
	transitions = [
	    (states[0], ("a", "a"), states[1]),
	    (states[0], ("a", "a"), states[2]),
	    (states[1], ("a", "a"), states[0]),
	    (states[1], ("a", "a"), states[2]),
	    (states[2], ("a", "a"), states[3]),
	    (states[2], ("a", "a"), states[4]),
	    (states[3], ("a", "a"), states[2]),
	    (states[3], ("a", "a"), states[4]),
	    (states[4], ("a", "a"), states[2]),
	    (states[4], ("a", "a"), states[3]),
	]
	observations = [[
	    [states[0]],
	    [states[1]],
	    [states[2]],
	    [states[3], states[4]],
	], [
	    [states[0], states[3]],
	    [states[1], states[2], states[4]],
	]]
	return multiplayer_game.MultiplayerGame.create(states, initial, alphabet,
	                                               transitions, observations)
