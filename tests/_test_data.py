import unittest

from tests import data


class TestData(unittest.TestCase):

	def test_can_create_wagon_game(self):
		data.wagon()

	def test_can_create_wagon_projected_0_game(self):
		data.wagon_projected_0()

	def test_can_create_wagon_projected_0_transformed_game(self):
		data.wagon_projected_0_transformed()

	def test_can_create_wagon_projected_1_transformed_game(self):
		data.wagon_projected_1_transformed()

	def test_can_create_wagon_kbsc_game(self):
		data.wagon_kbsc()

	def test_can_create_magiian22_game(self):
		data.magiian22()

	def test_can_create_magiian22_kbsc_game(self):
		data.magiian22_kbsc()


if __name__ == "__main__":
	unittest.main()
