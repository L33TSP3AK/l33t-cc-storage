import sys, os, re, time, threading
from datetime import datetime
import pandas as pd
import webbrowser
import http.server
import socketserver
from translate import Translator
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog, QFileDialog, 
    QTextEdit, QTreeWidgetItem, QMenu, QAction, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QSplitter, QShortcut
)
from PyQt5.QtCore import Qt, QPoint, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QBrush, QKeySequence

from main_ui import Ui_CCStorage
import importfunctions
from importfunctions import (
    pdf_import_function, get_search_method, get_regex_patterns, 
    process_pdfs_default, process_pdfs_regex, add_to_tree_widget
)
from translate import Translator





class ContextMenu(QMenu):
    def __init__(self, parent=None, tree_widget=None, main_window=None):
        super().__init__(parent)
        self.tree_widget = tree_widget
        self.main_window = main_window
        
        # Set the background color to white
        self.setStyleSheet("QMenu { background-color: white; border: 1px solid #ccc; }"
                           "QMenu::item { padding: 5px 20px; }"
                           "QMenu::item:selected { background-color: #e0e0e0; }")

        self.setup_actions()
        self.translate_action = self.addAction("Translate")
        self.translate_action.triggered.connect(self.on_translate)


    def setup_actions(self):
        self.remove_action = self.addAction("Remove")
        self.copy_action = self.addAction("Copy Values")
        self.bincheck_action = self.addAction("BIN Check")
        
        # Connect actions to their respective methods
        self.remove_action.triggered.connect(self.on_remove)
        self.copy_action.triggered.connect(self.copy_values)
        self.bincheck_action.triggered.connect(self.on_bin_check)

    def on_remove(self):
        if self.tree_widget:
            root = self.tree_widget.invisibleRootItem()
            for item in self.tree_widget.selectedItems():
                (item.parent() or root).removeChild(item)
        else:
            print("Error: TreeWidget not set")

    def copy_values(self):
        if self.tree_widget:
            selected_items = self.tree_widget.selectedItems()
            if selected_items:
                values = [item.text(0) for item in selected_items]  # Assuming the value is in the first column
                QApplication.clipboard().setText("\n".join(values))
        else:
            print("Error: TreeWidget not set")

    def on_bin_check(self):
        if self.main_window:
            selected_items = self.tree_widget.selectedItems()
            if selected_items:
                bin_number = selected_items[0].text(0)[:6]  # Assuming BIN is first 6 digits of the first column
                self.main_window.perform_bin_check(bin_number)
        else:
            print("Error: Main window not set")


    def on_translate(self):
        if self.main_window:
            self.main_window.translate_selected_items()
        else:
            print("Error: Main window not set")






class DetailDialog(QDialog):
    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Card Details")
        self.setMinimumSize(600, 400)

        layout = QHBoxLayout()
        # Set the background color to white and apply styling
        self.setStyleSheet("""
            QDialog, QTextEdit, QWidget {
                background-color: white;
            }
            QDialog {
                border: 1px solid #ccc;
            }
            QLabel {
                font-weight: bold;
                margin-bottom: 5px;
            }
            QTextEdit {
                border: 1px solid #ddd;
                padding: 5px;
            }
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)

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
        
        # Initialize flags
        self.cc_api_obfuscating = False
        self.an_rn_api_obfuscating = False

        # Connect buttons
        self.import_data_button.clicked.connect(self.import_data_function)
        self.bin_check_button.clicked.connect(self.bin_check_function)
        self.pdf_import_button.clicked.connect(self.pdf_import_function)
        self.update_counts_button.clicked.connect(self.update_card_counts)

        # Set up console
        self.console_text.setReadOnly(True)
        self.setup_shortcuts()
        # Set up tree widget
        self.setup_tree_widget()

        # Set up API key text edits
        self.setup_api_key_edits()

    def show_context_menu(self, position):
        context_menu = ContextMenu(self, self.treeWidget, self)

    def setup_shortcuts(self):
        translate_shortcut = QShortcut(QKeySequence("Ctrl+Shift+T"), self)
        translate_shortcut.activated.connect(self.translate_selected_items)


    def translate_selected_items(self):
        selected_items = self.treeWidget.selectedItems()
        if not selected_items:
            self.console_text.append("No items selected for translation.")
            return
    
        target_lang = self.get_target_language()
        if not target_lang:
            return
    
        translator = Translator(to_lang=target_lang)
    
        for item in selected_items:
            for column in range(self.treeWidget.columnCount()):
                original_text = item.text(column)
                try:
                    translated_text = translator.translate(original_text)
                    item.setText(column, translated_text)
                except Exception as e:
                    self.console_text.append(f"Translation error: {str(e)}")
    
        self.console_text.append(f"Translation to {target_lang} completed.")
    
    def get_target_language(self):
        languages = {
            'fr': 'French',
            'es': 'Spanish',
            'de': 'German',
            'it': 'Italian',
            'zh': 'Chinese',
            'ja': 'Japanese'
        }
    
        target_lang, ok = QInputDialog.getItem(self, "Select Language", 
                                            "Choose target language:", 
                                            list(languages.values()), 0, False)
        if ok and target_lang:
            return list(languages.keys())[list(languages.values()).index(target_lang)]
        return None
    
    def setup_tree_widget(self):
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.show_context_menu)
        self.treeWidget.itemDoubleClicked.connect(self.show_detail_dialog)

    def setup_api_key_edits(self):
        self.cc_api_textEdit.focusOutEvent = self.cc_api_focus_out
        self.an_rn_api_textEdit.focusOutEvent = self.an_rn_api_focus_out

    def show_context_menu(self, position):
        context_menu = ContextMenu(self, self.treeWidget, self)
        
        # Adjust the position to ensure the menu is fully visible
        global_pos = self.treeWidget.viewport().mapToGlobal(position)
        screen_rect = QApplication.desktop().screenNumber(self)
        screen = QApplication.desktop().screenGeometry(screen_rect)

        menu_rect = context_menu.sizeHint()
        x = global_pos.x()
        y = global_pos.y()

        if x + menu_rect.width() > screen.right():
            x = screen.right() - menu_rect.width()
        if y + menu_rect.height() > screen.bottom():
            y = screen.bottom() - menu_rect.height()

        # Show the menu at the adjusted position
        context_menu.exec_(QPoint(x, y))

    def perform_bin_check(self, bin_number):
        # Set the BIN number in the text edit
        self.bin_check_textedit.setPlainText(bin_number)
        # Call the bin check function
        self.bin_check_function()


    def remove_item(self, item_text):
        # Implement item removal logic
        print(f"Removing item: {item_text}")

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
            'Card Number': r'Card Number:\s*(\d{16})|^(\d{16})',
            'Expiration Date': r'Expiration Date:\s*(\d{5})|(?:^|\|)(\d{5})(?:\||$)',
            'CVV': r'CVV2.*?:\s*(\d{3})|(?:^|\|)(\d{3})(?:\||$)',
            'First Name': r'First Name:\s*(\w+)|(?:^|\|)(\w+)(?:\||$)',
            'Last Name': r'Last Name:\s*(\w+)|(?:^|\|)(\w+)(?:\||$)',
            'Address': r'Address:\s*(.*?)(?:,|\n)|(?:^|\|)([\w\s]+)(?:\||$)',
            'City': r'City:\s*(\w+)|(?:^|\|)(\w+)(?:\||$)',
            'State': r'State:\s*([A-Z]{2})|(?:^|\|)([A-Z]{2})(?:\||$)',
            'Zip Code': r'Zip Code:\s*(\d{5})|(?:^|\|)(\d{5})(?:\||$)',
            'Email': r'Email:\s*(\S+@\S+)|(?:^|\|)(\S+@\S+)(?:\||$)',
            'Date of Birth': r'Date of Birth:\s*(\d{2}/\d{2}/\d{2,4})|(?:^|\|)(\d{2}/\d{2}/\d{2,4})(?:\||$)',
            'Social Security Number': r'Social Security Number:\s*(\d{9})|(?:^|\|)(\d{9})(?:\||$)'
        }
    
        # Words to ignore
        ignore_words = ['VISA', 'MASTERCARD', 'AMEX', 'DISCOVER']
    
        data = []
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt') or filename.endswith('.pdf'):
                file_path = os.path.join(folder_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='iso-8859-1') as file:
                            content = file.read()
                    except UnicodeDecodeError:
                        self.console_text.append(f"Error reading file {filename}. Skipping.")
                        continue
    
                # Preprocess content to remove ignored words
                for word in ignore_words:
                    content = re.sub(r'\b' + word + r'\b', '', content, flags=re.IGNORECASE)
    
                card_data = {'Date Imported': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
                for key, pattern in patterns.items():
                    match = re.search(pattern, content)
                    if match:
                        # Use the first non-None group
                        value = next((g for g in match.groups() if g is not None), '')
                        card_data[key] = value.strip()
    
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
    
    def obfuscate_key(self, key):
        """Helper function to obfuscate the API key"""
        if len(key) <= 4:
            return '*' * len(key)
        return key[:4] + '*' * (len(key) - 4)

    def cc_api_focus_out(self, event):
        """Obfuscate the CC API key when focus is lost"""
        if not self.cc_api_obfuscating:
            self.cc_api_obfuscating = True
            key = self.cc_api_textEdit.toPlainText().strip()
            obfuscated_key = self.obfuscate_key(key)
            self.cc_api_textEdit.setPlainText(obfuscated_key)
            self.cc_api_obfuscating = False
        super(QTextEdit, self.cc_api_textEdit).focusOutEvent(event)

    def an_rn_api_focus_out(self, event):
        """Obfuscate the AN RN API key when focus is lost"""
        if not self.an_rn_api_obfuscating:
            self.an_rn_api_obfuscating = True
            key = self.an_rn_api_textEdit.toPlainText().strip()
            obfuscated_key = self.obfuscate_key(key)
            self.an_rn_api_textEdit.setPlainText(obfuscated_key)
            self.an_rn_api_obfuscating = False
        super(QTextEdit, self.an_rn_api_textEdit).focusOutEvent(event)








    def import_data(self):
        df = import_data_function(self)
        if df is not None:
            self.console_text.append(f"<font color='red'>Data preview:</font>")
            self.console_text.append(f"<font color='red'>{df.head().to_string()}</font>")

    
    def bin_check_function(self):
        import requests
        import json
        import html
    
        # Get the API key from cc_api_textEdit
        api_key = self.cc_api_textEdit.toPlainText().strip()
    
        # Get the BIN from bin_check_textedit, taking only the first 6 digits
        full_input = self.bin_check_textedit.toPlainText().strip()
        bin = ''.join(filter(str.isdigit, full_input))[:6]  # Extract digits and take first 6
    
        # API endpoint URL
        url = "https://zylalabs.com/api/3039/credit+card+validation+check+api/3211/card+authentication"
    
        # Query parameters
        params = {
            "bin": bin
        }
    
        # Headers
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
    
        def format_response(response_data):
            """Helper function to format the response in the desired structure"""
            data = response_data.get('data', {})
            formatted_response = f"         BIN: \"{data.get('bin_iin', '')}\",\n"
            formatted_response += f"        Card Brand: \"{data.get('card_brand', '')}\",\n"
            formatted_response += f"        Card Type: \"{data.get('card_type', '')}\",\n"
            formatted_response += f"        Card Level: \"{data.get('card_level', '')}\",\n"
            formatted_response += f"        Branch Name: \"{data.get('issuer_name_bank', '')}\",\n"
            formatted_response += f"        Bank Website: \"{data.get('issuer_bank_website', '')}\",\n"
            formatted_response += f"        Bank Phone: \"{data.get('issuer_bank_phone', '')}\",\n"
            formatted_response += f"        Country Name: \"{data.get('iso_country_name', '')}\",\n"
            formatted_response += f"        Country Code: \"{data.get('iso_country_code', '')}\"\n\n"
            f"        API Key Used: \"{obfuscated_key}\"\n",  # Display obfuscated key

            # Add the footer
            formatted_response += "------ Thanks for Using L33T CC Storage Utility -------\n"
            formatted_response += "                 -------- @L33TSP3AK1337 -----------\n"
    
            # Escape HTML for safe display
            html_response = f'<pre style="color: #FF0000; font-family: monospace;">{html.escape(formatted_response)}</pre>'
            return html_response



        def set_red_text(text):
            """Helper function to set text in bright red color"""
            html_text = f'<span style="color: #FF0000;">{html.escape(text)}</span>'
            self.bin_check_console.setHtml(html_text)
    
        try:
            # Validate API key
            if not api_key:
                raise ValueError("API key is missing. Please enter a valid API key.")
    
            # Validate BIN input
            if len(bin) < 6:
                raise ValueError(f"Invalid BIN. Please enter at least 6 digits. Current input: {bin}")
    
            # Make the GET request
            response = requests.get(url, params=params, headers=headers)
    
            # Check if the request was successful
            response.raise_for_status()
    
            # Parse the JSON response
            json_response = response.json()
    
            # Check if the BIN is valid
            if not json_response.get('isValid', False):
                raise ValueError(f"Invalid BIN: {json_response.get('message', 'Unknown error')}")
    
            # Format and display the response
            formatted_html = format_response(json_response)
            self.bin_check_console.setHtml(formatted_html)
    
        except ValueError as ve:
            # Handle invalid input (API key or BIN)
            set_red_text(f"Error: {str(ve)}")
        except requests.exceptions.RequestException as e:
            # Handle any request errors and display them in the console
            error_message = f"Request Error: {str(e)}"
            set_red_text(error_message)
        except json.JSONDecodeError:
            # Handle JSON parsing errors
            error_message = "Error: Unable to parse the API response"
            set_red_text(error_message)
        except Exception as e:
            # Handle any other unexpected errors
            error_message = f"Unexpected Error: {str(e)}"
            set_red_text(error_message)



    def routing_number_check_function(self):
        import requests
        import json
    
        # Get the API key from cc_api_textEdit
        api_key = self.cc_api_textEdit.text()
    
        # API endpoint URL
        url = "https://zylalabs.com/api/331/routing+number+bank+lookup+api/1875/get+bank+details"
    
        # Query parameters
        params = {
            "routingnumber": "312081089"
        }
    
        # Headers
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
    
        try:
            # Make the GET request
            response = requests.get(url, params=params, headers=headers)
    
            # Check if the request was successful
            response.raise_for_status()
    
            # Parse the JSON response
            json_response = response.json()
    
            # Display the JSON response in the bin_check_console
            formatted_json = json.dumps(json_response, indent=2)
            self.bin_check_console.setPlainText(formatted_json)
    
        except requests.exceptions.RequestException as e:
            # Handle any errors and display them in the console
            error_message = f"Error: {str(e)}"
            self.bin_check_console.setPlainText(error_message)

    def pdf_import_function(self):
        pdf_import_function(self)

    # Add these methods to your MainWindow class
    get_search_method = get_search_method
    get_regex_patterns = get_regex_patterns
    process_pdfs_default = process_pdfs_default
    process_pdfs_regex = process_pdfs_regex
    add_to_tree_widget = add_to_tree_widget





def update_statistics(self):
    stats_text = f"""
    <font color='blue'>PDF Processing Statistics:</font>
    <ul>
    <li>Total PDFs found: {self.total_pdfs}</li>
    <li>PDFs scanned: {self.scanned_pdfs}</li>
    <li>PDFs remaining: {self.remaining_pdfs}</li>
    <li>Results found: {self.results_found}</li>
    <li>PDFs skipped: {self.skipped_pdfs}</li>
    </ul>
    """
    self.textBrowser.setHtml(stats_text)






def update_statistics(self):
    stats_text = f"""
    <font color='blue'>PDF Processing Statistics:</font>
    <ul>
    <li>Total PDFs found: {self.total_pdfs}</li>
    <li>PDFs scanned: {self.scanned_pdfs}</li>
    <li>PDFs remaining: {self.remaining_pdfs}</li>
    <li>Results found: {self.results_found}</li>
    <li>PDFs skipped: {self.skipped_pdfs}</li>
    </ul>
    """
    self.textBrowser.setHtml(stats_text)







if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())