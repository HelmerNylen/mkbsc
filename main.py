#!/usr/bin/env python3

from mkbsc import MultiplayerGame, iterate_until_isomorphic, \
                  export, to_string, from_string, to_file, from_file

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

#G is a MultiplayerGame-object, and so are GK and GK0
G = MultiplayerGame.create(L, L0, Sigma, Delta, Obs)
GK = G.KBSC()
GK0 = GK.project(0)

#export the GK game to ./pictures/GK.png
export(GK, "GK")
