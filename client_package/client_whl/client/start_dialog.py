from PyQt6.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel
from PyQt6.QtCore import QEvent


class UserNameDialog(QDialog):
    '''Класс реализующий стартовый диалог с запросом логина и пароля пользователя'''
    def __init__(self):
        super().__init__()

        self.ok_pressed = False

        self.setWindowTitle('Привет!')
        self.setFixedSize(175, 93)

        self.label = QLabel('Введите имя пользователя: ', self)
        self.label.move(10, 10)
        self.label.setFixedSize(150, 10)

        self.client_name = QLineEdit(self)
        self.client_name.setFixedSize(154, 20)
        self.client_name.move(10, 30)

        self.btn_ok = QPushButton('Начать', self)
        self.btn_ok.move(10, 60)
        self.btn_ok.clicked.connect(self.click)

        self.btn_cancel = QPushButton('Выход', self)
        self.btn_cancel.move(90, 60)
        self.btn_cancel.clicked.connect(QApplication.exit)

        self.show()

    def click(self):
        '''Метод - обработчик кнопки ОК, если поле ввод не пустое,
        ставим флаг и завершаем приложение'''
        if self.client_name.text():
            self.ok_pressed = True
            QApplication.exit()


if __name__ == '__main__':
    app = QApplication([])
    dial = UserNameDialog()
    app.exec()