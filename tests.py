from bs4 import BeautifulSoup
from main import Animals
import unittest

IMAGE_DIRECTORY = '/temp'


class TestAnimals(unittest.TestCase):

    def setUp(self) -> None:
        self.animal = Animals()

    def test_parse_animal(self):
        tag = BeautifulSoup('<td><a href="/wiki/Albatross" title="Albatross">Albatross</a></td>', 'lxml')('td')[0]
        animal_name = 'Albatross'
        self.assertEqual(self.animal.parse_animal(tag), animal_name)
        self.assertIn(animal_name, self.animal.animal_links)

    def test_parse_collateral_adjectives(self):
        tag = BeautifulSoup(
            '<td>bovine<sup id="cite_ref-37" class="reference"><a href="#cite_note-37">[note 4]</a></sup><br> taurine '
            '(male)<br> vaccine (female)<br> vituline (young)</td>', 'lxml')
        collateral_adjectives = tag('td')[0].find_all(text=True, recursive=False)
        animal_name = 'Cattle'
        self.animal.parse_collateral_adjectives(collateral_adjectives, animal_name)
        self.assertEqual(len(self.animal.collateral_adjectives), 4)
        self.assertIn('bovine', self.animal.collateral_adjectives)
        self.assertTrue(all(val == [animal_name] for val in self.animal.collateral_adjectives.values()))


if __name__ == '__main__':
    unittest.main()
