import logging
import os
import subprocess
import sys
import threading

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

from PyQt6.QtCore import QObject, pyqtSignal, QThread

class findapi(QObject):
    finishedSignal = pyqtSignal()  # 你可以定义更多的信号，例如传递进度信息等
    errorSignal = pyqtSignal(str)  # 用于发送错误消息到主线程

    def __init__(self, input_files,log_display):
        super().__init__()
        self.input_files = input_files
        self.log_display=log_display


    def doWork(self):
        for i in range(len(self.input_files)):
            path = self.input_files[i]
            file_name = path[path.rfind("/") + 1:]
            if '-' not in file_name:
                frame_name = file_name
            else:
                frame_name = file_name[:file_name.find('-')]

            try:
                print('Looking for api...')
                find_api(path, frame_name, file_name)
                print('Run successfully')
            except subprocess.CalledProcessError as e:
                self.errorSignal.emit(f"Error in Program1: {e}")
            except FileNotFoundError:
                self.errorSignal.emit("File not found!")
            except PermissionError:
                self.errorSignal.emit("You don't have permission to access the file!")
        self.finishedSignal.emit()


class detectsmell(QObject):
    finishedSignal = pyqtSignal()  # 你可以定义更多的信号，例如传递进度信息等
    updateSignal = pyqtSignal(str,dict)  # 假设你想传递一个字符串来更新UI
    errorSignal = pyqtSignal(str)  # 用于发送错误消息到主线程

    def __init__(self, input_files,log_display):
        super().__init__()
        self.input_files = input_files
        self.log_display=log_display
    def doWork(self):

        for i in range(len(self.input_files)):

            path = self.input_files[i]
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
                self.errorSignal.emit(f"Error in Program1: {e}")
            except FileNotFoundError:
                self.errorSignal.emit("File not found!")
            except PermissionError:
                self.errorSignal.emit("You don't have permission to access the file!")
            csv_files = get_smell_files(frame_name, file_name)
            self.updateSignal.emit(file_name, csv_files)
            # 在初始化中加载多个CSV文件
        self.finishedSignal.emit()


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

        self.run1_button.clicked.connect(self.startRunningFindAPI)
        self.run_button_layout.addWidget(self.run1_button)

        self.run2_button = QPushButton('DetectSmell', self)
        self.run2_button.clicked.connect(self.startRunningDetectSmell)
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

    def startRunningFindAPI(self):
        try:
            self.worker1 = findapi(self.get_folders(), self.log_display)
            self.thread1 = QThread()
            self.worker1.moveToThread(self.thread1)
            self.thread1.started.connect(self.worker1.doWork)
            # 连接工作线程的信号到主线程的槽函数
            self.worker1.errorSignal.connect(self.handleFindAPIError)

            self.worker1.finishedSignal.connect(self.onFindAPIFinished)  # 可以连接到一个槽函数以处理任务完成后的操作

            self.worker1.finishedSignal.connect(self.thread1.quit)
            self.worker1.finishedSignal.connect(self.worker1.deleteLater)
            self.thread1.finished.connect(self.thread1.deleteLater)
            self.thread1.start()

        except Exception as e:
            error_message = f"Error starting FindAPI thread: {e}"

            logging.error(error_message)

            self.log_display.append(error_message)

    def onFindAPIFinished(self):
        # 当耗时任务完成后执行的代码
        print("Finding Finished!")

    def startRunningDetectSmell(self):
        try:
            self.worker2 = detectsmell(self.get_folders(), self.log_display)
            self.thread2 = QThread()
            self.worker2.moveToThread(self.thread2)
            self.thread2.started.connect(self.worker2.doWork)
            self.worker2.errorSignal.connect(self.handleDetectSmellError)
            self.worker2.updateSignal.connect(self.updateUI)  # 连接更新UI的槽函数
            self.worker2.finishedSignal.connect(self.onDetectSmellFinished)  # 可以连接到一个槽函数以处理任务完成后的操作
            self.worker2.finishedSignal.connect(self.thread2.quit)
            self.worker2.finishedSignal.connect(self.worker2.deleteLater)
            self.thread2.finished.connect(self.thread2.deleteLater)

            self.thread2.start()
        except Exception as e:
            error_message = f"Error starting DetectSmell thread: {e}"

            logging.error(error_message)

            self.log_display.append(error_message)

    def updateUI(self,file_name, csv_files):
        self.load_multiple_csv_files(file_name, csv_files)
    def onDetectSmellFinished(self):
        # 当耗时任务完成后执行的代码
        print("Detection Finished!")

    def handleFindAPIError(self, message):
        """Handle errors from the findapi worker."""
        self.log_display.append(f"FindAPI Error: {message}")

    def handleDetectSmellError(self, message):
        """Handle errors from the detectsmell worker."""
        self.log_display.append(f"DetectSmell Error: {message}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CombinedApp()
    window.show()
    sys.exit(app.exec())
