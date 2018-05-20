# Documentation

The project has been commented with Python docstrings, so detailed information about the classes and methods can be found by running `pydoc3 -b` from the project's root folder and opening the `mkbsc` module in the browser. While each method has an explanation of its use and parameters, the code itself is less commented as well as a bit messy in some places (one of the authors was a bit too fond of list comprehensions).

Below is a quick rundown of some of the important classes and functions in the package. To use them, simply import them into your script with e.g. `from mkbsc import MultiplayerGame, export, iterate_until_isomorphic`.

#### `MultiplayerGame`
The most important class in the package. It can represent both single- and multi-player games. Instances of this class should be considered to be immutable.

##### `.create(content, initial, alphabet, transition_edges, state_groupings, **attributes)`
**Returns:** An instance of `MultiplayerGame`

Creates and validates a new multi-player game. The `attributes` are optional and are passed to Graphviz when exporting the game. How to format the arguments is described in detail in the tutorial below.

##### `.project(player)`
**Returns:** An instance of `MultiplayerGame`

Projects the game onto the specified (zero-indexed) player, the result being a single-player game.

##### `.KBSC()`
**Returns:** An instance of `MultiplayerGame`

Applies the appropriate Knowledge-Based Subset Construct to the game and returns the constructed game.

##### `.isomorphic(other, consider_observations = False)`
**Returns:** `True` or `False`

Checks if the graph of the game is isomorphic to that of `other`. By default, it only looks at the transitions and initial states of the games. If `consider_observations` is `True`, it will also require the observations to partition the games in the same way for them to be isomorphic.

##### `.post(action, states)`
**Returns:** A `set` of `State` objects

Implementation of the Post-operator. `action` is a (joint) action in the game's alphabet, and `states` is an iterable of `State` objects (just the knowledge in the states, e.g. `[0, 2]`, will *not* work).

##### `.state(knowledge)`
**Returns:** An instance of `State`

Find the state in the game with the specified knowledge.
    
##### `.states_by_consistent_base(base)`
**Returns:** A `set` of `State` objects

Get all `State` objects which are consistent with the specified base.

#### `export(game, filename, view = True, folder = "pictures", epistemic = "nice", supress_edges = False, group_observations = None, target_states = None, **kwargs)`
Exports `game` as a PNG image in "`filename`.png". If `view` is `True`, it also opens the picture afterwards. `folder` specifies which directory to save the image in. `epistemic` determines how the information in the states are rendered. The default is `"nice"`, which tries to balance readability and compactness, and another option is `"isocheck"`, which only renders the consistent base of the states. If `supress_edges` is `True`, the transitions in the graph will have no action labels. `group_observations = True` attempts to render dashed boxes around the states in an observation rather than dashed, complete graphs between them, but is a bit buggy and only works with single-player games. Finally, `target_states` is an iterable of the consistent bases which should be marked in the rendered image. For example, `[[3], [0, 1]]` marks the states whose consistent base is either `{3}` or `{0, 1}`. Can be used to mark states for reachability or safety objectives, for instance. Any keyword parameters not mentioned here are passed on to the `MultiplayerGame.to_dot()` function.

#### `iterate_until_isomorphic(G, limit = -1, print_size = False, verbose = True)`
**Returns:** A tuple `(log, G_final, iso_type)`, where `log` is an iterable, `G_final` is a `MultiplayerGame`, and `iso_type` is 0, 1 or 2.

Iterates the MKBSC on `G` until an iteration is isomorphic to the previous one with regards to observations, or `limit` iterations has been completed. `-1` disables the limit. If `print_size` is `True`, it will print the sizes of the games as the iteration runs. If `verbose` is `True`, extra information is added to the printed message and log. The retuned log will contain the same information which is printed with `print_size` set to `True`. `G_final` will be the last game in the iteration, *unless* the last game is isomorphic to the second to last game with regards to observations. In that case, `G_final` will be the second to last game. `iso_type` will be 0 if the game did not stabilize, 1 if the last game was isomorphic to the second to last but not w.r.t. observations, and 2 if the last game was isomorphic to the second to last w.r.t. observations.

#### `Alphabet`
Alphabet of actions for multi-player games. Can be iterated over or accessed by index to retrieve the players' individual action alphabets as tuples.

##### `.permute()`
**Returns:** An iterator.

Yields every possible joint action. Usually used in loops, e.g. `for joint_action in G.alphabet.permute()`.

#### `State`
The objects which contain the knowledge of all the players, and make up the vertices in the game graph. The knowledge of a player can be accessed by index, e.g. `s[1]` for player 1's knowledge in state `s`.

##### `.consistent_base()`
**Returns:** A `set` of `State` objects.

Returns the states in the base game that are consistent with the knowledge in this state.

# Tutorial
*The tutorial assumes that the reader is familiar with multi-player games of imperfect information*

When creating a game, `main.py` will usually look something like the following:

```python
from mkbsc import MultiplayerGame, export, iterate_until_isomorphic

#states
L = [0, 1, 2]
#initial state
L0 = 0
#action alphabet
Sigma = (("w", "p"), ("w", "p"))
#action labeled transitions
Delta = [
    (0, ("p", "p"), 0), (0, ("w", "w"), 0),
    (0, ("w", "p"), 1), (0, ("p", "w"), 2),
    (1, ("p", "p"), 1), (1, ("w", "w"), 1),
    (1, ("w", "p"), 2), (1, ("p", "w"), 0),
    (2, ("p", "p"), 2), (2, ("w", "w"), 2),
    (2, ("w", "p"), 0), (2, ("p", "w"), 1)
]
#observation partitioning
Obs = [
    [[0, 1], [2]],
    [[0, 2], [1]]
]

#G is a MultiplayerGame-object
G = MultiplayerGame.create(L, L0, Sigma, Delta, Obs)

#operations on G below...
```

There are five components to a game:
- The states are represented by `L`, which is an iterable of unique numbers or strings. `['initial', 'good', 'bad', 'win', 'lose']` is valid, just like `[0, 1, 2]` or `range(3)` (which are equivalent).
- The initial state is represented by `L0`, an element in `L`.
- The action alphabet is represented by `Sigma`. `Sigma` is an iterable where the elements are the individual action alphabets of each player. These individual action alphabets should be iterables of strings. For example, if player 0 can wait or push the individual alphabet is `('wait', 'push')`. If player 1 can jump or push their action alphabet is `('jump', 'push')`, and the total becomes `Sigma = [('wait', 'push'), ('jump', 'push')]`. If the actions are single letters (e.g. `'w'` and `'p'` for the former and `'j'` and `'p'` for the latter), the individual alphabet can be a single string (`'wp'` or `'jp'`), and the total `Sigma` can be written as `['wp', 'jp']`.
- The transitions are represented by `Delta`. `Delta` is an iterable where the elements define the specific transitions. The elements are 3-tuples (or equivalent iterables) such as `(0, ('wait', 'push'), 1)`, which would represent a transition from state `0` to state `1` with the joint action `('wait', 'push')`. Just like in the alphabets, if the actions are single letters (here `'w'` and `'p'`), the transition could be written as `(0, 'wp', 1)`. The Ellipsis object in Python, written as `...`, can be used to indicate that every joint action should lead between the specified states. In the example above, `(0, ..., 1)` would expand to `(0, 'ww', 1)`, `(0, 'wp', 1)`, `(0, 'pw', 1)`, and `(0, 'pp', 1)`. Furthermore, there is a quick way to specify that an action should lead to multiple states. Writing a set of receiving states, such as in `(0, 'wp', {1, 2})`, expands to `(0, 'wp', 1)` and `(0, 'wp', 2)`. These features can be combined - for example, `(0, ..., {0, 1})` means that every joint action can lead to either `0` or `1`.
- The observation partitionings is represented by `Obs`, which is an iterable of the partitioning of each player. An observation is defined as an iterable of states, e.g. `[1, 2]` for an equivalence between 1 and 2. Singleton observations are allowed as well, e.g. `[0]`. These are combined in an iterable for each player, for instance `[[1, 2], [0]]`, in which every state must occur exactly once. In a partitioning, the Ellipsis `...` can be used to signal that all states which do not occur should form singleton observations. That is, `[[0, 1], ...]` could replace player 0's partitioning in the example file above.


```python
#continuation of the above file example

#we export the game to see what it looks like
#the resulting image is saved to "pictures/G.png" and should open automatically
export(G, "G")

#we can apply the MKBSC to G by simply calling G.KBSC()
GK = G.KBSC()

#we can apply the MKBSC again to the constructed game in the same way,
#or construct G2K directly by G.KBSC().KBSC()
G2K = GK.KBSC()

#we can project any multi-player game onto a player as follows
G2K0 = G2K.project(0)

#we export this game as well, but do not open it automatically
#we also mark all states which correspond to state 0 in G
export(G2K0, "G2K0", view = False, target_states = [[0]])

#we iterate the MKBSC until the game stabilizes, but at most ten times
#during the iteration we print the sizes to the console
log, G_final, iso = iterate_until_isomorphic(G, 10, True)

#we export the resulting game but only render the consistent base of the states,
#as the image otherwise would be very large
export(G_final, "very_iterated_G", view = False, epistemic = "isocheck")

```
