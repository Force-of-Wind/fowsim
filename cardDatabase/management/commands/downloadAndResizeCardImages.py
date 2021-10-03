from string import digits
import tempfile
import urllib.parse
import requests
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from django.core import files

from fowsim import constants as CONS
from cardDatabase.models.CardType import Card

class Command(BaseCommand):
    help = 'Downloads all jpg files and resizes them to 480x670 px in img_dir labelled by set ID e.g. TSW-001.jpg, TSW-001*.jpg, etc. Must run importjson beforehand.'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--destination', type=str, default='./cardDatabase/static/cards/',
                            help='define a destination directory other than cardDatabase/static/cards/')

    def handle(self, *args, **kwargs):
        # Based off code provided by Kossetsu
        destination = kwargs['destination']
        top_url = 'http://www.fowtcg.com'
        failures = []
        for card in Card.objects.filter(pk__gte=12094):
            if card.set_code not in CONS.FOWTCG_CARD_DATABASE_SET_INDEX:
                # Ignore sets that aren't on fowtcg.com, mostly just valhalla and some promos
                continue
            url = 'http://www.fowtcg.com/cards?s[]=%s&w=' % CONS.FOWTCG_CARD_DATABASE_SET_INDEX[card.set_code]
            search_url = url + urllib.parse.quote(card.name).replace('%20', '+')
            print('Requesting ' + search_url)
            response = requests.get(search_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            search_result = soup.find('div', {'class': 'search-result-detail'})

            if search_result:
                link_suffix = search_result.find('a')['href']
            else:
                failures.append(card.name)
                continue

            card_page_url = top_url + link_suffix
            print('Searching for card at: ' + card_page_url)

            card_response = requests.get(card_page_url)
            card_soup = BeautifulSoup(card_response.text, 'html.parser')
            img_url = card_soup.find('img', {'class': 'img-responsive'})['src']
            print('Downloading img from: ' + img_url)

            image_request = requests.get(img_url, stream=True)

            temp = tempfile.NamedTemporaryFile()

            for block in image_request.iter_content(1024 * 8):
                if not block:
                    break
                temp.write(block)

            size = 480, 670
            im = Image.open(temp)
            if im.mode == "RGBA":
                new_image = Image.new("RGBA", im.size, "WHITE")
                new_image.paste(im, (0, 0), im)
                im = new_image
                im = im.convert("RGB")

            im = im.resize(size, Image.ANTIALIAS)
            im_io = BytesIO()
            im.save(im_io, 'JPEG', quality=70)

            with open(destination + card.card_image_filename, 'wb') as output:
                output.write(im_io.getbuffer())
            print('Saved image to: ' + destination + card.card_image_filename)

        print("Failures loading the following images:")
        print(failures)