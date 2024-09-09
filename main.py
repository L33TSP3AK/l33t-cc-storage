import sys
from main_ui import Ui_CCStorage
import importfunctions
from importfunctions import pdf_import_function, get_search_method, get_regex_patterns, process_pdfs_default, process_pdfs_regex, add_to_tree_widget
from PyQt5.QtWidgets import QTextEdit, QFileDialog, QTreeWidgetItem, QMenu, QAction, QWidget, QMainWindow, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush
import pandas as pd
from datetime import datetime
import sqlite3
import os
import re
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QSplitter
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal
from main_ui import Ui_CCStorage
import webbrowser
import http.server
import socketserver
import threading
import time
from data.database import *

class LoadingThread(QThread):
    finished = pyqtSignal()

    def run(self):
        # Start the web server in a separate thread
        server_thread = threading.Thread(target=self.run_server)
        server_thread.start()

        # Open the loading animation in the default web browser
        webbrowser.open('http://localhost:8000/loading_animation.html')

        # Simulate some work (replace this with your actual initialization code)
        time.sleep(5)

        # Signal that the loading is finished
        self.finished.emit()

    def run_server(self):
        PORT = 8000
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Serving at port {PORT}")
            httpd.serve_forever()




class ContextMenu(QMenu):
    remove_requested = pyqtSignal(str)
    test_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_actions()

    def setup_actions(self):
        self.remove_action = QAction("Remove", self)
        self.bincheck_action = QAction("BIN Check", self)
        self.test_action = QAction("Submit Test", self)
        
        self.addAction(self.remove_action)
        self.addAction(self.bincheck_action)
        self.addAction(self.test_action)
        
        self.remove_action.triggered.connect(self.on_remove)
        self.bincheck_action.triggered.connect(self.bin_check_function)
        self.test_action.triggered.connect(self.on_test)

    def on_remove(self, item_text):
        root = self.treeWidget.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item.text(0) == item_text:  # Assuming the text is in the first column
                root.removeChild(item)
                break
        self.update_card_counts()



    def on_test(self, item_text):
        # Implement your test logic here
        print(f"Testing item: {item_text}")

    def bin_check_function(self, item_text):
        # Implement your BIN check logic here
        print(f"Performing BIN check for: {item_text}")





class DetailDialog(QDialog):
    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Card Details")
        self.setMinimumSize(600, 400)

        layout = QHBoxLayout()

        # Left side: Detailed information
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel("Card Details"))
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setPlainText("\n".join([f"{key}: {value}" for key, value in item_data.items()]))
        self.info_text.setTextColor(QColor(255, 255, 255))  # Set text color to white
        info_layout.addWidget(self.info_text)

        button_layout = QHBoxLayout()
        self.copy_button = QPushButton("Copy")
        self.close_button = QPushButton("Close")
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.close_button)
        info_layout.addLayout(button_layout)

        # Right side: Test area
        test_layout = QVBoxLayout()
        test_layout.addWidget(QLabel("Test Area"))
        self.test_input = QTextEdit()
        self.test_result = QTextEdit()
        self.test_result.setReadOnly(True)
        self.test_result.setTextColor(QColor(255, 255, 255))  # Set test result text color to white
        self.test_button = QPushButton("Test")
        test_layout.addWidget(self.test_input)
        test_layout.addWidget(self.test_button)
        test_layout.addWidget(self.test_result)

        # Add both sides to a splitter
        splitter = QSplitter(Qt.Horizontal)
        left_widget = QWidget()
        left_widget.setLayout(info_layout)
        right_widget = QWidget()
        right_widget.setLayout(test_layout)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

        # Connect buttons
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.close_button.clicked.connect(self.close)
        self.test_button.clicked.connect(self.run_test)

    def copy_to_clipboard(self):
        QApplication.clipboard().setText(self.info_text.toPlainText())

    def run_test(self):
        test_input = self.test_input.toPlainText()
        # Implement your test logic here
        self.test_result.setPlainText(f"Test result: {test_input}")



class CardCounter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Assume these LCDNumber widgets are already set up in your UI
        self.discover_lcdNumber = self.findChild(QLCDNumber, 'discover_lcdNumber')
        self.master_lcdNumber = self.findChild(QLCDNumber, 'master_lcdNumber')
        self.visa_lcdNumber = self.findChild(QLCDNumber, 'visa_lcdNumber')
        self.total_lcdNumber = self.findChild(QLCDNumber, 'total_lcdNumber')

    def count_cards(self):
        # Get the current counts from the LCD displays
        discover_count = int(self.discover_lcdNumber.value())
        master_count = int(self.master_lcdNumber.value())
        visa_count = int(self.visa_lcdNumber.value())

        # Calculate the total
        total_count = discover_count + master_count + visa_count

        # Update the total LCD display
        self.total_lcdNumber.display(total_count)

        # Print the results to the console
        print(f"Discover Cards: {discover_count}")
        print(f"Mastercard Cards: {master_count}")
        print(f"Visa Cards: {visa_count}")
        print(f"Total Cards: {total_count}")






class MainWindow(QMainWindow, Ui_CCStorage):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.import_data_button.clicked.connect(self.import_data_function)
        self.bin_check_button.clicked.connect(self.bin_check_function)
        self.pdf_import_button.clicked.connect(self.pdf_import_function)
        self.console_text.setReadOnly(True)
        self.import_data_button.clicked.connect(self.import_data_function)
        self.bin_check_button.clicked.connect(self.bin_check_function)
        self.pdf_import_button.clicked.connect(self.pdf_import_function)
        self.console_text.setReadOnly(True)
        self.apply_context_menu()
        self.treeWidget.itemDoubleClicked.connect(self.show_detail_dialog)

        # Connect a button to update the counts
        self.update_counts_button.clicked.connect(self.update_card_counts)
        self.setup_context_menu()

    def setup_context_menu(self):
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        context_menu = ContextMenu(self.treeWidget)
        context_menu.remove_requested.connect(self.remove_item)
        context_menu.test_requested.connect(self.test_item)
        context_menu.exec_(self.treeWidget.mapToGlobal(position))


    
    def apply_context_menu(self):
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.show_context_menu)

    
    def remove_item(self, item_text):
        # Implement item removal logic
        print(f"Removing item: {item_text}")




    def test_item(self, item_text):
        # Implement your test logic here
        print(f"Testing item: {item_text}")

    def show_detail_dialog(self, item, column):
        # Collect data from all columns
        item_data = {}
        for col in range(self.treeWidget.columnCount()):
            header = self.treeWidget.headerItem().text(col)
            value = item.text(col)
            item_data[header] = value

        # Create and show the detail dialog
        dialog = DetailDialog(item_data, self)
        dialog.exec_()
    
    
    def update_card_counts(self):
        # This method should be called whenever you want to update the counts
        discover_count = 0
        master_count = 0
        visa_count = 0
        amex_count = 0
    
        # Iterate through your data (e.g., treeWidget items) and count each card type
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            card_number = item.text(1)  # Assuming the card number is in the second column
            if card_number.startswith('6'):
                discover_count += 1
            elif card_number.startswith('5'):
                master_count += 1
            elif card_number.startswith('4'):
                visa_count += 1
            elif card_number.startswith('3'):
                amex_count += 1
    
        # Update the LCD displays
        self.discover_lcdNumber.display(discover_count)
        self.master_lcdNumber.display(master_count)
        self.visa_lcdNumber.display(visa_count)
        self.amex_lcdNumber.display(amex_count)  # Make sure you have an amex_lcdNumber in your UI
    
        # Calculate and display the total
        total_count = discover_count + master_count + visa_count + amex_count
        self.total_lcdNumber.display(total_count)
    
        # Print the results to the console
        print(f"Discover Cards: {discover_count}")
        print(f"Mastercard Cards: {master_count}")
        print(f"Visa Cards: {visa_count}")
        print(f"Amex Cards: {amex_count}")
        print(f"Total Cards: {total_count}")
    
    def import_data_function(self):
        # Ask user to select a folder
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder Containing Text Files")
        if not folder_path:
            self.console_text.append("Import cancelled.")
            return
    
        self.console_text.append(f"Selected folder: {folder_path}")
    
        # Regular expressions for extracting card details
        patterns = {
            'CC': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'MM/YY': r'\b(0[1-9]|1[0-2])/\d{2}\b',
            'CVV': r'\b\d{3,4}\b',
            'NAME': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
            'ADDRESS': r'\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)',
            'CITY': r'\b[A-Z][a-z]+(?:[\s-][A-Z][a-z]+)*\b',
            'STATE': r'\b[A-Z]{2}\b',
            'ZIP': r'\b\d{5}(?:-\d{4})?\b',
            'COUNTRY': r'\b(?:USA|United States|Canada)\b',
            'I.P': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'UA': r'Mozilla/5.0.*'
        }
    
        data = []
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(folder_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                except UnicodeDecodeError:
                    try:
                        # If UTF-8 fails, try with ISO-8859-1
                        with open(file_path, 'r', encoding='iso-8859-1') as file:
                            content = file.read()
                    except UnicodeDecodeError:
                        # If both fail, skip this file and log an error
                        self.console_text.append(f"Error reading file {filename}. Skipping.")
                        continue
    
                card_data = {'Date Imported': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                for key, pattern in patterns.items():
                    match = re.search(pattern, content)
                    card_data[key] = match.group() if match else ''
                
                card_data['SOURCED'] = filename
                data.append(card_data)
    
        # Create DataFrame
        df = pd.DataFrame(data)
    
        # Add data to treeWidget
        self.treeWidget.clear()
        bright_green = QColor(0, 255, 0)  # RGB for bright green
        for _, row in df.iterrows():
            item = QTreeWidgetItem(self.treeWidget)
            for col, value in enumerate(row):
                item.setText(col, str(value))
                item.setForeground(col, QBrush(bright_green))
    
        self.console_text.append(f"Imported {len(data)} card details.")
        
        return df
    
    # In your MainWindow class:
    def import_data(self):
        df = import_data_function(self)
        if df is not None:
            self.console_text.append(f"<font color='red'>Data preview:</font>")
            self.console_text.append(f"<font color='red'>{df.head().to_string()}</font>")



    def bin_check_function(self):
        bin_check_function(self)

    def pdf_import_function(self):
        pdf_import_function(self)

    # Add these methods to your MainWindow class
    get_search_method = get_search_method
    get_regex_patterns = get_regex_patterns
    process_pdfs_default = process_pdfs_default
    process_pdfs_regex = process_pdfs_regex
    add_to_tree_widget = add_to_tree_widget




















if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())