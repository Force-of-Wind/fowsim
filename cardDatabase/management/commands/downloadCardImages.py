from joblib import Parallel, delayed
from lxml import html
from urllib.request import urlopen, urlretrieve
from urllib.error import HTTPError

from django.core.management.base import BaseCommand

from fowsim import constants as CONS


class Command(BaseCommand):
    help = 'Downloads all jpg files to img_dir labelled by set ID e.g. TSW-001.jpg, TSW-001*.jpg, etc'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--destination', type=str, default='./cardDatabase/static/cards/',
                            help='define a destination directory other than cardDatabase/static/cards/')

    def handle(self, *args, **kwargs):
        # Based off code provided by Achifaifa
        destination = kwargs['destination']
        results = Parallel(n_jobs=4)(delayed(Command.downloadCardAtIndex)(i, destination) for i in range(0, 6000))

    @classmethod
    def downloadCardAtIndex(cls, index, dir_to_save):
        try:
            request = urlopen("http://fowtcg.com/card/%d" % index)
        except HTTPError:
            # Lots of unused numbers, just update range to > maximum when necessary
            print('Card not found at i=' + str(index))
            return
        else:
            elements = html.fromstring(request.read())
            url = elements.find_class('img-responsive')[0].get('src')
            code = elements.find_class('prop-value')[0].text.replace("/", "-")
            # * is a special character for double sided cards, can't save * in Windows filenames. Use ^ instead
            img_destination = ("%s%s.jpg" % (dir_to_save, code)).replace('*', CONS.DOUBLE_SIDED_CARD_CHARACTER)
            urlretrieve(url, img_destination)
            print('Saved card to: ' + img_destination)
            return
