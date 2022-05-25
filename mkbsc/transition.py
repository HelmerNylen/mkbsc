from typing import Generic, Iterable, TypeVar

from mkbsc.state import State, StateContent

V = TypeVar("V")


class Transition(Generic[StateContent, V]):
	"""Represents a transition between two states"""

	def __init__(self, start: State[StateContent], joint_action: Iterable[V],
	             end: State[StateContent]):
		"""Create a new transition"""
		self.start: State[StateContent] = start
		self.joint_action = tuple(joint_action)
		self.end: State[StateContent] = end

	def __getitem__(self, index: int) -> V:
		"""Get the action of a certain player"""
		return self.joint_action[index]

	def __repr__(self) -> str:
		return str(self)

	def __str__(self) -> str:
		return f"{self.start} --{self.joint_action}-> {self.end}"

	def label(self) -> str:
		"""Return the string representation of the joint action"""
		if len(self.joint_action) > 1:
			return "(" + ", ".join(
			    str(action) for action in self.joint_action) + ")"
		else:
			return str(self.joint_action[0])
