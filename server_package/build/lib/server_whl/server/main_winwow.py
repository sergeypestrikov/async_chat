from PyQt6.QtWidgets import QMainWindow, QWidgetAction, QLabel, QTableView, QApplication
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import QTimer

from stat_window import StatWindow
from config_window import ConfigWindow
from add_user import RegisterUser
from remove_user import DelUserDialog


class MainWindow(QMainWindow):
    '''Класс - основное окно сервера'''
    def __init__(self, database, server, config):
        # Конструктор предка
        super().__init__()
        # БД сервера
        self.database = database

        self.server_thread = server
        self.config = config
        # Ярлык выхода
        self.exitAction = QWidgetAction('Выход', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.triggered.connect(QApplication.quit)
        # Кнопка обновить список клиентов
        self.refresh_button = QWidgetAction('Обновить список', self)
        # Кнопка настроек сервера
        self.config_btn = QWidgetAction('Настройки сервера', self)
        # Кнопка регистрации пользователя
        self.register_btn = QWidgetAction('Регистрация пользователя', self)
        # Кнопка удаления пользователя
        self.remove_btn = QWidgetAction('Удаление пользователя', self)
        # Кнопка вывести историю сообщений
        self.show_history_button = QWidgetAction('История клиентов', self)
        # Статусбар
        self.statusBar()
        self.statusBar().showMessage('Сервер работает')
        # Тулбар
        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(self.exitAction)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.show_history_button)
        self.toolbar.addAction(self.config_btn)
        self.toolbar.addAction(self.register_btn)
        self.toolbar.addAction(self.remove_btn)
        # Настройки геометрии основного окна
        self.setFixedSize(500, 500)
        self.setWindowTitle('myChat тестовая версия')
        # Надпись о том, что ниже список подключённых клиентов
        self.label = QLabel('Список подключённых клиентов:', self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 25)
        # Окно со списком подключённых клиентов
        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(10, 45)
        self.active_clients_table.setFixedSize(780, 400)
        # Таймер, обновляющий список клиентов 1 раз в секунду
        self.timer = QTimer()
        self.timer.timeout.connect(self.create_users_model)
        self.timer.start(1000)
        # Связываем кнопки с процедурами
        self.refresh_button.triggered.connect(self.create_users_model)
        self.show_history_button.triggered.connect(self.show_statistics)
        self.config_btn.triggered.connect(self.server_config)
        self.register_btn.triggered.connect(self.reg_user)
        self.remove_btn.triggered.connect(self.rem_user)
        # Последним параметром отображаем окно.
        self.show()

    def create_users_model(self):
        '''Метод заполняющий таблицу активных пользователей'''
        list_users = self.database.active_users_list()
        list = QStandardItemModel()
        list.setHorizontalHeaderLabels(
            ['Имя Клиента', 'IP', 'Порт', 'Время подключения'])
        for row in list_users:
            user, ip, port, time = row
            user = QStandardItem(user)
            user.setEditable(False)
            ip = QStandardItem(ip)
            ip.setEditable(False)
            port = QStandardItem(str(port))
            port.setEditable(False)
            time = QStandardItem(str(time.replace(microsecond=0)))
            time.setEditable(False)
            list.appendRow([user, ip, port, time])
        self.active_clients_table.setModel(list)
        self.active_clients_table.resizeColumnsToContents()
        self.active_clients_table.resizeRowsToContents()

    def show_statistics(self):
        '''Метод создающий окно со статистикой клиентов'''
        global stat_window
        stat_window = StatWindow(self.database)
        stat_window.show()

    def server_config(self):
        '''Метод создающий окно с настройками сервера'''
        global config_window
        # Окно и текущие параметры
        config_window = ConfigWindow(self.config)

    def reg_user(self):
        '''Метод создающий окно регистрации пользователя'''
        global reg_window
        reg_window = RegisterUser(self.database, self.server_thread)
        reg_window.show()

    def rem_user(self):
        '''Метод создающий окно удаления пользователя'''
        global rem_window
        rem_window = DelUserDialog(self.database, self.server_thread)
        rem_window.show()