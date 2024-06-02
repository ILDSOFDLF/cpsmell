import logging
import os
import subprocess
import sys
import threading

import pandas as pd
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFileDialog, QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
                             QSplitter, QHeaderView, QTabWidget, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt

from utils.client import find_api
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
    finishedSignal = pyqtSignal()
    errorSignal = pyqtSignal(str)

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
                print('Find language interface...')
                find_api(path, frame_name, file_name)
                print('Run successfully')
            except subprocess.CalledProcessError as e:
                self.errorSignal.emit(f"Error in Program1: {e}")
            except FileNotFoundError:
                self.errorSignal.emit("The file could not be found!")
            except PermissionError:
                self.errorSignal.emit("No permission to access the file!")
        self.finishedSignal.emit()


class detectsmell(QObject):
    finishedSignal = pyqtSignal()
    updateSignal = pyqtSignal(str,dict)
    errorSignal = pyqtSignal(str)

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
                print('Detect smell...')
                # detect_smells(frame_name, file_name)
                print('Detect is completed')
            except subprocess.CalledProcessError as e:
                # 如果有错误，显示在日志框中
                self.errorSignal.emit(f"Error in Program1: {e}")
            except FileNotFoundError:
                self.errorSignal.emit("The file cannot be found!")
            except PermissionError:
                self.errorSignal.emit("No permission to access the file!")
            csv_files = get_smell_files(frame_name, file_name)
            self.updateSignal.emit(file_name, csv_files)

        self.finishedSignal.emit()


class CombinedApp(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setWindowTitle("CPsmell")

        self.tab_widget = QTabWidget()
        self.splitter.addWidget(self.tab_widget)

        self.right_layout = QVBoxLayout()

        self.folder_list = QListWidget(self)
        self.folder_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.right_layout.addWidget(self.folder_list)

        self.button_layout = QHBoxLayout()

        self.add_button = QPushButton('Add Files', self)
        self.add_button.clicked.connect(self.add_folders)
        self.button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton('Delete Files', self)
        self.delete_button.clicked.connect(self.delete_folders)
        self.button_layout.addWidget(self.delete_button)

        self.right_layout.addLayout(self.button_layout)

        self.run_button_layout = QHBoxLayout()

        self.run1_button = QPushButton('Find Language Interface', self)

        self.run1_button.clicked.connect(self.startRunningFindAPI)
        self.run_button_layout.addWidget(self.run1_button)

        self.run2_button = QPushButton('Detect Smell', self)
        self.run2_button.clicked.connect(self.startRunningDetectSmell)
        self.run_button_layout.addWidget(self.run2_button)

        self.right_layout.addLayout(self.run_button_layout)

        self.setup_logging("app_log.log")

        self.log_display = QTextEdit(self)
        self.log_display.setReadOnly(True)

        self.right_layout.addWidget(self.log_display)

        sys.stdout.write = self.append_log
        sys.stderr.write = self.append_log

        self.right_widget = QWidget()
        self.right_widget.setLayout(self.right_layout)
        self.splitter.addWidget(self.right_widget)

        self.layout.addWidget(self.splitter)
        self.setLayout(self.layout)

        self.resize(900, 600)

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
            folder = QFileDialog.getExistingDirectory(self, "Select the folder")
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
        self.log_display.append(text)
        QApplication.processEvents()

    def resizeEvent(self, event):

        total_width = self.width()
        left_width = int(total_width * 2 / 3)
        right_width = total_width - left_width

        self.splitter.setSizes([left_width, right_width])

        super().resizeEvent(event)

    def startRunningFindAPI(self):
        try:
            self.worker1 = findapi(self.get_folders(), self.log_display)
            self.thread1 = QThread()
            self.worker1.moveToThread(self.thread1)
            self.thread1.started.connect(self.worker1.doWork)

            self.worker1.errorSignal.connect(self.handleFindAPIError)

            self.worker1.finishedSignal.connect(self.onFindAPIFinished)

            self.worker1.finishedSignal.connect(self.showCompletionMessage)

            self.worker1.finishedSignal.connect(self.thread1.quit)
            self.worker1.finishedSignal.connect(self.worker1.deleteLater)
            self.thread1.finished.connect(self.thread1.deleteLater)
            self.thread1.start()

        except Exception as e:
            error_message = f"Error starting FindAPI thread: {e}"

            logging.error(error_message)

            self.log_display.append(error_message)

    def onFindAPIFinished(self):
        print("Execution success!")

    def startRunningDetectSmell(self):
        try:
            self.worker2 = detectsmell(self.get_folders(), self.log_display)
            self.thread2 = QThread()
            self.worker2.moveToThread(self.thread2)
            self.thread2.started.connect(self.worker2.doWork)
            self.worker2.errorSignal.connect(self.handleDetectSmellError)
            self.worker2.updateSignal.connect(self.updateUI)
            self.worker2.finishedSignal.connect(self.onDetectSmellFinished)
            self.worker2.finishedSignal.connect(self.thread2.quit)
            self.worker2.finishedSignal.connect(self.worker2.deleteLater)
            self.thread2.finished.connect(self.thread2.deleteLater)

            self.thread2.start()
        except Exception as e:
            error_message = f"Error starting DetectSmell thread: {e}"

            logging.error(error_message)

            self.log_display.append(error_message)

    def showCompletionMessage(self):
        # Display a completion message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Find language interface")
        msg_box.setText("Find Language Interface is successful！")
        msg_box.exec()

    def updateUI(self,file_name, csv_files):
        self.load_multiple_csv_files(file_name, csv_files)
    def onDetectSmellFinished(self):
        print("Detect successfully!")

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
