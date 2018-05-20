import networkx as nx
from networkx.drawing.nx_pydot import to_pydot

class Observation:
    """Represents an observation of several states in a game"""
    _idcounter = 0
    def __init__(self, *states):
        """Create a new observation

        ex. o = Observation(s0, s2, s3)"""
        self.states = tuple(states)
        self.id = Observation._idcounter
        Observation._idcounter += 1
    def __len__(self):
        """Return the number of states in the observation"""
        return len(self.states)
    def __iter__(self):
        """Iterate over the states"""
        for state in self.states:
            yield state
        
    def _subgraph(self, attributes=None):
        """Generates a networkx subgraph of the states"""
        subgraph = nx.Graph()
        subgraph.add_nodes_from(self.states)
        
        if not attributes:
            attributes = { "style": "dashed" }
        subgraph.graph["graph"] = attributes

        return subgraph

    def to_dot(self, attributes=None):
        """Returns the dot representation of the states in the observation"""
        s = to_pydot(self._subgraph(attributes)).to_string()
        s = "subgraph cluster" + str(self.id) + " {" + s[s.index("\n"):]
        return s
