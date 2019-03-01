from PyQt5.QtWidgets import (QDialog, QLineEdit, QVBoxLayout, QPushButton, QLabel)
import requests

URL = "https://github.com/unicode-table/unicode-table-data/archive/master.zip"


class Downloader(QDialog):
    def __init__(self, file_name, parent):
        super(Downloader, self).__init__(parent)

        self.file_name = file_name

        self.label = QLabel('"{0}" не найден.\nМожно взять здесь:'.format(file_name))
        self.edit = QLineEdit(URL)
        self.button = QPushButton('Скачать')
        self.button.clicked.connect(self.downloadUTData)

        main_box = QVBoxLayout()
        main_box.addWidget(self.label)
        main_box.addWidget(self.edit)
        main_box.addWidget(self.button)
        self.setLayout(main_box)
        self.setFixedWidth(500)
        self.setWindowTitle(parent.APP_NAME)

    # загрузка архива с данными с github через requests
    def downloadUTData(self):
        self.button.setDisabled(True)
        self.button.setText('Загрузка...')
        self.edit.setDisabled(True)
        self.repaint()
        try:
            r = requests.get(URL, allow_redirects=True)
            if r.status_code > 200:
                raise Exception('Невозможно скачать архив.')
            open(self.file_name, 'wb').write(r.content)
            self.accept()
        except Exception as e:
            self.label.setText('Ошибка: ' + str(e))
            self.button.setText('Загрузка не удалась...')
