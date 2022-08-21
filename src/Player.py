import pickle

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox, QApplication, QPushButton, QLabel, QLineEdit
from PyQt5.QtCore import Qt
from Sockets import Client
from threading import Thread
import sys
import numpy as np
import json


class Player(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.client = Client()
        self.marks = 0
        self.color_answer = []
        self.end = False
        self.final = False
        self.answers = []
        self.functions = [self.key0, self.key1]
        self.player_answers = []
        self.date = np.datetime64('today')
        with open("ip.json", 'r') as fp:
            self.server_ip = json.load(fp)
        # self.server_ip = '66.25.19.20'
        self.fill_hello_page()

    def key0(self, message):  # добавление условий заданий и last_index+1
        self.stacked_widget.setCurrentIndex(2)
        self.game_var = message
        self.formula = self.game_var["formula"]
        self.last_index = 1
        self.label.setText('Вопрос ' + str(self.last_index) + ' из ' + str(len(self.game_var)-1))
        self.text_browser.append(self.set_text(str(self.last_index)))
        self.last_index += 1

    def key1(self, message):
        if message:  # ?
            self.show_correct_btn.setHidden(False)  # показать кнопку "посмотреть ответы"

    def fill_hello_page(self):
        # Общие настройки
        self.setObjectName("MainWindow")

        # Получить размер разрешения монитора
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.screen_height = self.screenRect.height()
        self.screen_width = self.screenRect.width()
        print(self.screen_height)
        print(self.screen_width)

        self.setGeometry(int(0.1 * self.screen_width), int(0.05 * self.screen_height), int(0.85 * self.screen_width),
                         int(0.85 * self.screen_height))  # размер главного окна
        self.setStyleSheet('background-color: rgb(160, 185, 194); font: 12pt Tahoma')
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.stacked_widget = QtWidgets.QStackedWidget(self.centralwidget)
        self.widget_width = int(0.8 * self.screen_width)
        self.widget_height = int(0.85 * self.screen_height)
        self.stacked_widget.setGeometry(QtCore.QRect(0, 0, self.widget_width, self.widget_height))  # положение виджета
        self.stacked_widget.setObjectName("stacked_widget")

        # Окна
        self.connection_page = QtWidgets.QWidget()
        self.connection_page.setObjectName("connection_page")

        self.pixmap = QPixmap('logo100.png').scaled(100, 100)
        self.image = QLabel(self.connection_page)
        self.image.move(10, 10)
        self.image.setPixmap(self.pixmap)

        # Надпись ФИО
        self.name_label = QLabel(self.connection_page)  # в виджете подключения
        self.name_label.setGeometry(QtCore.QRect(int(0.387 * self.widget_width), int(0.27 * self.widget_height),
                                                 int(0.225 * self.widget_width), int(0.047 * self.widget_height)))
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setObjectName("name_label")
        self.name_label.setText("Введите ФИО, номер взвода:")

        # Поле ввода ФИО
        self.name_line_edit = QLineEdit(self.connection_page)  # в виджете подключения
        self.name_line_edit.setStyleSheet('background-color: rgb(160, 185, 194)')
        self.name_line_edit.setGeometry(QtCore.QRect(int(0.387 * self.widget_width), int(0.332 * self.widget_height),
                                                     int(0.225 * self.widget_width), int(0.047 * self.widget_height)))
        self.name_line_edit.setObjectName("name_line_edit")
        self.name_line_edit.setStyleSheet("background: white;")


        # Кнопка подключиться
        self.connect_btn = QPushButton(self.connection_page)  # в виджете подключения
        self.connect_btn.setGeometry(QtCore.QRect(int(0.612 * self.widget_width), int(0.71 * self.widget_height),
                                                  int(0.163 * self.widget_width), int(0.061 * self.widget_height)))
        self.connect_btn.setObjectName("connect_btn")
        self.connect_btn.setText("Подключиться")
        self.connect_btn.clicked.connect(self.connect_btn_click)
        self.connect_btn.setStyleSheet(button_style(14))

        # Кнопка настройки
        self.settings_btn = QPushButton(self.connection_page)  # в виджете подключения
        self.settings_btn.setGeometry(QtCore.QRect(int(0.224 * self.widget_width), int(0.71 * self.widget_height),
                                                   int(0.163 * self.widget_width), int(0.061 * self.widget_height)))
        self.settings_btn.setObjectName("settings_btn")
        self.settings_btn.setText("Настройки")
        self.settings_btn.clicked.connect(self.settings_btn_click)
        self.settings_btn.setStyleSheet(button_style(14))

        self.wait_page = QtWidgets.QWidget()
        self.wait_page.setObjectName("wait_page")

        self.image = QLabel(self.wait_page)
        self.image.move(10, 10)
        self.image.setPixmap(self.pixmap)

        # надпись ожидание
        self.wait_label = QtWidgets.QLabel(self.wait_page)  # в виджете ожидания
        self.wait_label.setText('Ожидание')
        self.wait_label.setStyleSheet('font: 46pt Tahoma')
        self.wait_label.setAlignment(Qt.AlignCenter)
        self.wait_label.setGeometry(QtCore.QRect(int(0.27 * self.widget_width), int(0.388 * self.widget_height),
                                                 int(0.458 * self.widget_width), int(0.118 * self.widget_height)))
        self.wait_label.setObjectName("wait_label")

        self.quest_page = QtWidgets.QWidget()  # размеры проверить
        self.quest_page.setObjectName("quest_page")

        self.image = QLabel(self.quest_page)
        self.image.move(10, 10)
        self.image.setPixmap(self.pixmap)

        # надпись номера вопроса из
        self.label = QtWidgets.QLabel(self.quest_page)  # в виджете гостя (выполнение теста)
        self.label.setGeometry(QtCore.QRect(int(0.5 * self.widget_width), int(0.106 * self.widget_height),
                                            int(0.225 * self.widget_width), int(0.118 * self.widget_height)))
        self.label.setObjectName("label")

        # условие задачи
        self.text_browser = QtWidgets.QTextBrowser(self.quest_page)  # в виджете гостя (выполнение теста)
        self.text_browser.setStyleSheet(text_style())
        self.text_browser.setGeometry(QtCore.QRect(int(0.045 * self.widget_width), int(0.282 * self.widget_height),
                                                   int(0.459 * self.widget_width), int(0.306 * self.widget_height)))
        self.text_browser.setObjectName("text_browser")

        # поле ввода ответа
        self.text_edit = QtWidgets.QTextEdit(self.quest_page)  # в виджете гостя (выполнение теста)
        self.text_edit.setPlaceholderText('Введите ответ...')
        self.text_edit.setStyleSheet(text_style())
        self.text_edit.setGeometry(QtCore.QRect(int(0.595 * self.widget_width), int(0.282 * self.widget_height),
                                                int(0.459 * self.widget_width), int(0.306 * self.widget_height)))
        self.text_edit.setObjectName("text_edit")

        # кнопка след. вопроса
        self.next_btn = QtWidgets.QPushButton(self.quest_page)  # в виджете гостя (выполнение теста)
        self.next_btn.setStyleSheet(button_style(font_size=13))
        self.next_btn.clicked.connect(self.next_quest_func)  # при нажатии на кнопку "Далее"
        self.next_btn.setText('Далее')
        self.next_btn.setGeometry(QtCore.QRect(int(0.72 * self.widget_width), int(0.882 * self.widget_height),
                                               int(0.1 * self.widget_width), int(0.061 * self.widget_height)))
        self.next_btn.setObjectName("next_btn")

        self.result_page = QtWidgets.QWidget()  # размеры проверить
        self.result_page.setObjectName("result_page")

        self.image = QLabel(self.result_page)
        self.image.move(10, 10)
        self.image.setPixmap(self.pixmap)

        # надпись результата
        self.result_label = QtWidgets.QLabel(self.result_page)  # в виджете результатов
        self.result_label.setStyleSheet('font: 32pt Tahoma')
        self.result_label.setAlignment(Qt.AlignCenter)
        # self.result_label.setText('{}, вы набрали {} баллов.'.format(self.name, self.marks))
        self.result_label.setGeometry(QtCore.QRect(int(0.137 * self.widget_width), int(0.35 * self.widget_height),
                                                   int(0.725 * self.widget_width), int(0.235 * self.widget_height)))
        self.result_label.setObjectName("result_label")

        # кнопка показа ответов
        self.show_correct_btn = QtWidgets.QPushButton(self.result_page)  # в виджете результатов
        self.show_correct_btn.setStyleSheet(button_style(font_size=16))
        self.show_correct_btn.clicked.connect(self.show_correct_func)  # при нажатии на кнопку "Посмотреть ответы"
        self.show_correct_btn.setText('Посмотреть ответы')
        self.show_correct_btn.setGeometry(QtCore.QRect(int(0.343 * self.widget_width), int(0.765 * self.widget_height),
                                                       int(0.313 * self.widget_width), int(0.118 * self.widget_height)))
        self.show_correct_btn.setHidden(True)  # скрыть кнопку "Посмотреть ответы"

        self.show_correct_page = QtWidgets.QWidget()
        self.answers_frame = QtWidgets.QFrame(self.show_correct_page)

        self.image = QLabel(self.show_correct_page)
        self.image.move(10, 10)
        self.image.setPixmap(self.pixmap)

        # Страница настроек ip
        self.settings_page = QtWidgets.QWidget()
        self.settings_page.setObjectName("settings_page")

        self.image = QLabel(self.settings_page)
        self.image.move(10, 10)
        self.image.setPixmap(self.pixmap)

        # Надпись ip
        self.settings_label = QLabel(self.settings_page)  # в виджете подключения
        self.settings_label.setGeometry(QtCore.QRect(int(0.387 * self.widget_width), int(0.27 * self.widget_height),
                                                     int(0.225 * self.widget_width), int(0.047 * self.widget_height)))
        self.settings_label.setAlignment(Qt.AlignCenter)
        self.settings_label.setObjectName("settings_label")
        self.settings_label.setText("Введите ip сервера:")

        # Поле ввода ip
        self.settings_line_edit = QLineEdit(self.settings_page)  # в виджете подключения
        self.settings_line_edit.setStyleSheet('background-color: rgb(160, 185, 194)')
        self.settings_line_edit.setGeometry(
            QtCore.QRect(int(0.387 * self.widget_width), int(0.332 * self.widget_height),
                         int(0.225 * self.widget_width), int(0.047 * self.widget_height)))
        self.settings_line_edit.setObjectName("settings_line_edit")
        self.settings_line_edit.setStyleSheet("background: white;")
        self.settings_line_edit.setPlaceholderText(self.server_ip)

        # Кнопка применить
        self.apply_btn = QPushButton(self.settings_page)  # в виджете подключения
        self.apply_btn.setGeometry(QtCore.QRect(int(0.612 * self.widget_width), int(0.71 * self.widget_height),
                                                int(0.163 * self.widget_width), int(0.061 * self.widget_height)))
        self.apply_btn.setObjectName("apply_btn")
        self.apply_btn.setText("Применить")
        self.apply_btn.clicked.connect(self.apply_btn_click)
        self.apply_btn.setStyleSheet(button_style(14))

        self.stacked_widget.addWidget(self.connection_page)
        self.stacked_widget.addWidget(self.wait_page)
        self.stacked_widget.addWidget(self.quest_page)
        self.stacked_widget.addWidget(self.result_page)
        self.stacked_widget.addWidget(self.show_correct_page)
        self.stacked_widget.addWidget(self.settings_page)
        self.setCentralWidget(self.centralwidget)
        self.stacked_widget.setCurrentIndex(0)

    def show_correct_func(self):  # показать ответы
        self.answers_frame.setGeometry(QtCore.QRect(int(0.225 * self.widget_width), int(0.153 * self.widget_height),
                                                    int(0.75 * self.widget_width), 500))
        self.answers_frame.setStyleSheet(frame_style())
        self.table_answers = QtWidgets.QTableWidget(self.answers_frame)
        self.table_answers.setStyleSheet('background-color: white')
        self.table_answers.setGeometry(QtCore.QRect(int(0.025 * self.widget_width), int(0.031 * self.widget_height),
                                                    int(0.7 * self.widget_width), 460))
        self.table_answers.setColumnCount(4)  # кол-во колонок
        self.table_answers.setRowCount(len(self.game_var)-1)  # кол-во строк, заданий
        # скрытие колонки нумерации строк ?
        self.table_answers.verticalHeader().setHidden(True)
        self.table_answers.setHorizontalHeaderLabels(
            ['№ вопроса', 'Тип задания', 'Ваш ответ', 'Правильный ответ'])

        for i in range(4):  # установка ширины колонок
            self.table_answers.horizontalHeaderItem(i).setTextAlignment(Qt.AlignLeft)
            if i in [0, 1]:
                w = int(0.055 * self.widget_width)
            else:
                w = int(0.27 * self.widget_width)
            self.table_answers.setColumnWidth(i, w)  # установка ширины колонок
        for i in range(len(self.game_var)-1):  # для каждого задания
            info = self.game_var[str(i + 1)]  # хз почему game_var[str(i + 1)] ?
            self.table_answers.setItem(i, 0, QtWidgets.QTableWidgetItem(str(i + 1)))  # номер вопроса
            self.table_answers.setItem(i, 1, QtWidgets.QTableWidgetItem(info[0]))  # тип задания
            self.table_answers.setItem(i, 2, QtWidgets.QTableWidgetItem(self.answers[i]))  # ваш ответ
            # выделение правильных и неправильных ответов
            if self.color_answer[i] == '1':
                self.table_answers.item(i, 2).setBackground(QtGui.QColor(0, 153, 0))
            elif self.color_answer[i] == '0':
                self.table_answers.item(i, 2).setBackground(QtGui.QColor(204, 0, 0))
            if info[0] != '6':
                self.table_answers.setItem(i, 3, QtWidgets.QTableWidgetItem(info[10]))  # правильный ответ
            elif info[0] == '6':
                ans = ''
                for j in range(0, len(info[10])):
                    ans += '{}-ая подсеть:\n'.format(j + 1)
                    ans += 'Адрес подсети: {}\n'.format(info[10][j][0])  # правильный ответ для 6-ой
                    ans += 'Широковещательный адрес: {}\n'.format(info[10][j][1])
                    ans += 'Пул адресов от: {}\n'.format(info[10][j][2])
                    ans += 'Пул адресов до: {}\n'.format(info[10][j][3])
                    ans += 'Маска подсети: {}\n'.format(info[10][j][4])
                self.table_answers.setItem(i, 3, QtWidgets.QTableWidgetItem(ans))
        self.table_answers.resizeRowsToContents()
        self.stacked_widget.setCurrentIndex(4)

    def set_text(self, index):  # возвращает условие задачи №index
        self.tip = self.game_var[index][0]
        ip = self.game_var[index][1]
        maska = self.game_var[index][2]
        adres_hosta = self.game_var[index][3]
        network5 = self.game_var[index][4]
        kolvo_podsetey = self.game_var[index][5]
        kolvo_hostov = self.game_var[index][6]
        network6 = self.game_var[index][7]
        razmery_podsetey = self.game_var[index][8]
        adresa_podsetey = self.game_var[index][9]

        if self.tip == '1':
            result_text = 'По заданным IP-адресу узла и маске\nопределите адрес сети:'
            result_text += '\nIP-адрес: {}\nМаска: {}.'.format(ip, maska)
        elif self.tip == '2':
            result_text = 'По заданным IP-адресу узла и маске подсети\nопределите порядковый номер хоста в сети:'
            result_text += '\nIP-адрес: {}\nМаска подсети: {}.'.format(ip, maska)
        elif self.tip == '3':
            result_text = 'По заданной маске подсети определите\nвозможное количество узлов в сети,'
            result_text += '\nесли два адреса не используются.\nМаска подсети: {}.'.format(maska)
        elif self.tip == '4':
            result_text = 'Определите маску для хоста с адресом\n{}'.format(adres_hosta)
        elif self.tip == '5':
            result_text = 'Определите маску для проекта:\nсеть '
            result_text += '{},\n{} подсетей\nи {} хостов.'.format(network5, kolvo_podsetey, kolvo_hostov)
        elif self.tip == '6':
            result_text = 'Разделите сеть {} на 3 разные подсети.\nНайдите и запишите в каждой '.format(network6)
            result_text += 'подсети ее адреса,\nшироковещательный адрес, пул разрешенных\nк выдаче адресов и маску.'
            result_text += '\nУказываю требуемые размеры подсетей:\n1) Подсеть на {} '.format(razmery_podsetey[0])
            result_text += 'адресов,\n2) Подсеть на {} адресов,\n'.format(razmery_podsetey[1])
            result_text += '3) Подсеть на {} адресов.'.format(razmery_podsetey[2])
        elif self.tip == '7':
            result_text = 'Даны 4 подсети:\n1) {}\n2) {}'.format(adresa_podsetey[0], adresa_podsetey[1])
            result_text += '\n3) {}\n4) {}\n'.format(adresa_podsetey[2], adresa_podsetey[3])
            result_text += 'Просуммируйте подсети и найдите маску,\nкоторая сможет покрыть их, не задевая'
            result_text += '\nпри этом соседние подсети.'
        return result_text

    def next_quest_func(self):
        self.send_server()  # отправляет данные
        if ((self.last_index - 1) == (len(self.game_var)-1)):  # последний вопрос
            self.grade()
            self.end = True  # игрок закончил
            self.send_server()  # отправка данных
            self.result_label.setText(
                '{}, \nВы набрали {} из {}.\nВаша оценка: {}'.format(self.player_name, self.marks,
                                                                     (len(self.game_var)-1), self.final_grade))
            self.stacked_widget.setCurrentIndex(3)  # виджет 3
        else:  # если вопрос не последний, то печать следующего
            self.label.setText('Вопрос ' + str(self.last_index) + ' из ' + str(len(self.game_var)-1))
            self.text_edit.clear()  # очистить поле ответа
            self.text_browser.setText(self.set_text(str(self.last_index)))  # вывод условия след задачи
            self.last_index += 1

    def listen_server(self):  # слушаем сервер
        while True:
            data = self.client.socket.recv(2048)
            data = pickle.loads(data)
            # ?
            self.functions[data['Key']](data['Message'])  # functions = [self.key0, self.key1], key0,1 - функции

    def closeEvent(self, event):
        self.close()
        self.client.socket.close()

    def send_server(self):
        if self.end:  # если закончил, key = 2
            data = {'Key': 2, 'Message': [self.player_answers]}  # в словарь
            # дата{key - 2, message - массив словарей ответов игрока}
        else:
            if self.tip != '6':
                player_answer = self.text_edit.toPlainText()  # текст из поля ввода ответа
                self.answers.append(player_answer)  # в массив answers добавляем в конец ответ
                # сравниваем ответ игрока с верным
                correct = int(player_answer == self.game_var[str(self.last_index - 1)][10])
            else:
                cnt = 0
                player_answer = self.text_edit.toPlainText().split('\n')
                for i in range(0, len(player_answer)):
                    if str(player_answer[i]) == str(self.game_var[str(self.last_index - 1)][10][i // 5][i % 5]):
                        cnt += 1
                if cnt == 15:
                    correct = 1
                else:
                    correct = 0
                self.answers.append(self.text_edit.toPlainText())

            self.marks += correct  # добавляем баллы 0 или 1
            self.color_answer.append(str(correct))
            self.player_answers.append({'ФИО': self.player_name, 'Дата': self.date, 'Тип задачи': self.tip,
                                        'Правильно': correct})
            # игрок не закончил, key = 1
            data = {'Key': 1, 'Message': [self.player_name, correct]}  # словарь
            # data{ message = массив[имя игрока, 0 или 1] }
        data = pickle.dumps(data)  # отправляем data на сервер
        self.client.socket.send(data)  # отправляем data на сервер

    def connect_btn_click(self):
        try:
            # IP сервера по умолчанию
            with open("ip.json", 'r') as fp:
                self.server_ip = json.load(fp)
            # self.server_ip = '66.25.19.20'
            self.client.socket.connect((self.server_ip, 1234))  # подключение к введенному IP и 1234 порту
            self.client.socket.settimeout(None)
            self.player_name = self.name_line_edit.text()  # введенное имя игрока
            data = {'Key': 0, 'Message': self.player_name}  # словарь data{key - 0, message - имя игрока}
            data = pickle.dumps(data)  # записывает сериализованный объект в файл
            self.client.socket.send(data)  # отправляет словарь data
            listen_thread = Thread(target=self.listen_server)  # многопоточное прослушивание
            listen_thread.start()  # многопоточное прослушивание
            self.stacked_widget.setCurrentIndex(1)  # вывести на экран 1 виджет
        except:
            alert = QMessageBox()
            alert.setText('Ошибка подключения к серверу!')
            alert.exec_()

    # настройки
    def settings_btn_click(self):
        self.stacked_widget.setCurrentIndex(5)  # вывести на экран 5 виджет settings_page

    # применить настройки ip
    def apply_btn_click(self):
        if self.settings_line_edit.text() != '':  # введенный игроком IP != пустота
            self.server_ip = self.settings_line_edit.text()
            # перезапись ip.json
            with open('ip.json', 'w') as fp:
                json.dump(self.server_ip, fp)
            self.settings_line_edit.setText('')
            self.settings_line_edit.setPlaceholderText(self.server_ip)
        self.stacked_widget.setCurrentIndex(0)  # вывести на экран 0 виджет connection_page

    # функция подсчитывания оценки
    def grade(self):
        self.min_grade_5 = self.formula[0]
        self.min_grade_4 = self.formula[1]
        self.min_grade_3 = self.formula[2]
        self.final_grade = ''
        if int(self.marks) / (len(self.game_var)-1) >= int(self.min_grade_5) / 100:
            self.final_grade = '5'
        elif int(self.marks) / (len(self.game_var)-1) >= int(self.min_grade_4) / 100:
            self.final_grade = '4'
        elif int(self.marks) / (len(self.game_var)-1) >= int(self.min_grade_3) / 100:
            self.final_grade = '3'
        else:
            self.final_grade = '2'


def button_style(font_size=16):  # стиль кнопок
    s = r"""QPushButton {
                             border: 2px;
                             border-radius: 6px;
                             background-color: #e69422;
                             min-width: 80px;
                            font: """
    s += str(font_size) + """pt "Tahoma";
                         }
                         QPushButton:hover {
                             background-color: #688f8d;
                             cursor: pointer;
                         }"""
    return s


def frame_style():  # показать ответы
    s = """QFrame {
                 border: 2px;
                 border-radius: 12px;
                 background-color: #efd2ac;
             }"""

    return s


def text_style():  # условия задачи #a1c2a0
    s = """border: 2px; border-radius: 8px; background-color: #e6cf9c; font: 12pt;"""
    return s


app = QtWidgets.QApplication(sys.argv)
player = Player()
player.show()
sys.exit(app.exec_())
