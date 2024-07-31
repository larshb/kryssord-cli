#!/usr/bin/env python3

from logging import basicConfig, debug
from requests import get
from requests.utils import quote
from html.parser import HTMLParser
from xml.dom.minidom import parseString
from bs4 import BeautifulSoup

from fx import crossword_format

# Logging
LOGLEVEL = "INFO"
try:
    from rich.logging import RichHandler
    basicConfig(
        level=LOGLEVEL,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()]
    )
except:
    basicConfig(level=LOGLEVEL)


# Formatting
ESC = '\x1b'
def csi(*args):
    return ESC + '[' + ';'.join(str(a) for a in args)
def sgr(*args):
    return csi(*args) + 'm'
def cuu(*args):
    return csi(*args) + 'A'

class FMT:
    NONE       = sgr(0)
    BOLD       = sgr(1)
    DIM        = sgr(2)
    ITALIC     = sgr(3)
    UNDERLINED = sgr(4)
    INVERTED   = sgr(7)
    EMPHASIZED = sgr(1, 4)

def bold(str):
    return FMT.BOLD + str + FMT.NONE


FANCY = True
if FANCY:
    from fx import fullsize_input as input


class KryssordOrg:

    URL = "https://www.kryssord.org"

    def search(self, a, b):

        url = self.URL + '/search.php'
        response = get(url, params={'a': a, 'b': b})
        return response

    def lookup(self, a, b=""):
        response = self.search(a, b)
        soup = BeautifulSoup(response.text, 'html.parser')
        words = [td.a.text for td in soup.find_all('td', {'class': 'word'})]
        for h1 in soup.find_all('h1'):
            if h1.strong:
                n = int(h1.strong.text)

        return words, n, response.url


class CLI:
    def __init__(self):
        self.api = KryssordOrg()

    def clear(self):
        print(csi("2J"))

    def print_help(self):
        print(f"{FMT.INVERTED}?{FMT.NONE} eller {FMT.INVERTED}.{FMT.NONE} for ukjent bokstav")
        print(f"{FMT.INVERTED}*{FMT.NONE} for et arbitrært antall ukjente")
        print("")

    def print_results(self, a, b, words, n, url):
        self.clear()
        # a = a.replace('?', '⬜').replace('*', '⬚') # □ ▢ …
        # b = b.replace('?', '⬜').replace('*', '⬚') # □ ▢ …
        header = f"Fant {FMT.EMPHASIZED}{n}{FMT.NONE} synonym til {FMT.EMPHASIZED}{a}{FMT.NONE}"
        if b:
            header += f" med mønster {FMT.EMPHASIZED}{b}{FMT.NONE}"
            header += '\n' + crossword_format(b)
        print(header + '\n')
        try:  # Rich table
            from rich.console import Console
            from rich.table import Table
            table = Table() #(show_header=False)
            table.add_column("#", justify="right")
            table.add_column("Synonym")
            for word in words:
                table.add_row(str(len(word)), word)
            Console().print(table)
        except:  # Pure Python
            for word in words:
                print(f"  [{len(word):2d}] {word}")
        if n != len(words):
            print(f"\n{FMT.ITALIC}({len(words)}/{n}){FMT.NONE}"
                + f" {FMT.UNDERLINED}{sgr('34')}{url}{FMT.NONE}")
        print(f"{FMT.UNDERLINED}                \n{FMT.NONE}")

    def interactive_lookup(self):
        self.print_help()
        while not (a := input(bold("Spørreord: ")).replace('.', '?')):
            print(cuu(1), end="")
        b = input(bold("Mønster..: ")).replace('.', '?')
        print(FMT.ITALIC + sgr('32') + "Laster..." + FMT.NONE)
        words, n, url = self.api.lookup(a, b)
        self.print_results(a, b, words, n, url)


def main(argv):
    cli = CLI()
    print(csi("?1049h"))
    try:
        a = 'nøtt'
        b = 'k?y?s*d'
        words, n, url = cli.api.lookup(a, b)
        cli.print_results(a, b, words, n, url)
        while True:
            cli.interactive_lookup()
    except KeyboardInterrupt:
        pass
    except UnboundLocalError:
        pass
    except EOFError:
        pass
    finally:
        print(csi("?1049l"))


if __name__ == '__main__':

    from sys import argv
    main(argv)
