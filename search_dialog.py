from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QAbstractItemView, QComboBox, QDialog, QHBoxLayout,
                             QVBoxLayout, QHeaderView, QPushButton, QTableWidget,
                             QTableWidgetItem)
from data_loader import UnicodeTable


SEARCH_MODES = [
    'по названию раздела',
    'по названию символа',
    'по символу',
    'по HEX коду',
    'по DEC коду']


class UnicodeSearch(QDialog):
    def __init__(self, parent):
        super(UnicodeSearch, self).__init__(parent)

        self.parent = parent

        self.selected_item = None
        self.selected_code = -1
        self.recent_searches = []

        # таблица с результатами поиска
        self.results = QTableWidget()
        self.results.verticalHeader().hide()
        self.results.horizontalHeader().hide()
        self.results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.results.setColumnCount(4)
        self.results.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.results.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results.cellActivated.connect(self.selectItem)

        # строка поиска, сохраняет введенные ранее строки
        self.combo = QComboBox()
        self.combo.setEditable(True)
        self.combo.setInsertPolicy(QComboBox.NoInsert)
        self.combo.lineEdit().setClearButtonEnabled(True)
        self.combo.currentIndexChanged.connect(self.searchClicked)
        self.search_mode = QComboBox()
        self.search_mode.addItems(SEARCH_MODES)
        self.lang_select = QComboBox()
        self.lang_select.addItems(parent.LANG_STRINGS)
        current_lang_index = parent.LANG_STRINGS.index(parent.table.lang)
        self.lang_select.setCurrentIndex(current_lang_index)
        self.lang_select.currentIndexChanged.connect(self.reloadUT)
        search_button = QPushButton(parent.search_icon, '')
        search_button.setToolTip('начать поиск')
        search_button.clicked.connect(self.searchClicked)

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.combo, 1)
        top_bar.addWidget(self.search_mode)
        top_bar.addWidget(self.lang_select)
        top_bar.addWidget(search_button)

        main_box = QVBoxLayout()
        main_box.addLayout(top_bar)
        main_box.addWidget(self.results)

        self.setLayout(main_box)
        self.resize(680, 680)
        self.searchClicked()

    # перезагрузка имен разделов/символов на указанном языке
    def reloadUT(self):
        self.parent.table = UnicodeTable(
            self.parent.UT_FILENAME,
            self.lang_select.currentText())
        self.search_mode.setCurrentIndex(0)
        self.combo.setCurrentText('')
        self.searchClicked()

    def searchClicked(self):
        items = []
        ut = self.parent.table
        self.block_mode = False
        text = self.combo.currentText()
        if text not in self.recent_searches:
            self.recent_searches.append(text)
            self.combo.addItem(text)
        mode = self.search_mode.currentIndex()
        if mode == 0:
            items = ut.find_block_name(text)
            self.block_mode = True
        if mode == 1:
            if len(text) < 3:
                self.combo.setCurrentText('не меньше 3 букв')
            else:
                items = ut.find_symbol_name(text)
        if mode == 2:
            items = ut.find_symbols(text)
        if mode == 3:
            items = ut.find_codes(text, 16)
        if mode == 4:
            items = ut.find_codes(text, 10)

        self.results.setRowCount(0)
        for entry in items:
            row = self.results.rowCount()
            self.results.insertRow(row)
            self.results.setItem(row, 0, QTableWidgetItem(entry[0]))
            self.results.setItem(row, 3, QTableWidgetItem(entry[2]))
            self.results.setItem(row, 1, QTableWidgetItem(' {:05X}'.format(entry[1])))
            self.results.setItem(row, 2, QTableWidgetItem(chr(entry[1])))

        self.results.sortByColumn(1, Qt.AscendingOrder)

        if self.block_mode:
            self.setWindowTitle('{0} — {1} разделов'.format(
                self.parent.APP_NAME, len(items)))
        else:
            self.setWindowTitle('{0} — {1} символов'.format(
                self.parent.APP_NAME, len(items)))

    # выбор одной строки из результатов поиска и
    # возвращение в главное окно к выбранной позиции, сохраняемой в закладки
    def selectItem(self, row, column):
        if self.block_mode:
            self.selected_item = self.results.item(row, 0).text()
        else:
            self.selected_item = '{0} ({1})'.format(
                self.results.item(row, 3).text(), self.results.item(row, 0).text())
        self.selected_code = int(self.results.item(row, 1).text(), 16)
        self.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.searchClicked()
