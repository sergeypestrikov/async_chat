import sys
import os

import self as self
from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import QWidget, QApplication, QVBoxLayout, QMainWindow, QWidgetAction, QLabel, QTableView, QDialog, QPushButton, QLineEdit, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon, QAction


def gui_model(database):
    '''Создание таблицы QModel для отображения в окне программы'''
    list_users = database.active_users_list()
    list = QStandardItemModel()
    list.setHorizontalHeaderLabels(['Имя клиента', 'IP', 'Порт', 'Время подключения'])
    for row in list_users:
        user, ip, port, time = row
        user = QStandardItem(user)
        user.setEditable(False)
        ip = QStandardItem(ip)
        ip.setEditable(False)
        port = QStandardItem(str(port))
        port.appendRow([user, ip, port, time])
    return list


def create_msg_history_model(database):
    '''Заполнение таблицы историей сообщений'''
    # Список записей из базы
    history_list = database.message_history()
    # Объект модели данных
    list = QStandardItemModel()
    list.setHorizontalHeaderLabels(['Имя клиента', 'Последний вход', 'Сообщение отправлено', 'Кол-во сообщений'])
    for row in history_list:
        user, last_seen, sent, received = row
        user = QStandardItem(user)
        user.setEditable(False)
        last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
        last_seen.setEditable(False)
        sent = QStandardItem(str(sent))
        sent.setEditable(False)
        received = QStandardItem(str(received))
        received.setEditable(False)
        list.appendRow([user, last_seen, sent, received])
    return list

# Основное окно
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.setWindowTitle('Chat project')

    def initUI(self):
        # Кнопка выхода
        exitAction = QAction('Выход', self)
        exitAction.triggered.connect(QApplication.quit)
        # Кнопка обновить
        self.refresh_button = QAction('Обновить список', self)
        # Кнопка настроек сервера
        self.config_button = QAction('Настройки сервера', self)
        # Вывод истории сообщений
        self.show_history_button = QAction('История клиентов', self)
        # Статус-панель
        self.statusBar()
        # Тулбар
        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.show_history_button)
        self.toolbar.addAction(self.config_button)

        self.setFixedSize(500, 500)
        self.setWindowTitle('Давайте общаться')
        # Инфа, что ниже список подключённых клиентов
        self.label = QLabel('Список подключённых клиентов:', self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 25)
        # Окно со списком подключённых клиентов
        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(10, 45)
        self.active_clients_table.setFixedSize(780, 400)

        self.show()

# Окно с историей пользователей
class HistoryWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Статистика клиентов')
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        # Кнопка закрытия окна
        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)
        # Лист с историей
        self.history_table = QTableView(self)
        self.history_table.move(10, 10)
        self.history_table.setFixedSize(580, 620)

        self.show()

# Окно настроек
class ConfigWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(365, 260)
        self.setWindowTitle('Настройки сервера')

        # Надпись о файле базы данных
        self.db_path_label = QLabel('Путь до файла базы данных: ', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        # Строка с путём базы
        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)

        # Кнопка выбора пути
        self.db_path_select = QPushButton('Обзор...', self)
        self.db_path_select.move(275, 28)

        # Функция обработчик открытия окна выбора папки
        def open_file_dialog():
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory()
            path = path.replace('/', '\\')
            self.db_path.insert(path)

        self.db_path_select.clicked.connect(open_file_dialog)

        # Метка с именем поля файла базы данных
        self.db_file_label = QLabel('Имя файла базы данных: ', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)

        # Поле для ввода имени файла
        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150, 20)

        # Метка с номером порта
        self.port_label = QLabel('Номер порта для соединений:', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)

        # Поле для ввода номера порта
        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        # Метка с адресом для соединений
        self.ip_label = QLabel('С какого IP принимаем соединения:', self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(180, 15)

        # Метка с напоминанием о пустом поле
        self.ip_label_note = QLabel('Оставьте это поле пустым, чтобы принимать соединения с любых адресов.', self)
        self.ip_label_note.move(10, 168)
        self.ip_label_note.setFixedSize(500, 30)

        # Поле для ввода ip
        self.ip = QLineEdit(self)
        self.ip.move(200, 148)
        self.ip.setFixedSize(150, 20)

        # Кнопка сохранения настроек
        self.save_btn = QPushButton('Сохранить', self)
        self.save_btn.move(190, 220)

        # Кнопка закрытия окна
        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.statusBar().showMessage('Тестовый запуск')
    test = QStandardItemModel(window)
    test.setHorizontalHeaderLabels(['Имя клиента', 'IP', 'Порт', 'Время подключения'])
    test.appendRow([QStandardItem('1'), QStandardItem('2'), QStandardItem('3')])
    test.appendRow([QStandardItem('4'), QStandardItem('5'), QStandardItem('6')])
    window.active_clients_table.setModel(test)
    window.active_clients_table.resizeColumnsToContents()
    print('Готово')
    window.show()
    app.exec()
    print('Теперь точно готово')
    # app = QApplication(sys.argv)
    # message = QMessageBox
    # dial = ConfigWindow()
    #
    # app.exec()