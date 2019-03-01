#! /usr/bin/python3

import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (QDialog, QInputDialog, QWidget, QPushButton, QLineEdit,
                             QHBoxLayout, QVBoxLayout, QSizePolicy, QMessageBox,
                             QApplication, QScrollArea, QComboBox)
from charwidget import CharacterWidget
from data_loader import UnicodeTable, Settings
from search_dialog import UnicodeSearch
from download_dialog import Downloader


class Main(QWidget):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

        self.APP_NAME = 'qUnicoder'
        self.UT_FILENAME = 'unicode-table-data-master.zip'
        self.LANG_STRINGS = ['ru', 'en']
        self.search_icon = QIcon('icons/search24.png')

        self.big_font = QFont("Serif", 18)
        self.big_font.setStyleHint(QFont.Serif)

        self.settings = Settings(self.APP_NAME)

        if not os.path.exists(self.UT_FILENAME):
            dl_dialog = Downloader(self.UT_FILENAME, self)
            if dl_dialog.exec_() != QDialog.Accepted:
                sys.exit()

        self.table = UnicodeTable(self.UT_FILENAME, self.settings.lang)

        self.edit = QLineEdit()
        self.edit.setClearButtonEnabled(True)
        self.edit.setFont(self.big_font)
        self.edit.setText(self.settings.editstring)

        copy_button = QPushButton(QIcon('icons/copy24.png'), '')
        copy_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        copy_button.setToolTip('копировать в буфер')
        copy_button.clicked.connect(self.copyClicked)

        edit_bar = QHBoxLayout()
        edit_bar.addWidget(self.edit, 1)
        edit_bar.addWidget(copy_button)

        self.chars = CharacterWidget(self)
        self.chars.characterSelected.connect(self.edit.insert)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.chars)
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.adjustMapPos)
        self.scroll_area.setAlignment(Qt.AlignHCenter)
        self.scroll_area.setFocusProxy(self.edit)
        self.scroll_area.setMinimumWidth(self.chars.width() + self.chars.cell_size)

        # закладки для быстрого доступа к позиции в таблице
        self.bookmarks = QComboBox()
        self.bookmarks.activated.connect(self.jumpToBookmark)
        self.bookmarks.currentIndexChanged.connect(self.jumpToBookmark)
        self.bookmarks.addItems(self.settings.bookmarks)

        # сохранить текущую позицию CharacterWidget в закладки
        bookmark_button = QPushButton(QIcon('icons/bookmark24.png'), '')
        bookmark_button.setToolTip('добавить закладку')
        bookmark_button.clicked.connect(self.setBookmark)

        # открыть окно поиска разделов/символов в юникоде
        find_button = QPushButton()
        find_button.setIcon(self.search_icon)
        find_button.setToolTip('поиск в юникоде')
        find_button.clicked.connect(self.unicodeSearch)

        del_button = QPushButton(QIcon('icons/backspace24.png'), '')
        del_button.setToolTip('удалить закладку')
        del_button.clicked.connect(self.delBookmark)

        bookmark_bar = QHBoxLayout()
        bookmark_bar.addWidget(self.bookmarks, 1)
        bookmark_bar.addWidget(bookmark_button)
        bookmark_bar.addWidget(del_button)
        bookmark_bar.addWidget(find_button)

        self.main_box = QVBoxLayout()
        self.main_box.addLayout(bookmark_bar)
        self.main_box.addWidget(self.scroll_area, 1)
        self.main_box.addLayout(edit_bar)

        self.setLayout(self.main_box)
        self.setMinimumHeight(716)
        self.setWindowTitle(self.APP_NAME)

    # сохранить текущую позицию в CharacterWidget в закладки
    def setBookmark(self):
        code = self.scroll_area.verticalScrollBar().value() // \
            self.chars.cell_size * self.chars.columns
        text, ok = QInputDialog.getText(
            self, self.APP_NAME,
            'Добавить закладку для позиции 0x{:04X}:\t\t'.format(code),
            QLineEdit.Normal, self.table._symbol_list[code])
        if ok:
            self.bookmarks.insertItem(0, '{0:04X} - {1}'.format(code, text))
            self.bookmarks.setCurrentIndex(0)

    # открыть окно поиска разделов/символов в юникоде
    def unicodeSearch(self):
        bs = UnicodeSearch(self)
        if bs.exec_() == QDialog.Accepted:
            text = '{0:04X} - {1}'.format(bs.selected_code, bs.selected_item)
            i = self.bookmarks.findText(text)
            if i != -1:
                self.bookmarks.removeItem(i)
            self.bookmarks.insertItem(0, text)
            self.bookmarks.setCurrentIndex(0)
            self.scroll_area.verticalScrollBar().setValue(
                self.chars.cell_size * (bs.selected_code // self.chars.columns))

    def delBookmark(self):
        self.bookmarks.removeItem(self.bookmarks.currentIndex())

    # быстрая перемотка CharacterWidget до нужной позиции
    def jumpToBookmark(self, index):
        code = 32
        if self.bookmarks.count() > 0:
            code = int(self.bookmarks.itemText(index)[:5], 16)
        self.scroll_area.verticalScrollBar().setValue(
            self.chars.cell_size * (code // self.chars.columns))
        self.edit.setFocus()

    def copyClicked(self):
        self.edit.selectAll()
        self.edit.copy()

    # выровнять положение CharacterWidget в scroll_area
    def adjustMapPos(self, pos):
        row = pos // self.chars.cell_size
        self.scroll_area.verticalScrollBar().setValue(
            row * self.chars.cell_size)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F1:
            QMessageBox.aboutQt(self, "Ҏγ†øη " + sys.version)
        if event.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        self.settings.lang = self.table.lang
        self.settings.bookmarks = [
            self.bookmarks.itemText(i) for i in range(self.bookmarks.count())]
        self.settings.editstring = self.edit.text()
        self.settings.save()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icons/favicon.ico'))
    mainWidget = Main()
    mainWidget.show()
    sys.exit(app.exec_())
