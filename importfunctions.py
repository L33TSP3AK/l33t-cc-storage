import os
import re
import PyPDF2
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QWidget, QListWidgetItem, QListWidget, QRadioButton, QFileDialog, QTextEdit, QSplitter)
from PyQt5.QtGui import QFont, QColor
import PyPDF2
from regex import CREDIT_CARD_PATTERNS, CREDIT_CARD_PATTERNS_TOOLTIPS
from PyQt5.QtWidgets import QTreeWidgetItem, QTreeWidget





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


def pdf_import_function(self):
    # Reset statistics
    self.total_pdfs = 0
    self.scanned_pdfs = 0
    self.remaining_pdfs = 0
    self.results_found = 0
    self.skipped_pdfs = 0

    # Select folder containing PDF files
    folder_path = QFileDialog.getExistingDirectory(self, "Select Folder Containing PDF Files")
    if not folder_path:
        self.console_text.append("<font color='red'>PDF import cancelled.</font>")
        return

    self.console_text.append(f"<font color='red'>Selected folder: {folder_path}</font>")

    # Count total PDFs
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    self.total_pdfs = len(pdf_files)
    self.remaining_pdfs = self.total_pdfs
    self.update_statistics()

    # Ask user for search method
    search_method = self.get_search_method()
    if not search_method:
        self.console_text.append("<font color='red'>Search method selection cancelled.</font>")
        return

    if search_method == "Default":
        self.process_pdfs_default(folder_path)
    else:
        regex_patterns = self.get_regex_patterns()
        if regex_patterns:
            self.process_pdfs_regex(folder_path, regex_patterns)
        else:
            self.console_text.append("<font color='red'>Regex pattern selection cancelled.</font>")

    # Final update of statistics
    self.update_statistics()




def process_pdfs_default(self, folder_path):
    self.console_text.append("<font color='red'>Processing PDFs with default method...</font>")
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            self.console_text.append(f"<font color='red'>Processing: {filename}</font>")
            try:
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    
                    # Process the text and add to tree widget
                    self.add_to_tree_widget(filename, text)
                    
                    self.scanned_pdfs += 1
                    self.remaining_pdfs -= 1
                    self.results_found += 1  # Assuming each processed PDF counts as a result
            except Exception as e:
                self.console_text.append(f"<font color='red'>Error processing {filename}: {str(e)}</font>")
                self.skipped_pdfs += 1
                self.remaining_pdfs -= 1
            
            self.update_statistics()


def process_pdfs_regex(self, folder_path):
    self.console_text.append("<font color='red'>Processing PDFs with regex patterns...</font>")
    
    # Define regex patterns for each field
    patterns = {
        'Account Number': r'\b\d{10,12}\b',  # 10-12 digit number
        'Routing Number': r'\b\d{9}\b',  # 9 digit number
        'Name': r'(?:Mr\.|Mrs\.|Ms\.|Dr\.)\s([A-Z][a-z]+ [A-Z][a-z]+)',
        'Address': r'\d{1,5}\s\w.\s(\b\w*\b\s){1,2}\w*\.',
        'City': r'(?<=\n)([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
        'State': r'\b([A-Z]{2})\b',
        'ZIP': r'\b\d{5}(?:-\d{4})?\b',
        'Country': r'\b(USA|United States|Canada)\b',
        'DOB': r'\b(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/\d{4}\b',
        'SSN': r'\b\d{3}-\d{2}-\d{4}\b'
    }

    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            self.console_text.append(f"<font color='red'>Processing: {filename}</font>")
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                results = {
                    'Date Imported': date.today().strftime("%Y-%m-%d"),
                    'Account Type': 'Unknown',  # You may need to determine this separately
                    'Bank': 'Unknown'  # You may need to determine this separately
                }
                
                for field, pattern in patterns.items():
                    matches = re.findall(pattern, text)
                    if matches:
                        results[field] = matches[0]  # Take the first match
                    else:
                        results[field] = 'N/A'
                
                self.add_to_tree_widget(filename, results)

def add_to_tree_widget(self, filename, data):
    self.console_text.append(f"<font color='red'>Adding data for {filename} to treeWidget_2</font>")
    
    item = QTreeWidgetItem(self.treeWidget_2)
    
    # Set the data in the order specified
    columns = ['Date Imported', 'Account Type', 'Bank', 'Name', 'Account Number', 'Routing Number', 
               'Address', 'City', 'State', 'ZIP', 'Country', 'DOB', 'SSN']
    
    for i, column in enumerate(columns):
        if isinstance(data, dict):
            item.setText(i, str(data.get(column, 'N/A')))
        elif isinstance(data, str):
            # If data is a string (full text), put it in the last column
            if i == len(columns) - 1:
                item.setText(i, data[:100] + '...' if len(data) > 100 else data)
            else:
                item.setText(i, 'N/A')
    
    self.treeWidget_2.addTopLevelItem(item)

def get_search_method(self):
    dialog = QDialog(self)
    dialog.setWindowTitle("Select Search Method")
    layout = QVBoxLayout()

    # Create a red font
    red_font = QFont()
    red_font.setStyleStrategy(QFont.PreferAntialias)

    # Style sheet for red text
    red_style = "color: red;"

    default_radio = QRadioButton("Default")
    regex_radio = QRadioButton("Specify Regex")
    default_radio.setChecked(True)

    # Apply red font and style to radio buttons
    default_radio.setFont(red_font)
    regex_radio.setFont(red_font)
    default_radio.setStyleSheet(red_style)
    regex_radio.setStyleSheet(red_style)

    layout.addWidget(default_radio)
    layout.addWidget(regex_radio)

    ok_button = QPushButton("OK")
    ok_button.clicked.connect(dialog.accept)
    
    # Apply red font and style to OK button
    ok_button.setFont(red_font)
    ok_button.setStyleSheet(red_style)

    layout.addWidget(ok_button)

    dialog.setLayout(layout)

    if dialog.exec_() == QDialog.Accepted:
        if default_radio.isChecked():
            return "Default"
        else:
            return "Regex"
    return None
    
    


def get_regex_patterns(self):
    dialog = QDialog(self)
    dialog.setWindowTitle("Select Regex Patterns")
    main_layout = QHBoxLayout()

    # Left side (Regex selection)
    left_layout = QVBoxLayout()

    # Create fonts and styles
    red_font = QFont()
    red_font.setStyleStrategy(QFont.PreferAntialias)
    red_style = "color: red; font-size: 12px;"
    bright_green_style = "color: #00FF00; font-size: 12px;"  # Brighter green
    yellow_highlight_style = "background-color: #FFFF99;"  # Yellowish highlight

    predefined_patterns = [
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone number
        r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",  # IP address
        r"\b[A-Z]{2}\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b",  # IBAN
        r"\b[A-Z]{2}\d{2}[A-Z]{4}\d{10}\b",  # BIC/SWIFT
    ]

    list_widget = QListWidget()
    for card_type, pattern in CREDIT_CARD_PATTERNS.items():
        item = QListWidgetItem(f"{card_type}: {pattern}")
        item.setData(Qt.UserRole, pattern)
        item.setToolTip(CREDIT_CARD_PATTERNS_TOOLTIPS.get(card_type, "No tooltip available"))
        list_widget.addItem(item)
    list_widget.setSelectionMode(QListWidget.MultiSelection)
    list_widget.setStyleSheet(f"""
        {red_style}
        QListWidget::item:selected {{
            {yellow_highlight_style}
        }}
    """)
    for pattern in predefined_patterns:
        list_widget.addItem(pattern)
    list_widget.setSelectionMode(QListWidget.MultiSelection)
    list_widget.setStyleSheet(f"""
        {red_style}
        QListWidget::item:selected {{
            {yellow_highlight_style}
        }}
    """)

    custom_regex_label = QLabel("Custom Regex:")
    custom_regex_input = QLineEdit()
    custom_regex_input.setStyleSheet(bright_green_style)

    patterns_label = QLabel("Select predefined patterns:")
    patterns_label.setStyleSheet(red_style)

    left_layout.addWidget(patterns_label)
    left_layout.addWidget(list_widget)
    left_layout.addWidget(custom_regex_label)
    left_layout.addWidget(custom_regex_input)

    # Buttons layout
    buttons_layout = QHBoxLayout()

    submit_button = QPushButton("Submit Custom")
    ok_button = QPushButton("OK")
    test_button = QPushButton("Test")

    for button in [submit_button, ok_button, test_button]:
        button.setStyleSheet(red_style + """
        background-color: #f0f0f0;
        border: 2px solid red;
        border-radius: 5px;
        padding: 5px;
        """)

    buttons_layout.addWidget(submit_button)
    buttons_layout.addWidget(ok_button)
    buttons_layout.addWidget(test_button)

    left_layout.addLayout(buttons_layout)

    # Right side (Test results)
    right_layout = QVBoxLayout()
    test_results = QTextEdit()
    test_results.setReadOnly(True)
    test_results.setStyleSheet(red_style)
    right_layout.addWidget(QLabel("Test Results:"))
    right_layout.addWidget(test_results)

    # Add layouts to main layout
    splitter = QSplitter(Qt.Horizontal)
    left_widget = QWidget()
    left_widget.setLayout(left_layout)
    right_widget = QWidget()
    right_widget.setLayout(right_layout)
    splitter.addWidget(left_widget)
    splitter.addWidget(right_widget)
    main_layout.addWidget(splitter)

    dialog.setLayout(main_layout)
    dialog.resize(800, 400)

    selected_patterns = []

    def submit_custom():
        custom_pattern = custom_regex_input.text().strip()
        if custom_pattern:
            list_widget.addItem(custom_pattern)
            custom_regex_input.clear()

    # Context menu for list items
    def show_context_menu(position):
        menu = QMenu()
        remove_action = QAction("Remove", list_widget)
        test_action = QAction("Submit Test", list_widget)
        
        menu.addAction(remove_action)
        menu.addAction(test_action)
        
        action = menu.exec_(list_widget.mapToGlobal(position))
        
        if action == remove_action:
            list_widget.takeItem(list_widget.currentRow())
        elif action == test_action:
            current_item = list_widget.currentItem()
            if current_item:
                test_regex(current_item.text())



    def test_regex():
        file_path, _ = QFileDialog.getOpenFileName(dialog, "Select PDF file", "", "PDF Files (*.pdf)")
        if file_path:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                test_results.clear()
                for pattern in [item.text() for item in list_widget.selectedItems()] + [custom_regex_input.text().strip()]:
                    if pattern:
                        matches = re.findall(pattern, text)
                        test_results.append(f"Pattern: {pattern}")
                        test_results.append(f"Matches: {matches[:10]}")  # Show first 10 matches
                        test_results.append("")

    submit_button.clicked.connect(submit_custom)
    ok_button.clicked.connect(dialog.accept)
    test_button.clicked.connect(test_regex)

    if dialog.exec_() == QDialog.Accepted:
        selected_patterns = [item.text() for item in list_widget.selectedItems()]
        custom_pattern = custom_regex_input.text().strip()
        if custom_pattern:
            selected_patterns.append(custom_pattern)

    return selected_patterns
