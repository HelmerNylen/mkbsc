import unittest

from mkbsc import multiplayer_game
from tests import data


class TestMultiplayerGame(unittest.TestCase):

	def assertGameEquivalent(
	    self,
	    first: multiplayer_game.MultiplayerGame,
	    second: multiplayer_game.MultiplayerGame,
	    msg: str = "The games are not equivalent",
	) -> None:
		self.assertTrue(first.isomorphic(second, consider_observations=True),
		                "The games are not isomorphic: " + msg)
		self.assertEqual(
		    first.alphabet.actions,
		    second.alphabet.actions,
		    "The games have different action alphabets: " + msg,
		)
		# TODO: check state content

	def test_projection_correct_result_on_wagon_game(self):
		game = data.wagon()
		expected = data.wagon_projected_0()

		self.assertGameEquivalent(game.project(0), expected)

	def test_singleplayer_kbsc_correct_result_on_wagon_game(self):
		game = data.wagon_projected_0()
		expected = data.wagon_projected_0_transformed()

		self.assertGameEquivalent(game.KBSC(), expected)

	# def test_synchronous_product_correct_result_on_wagon_game(self):
	# 	base = data.wagon()
	# 	first = data.wagon_projected_0_transformed()
	# 	second = data.wagon_projected_1_transformed()
	# 	expected = data.wagon_kbsc()

	# 	actual = base._synchronous_product([first, second])

	# 	self.assertGameEquivalent(actual, expected)

	def test_multiplayer_kbsc_correct_result_on_wagon_game(self):
		game = data.wagon()
		expected = data.wagon_kbsc()

		self.assertGameEquivalent(game.KBSC(), expected)

	def test_multiplayer_kbsc_prunes_invalid_transitions(self):
		game = data.magiian22()
		expected = data.magiian22_kbsc()

		self.assertGameEquivalent(game.KBSC(), expected)


if __name__ == "__main__":
	unittest.main()
