from selenium import webdriver
import itertools
import re
from bs4 import BeautifulSoup


class FenGenerator:

    # Location of the puzzle source.
    url = 'http://www.chesspuzzles.com/mate-in-three'

    # Path to phantomJs.
    path = 'D:\\phantomjs\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe'

    # Piece names on chesspuzzles.com.
    piece_names = {'wpawn': 'P', 'wknight': 'N', 'wbishop': 'B',
                   'wrook': 'R', 'wqueen': 'Q', 'wking': 'K',
                   'bpawn': 'p', 'bknight': 'n', 'bbishop': 'b',
                   'brook': 'r', 'bqueen': 'q', 'bking': 'k',
                   'empty': '1'}

    # Precomputed puzzles.
    precomputed = [
        '8/R2N1R2/P2kB3/3P4/5K2/8/8/8 w - - 0 1',
        '8/4R3/1pN2p2/1N1k4/1P6/4p1P1/4B3/4K3 w - - 0 1'
    ]

    # Split a list into n lists of equal length.
    def _split(self, A, n):
        return [A[i: i + n] for i in range(0, len(A), n)]

    # Fetcg a soup from mate-in-3 website.
    def _fetch_soup(self):
        driver = webdriver.PhantomJS(executable_path=self.path)
        driver.get(self.url)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        return soup

    # Create a fenstring from rows.
    def _rows_to_fen(self, rows, to_move):
        fen = ''
        for i in range(8):
            if i > 0:
                fen += '/'
            split_row = [list(v) for k, v in itertools.groupby(rows[i])]
            for chunk in split_row:
                if chunk[0] == '1':
                    fen += str(len(chunk))
                else:
                    fen += ''.join(chunk)
        fen += ' ' + to_move + ' - - 0 1'
        return fen

    # Return a fen representing the game board.
    def get_board(self, index):
        if index > -1 and index < len(self.precomputed):
            # Return one of the precomputed boards.
            return self.precomputed[index]
        elif index == -1:
            # Fetch a new board.
            soup = self._fetch_soup()
            to_move = soup.find('div', attrs={'id': 'to_move'}).text[0]
            # Extract pieces.
            pieces = []
            for td in soup.find_all('td', re.compile("^sq\w")):
                for piece_div in td.findChildren():
                    pieces.append(self.piece_names[piece_div['class'][0]])
            # Create a fenstring.
            rows = self._split(pieces, 8)
            fen = self._rows_to_fen(rows, to_move)
            return fen
        raise Exception('Unknown board.')
