class Partitioning:
    """Represents a partitioning of observations"""
    def __init__(self, *observations):
        """Create a new partitioning

        ex. p = Partitioning(o1, o2, o3)"""
        self.observations = tuple(observations)
    def __iter__(self):
        """Iterate over the observations"""
        for observation in self.observations:
            yield observation
        
    def valid(self, states):
        """Test if the partitioning contains all states"""
        s = set()
        for observation in self.observations:
            for state in observation:
                if state in s:
                    return False
                else:
                    s.add(state)
        
        return frozenset(s) == frozenset(states)
