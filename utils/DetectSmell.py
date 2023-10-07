import logging
import os
import subprocess
import sys
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFileDialog, QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
                             QSplitter, QHeaderView, QTabWidget, QTextEdit)
from PyQt6.QtCore import Qt

from utils.client import find_api, detect_smells
from utils.metric import smell_alias
from utils.smell_verification import code_smell_results_files


def get_smell_files(frame_name,file_name):
    csv_files={}
    for i in range(8):
        path=os.path.join('detection_results',frame_name,file_name,code_smell_results_files[i])
        csv_files[path]=smell_alias[i]
    return csv_files


class CombinedApp(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)


        # 创建QTabWidget来容纳多个CSV数据显示
        self.tab_widget = QTabWidget()
        self.splitter.addWidget(self.tab_widget)

        self.right_layout = QVBoxLayout()

        self.folder_list = QListWidget(self)
        self.folder_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.right_layout.addWidget(self.folder_list)


        # 创建并排的添加和删除按钮
        self.button_layout = QHBoxLayout()

        self.add_button = QPushButton('Add', self)
        self.add_button.clicked.connect(self.add_folders)
        self.button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton('Delete', self)
        self.delete_button.clicked.connect(self.delete_folders)
        self.button_layout.addWidget(self.delete_button)

        self.right_layout.addLayout(self.button_layout)
        # 在日志框上面添加两个并排的按钮
        self.run_button_layout = QHBoxLayout()

        self.run1_button = QPushButton('FindAPI', self)

        self.run1_button.clicked.connect(self.execute_program1)
        self.run_button_layout.addWidget(self.run1_button)

        self.run2_button = QPushButton('DetectSmell', self)
        self.run2_button.clicked.connect(self.execute_program2)
        self.run_button_layout.addWidget(self.run2_button)

        # 将新的按钮布局加到右边的布局中
        self.right_layout.addLayout(self.run_button_layout)
        # 配置日志记录
        self.setup_logging("app_log.log")

        # 在按钮下方添加日志显示框
        self.log_display = QTextEdit(self)
        self.log_display.setReadOnly(True)  # 设置为只读，用户不能在里面输入内容

        self.right_layout.addWidget(self.log_display)

        # 重定向标准输出
        sys.stdout.write = self.append_log
        sys.stderr.write = self.append_log

        self.right_widget = QWidget()
        self.right_widget.setLayout(self.right_layout)
        self.splitter.addWidget(self.right_widget)

        self.layout.addWidget(self.splitter)
        self.setLayout(self.layout)

        self.resize(900, 600)  # 假设初始大小为 900x600，您可以根据需要进行调整

    def setup_logging(self, log_file_path):
        logging.basicConfig(filename=log_file_path, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("Application started")

    def load_csv_data(self, file_path):
        df = pd.read_csv(file_path)

        csv_display = QTableWidget(0, len(df.columns))
        csv_display.setHorizontalHeaderLabels(df.columns)

        header: QHeaderView = csv_display.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        csv_display.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        csv_display.setRowCount(0)

        for index, row in df.iterrows():
            row_num = csv_display.rowCount()
            csv_display.insertRow(row_num)
            for col_num, col_name in enumerate(df.columns):
                csv_display.setItem(row_num, col_num, QTableWidgetItem(str(row[col_name])))

        return csv_display

    def load_multiple_csv_files(self, group_name, csv_files):

        nested_tab_widget = QTabWidget()

        for file_path, custom_label in csv_files.items():
            csv_display = self.load_csv_data(file_path)
            nested_tab_widget.addTab(csv_display, custom_label)

        self.tab_widget.addTab(nested_tab_widget, group_name)

    def add_folders(self):
        while True:
            folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
            if not folder:
                break
            self.folder_list.addItem(QListWidgetItem(folder))
        logging.info("Folders added")

    def delete_folders(self):
        selected_items = self.folder_list.selectedItems()
        for item in selected_items:
            self.folder_list.takeItem(self.folder_list.row(item))
        logging.warning("Folders deleted")

    def get_folders(self):
        input_files=[]
        for index in range(self.folder_list.count()):
            input_files.append(self.folder_list.item(index).text())
        return input_files

    def append_log(self, text):
        self.log_display.append(text)  # 在 QTextEdit 中追加内容
        QApplication.processEvents()  # 使应用程序处理所有挂起的事件

    def resizeEvent(self, event):
        # 获取当前窗口的宽度
        total_width = self.width()

        # 左边布局占三分之二，右边布局占三分之一
        left_width = int(total_width * 2 / 3)
        right_width = total_width - left_width

        # 更新 QSplitter 的大小
        self.splitter.setSizes([left_width, right_width])

        super().resizeEvent(event)

    def execute_program1(self):
        input_files=self.get_folders()
        for i in range(len(input_files)):
            path = input_files[i]
            print(path)
            file_name = path[path.rfind("/") + 1:]
            if '-' not in file_name:
                frame_name = file_name
            else:
                frame_name = file_name[:file_name.find('-')]

            try:
                print('Looking for api...')
                find_api(path,frame_name, file_name)
                print('Run successfully')
            except subprocess.CalledProcessError as e:
                # 如果有错误，显示在日志框中
                self.log_display(f"Error in Program1: {e}")
            except FileNotFoundError:
                print("File not found!")
            except PermissionError:
                print("You don't have permission to access the file!")


    def execute_program2(self):
        input_files = self.get_folders()
        for i in range(len(input_files)):

            path = input_files[i]
            file_name = path[path.rfind("/") + 1:]
            if '-' not in file_name:
                frame_name = file_name
            else:
                frame_name = file_name[:file_name.find('-')]
            try:
                print('Detecting Smell...')
                detect_smells(frame_name, file_name)
                print('Detection completed')
            except subprocess.CalledProcessError as e:
                 # 如果有错误，显示在日志框中
                self.log_display(f"Error in Program1: {e}")
            except FileNotFoundError:
                print("File not found!")
            except PermissionError:
                print("You don't have permission to access the file!")
        # 在初始化中加载多个CSV文件

        csv_files=get_smell_files(frame_name,file_name)
        self.load_multiple_csv_files(file_name,csv_files)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CombinedApp()
    window.show()
    sys.exit(app.exec())
