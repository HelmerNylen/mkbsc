from .helper_functions import _permute

class Alphabet:
    """Represents the possible joint actions of the player coalition"""
    def __init__(self, *actions):
        """Generate a joint alphabet

        ex. a = Alphabet(('push', 'wait'), ('break', 'wait'))"""
        
        for playeractions in actions:
            s = set()
            for action in playeractions:
                assert action not in s
                s.add(action)
        
        self.actions = tuple(tuple(a for a in playeractions) for playeractions in actions)
    def __getitem__(self, index):
        """Get the alphabet (a tuple of the possible actions) for the specified player"""
        return self.actions[index]
    def __iter__(self):
        """Iterate over the individual alphabets"""
        for playeralphabet in self.actions:
            yield playeralphabet
    def __len__(self):
        """Get the number of individual alphabets"""
        return len(self.actions)
    def __str__(self):
        return str(self.actions)
        
    def permute(self):
        """Generate every possible joint action"""
        for joint_action in _permute(self.actions):
            yield joint_action
