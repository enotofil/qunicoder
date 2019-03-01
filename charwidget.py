from PyQt5.QtCore import pyqtSignal, QSize, Qt
from PyQt5.QtGui import QFontMetrics, QPainter
from PyQt5.QtWidgets import QToolTip, QWidget


class CharacterWidget(QWidget):

    characterSelected = pyqtSignal(str)

    def __init__(self, parent):
        super(CharacterWidget, self).__init__(parent)
        self.parent = parent
        self.color_hl = Qt.gray
        self.cell_size = 38
        self.columns = 16
        self.lastKey = -1
        self.currentKey = -1
        self.pressedKey = None
        self.setMouseTracking(True)
        self.setStyleSheet('''
            QToolTip {
                color: black;
                background-color: cornsilk;
                border: 1px;
                font-size: 14px;
            }''')

        self.fontMetrics = QFontMetrics(self.parent.big_font)

    def sizeHint(self):
        return QSize(self.columns * self.cell_size,
                     (131072 / self.columns) * self.cell_size)

    def mouseMoveEvent(self, event):
        if self.pressedKey:
            return
        widgetPosition = self.mapFromGlobal(event.globalPos())
        self.currentKey = (widgetPosition.y() // self.cell_size) * \
            self.columns + widgetPosition.x() // self.cell_size

        if self.currentKey != self.lastKey:
            self.lastKey = self.currentKey
            name = self.parent.table._symbol_list[self.currentKey]
            if name == "no info":
                QToolTip.hideText()
            else:
                info_str = ('<i style="text-align:center">{0}</i>'
                            '<pre style="text-align:center">Hex: {1:04X} | Dec: {1}</pre>'
                            '<p style="font-size:48px;text-align:center">{2}</p>').format(
                    name, self.currentKey, chr(self.currentKey))
                # info_str = '{0}\nU+{1:04X} | Dec:{1}'.format(name, self.currentKey)
                QToolTip.showText(event.globalPos(), info_str, self)
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            key_ch = chr(self.lastKey)
            if self.parent.table._symbol_list[self.currentKey] != "no info":
                self.pressedKey = self.currentKey
                self.characterSelected.emit(key_ch)
            self.update()
        else:
            super(CharacterWidget, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.currentKey = (event.y() // self.cell_size) * \
            self.columns + event.x() // self.cell_size
        self.pressedKey = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), Qt.white)
        painter.setFont(self.parent.big_font)

        redrawRect = event.rect()
        beginRow = redrawRect.top() // self.cell_size
        endRow = redrawRect.bottom() // self.cell_size
        beginColumn = redrawRect.left() // self.cell_size
        endColumn = redrawRect.right() // self.cell_size

        for row in range(beginRow, endRow + 1):
            for column in range(beginColumn, endColumn + 1):
                key = row * self.columns + column
                key_ch = chr(key)
                if self.parent.table._symbol_list[key] == "no info":
                    continue

                x, y = column * self.cell_size, row * self.cell_size

                painter.setPen(Qt.lightGray)
                painter.drawRect(x, y, self.cell_size, self.cell_size)

                if key == self.currentKey:
                    painter.fillRect(x + 1, y + 1, self.cell_size - 1,
                                     self.cell_size - 1, self.color_hl)

                if key == self.pressedKey:
                    painter.fillRect(x + 1, y + 1, self.cell_size,
                                     self.cell_size, Qt.black)

                    painter.setPen(self.color_hl)
                    painter.drawText(
                        x + (self.cell_size - self.fontMetrics.width(key_ch)) / 2,
                        y + 6 + self.fontMetrics.ascent(), key_ch)
                else:
                    painter.setPen(Qt.black)
                    painter.drawText(
                        x + (self.cell_size - self.fontMetrics.width(key_ch)) / 2,
                        y + 6 + self.fontMetrics.ascent(), key_ch)
