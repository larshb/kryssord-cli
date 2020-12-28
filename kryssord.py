# -*- coding: utf-8 -*-
import re
from requests import get
try:
    from urllib.parse import quote
except:
    from urlparse import urlparse as quote

# Local utilities
from formatting import color, bold, underline, colorize, clear

SEARCH_URI = "http://www.kryssord.org/search.php?a={query}&b={pattern}"
RESULT_REGEX = r'<td class="word"><a href=".*?">(.*?)<\/a>'
NRESULT_REGEX = r'Fant <strong>(\d+)<\/strong>'


class Search:

    def __init__(self, query, pattern='', load=True, parse=True, cache=False):
        self.query_raw = query
        self.query = quote(query)
        self.pattern_raw = pattern
        self.pattern = quote(pattern)
        self.uri = SEARCH_URI.format(query=self.query, pattern=self.pattern)
        if load: self.load()
        if parse: self.parse()
        if cache: self.cache()

    def load(self):
        self.response = get(self.uri)
        self.html = self.response.content.decode()
    
    def cache(self):
        open('.html', 'w').write(self.html)

    def parse(self):
        self.nResults = int(re.findall(NRESULT_REGEX, self.html)[0])
        self.results = re.findall(RESULT_REGEX, self.html)


def main(args):

    print(colorize('Laster...', color.YELLOW))

    query_raw, pattern_raw = 'nøtt', 'k*'
    s = Search(query_raw, pattern_raw, cache=True)

    # Formatting (short hand)
    nm = color.END
    ul = color.UNDERLINE
    bu = color.UNDERLINE + color.BOLD

    try:
        while True:

            clear()

            header = color.BOLD + color.YELLOW + \
                "~ Kryssordterminalen (kryssord.org) ~" + color.END
            print(header)
            print('')
            
            n_results_string = nm + "Fant " + bu + str(s.nResults) + nm + " synonym til " + bu + query_raw + nm
            if pattern_raw:
                n_results_string += " med mønster " + bu + pattern_raw + nm
            n_results_string += nm + ' \n'
            print(n_results_string)

            for word_raw in s.results:
                word = word_raw.encode().decode('utf-8')
                print(('  [%2d] ' % len(word)) + word)

            if len(s.results) < s.nResults:
                print('\n%d/%d, flere resultater: ' %
                      (len(s.results), s.nResults) + ul + s.uri + nm)

            print(bu + "\nNytt søk" + nm + ' ')
            print('')
            print(bu + '? :' + nm + ' plassholder for enkel, ukjent bokstav')
            print(bu + '* :' + nm + ' plassholder for ukjent antall bokstaver')
            print('Mønster kan du la være blankt')
            print('')
            print('Avslutt programmet med CTRL + C')
            print('')

            query_raw, pattern_raw = '', ''
            while not query_raw:
                query_raw = input(bold('Spørreord: '))
            pattern_raw = input(bold('Mønster..: '))
            print(colorize('Laster...', color.YELLOW))
            s = Search(query_raw, pattern_raw)
    except KeyboardInterrupt:
        print("Takk for laget. :)")
        clear()


if __name__ == "__main__":

    import sys
    main(sys.argv)
