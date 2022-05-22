from typing import Generic, Iterable, Iterator, Tuple, TypeVar

from .helper_functions import _permute

T = TypeVar("T")

class Alphabet(Generic[T]):
    """Represents the possible joint actions of the player coalition"""
    def __init__(self, *actions: Iterable[T]):
        """Generate a joint alphabet

        ex. a = Alphabet(('push', 'wait'), ('break', 'wait'))"""
        
        for playeractions in actions:
            s = set()
            for action in playeractions:
                assert action not in s
                s.add(action)
        
        self.actions = tuple(tuple(a for a in playeractions) for playeractions in actions)

    def __getitem__(self, index: int) -> Tuple[T, ...]:
        """Get the alphabet (a tuple of the possible actions) for the specified player"""
        return self.actions[index]

    def __iter__(self) -> Iterator[Tuple[T, ...]]:
        """Iterate over the individual alphabets"""
        for playeralphabet in self.actions:
            yield playeralphabet

    def __len__(self) -> int:
        """Get the number of individual alphabets"""
        return len(self.actions)

    def __str__(self) -> str:
        return str(self.actions)
        
    def permute(self) -> Iterator[Tuple[T, ...]]:
        """Generate every possible joint action"""
        for joint_action in _permute(self.actions):
            yield joint_action
