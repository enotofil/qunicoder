import re
import os
from zipfile import ZipFile
from io import TextIOWrapper
import pickle

'''
Settings загружает или сохраняет в файл <appname>.pickle
1. закладки
2. текущий язык
3. набранный текст
'''


class Settings:
    def __init__(self, filename):

        # defaults
        self.bookmarks = []
        self.lang = 'ru'
        self.editstring = ''

        self.filename = filename + '.pickle'
        if not os.path.exists(self.filename):
            print('No saved settings found.')
            return
        with open(self.filename, 'rb') as f:
            data = pickle.load(f)
            self.bookmarks = data['bookmarks']
            self.lang = data['lang']
            self.editstring = data['editstring']
            print('{0} bookmarks loaded from "{1}", lang="{2}", editstring="{3}"'.format(
                len(self.bookmarks), self.filename, self.lang, self.editstring))

    def save(self):
        with open(self.filename, 'wb') as f:
            pickle.dump({
                'bookmarks': self.bookmarks,
                'lang': self.lang,
                'editstring': self.editstring
            }, f)


'''
Открывает и читает архив с диапазонами и названиями на указанном языке.
Данные взяты отсюда:
https://github.com/unicode-table/unicode-table-data/archive/master.zip
'''


class UnicodeTable:

    def __init__(self, file_name, lang_str):
        self.lang = lang_str
        self.ok = False
        self.message = ''
        DATA_ROOT = file_name.split('.')[0]

        utdata_zip = ZipFile(file_name)

        self._no_info_str = "no info"
        self._blocks = []
        with utdata_zip.open(DATA_ROOT + '/data/blocks.txt') as f:
            f = TextIOWrapper(f, encoding='utf-8')
            self._blocks = re.findall(
                r'\[(.*)\]\n\s*diap\s*:\s([0-9A-F]{4,5}):([0-9A-F]{4,5})', f.read())
            # _blocks element: (block-name, first-hex-code, last-hex-code)
        print('{0} ranges loaded from "{1}"'.format(
            len(self._blocks), utdata_zip.filename))

        self._table = {}
        self._symbol_list = [self._no_info_str] * 0x100000

        target_str = '/loc/' + lang_str + '/symbols/'
        for name in utdata_zip.namelist():
            if (target_str in name) and (name[-1] != '/'):
                with utdata_zip.open(name) as f:
                    f = TextIOWrapper(f, encoding='utf-8')
                    symbols = re.findall(r'([0-9A-F]{4,5}): (.+)', f.read())
                    # symbols: (hex_code, localized_symbol_name)
                    for s in symbols:
                        self._symbol_list[int(s[0], 16)] = s[1]

        block_names = {}
        with utdata_zip.open(DATA_ROOT + '/loc/' + lang_str + '/blocks.txt') as f:
            f = TextIOWrapper(f, encoding='utf-8')
            for pair in re.findall('(.*):(.*)', f.read()):
                # pair: (block_name, localized_block_name)
                block_names[pair[0].strip()] = pair[1].strip()

        for block in self._blocks:
            block_name = block_names[block[0]]
            first = int(block[1], 16)
            if first > 0x1FFFF:
                continue
            last = int(block[2], 16)
            block_table = {}
            for i in range(first, last + 1):
                if self._symbol_list[i] != self._no_info_str:
                    block_table[i] = self._symbol_list[i]
            # no empty tables
            if len(block_table) > 0:
                self._table[block_name] = block_table
            else:
                print('empty block: ', block_name)
        print('UnicodeTable "{0}" data loaded from "{1}"'.format(
            lang_str, utdata_zip.filename))
        utdata_zip.close()
        self.ok = True

    def get_info_for(self, code):
        name = self._symbol_list[code]
        if name != self._no_info_str:
            return format(code, '04X') + " | " + name

    def find_block_name(self, sub_str):
        found = []
        for block_name, symbols in self._table.items():
            if sub_str.lower() in block_name.lower():
                first = 0xfffff
                for code, symbol_name in symbols.items():
                    first = min(first, code)
                found.append((block_name, first, ' {0} символов'.format(len(symbols))))
        return found

    def find_symbol_name(self, sub_str):
        found = []
        for block_name, symbols in self._table.items():
            for code, symbol_name in symbols.items():
                if sub_str.lower() in symbol_name.lower():
                    found.append((block_name, code, symbol_name))
        return found

    def find_symbols(self, sub_str):
        found = []
        for block_name, symbols in self._table.items():
            for code, symbol_name in symbols.items():
                if chr(code) in sub_str:
                    found.append((block_name, code, symbol_name))
        return found

    def find_codes(self, sub_str, base):
        found = []
        codes = []
        if base == 16:
            matches = re.findall(r'[0-9A-Fa-f]{1,5}', sub_str)
        if base == 10:
            matches = re.findall(r'[0-9]{1,6}', sub_str)
        for code in matches:
            codes.append(int(code, base))
        for block_name, symbols in self._table.items():
            for code, symbol_name in symbols.items():
                if code in codes:
                    found.append((block_name, code, symbol_name))
        return found

    def get_block(self, name):
        return(self._table[name])
