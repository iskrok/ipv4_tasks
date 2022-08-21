from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMessageBox, QAbstractItemView

from ip_tasks import *
from Sockets import Server

import sys
import json
import pickle
from threading import Thread


class PlayerTable:
    def __init__(self, root, max_players):

        self.l_quest = 100
        self.table = QtWidgets.QTableWidget(root)
        self.table.setGeometry(QtCore.QRect(30, 30, 840, 500))
        self.table.setStyleSheet('background-color: white')
        self.marks = '0'
        self.table.setColumnCount(4)
        self.table.setRowCount(max_players)
        self.table.setHorizontalHeaderLabels(['ФИО студента', 'Текущий вопрос', 'Количество баллов', 'Оценка'])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeaderItem(0).setToolTip("Column 1")
        for i in range(3):
            self.table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignLeft)
            if i == 0:
                w = 380
            else:
                w = 160
            self.table.setColumnWidth(i, w)

        self.last_index = 0
        self.finder = {}

        self.min_grade_5 = App.send_grades(App)[0]
        self.min_grade_4 = App.send_grades(App)[1]
        self.min_grade_3 = App.send_grades(App)[2]
        self.table.setSelectionMode(QAbstractItemView.NoSelection)

    def add(self, name):
        self.table.setItem(self.last_index, 0, QtWidgets.QTableWidgetItem(name))
        self.table.setItem(self.last_index, 1, QtWidgets.QTableWidgetItem('-'))
        self.table.setItem(self.last_index, 2, QtWidgets.QTableWidgetItem('0'))
        self.table.setItem(self.last_index, 3, QtWidgets.QTableWidgetItem('-'))
        self.finder[name] = [self.last_index, 1, 0]
        self.table.hide()
        self.table.show()
        self.last_index += 1

    def start(self):
        for i in range(0, self.last_index):
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem('Вопрос 1'))

    def change(self, name, correct, end=False):
        index = self.finder[name][0]
        if end:
            self.table.setItem(index, 1, QtWidgets.QTableWidgetItem('Закончил'))
            self.table.hide()
            self.table.show()
        else:
            self.finder[name][1] += 1
            quest_num = str(self.finder[name][1])
            if int(quest_num) > self.l_quest:
                self.table.setItem(index, 1, QtWidgets.QTableWidgetItem('Закончил'))
                self.table.hide()
                self.table.show()
            else:
                self.table.setItem(index, 1, QtWidgets.QTableWidgetItem('Вопрос ' + quest_num))

        self.finder[name][2] += correct
        self.marks = str(self.finder[name][2])
        self.table.setItem(index, 2, QtWidgets.QTableWidgetItem(self.marks))
        if int(self.marks) / self.l_quest >= int(self.min_grade_5) / 100:
            self.table.setItem(index, 3, QtWidgets.QTableWidgetItem('5'))
            self.table.item(index, 3).setForeground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
            self.table.item(index, 3).setTextAlignment(Qt.AlignCenter)
            self.table.item(index, 3).setBackground(QtGui.QColor(0, 153, 0))
        elif int(self.marks) / self.l_quest >= int(self.min_grade_4) / 100:
            self.table.setItem(index, 3, QtWidgets.QTableWidgetItem('4'))
            self.table.item(index, 3).setForeground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
            self.table.item(index, 3).setTextAlignment(Qt.AlignCenter)
            self.table.item(index, 3).setBackground(QtGui.QColor(0, 128, 255))
        elif int(self.marks) / self.l_quest >= int(self.min_grade_3) / 100:
            self.table.setItem(index, 3, QtWidgets.QTableWidgetItem('3'))
            self.table.item(index, 3).setForeground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
            self.table.item(index, 3).setTextAlignment(Qt.AlignCenter)
            self.table.item(index, 3).setBackground(QtGui.QColor(255, 128, 0))
        else:
            self.table.setItem(index, 3, QtWidgets.QTableWidgetItem('2'))
            self.table.item(index, 3).setForeground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
            self.table.item(index, 3).setTextAlignment(Qt.AlignCenter)
            self.table.item(index, 3).setBackground(QtGui.QColor(204, 0, 0))
        self.table.hide()
        self.table.show()

    def done(self):
        c = 0
        for i in range(0, self.last_index):
            if self.table.item(i, 1).text() == 'Закончил':
                c += 1
        if c == self.last_index:
            return True
        else:
            return False


class App(QtWidgets.QMainWindow):
    def setup_ui(self):
        # Общие настройки
        self.server_started = 0
        self.game_started = 0
        self.setWindowTitle("Задачи на IP")
        self.setObjectName("MainWindow")
        self.setFixedSize(1200, 800)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setStyleSheet('background-color: rgb(221, 188, 149); font: 10pt Tahoma')
        # Главное окно переключения виджетов
        self.mainStackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.mainStackedWidget.setGeometry(QtCore.QRect(0, 0, 1200, 800))
        self.mainStackedWidget.setObjectName("mainStackedWidget")

        # Первая страница с тремя кнопками
        self.hello_page = QtWidgets.QWidget()
        self.hello_page.setObjectName("hello_page")
        # Кнопка запуска игры
        self.start_btn = QtWidgets.QPushButton(self.hello_page)
        self.start_btn.clicked.connect(self.start_func)
        self.start_btn.setText('Начать')
        self.start_btn.setStyleSheet(button_style())
        self.start_btn.setEnabled(True)
        self.start_btn.setGeometry(QtCore.QRect(450, 270, 300, 60))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.start_btn.sizePolicy().hasHeightForWidth())
        self.start_btn.setSizePolicy(sizePolicy)
        self.start_btn.setObjectName("start_btn")
        # Кнопка создания варианта
        self.create_var_btn = QtWidgets.QPushButton(self.hello_page)
        self.create_var_btn.clicked.connect(lambda x: self.mainStackedWidget.setCurrentIndex(1))
        self.create_var_btn.setText('Создать вариант')
        self.create_var_btn.setStyleSheet(button_style())
        self.create_var_btn.setEnabled(True)
        self.create_var_btn.setGeometry(QtCore.QRect(450, 370, 300, 60))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.create_var_btn.sizePolicy().hasHeightForWidth())
        self.create_var_btn.setSizePolicy(sizePolicy)
        self.create_var_btn.setObjectName("create_var_btn")
        # Кнопка настроек
        self.settings_btn = QtWidgets.QPushButton(self.hello_page)
        self.settings_btn.setStyleSheet(button_style())
        self.settings_btn.setText('Настройки')
        self.settings_btn.clicked.connect(lambda x: self.mainStackedWidget.setCurrentIndex(2))
        self.settings_btn.setGeometry(QtCore.QRect(450, 470, 300, 60))

        # Добавление приветственной страницы на главный виджет
        self.mainStackedWidget.addWidget(self.hello_page)

        # Страница для создания варианта
        self.var_page = QtWidgets.QWidget()
        self.var_page.setObjectName("var_page")
        self.label = QtWidgets.QLabel(self.var_page)
        self.label.setGeometry(QtCore.QRect(0, 0, 1220, 40))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setFrameShape(QtWidgets.QFrame.Box)
        self.label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label.setLineWidth(2)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.var_page)
        self.label_2.setGeometry(QtCore.QRect(0, 40, 970, 80))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_2.setFont(font)
        self.label_2.setFrameShape(QtWidgets.QFrame.Box)
        self.label_2.setLineWidth(2)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.label_9 = QtWidgets.QLabel(self.var_page)
        self.label_9.setGeometry(QtCore.QRect(20, 710, 291, 71))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.pushButton = QtWidgets.QPushButton(self.var_page)
        self.pushButton.setGeometry(QtCore.QRect(980, 720, 200, 70))
        self.pushButton.clicked.connect(self.save_var)
        self.pushButton.setStyleSheet(button_style())
        font = QtGui.QFont()
        font.setPointSize(20)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")

        self.pushButton2 = QtWidgets.QPushButton(self.var_page)
        self.pushButton2.setGeometry(QtCore.QRect(750, 720, 200, 70))
        self.pushButton2.clicked.connect(lambda x: self.mainStackedWidget.setCurrentIndex(0))
        self.pushButton2.setStyleSheet(button_style())
        self.pushButton2.setText('Назад')
        font = QtGui.QFont()
        font.setPointSize(20)
        self.pushButton2.setFont(font)
        self.pushButton2.setObjectName("pushButton2")

        self.label_3 = QtWidgets.QLabel(self.var_page)
        self.label_3.setGeometry(QtCore.QRect(0, 200, 970, 80))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_3.setFont(font)
        self.label_3.setFrameShape(QtWidgets.QFrame.Box)
        self.label_3.setLineWidth(2)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.var_page)
        self.label_4.setGeometry(QtCore.QRect(0, 120, 970, 80))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setStrikeOut(False)
        self.label_4.setFont(font)
        self.label_4.setFrameShape(QtWidgets.QFrame.Box)
        self.label_4.setLineWidth(2)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.var_page)
        self.label_5.setGeometry(QtCore.QRect(0, 280, 970, 80))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_5.setFont(font)
        self.label_5.setFrameShape(QtWidgets.QFrame.Box)
        self.label_5.setLineWidth(2)
        self.label_5.setWordWrap(True)
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.var_page)
        self.label_6.setGeometry(QtCore.QRect(0, 360, 970, 80))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_6.setFont(font)
        self.label_6.setFrameShape(QtWidgets.QFrame.Box)
        self.label_6.setLineWidth(2)
        self.label_6.setWordWrap(True)
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.var_page)
        self.label_7.setGeometry(QtCore.QRect(0, 440, 970, 120))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_7.setFont(font)
        self.label_7.setFrameShape(QtWidgets.QFrame.Box)
        self.label_7.setLineWidth(2)
        self.label_7.setWordWrap(True)
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.var_page)
        self.label_8.setGeometry(QtCore.QRect(0, 560, 970, 110))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_8.setFont(font)
        self.label_8.setFrameShape(QtWidgets.QFrame.Box)
        self.label_8.setLineWidth(2)
        self.label_8.setWordWrap(True)
        self.label_8.setObjectName("label_8")
        self.spinBox_8 = QtWidgets.QSpinBox(self.var_page)
        self.spinBox_8.setGeometry(QtCore.QRect(330, 720, 130, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.spinBox_8.setFont(font)
        self.spinBox_8.setObjectName("spinBox_8")
        self.spinBox_8.setStyleSheet('font: 16pt Tahoma')
        self.spinBox = QtWidgets.QSpinBox(self.var_page)
        self.spinBox.setGeometry(QtCore.QRect(1120, 55, 70, 50))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.spinBox.setFont(font)
        self.spinBox.setObjectName("spinBox")
        self.spinBox.setStyleSheet('font: 16pt Tahoma')
        self.spinBox_2 = QtWidgets.QSpinBox(self.var_page)
        self.spinBox_2.setGeometry(QtCore.QRect(1120, 135, 70, 50))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.spinBox_2.setFont(font)
        self.spinBox_2.setObjectName("spinBox_2")
        self.spinBox_2.setStyleSheet('font: 16pt Tahoma')
        self.spinBox_3 = QtWidgets.QSpinBox(self.var_page)
        self.spinBox_3.setGeometry(QtCore.QRect(1120, 215, 70, 50))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.spinBox_3.setFont(font)
        self.spinBox_3.setObjectName("spinBox_3")
        self.spinBox_3.setStyleSheet('font: 16pt Tahoma')
        self.spinBox_4 = QtWidgets.QSpinBox(self.var_page)
        self.spinBox_4.setGeometry(QtCore.QRect(1120, 295, 70, 50))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.spinBox_4.setFont(font)
        self.spinBox_4.setObjectName("spinBox_4")
        self.spinBox_4.setStyleSheet('font: 16pt Tahoma')
        self.spinBox_5 = QtWidgets.QSpinBox(self.var_page)
        self.spinBox_5.setGeometry(QtCore.QRect(1120, 375, 70, 50))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.spinBox_5.setFont(font)
        self.spinBox_5.setObjectName("spinBox_5")
        self.spinBox_5.setStyleSheet('font: 16pt Tahoma')
        self.spinBox_6 = QtWidgets.QSpinBox(self.var_page)
        self.spinBox_6.setGeometry(QtCore.QRect(1120, 470, 70, 50))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.spinBox_6.setFont(font)
        self.spinBox_6.setObjectName("spinBox_6")
        self.spinBox_6.setStyleSheet('font: 16pt Tahoma')
        self.spinBox_7 = QtWidgets.QSpinBox(self.var_page)
        self.spinBox_7.setGeometry(QtCore.QRect(1120, 585, 70, 50))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.spinBox_7.setFont(font)
        self.spinBox_7.setObjectName("spinBox_7")
        self.spinBox_7.setStyleSheet('font: 16pt Tahoma')

        self.label.setText(" Выбор заданий")
        self.label.setStyleSheet('font: 24pt Tahoma')
        self.label_2.setText("1.  По заданным IP-адресу узла и маске определить адрес сети")
        self.label_2.setStyleSheet('font: 16pt Tahoma')
        self.label_9.setText("Количество вариантов:")
        self.label_9.setStyleSheet('font: 16pt Tahoma')
        self.pushButton.setText("Сохранить")
        self.label_3.setText("3.  По заданной маске подсети определить возможное количество узлов в сети")
        self.label_3.setStyleSheet('font: 16pt Tahoma')
        self.label_4.setText("2.  По заданным IP-адресу узла и маске подсети определить порядковый номер узла в сети")
        self.label_4.setStyleSheet('font: 16pt Tahoma')
        self.label_5.setText("4.  Определить маску для хоста с адресом")
        self.label_5.setStyleSheet('font: 16pt Tahoma')
        self.label_6.setText("5.  Определить маску для проекта")
        self.label_6.setStyleSheet('font: 16pt Tahoma')
        self.label_7.setText(
            "6. Разделить сеть на несколько разных подсетей. Найти и записать в каждой подсети ее адреса, "
            "широковещательный адрес, пул разрешенных к выдаче адресов и маску")
        self.label_7.setStyleSheet('font: 16pt Tahoma')
        self.label_8.setText(
            "7. Даны несколько подсетей. Просуммировать подсети и найти маску, которая сможет покрыть их, не задевая "
            "при этом соседние подсети")
        self.label_8.setStyleSheet('font: 16pt Tahoma')

        self.mainStackedWidget.addWidget(self.var_page)
        # Страница настроек
        self.settings_page = QtWidgets.QWidget()
        self.settings_page.setObjectName("settings_page")

        self.set_main_label = QtWidgets.QLabel(self.settings_page)
        self.set_main_label.setText("Формула оценки")
        self.set_main_label.setGeometry(QtCore.QRect(480, 200, 300, 50))
        self.set_main_label.setStyleSheet('font: 24pt Tahoma')

        self.set_label1 = QtWidgets.QLabel(self.settings_page)
        self.set_label1.setText("5 от:")
        self.set_label1.setGeometry(QtCore.QRect(520, 300, 90, 50))
        self.set_label1.setStyleSheet('font: 16pt Tahoma')
        self.set_line1 = QtWidgets.QLineEdit(self.settings_page)
        self.set_line1.setGeometry(QtCore.QRect(620, 300, 70, 50))
        self.set_line1.setStyleSheet('font: 16pt Tahoma')
        self.set_line1.setText(str(self.send_grades()[0]))

        self.set_label2 = QtWidgets.QLabel(self.settings_page)
        self.set_label2.setText("4 от:")
        self.set_label2.setGeometry(QtCore.QRect(520, 350, 90, 50))
        self.set_label2.setStyleSheet('font: 16pt Tahoma')
        self.set_line2 = QtWidgets.QLineEdit(self.settings_page)
        self.set_line2.setGeometry(QtCore.QRect(620, 350, 70, 50))
        self.set_line2.setStyleSheet('font: 16pt Tahoma')
        self.set_line2.setText(str(self.send_grades()[1]))

        self.set_label3 = QtWidgets.QLabel(self.settings_page)
        self.set_label3.setText("3 от:")
        self.set_label3.setGeometry(QtCore.QRect(520, 400, 90, 50))
        self.set_label3.setStyleSheet('font: 16pt Tahoma')
        self.set_line3 = QtWidgets.QLineEdit(self.settings_page)
        self.set_line3.setGeometry(QtCore.QRect(620, 400, 70, 50))
        self.set_line3.setStyleSheet('font: 16pt Tahoma')
        self.set_line3.setText(str(self.send_grades()[2]))

        self.set_label4 = QtWidgets.QLabel(self.settings_page)
        self.set_label4.setText("%")
        self.set_label4.setGeometry(QtCore.QRect(643, 260, 90, 40))
        self.set_label4.setStyleSheet('font: 16pt Tahoma')

        self.set_end_btn = QtWidgets.QPushButton(self.settings_page)
        self.set_end_btn.setStyleSheet(button_style())
        self.set_end_btn.setText("Назад")
        self.set_end_btn.setGeometry(QtCore.QRect(290, 600, 220, 50))
        self.set_end_btn.clicked.connect(lambda x: self.mainStackedWidget.setCurrentIndex(0))

        self.set_save_btn = QtWidgets.QPushButton(self.settings_page)
        self.set_save_btn.setStyleSheet(button_style())
        self.set_save_btn.setText("Сохранить")
        self.set_save_btn.setGeometry(QtCore.QRect(690, 600, 220, 50))
        self.set_save_btn.clicked.connect(self.save_conf)

        self.mainStackedWidget.addWidget(self.settings_page)

        # Страница подготовки игры

        self.game_page = QtWidgets.QWidget()
        self.game_page.setObjectName("game_page")
        # Надпись про выбор файла с вариантом
        self.num_quest_label = QtWidgets.QLabel(self.game_page)
        self.num_quest_label.setText('Файл с вариантом:')
        self.num_quest_label.setGeometry(QtCore.QRect(390, 20, 200, 30))
        self.num_quest_label.setObjectName("num_quest_label")
        self.num_quest_label.setStyleSheet('font: 16pt Tahoma')
        # Кнопка выбора файла с вариантом
        self.choose_file_btn = QtWidgets.QPushButton(self.game_page)
        self.choose_file_btn.setText('Выбрать файл')
        self.choose_file_btn.setStyleSheet(button_style())
        self.choose_file_btn.clicked.connect(self.choose_file_func)
        self.choose_file_btn.setGeometry(QtCore.QRect(610, 10, 200, 50))
        self.choose_file_btn.setObjectName("choose_file_btn")
        # Надписи предпросмотра варианта
        self.vars_num_label = QtWidgets.QLabel(self.game_page)
        self.vars_num_label.setGeometry(QtCore.QRect(475, 80, 250, 50))
        self.vars_num_label.setObjectName("vars_num_label")
        self.vars_num_label.setStyleSheet('font: 16pt Tahoma')

        self.task1_num_label = QtWidgets.QLabel(self.game_page)
        self.task1_num_label.setGeometry(QtCore.QRect(50, 150, 900, 50))
        self.task1_num_label.setObjectName("task1_num_label")
        self.task1_num_label.setWordWrap(True)
        self.task1_num_label.setStyleSheet('font: 16pt Tahoma')
        self.task1_count_label = QtWidgets.QLabel(self.game_page)
        self.task1_count_label.setGeometry(QtCore.QRect(1100, 150, 50, 50))
        self.task1_count_label.setObjectName("task1_count_label")
        self.task1_count_label.setStyleSheet('font: 16pt Tahoma')

        self.task2_num_label = QtWidgets.QLabel(self.game_page)
        self.task2_num_label.setGeometry(QtCore.QRect(50, 225, 900, 50))
        self.task2_num_label.setObjectName("task2_num_label")
        self.task2_num_label.setWordWrap(True)
        self.task2_num_label.setStyleSheet('font: 16pt Tahoma')
        self.task2_count_label = QtWidgets.QLabel(self.game_page)
        self.task2_count_label.setGeometry(QtCore.QRect(1100, 225, 50, 50))
        self.task2_count_label.setObjectName("task2_count_label")
        self.task2_count_label.setStyleSheet('font: 16pt Tahoma')

        self.task3_num_label = QtWidgets.QLabel(self.game_page)
        self.task3_num_label.setGeometry(QtCore.QRect(50, 300, 900, 50))
        self.task3_num_label.setObjectName("task3_num_label")
        self.task3_num_label.setWordWrap(True)
        self.task3_num_label.setStyleSheet('font: 16pt Tahoma')
        self.task3_count_label = QtWidgets.QLabel(self.game_page)
        self.task3_count_label.setGeometry(QtCore.QRect(1100, 300, 50, 50))
        self.task3_count_label.setObjectName("task3_count_label")
        self.task3_count_label.setStyleSheet('font: 16pt Tahoma')

        self.task4_num_label = QtWidgets.QLabel(self.game_page)
        self.task4_num_label.setGeometry(QtCore.QRect(50, 375, 900, 50))
        self.task4_num_label.setObjectName("task4_num_label")
        self.task4_num_label.setWordWrap(True)
        self.task4_num_label.setStyleSheet('font: 16pt Tahoma')
        self.task4_count_label = QtWidgets.QLabel(self.game_page)
        self.task4_count_label.setGeometry(QtCore.QRect(1100, 375, 50, 50))
        self.task4_count_label.setObjectName("task4_count_label")
        self.task4_count_label.setStyleSheet('font: 16pt Tahoma')

        self.task5_num_label = QtWidgets.QLabel(self.game_page)
        self.task5_num_label.setGeometry(QtCore.QRect(50, 450, 900, 50))
        self.task5_num_label.setObjectName("task5_num_label")
        self.task5_num_label.setWordWrap(True)
        self.task5_num_label.setStyleSheet('font: 16pt Tahoma')
        self.task5_count_label = QtWidgets.QLabel(self.game_page)
        self.task5_count_label.setGeometry(QtCore.QRect(1100, 450, 50, 50))
        self.task5_count_label.setObjectName("task5_count_label")
        self.task5_count_label.setStyleSheet('font: 16pt Tahoma')

        self.task6_num_label = QtWidgets.QLabel(self.game_page)
        self.task6_num_label.setGeometry(QtCore.QRect(50, 525, 900, 50))
        self.task6_num_label.setObjectName("task6_num_label")
        self.task6_num_label.setWordWrap(True)
        self.task6_num_label.setStyleSheet('font: 16pt Tahoma')
        self.task6_count_label = QtWidgets.QLabel(self.game_page)
        self.task6_count_label.setGeometry(QtCore.QRect(1100, 525, 50, 50))
        self.task6_count_label.setObjectName("task6_count_label")
        self.task6_count_label.setStyleSheet('font: 16pt Tahoma')

        self.task7_num_label = QtWidgets.QLabel(self.game_page)
        self.task7_num_label.setGeometry(QtCore.QRect(50, 600, 900, 50))
        self.task7_num_label.setObjectName("task7_num_label")
        self.task7_num_label.setWordWrap(True)
        self.task7_num_label.setStyleSheet('font: 16pt Tahoma')
        self.task7_count_label = QtWidgets.QLabel(self.game_page)
        self.task7_count_label.setGeometry(QtCore.QRect(1100, 600, 50, 50))
        self.task7_count_label.setObjectName("task7_count_label")
        self.task7_count_label.setStyleSheet('font: 16pt Tahoma')

        # Кнопка для создания игровой комнаты
        self.create_room_btn = QtWidgets.QPushButton(self.game_page)
        self.create_room_btn.setStyleSheet(button_style())
        self.create_room_btn.setText('Создать комнату')
        self.create_room_btn.clicked.connect(self.create_room_func)
        self.create_room_btn.setGeometry(QtCore.QRect(625, 700, 250, 50))
        self.create_room_btn.setObjectName("create_room_btn")
        # Кнопка возврата на главную
        self.back_btn = QtWidgets.QPushButton(self.game_page)
        self.back_btn.setStyleSheet(button_style())
        self.back_btn.setText('Назад')
        self.back_btn.clicked.connect(lambda x: self.mainStackedWidget.setCurrentIndex(0))
        self.back_btn.setGeometry(QtCore.QRect(325, 700, 250, 50))
        self.back_btn.setObjectName("back_btn")
        # Кнопка отправки задания
        self.send_task_btn = QtWidgets.QPushButton(self.game_page)
        self.send_task_btn.setStyleSheet(button_style())
        self.send_task_btn.setText('Отправить задание')
        self.send_task_btn.clicked.connect(self.start_game)
        self.send_task_btn.setGeometry(QtCore.QRect(625, 700, 250, 50))
        self.send_task_btn.setObjectName("send_task_btn")
        self.send_task_btn.setHidden(True)
        # Кнопка возврата к выбору варианта
        self.back_btn2 = QtWidgets.QPushButton(self.game_page)
        self.back_btn2.setStyleSheet(button_style())
        self.back_btn2.setText('Назад')
        self.back_btn2.clicked.connect(self.back_func)
        self.back_btn2.setGeometry(QtCore.QRect(325, 700, 250, 50))
        self.back_btn2.setObjectName("back_btn2")
        self.back_btn2.setHidden(True)
        # Кнопка для разрешения просмотра ответов
        self.ans_btn = QtWidgets.QPushButton(self.game_page)
        self.ans_btn.setStyleSheet(button_style())
        self.ans_btn.setText('Открыть ответы')
        self.ans_btn.clicked.connect(self.ans_func)
        self.ans_btn.setGeometry(QtCore.QRect(325, 700, 250, 50))
        self.ans_btn.setHidden(True)
        # Кнопка для завершения
        self.finish_btn = QtWidgets.QPushButton(self.game_page)
        self.finish_btn.setStyleSheet(button_style())
        self.finish_btn.setText('На главную')
        self.finish_btn.clicked.connect(self.finish_func)
        self.finish_btn.setGeometry(QtCore.QRect(625, 700, 250, 50))
        self.finish_btn.setHidden(True)

        self.mainStackedWidget.addWidget(self.game_page)
        self.setCentralWidget(self.centralwidget)
        self.mainStackedWidget.setCurrentIndex(0)

    def start_func(self):
        self.ans_btn.setDisabled(False)
        # Frame с карточками игроков
        self.players_frame = QtWidgets.QFrame(self.game_page)
        self.players_frame.setHidden(True)
        self.players_frame.setStyleSheet('background-color: white')
        self.players_frame.setGeometry(QtCore.QRect(155, 100, 900, 560))
        self.players_frame.setStyleSheet(frame_style())
        self.players_frame.setObjectName("players_frame")
        self.table_players = PlayerTable(self.players_frame, 30)
        self.mainStackedWidget.setCurrentIndex(3)

    def ans_func(self):
        if self.table_players.done():
            self.ans_btn.setDisabled(True)
            data = {'Key': 1, 'Message': True}
            data = pickle.dumps(data)
            for user in self.server.players:
                user.sendall(data)
        else:
            alert = QMessageBox(self.centralwidget)
            alert.setIcon(QMessageBox.Question)
            alert.setText("Не все игроки закончили.\nВы уверены что хотите открыть ответы?")
            alert.setWindowTitle("Внимание!")
            alert.addButton("Да", QMessageBox.YesRole)
            alert.addButton("Нет", QMessageBox.RejectRole)
            ret = alert.exec()
            if ret == 0:
                self.ans_btn.setDisabled(True)
                data = {'Key': 1, 'Message': True}
                data = pickle.dumps(data)
                for user in self.server.players:
                    user.sendall(data)
            else:
                alert.close()

    def finish_func(self):
        if self.table_players.done():
            self.mainStackedWidget.setCurrentIndex(0)
            self.server_started = 0
            self.game_started = 0
            self.back_func()
            self.ans_btn.setHidden(True)
            self.finish_btn.setHidden(True)
            self.server.socket.close()
        else:
            alert = QMessageBox(self.centralwidget)
            alert.setIcon(QMessageBox.Question)
            alert.setText("Не все игроки закончили.\nВы уверены что хотите выйти?")
            alert.setWindowTitle("Внимание!")
            alert.addButton("Да", QMessageBox.YesRole)
            alert.addButton("Нет", QMessageBox.RejectRole)
            ret = alert.exec()
            if ret == 0:
                self.mainStackedWidget.setCurrentIndex(0)
                self.server_started = 0
                self.game_started = 0
                self.back_func()
                self.ans_btn.setHidden(True)
                self.finish_btn.setHidden(True)
                self.server.socket.close()
            else:
                alert.close()

    def start_game(self):
        self.send_task_btn.setHidden(True)
        self.back_btn2.setHidden(True)
        self.create_room_btn.setHidden(True)
        self.finish_btn.setHidden(False)
        self.ans_btn.setHidden(False)
        if len(self.var_file) == 0:
            self.ans_btn.setHidden(True)
            self.finish_btn.setHidden(True)
            self.send_task_btn.setHidden(False)
            self.back_btn2.setHidden(False)
            QMessageBox().warning(self.centralwidget, "Ошибка!", "Не выбрано задание")
            self.back_func()
        else:
            self.table_players.l_quest = len(self.var_file[0]) - 1
            i = 0
            if len(self.server.players) == 0:
                self.ans_btn.setHidden(True)
                self.finish_btn.setHidden(True)
                self.send_task_btn.setHidden(False)
                self.back_btn2.setHidden(False)
                QMessageBox().warning(self.centralwidget, "Ошибка!", "Нет подключенных игроков")

            elif len(self.server.players) > len(self.var_file):
                self.ans_btn.setHidden(True)
                self.finish_btn.setHidden(True)
                self.send_task_btn.setHidden(False)
                self.back_btn2.setHidden(False)
                QMessageBox().warning(self.centralwidget, "Ошибка!",
                                      "Игроков больше чем вариантов.\nВыберете другой файл с заданиями")
                self.back_func()
            else:
                self.table_players.start()
                for user in self.server.players:
                    if i < len(self.var_file):
                        data = {'Key': 0, 'Message': self.var_file[i]}
                        data = pickle.dumps(data)
                        user.sendall(data)
                        i += 1
                    else:
                        data = {'Key': 0, 'Message': ''}
                        data = pickle.dumps(data)
                        user.sendall(data)
                self.game_started = 1

    def create_room_func(self):

        self.choose_file_btn.setHidden(True)
        self.num_quest_label.setHidden(True)
        self.vars_num_label.setHidden(True)
        self.task1_num_label.setHidden(True)
        self.task2_num_label.setHidden(True)
        self.task3_num_label.setHidden(True)
        self.task4_num_label.setHidden(True)
        self.task5_num_label.setHidden(True)
        self.task6_num_label.setHidden(True)
        self.task7_num_label.setHidden(True)
        self.task1_count_label.setHidden(True)
        self.task2_count_label.setHidden(True)
        self.task3_count_label.setHidden(True)
        self.task4_count_label.setHidden(True)
        self.task5_count_label.setHidden(True)
        self.task6_count_label.setHidden(True)
        self.task7_count_label.setHidden(True)
        self.players_frame.setHidden(False)
        self.back_btn.setHidden(True)
        self.create_room_btn.setHidden(True)
        self.send_task_btn.setHidden(False)
        self.back_btn2.setHidden(False)
        if self.server_started == 0:
            self.server = Server(self.table_players)
            self.server.socket.bind(('', 1234))
            self.server.socket.listen(3)
            self.server.socket.setblocking(False)
            self.server_thread = Thread(target=self.server.start)
            self.server_thread.start()
            self.server_started = 1

    def choose_file_func(self):
        name = QtWidgets.QFileDialog.getOpenFileName()
        name = name[0]
        n = len(name.split('/'))
        if name.split('/')[n - 1][:3] == 'ip_':
            with open(name, 'r') as fp:
                self.var_file = json.load(fp)
            self.tasks_num()
            self.vars_num_label.setText("Количество вариантов: {}".format(str(len(self.var_file))))
            self.task1_num_label.setText("1.  По заданным IP-адресу узла и маске определить адрес сети")
            self.task2_num_label.setText(
                "2.  По заданным IP-адресу узла и маске подсети определить порядковый номер узла в сети")
            self.task3_num_label.setText("3.  По заданной маске подсети определить возможное количество узлов в сети")
            self.task4_num_label.setText("4.  Определить маску для хоста с адресом")
            self.task5_num_label.setText("5.  Определить маску для проекта")
            self.task6_num_label.setText(
                "6. Разделить сеть на несколько разных подсетей. Найти и записать в каждой подсети ее адреса, "
                "широковещательный адрес, пул разрешенных к выдаче адресов и маску")
            self.task7_num_label.setText(
                "7. Даны несколько подсетей. Просуммировать подсети и найти маску, которая сможет покрыть их, не задевая "
                "при этом соседние подсети")

            self.task1_count_label.setText(str(self.task1_num))
            self.task2_count_label.setText(str(self.task2_num))
            self.task3_count_label.setText(str(self.task3_num))
            self.task4_count_label.setText(str(self.task4_num))
            self.task5_count_label.setText(str(self.task5_num))
            self.task6_count_label.setText(str(self.task6_num))
            self.task7_count_label.setText(str(self.task7_num))

        else:
            QMessageBox().warning(self.centralwidget, "Ошибка!",
                                  " Выберите подходящий файл.\n Его имя должно начинаться с 'ip_'")

    def save_var(self):
        new_var = []
        vars_number = self.spinBox_8.value()
        if self.spinBox_8.value() == 0:
            QMessageBox().warning(self.centralwidget, "Ошибка!", "Введите количество вариантов")
        elif self.spinBox.value() == 0 and self.spinBox_2.value() == 0 and self.spinBox_3.value() == 0 and self.spinBox_4.value() == 0 and self.spinBox_5.value() == 0 and self.spinBox_6.value() == 0 and self.spinBox_7.value() == 0:
            QMessageBox().warning(self.centralwidget, "Ошибка!", "Введите количество заданий")
        else:
            for i in range(0, vars_number):
                new_var.append(self.gen_var())
            name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
            name = name[0] + '.json'
            with open(name, 'w') as fp:
                json.dump(new_var, fp)
            self.mainStackedWidget.setCurrentIndex(0)

    def gen_var(self):
        new_var = {}
        cnt = 1

        if self.spinBox.value != 0:
            task1_number = self.spinBox.value()
            for i in range(0, task1_number):
                new_var[str(cnt)] = task1()
                cnt += 1

        if self.spinBox_2.value != 0:
            task2_number = self.spinBox_2.value()
            for i in range(0, task2_number):
                new_var[str(cnt)] = task2()
                cnt += 1

        if self.spinBox_3.value != 0:
            task3_number = self.spinBox_3.value()
            for i in range(0, task3_number):
                new_var[str(cnt)] = task3()
                cnt += 1

        if self.spinBox_4.value != 0:
            task4_number = self.spinBox_4.value()
            for i in range(0, task4_number):
                new_var[str(cnt)] = task4()
                cnt += 1

        if self.spinBox_5.value != 0:
            task5_number = self.spinBox_5.value()
            for i in range(0, task5_number):
                new_var[str(cnt)] = task5()
                cnt += 1

        if self.spinBox_6.value != 0:
            task6_number = self.spinBox_6.value()
            for i in range(0, task6_number):
                new_var[str(cnt)] = task6()
                cnt += 1

        if self.spinBox_7.value != 0:
            task7_number = self.spinBox_7.value()
            for i in range(0, task7_number):
                new_var[str(cnt)] = task7()
                cnt += 1
        new_var["formula"] = [self.grades[0],self.grades[1],self.grades[2]]

        return new_var

    def save_conf(self):
        if int(self.set_line1.text()) <= int(self.set_line2.text()) or int(self.set_line1.text()) <= int(
                self.set_line3.text()) or int(self.set_line2.text()) <= int(self.set_line3.text()) or int(
            self.set_line1.text()) > 100 or int(self.set_line2.text()) > 100 or int(self.set_line3.text()) > 100:
            QMessageBox().warning(self.centralwidget, "Ошибка!", "Неправильно введена формула")
        else:
            with open('config.json', 'w') as fp:
                json.dump([self.set_line1.text(), self.set_line2.text(), self.set_line3.text()], fp)
            QMessageBox().information(self.centralwidget, "Успешно!", "Настройки сохранены")

    def closeEvent(self, event):
        if self.server_started:
            if self.game_started:
                if self.table_players.done():
                    self.close()
                    self.server.socket.close()
                else:
                    alert = QMessageBox(self.centralwidget)
                    alert.setIcon(QMessageBox.Question)
                    alert.setText("Не все игроки закончили.\nВы уверены что хотите выйти?")
                    alert.setWindowTitle("Внимание!")
                    alert.addButton("Да", QMessageBox.YesRole)
                    alert.addButton("Нет", QMessageBox.RejectRole)
                    ret = alert.exec()
                    if ret == 0:
                        self.close()
                        self.server.socket.close()
                    else:
                        QtCore.QEvent.ignore(event)
                        alert.close()
            else:
                self.close()
                self.server.socket.close()

    def back_func(self):
        self.choose_file_btn.setHidden(False)
        self.num_quest_label.setHidden(False)
        self.vars_num_label.setHidden(False)
        self.task1_num_label.setHidden(False)
        self.task2_num_label.setHidden(False)
        self.task3_num_label.setHidden(False)
        self.task4_num_label.setHidden(False)
        self.task5_num_label.setHidden(False)
        self.task6_num_label.setHidden(False)
        self.task7_num_label.setHidden(False)
        self.task1_count_label.setHidden(False)
        self.task2_count_label.setHidden(False)
        self.task3_count_label.setHidden(False)
        self.task4_count_label.setHidden(False)
        self.task5_count_label.setHidden(False)
        self.task6_count_label.setHidden(False)
        self.task7_count_label.setHidden(False)
        self.players_frame.setHidden(True)
        self.back_btn.setHidden(False)
        self.create_room_btn.setHidden(False)
        self.send_task_btn.setHidden(True)
        self.back_btn2.setHidden(True)

    def send_grades(self):
        with open("config.json", 'r') as fp:
            self.grades = json.load(fp)
        return self.grades

    def tasks_num(self):
        self.task1_num = 0
        self.task2_num = 0
        self.task3_num = 0
        self.task4_num = 0
        self.task5_num = 0
        self.task6_num = 0
        self.task7_num = 0
        for task in self.var_file[0]:
            if self.var_file[0][task][0] == '1':
                self.task1_num += 1
            if self.var_file[0][task][0] == '2':
                self.task2_num += 1
            if self.var_file[0][task][0] == '3':
                self.task3_num += 1
            if self.var_file[0][task][0] == '4':
                self.task4_num += 1
            if self.var_file[0][task][0] == '5':
                self.task5_num += 1
            if self.var_file[0][task][0] == '6':
                self.task6_num += 1
            if self.var_file[0][task][0] == '7':
                self.task7_num += 1


    def __init__(self):
        super(App, self).__init__()
        self.button_style = """QPushButton {
                                                 border: 2px;
                                                 border-radius: 6px;
                                                 background-color: rgb(222, 196, 158);
                                                 min-width: 80px;
                                                padding: 18px 32px;
                                                font: 16pt "Tahoma";
                                             }

                                             QPushButton:hover {
                                                 background-color: rgb(204, 176, 135);
                                             }"""
        self.var_file = []
        self.setup_ui()
        self.table_var_flag = False
        self.shutdown = False



def button_style(font_size=16):
    s = r"""QPushButton {
                             border: 2px;
                             border-radius: 6px;
                             background-color: rgb(120, 165, 163);
                             min-width: 80px;
                            font: """
    s += str(font_size) + """pt "Tahoma";
                         }

                         QPushButton:hover {
                             background-color: rgb(104, 143, 141);
                         }"""
    return s


def frame_style():
    s = """QFrame {
                 border: 2px;
                 border-radius: 12px;
                 background-color: rgb(239, 210, 172);
             }"""

    return s


def text_style():
    s = """background-color: rgb(248, 218, 179); font: 12pt;"""
    return s


def frame_input_style():
    s = """background-color: rgb(239, 210, 172);"""
    return s


def input_style():
    s = """background-color: rgb(248, 218, 179);"""
    return s


app = QtWidgets.QApplication([])
app.setStyle("fusion")
application = App()

application.show()

sys.exit(app.exec_())
