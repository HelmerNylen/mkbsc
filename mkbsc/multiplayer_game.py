from .alphabet          import Alphabet
from .state             import State
from .observation       import Observation
from .partitioning      import Partitioning
from .transition        import Transition
from .helper_functions  import _permute, _lookup, _lookup_by_base, _reachable, consistent, powerset

#import threading
#import time
from itertools          import chain, combinations, permutations
from collections        import deque

import networkx as nx
from networkx.algorithms.isomorphism    import is_isomorphic
from networkx.drawing.nx_pydot          import to_pydot


class MultiplayerGame:
    """Represents a game of one or more players

    The easiest way to create a new game is to call MultiplayerGame.create() with the
    appropriate parameters. Among other things, the game has methods to apply the (M)KBSC,
    to project the game onto a certain player, to check for isomorphism and to export the
    game as a dot string."""
    
    def __init__(self, states, initial_state, alphabet, transitions, partitionings, remove_unreachable=False, validate=False, **attributes):
        """Create a new game and optionally validate and remove unreachable states."""
        
        self.states = states
        self.initial_state = initial_state
        self.alphabet = alphabet
        self.transitions = transitions
        self.partitionings = partitionings
        
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
                    
            self.graph.add_edge(transition.start, transition.end,
                label=transition.label(), key=transition.joint_action, action=transition.joint_action)
                
        if remove_unreachable:
            to_remove = (set(self.states) - _reachable(self.graph, self.initial_state)) - {self.initial_state}
            #print("Removing " + str(to_remove))
            self.graph.remove_nodes_from(to_remove)
            
    def create(content, initial, alphabet, transition_edges, state_groupings, **attributes):
        """Create a new game and validate it

        content -- the knowledge of the states, ex. [1, 2, 3] or range(5)
        initial -- the knowledge in the initial state, ex. 1
        alphabet -- the alphabet of actions, ex. (['a', 'b'], ['1', '2']) or ('ab', '12')
        transition_edges -- the edges in the game graph, ex. [(1, ('a', '1'), 2), (2, 'b1', 3)]
        state_groupings -- the observation partitionings, ex. ([[1, 2], [3]], [[1], [2, 3]])"""
        
        states = tuple(set(map(lambda x: State(x), content)))
        initial_state = _lookup(states, initial)
        
        if type(alphabet) is not Alphabet:
            alphabet = Alphabet(*alphabet)
        
        transitions = []
        expanded_edges = []
        for edge_iterable in [transition_edges, expanded_edges]:
            for edge in edge_iterable:
                if type(edge[2]) is set:
                    for edge_end in edge[2]:
                        expanded_edges.append((edge[0], edge[1], edge_end))
                    continue
                        
                start = _lookup(states, edge[0])
                end = _lookup(states, edge[2])
                if edge[1] == Ellipsis:
                    for joint_action in alphabet.permute():
                        transitions.append(Transition(start, joint_action, end))
                else:
                    transitions.append(Transition(start, edge[1], end))
            
        transitions = tuple(transitions)


        partitionings = []
        for grouping in state_groupings:
            observations = []
            ellipsis = False
            for group in grouping:
                if group == Ellipsis:
                    ellipsis = True
                    continue
                observations.append(Observation(*[_lookup(states, s) for s in group]))
            if ellipsis:
                covered_states = set()
                for observation in observations:
                    covered_states.update(observation)

                for state in states:
                    if state not in covered_states:
                        observations.append(Observation(state))
            
            partitionings.append(Partitioning(*observations))
        
        partitionings = tuple(partitionings)
        
        
        return MultiplayerGame(states, initial_state, alphabet, transitions, partitionings, False, True, **attributes)
    
    def _create_from_serialized(states, initial_state, alphabet, transitions, state_groupings, validate=True, **attributes):
        """Create a new game from serialized data and validate it"""
        
        states = tuple(states)
        
        if type(alphabet) is not Alphabet:
            alphabet = Alphabet(*alphabet)
        
        transitions = tuple(map(lambda edge: Transition(*edge), transitions))
        
        partitionings = tuple(map(lambda grouping: Partitioning(*[Observation(*group) for group in grouping]), state_groupings))
        
        
        return MultiplayerGame(states, initial_state, alphabet, transitions, partitionings, False, validate, **attributes)
        
    def state(self, knowledge):
        """Get the state object with the specified knowledge"""
        return _lookup(self.states, knowledge, len(self.states[0].knowledges) == 1)
    
    def states_by_consistent_base(self, base):
        """Get the state objects which represent the specified base states"""
        return _lookup_by_base(self.states, base)
    
    def post(self, action, states):
        """Get the states that are possible after taking a certain action in one of the specified states"""
        
        res = set()
        if self.player_count == 1:
            action = (action,)
        if not hasattr(states, '__iter__'):
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

    def reachable(self, initial=None):
        """Get the reachable states in a game, optionally given a certain initial state"""
        
        res = set()
        if not initial:
            initial = self.initial_state
            res.add(self.initial_state)
        return res.union(_reachable(self.graph, initial))
        
    def to_dot(self, group_observations=None, group_by_base=False, group_edges=True, epistemic=False, \
               supress_edges=False, color_scheme="set19", colorfunc=lambda x:x+1, observations_constrain=True, \
               target_states=None, **kwargs):
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
                    edges = [edge for edge in G.edges(node, data=True) if edge[1] == neighbor]
                    if len(edges) == 1:
                        continue

                    label = ", ".join(map(lambda edge: edge[2]["label"], edges))
                    superaction = tuple(edge[2]["action"] for edge in edges)
                    
                    if len(set(superaction)) == len(all_joint_actions):
                        label = "(-)"

                    total_attributes = {}
                    
                    for edge in edges:
                        if edge[2]["action"]:
                            current_attributes = G[edge[0]][edge[1]][edge[2]["action"]]
                            for key in current_attributes:
                                if key not in ["label", "action", "key"]:
                                    total_attributes[key] = current_attributes[key]
                            
                            G.remove_edge(edge[0], edge[1], edge[2]["action"])
                            
                    G.add_edge(node, neighbor, label=label, key=superaction, action=superaction, **total_attributes)

        for edge in G.edges(data="action"):
            if edge[0] == edge[1]:
                G[edge[0]][edge[1]][edge[2]]["dir"] = "back"
        
        if supress_edges:
            for edge in G.edges(data="action"):
                G[edge[0]][edge[1]][edge[2]]["label"] = ""
                
        
        epistemic_functions = {"verbose": State.epistemic_verbose, "nice": State.epistemic_nice, "isocheck": State.epistemic_isocheck}
        if epistemic:
            func = epistemic_functions[epistemic.lower()]
            for state in G.nodes():
                G.nodes[state]["label"] = func(state)
            
        G.add_node("hidden", shape="none", label="")
        G.add_edge("hidden", self.initial_state)

        if target_states:
            for i in range(len(target_states)):
                if type(target_states[i]) is not State:
                    target_states[i:i+1] = _lookup_by_base(self.states, target_states[i])
            for target_state in target_states:
                G.nodes[target_state]["shape"] = "doublecircle"
        
        #if group_observations is None:
        #    group_observations = (self.player_count == 1)
        
        if group_observations:
            State.compact_representation = True
            arr = to_pydot(G).to_string().split("\n")
            for player, partitioning in enumerate(self.partitionings):
                arr[-2:-2] = [observation.to_dot({"style": "dashed", "label": "~" + str(player) if self.player_count > 1 else ""}) for observation in partitioning]
            
            State.compact_representation = False
            return "\n".join(arr)
        else:
            for player, partitioning in enumerate(self.partitionings):
                for observation in partitioning:
                    if len(observation) > 1: 
                        for start, end in combinations(observation, 2):
                            G.add_edge(start, end, style="dashed", label="~" + str(player) if self.player_count > 1 else "",
                                arrowhead="none", colorscheme=color_scheme, color=colorfunc(player), constraint=observations_constrain)
            
            State.compact_representation = True        
            arr = to_pydot(G).to_string().split("\n")
            if group_by_base:
                groups = {}
                for state in self.states:
                    fs = frozenset(state.consistent_base())
                    if fs not in groups:
                        groups[fs] = set()
                    groups[fs].add(state)
                
                #print(groups.keys())
                
                for i, group in enumerate(groups):
                    subgraph = nx.Graph()
                    subgraph.graph["graph"] = { "style": "invis" }
                    subgraph.add_nodes_from(groups[group])
                    s = to_pydot(subgraph).to_string()
                    s = "subgraph cluster" + str(i) + " {" + s[s.index("\n"):]
                    arr[-2:-2] = [s]
                
            State.compact_representation = False
            return "\n".join(arr)
    
    def project(self, player):
        """Project the game onto a player"""
        
        assert player < self.player_count
        
        states = self.states
        initial_state = self.initial_state
        alphabet = Alphabet(self.alphabet[player])
        
        transitions = [Transition(t.start, (t.joint_action[player],), t.end) for t in self.transitions]
        partitionings = (self.partitionings[player],)
        
        attributes = self.graph.graph["graph"]
        
        return MultiplayerGame(states, initial_state, alphabet, transitions, partitionings, **attributes)
        
    
    def _synchronous_product(self, games):
        """Combine singleplayer knowledge-based games into a single knowledge-based multiplayer game"""
        
        initial_states = tuple(game.initial_state for game in games)
        initial_knowledges = tuple(state.knowledges[0] for state in initial_states)
        transitions = []
        
        states = {initial_knowledges: State(*initial_knowledges)}
        
        tested = set()
        queue = deque([(initial_states, consistent(initial_states))])
        
        """
        debugThread = None
        done = False
        counter = 0
        if debug:
            def checker():
                i = 0
                while not done:
                    i += 1
                    if i == 10:
                        print(str(counter) + " / " + str(len(queue)) + " / " + str(len(states)))
                        i = 0
                    time.sleep(0.5)
                    
            
            debugThread = threading.Thread(target=checker, daemon=True)
            debugThread.start()
        """
            
        while len(queue):
            #counter += 1
            #print("Loop!")
            state_tuple, possible = queue.pop()
            #print(state_tuple)
            
            if state_tuple in tested:
                #print("Tested, skipping")
                continue
            else:
                tested.add(state_tuple)
            
            #print("Possible: " + str(possible))
            for joint_action in self.alphabet.permute():
                #print("Action: " + str(joint_action))
                
                possible_post = self.post(joint_action, possible)
                #print("Possible (post): " + str(possible_post))
                
                players_post = [games[i].post(joint_action[i], state_tuple[i]) for i in range(self.player_count)]
                #print("Players' post (unfiltered): " + str(players_post))
                
                for i in range(self.player_count):
                    players_post[i] = set(filter(lambda state: not state.knowledges[0].isdisjoint(possible_post), players_post[i]))
                #print("Players' post (filtered):   " + str(players_post))
                
                for possible_knowledge in _permute(players_post):
                    #print("Possible knowledge: " + str(possible_knowledge))
                    knowledge_tuple = tuple(state.knowledges[0] for state in possible_knowledge)
                    if knowledge_tuple not in states:
                        #print("It's new")
                        cons = consistent(possible_knowledge)
                        #print("Consistent: " + str(cons))
                        
                        if len(cons):
                            #print("Adding to res and queue")
                            states[knowledge_tuple] = State(*knowledge_tuple)
                            queue.appendleft((possible_knowledge, cons))
                        else:
                            continue
                    
                    #print("Adding transition")
                    k = tuple(state.knowledges[0] for state in state_tuple)
                    fromstate = states[k]
                    tostate = states[knowledge_tuple]
                    
                    transitions.append(Transition(fromstate, joint_action, tostate))
        
        #done = True
        
        initial_state = states[initial_knowledges]
        states = list(states.values())
        attributes = self.graph.graph["graph"]
        
        observation_dicts = [{} for player in range(self.player_count)]
        for state in states:
            for i in range(self.player_count):
                if state[i] in observation_dicts[i]:
                    observation_dicts[i][state[i]].add(state)
                else:
                    observation_dicts[i][state[i]] = {state}
            
        partitionings = tuple(Partitioning(*[Observation(*observation_dicts[i][knowledge]) for knowledge in observation_dicts[i]]) for i in range(self.player_count))
        
        #print("Sync game creation")
        return MultiplayerGame(states, initial_state, self.alphabet, transitions, partitionings, **attributes)
        
        
        
    def KBSC(self):
        """Apply the KBSC to the game (or MKBSC in the multiplayer case)"""
        
        if self.player_count > 1:
            games = [self.project(player).KBSC() for player in range(self.player_count)]
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
                        knowledge = post_states.intersection(obs.states)
                        if knowledge:
                            knowledge = frozenset(knowledge)
                            tostate = states.get(knowledge)
                            if not tostate:
                                tostate = State(knowledge)
                                states[knowledge] = tostate
                                queue.appendleft(tostate)
                            
                            
                            transitions.append(Transition(fromstate, (action,), tostate))
            
            states = list(states.values())
            
            partitionings = (Partitioning(*[Observation(state) for state in states]),)
            attributes = self.graph.graph["graph"]
            
            #print("KBSC game creation")
            return MultiplayerGame(states, initial_state, self.alphabet, transitions, partitionings, remove_unreachable=True, **attributes)
    
    def isomorphic(self, other, consider_observations=False):
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
            s += "Spelare " + str(player) + ": " + ", ".join([str(tuple(sorted([s.epistemic_isocheck() for s in o]))) for o in sorted(partitioning.observations, key=lambda o: len(o)) if len(o) > 1])
            s += "\n"
        return s
