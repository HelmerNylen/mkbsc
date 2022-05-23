import unittest

from mkbsc import alphabet


class TestAlphabet(unittest.TestCase):

	def setUp(self):
		super().setUp()
		self.alphabet = alphabet.Alphabet([1, 2, 3], ["jump", "run"])

	def test_actions(self):
		expected = ((1, 2, 3), ("jump", "run"))
		self.assertEqual(self.alphabet.actions, expected)

	def test_getitem(self):
		self.assertEqual(self.alphabet[0], (1, 2, 3))
		self.assertEqual(self.alphabet[1], ("jump", "run"))

	def test_len(self):
		self.assertEqual(len(self.alphabet), 2)

	def test_iter(self):
		expected = ((1, 2, 3), ("jump", "run"))
		self.assertSequenceEqual(self.alphabet, expected)

	def test_permute(self):
		expected = ((1, "jump"), (1, "run"), (2, "jump"), (2, "run"),
		            (3, "jump"), (3, "run"))
		self.assertCountEqual(self.alphabet.permute(), expected)

	def test_alphabet_error_on_duplicate_actions(self):
		with self.assertRaises(AssertionError):
			alphabet.Alphabet([1, 2], ["a", "a"])


if __name__ == "__main__":
	unittest.main()
