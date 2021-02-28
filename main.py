from pathlib import Path
from typing import List
from concurrent.futures import ThreadPoolExecutor
import bs4
import json
import pprint
import requests
import shutil

BASE_URL = 'https://en.wikipedia.org/wiki/List_of_animal_names'
API_BASE_URL = 'https://en.wikipedia.org/api/rest_v1/page/summary/'


class Animals:
    def __init__(self):
        self.collateral_adjectives = {}
        self.animal_links = {}

    def get_page_rows(self, url: str) -> List[bs4.element.ResultSet]:
        """
        A function that gets the animals list page and returns each row that contains an animal
        :param url: gets the url of the desired Wikipedia page
        :return: a list of BeautifulSoup ResultSet objects, each is representing an animal row from the table
        """
        animal_page = requests.get(url)
        parsed_page = bs4.BeautifulSoup(animal_page.text, 'xml')
        all_rows = parsed_page('table')[-1].find_all('tr')
        return [row('td') for row in all_rows if row('td') and len(row('td')) == 7]

    def parse_row(self, row_cells: bs4.element.ResultSet):
        """
        Parse each row of the table
        :param row_cells: the individual cells (td) of each row in the table
        :return:
        """
        name = self.parse_animal(row_cells[0])
        get_collateral_adjectives = row_cells[5].find_all(text=True, recursive=False)
        self.parse_collateral_adjectives(get_collateral_adjectives, name)

    def parse_animal(self, animal_name_cell: bs4.element.Tag) -> str:
        """
        Parse the animal's name cell and extract the animal's name and the link to it's webpage and put it in the
        'animal_links' dictionary
        :param animal_name_cell: the cell in the row that contains the animal's name
        :return:
        """
        animal_tag = animal_name_cell.a['title']
        animal_name = animal_tag[:animal_tag.index('(') - 1] if '(' in animal_tag else animal_tag
        animal_page_link = f'{API_BASE_URL}{animal_tag}'
        animal_data_object = json.loads(requests.get(animal_page_link).text)

        # some animals in the list don't contain images
        if 'thumbnail' in animal_data_object:
            self.animal_links[animal_name] = animal_data_object['thumbnail']['source']
        return animal_name

    def parse_collateral_adjectives(self, collateral_adjectives: bs4.element.ResultSet, animal_name: str):
        """
        Clean the list of Collateral Adjectives
        :param collateral_adjectives: a list of the collateral adjectives for a specific animal
        :param animal_name: The name of the animal
        :return:
        """
        for collateral_adjective in collateral_adjectives:
            collateral_adjective = collateral_adjective.strip()
            if '(' in collateral_adjective:
                collateral_adjective = collateral_adjective[:collateral_adjective.index('(') - 1]
            if collateral_adjective not in self.collateral_adjectives:
                self.collateral_adjectives[collateral_adjective] = []
            self.collateral_adjectives[collateral_adjective].append(animal_name)

    def download_image(self, animal_name: str):
        """
        Download the image of the animal from its webpage
        :param animal_name: A string with the animal's name
        :return:
        """
        url = self.animal_links[animal_name]
        img_data = requests.get(url).content
        with open(f'temp/{animal_name}.jpg', 'wb') as handler:
            handler.write(img_data)
        return f'{animal_name} was downloaded'


if __name__ == '__main__':
    animals = Animals()
    rows = animals.get_page_rows(BASE_URL)

    with ThreadPoolExecutor() as executor:
        executor.map(animals.parse_row, rows)

    # just in case this folder already exists in this project, obviously would need a lot more safeguards in case of
    # an actual project
    if Path(f'{Path(__file__).parent.absolute()}/temp').exists():
        shutil.rmtree(f'{Path(__file__).parent.absolute()}/temp')
    Path(f'{Path(__file__).parent.absolute()}/temp').mkdir()

    with ThreadPoolExecutor() as executor:
        img_results = executor.map(animals.download_image, animals.animal_links.keys())

    pprint.pprint(animals.collateral_adjectives)
