# Card Storage Application

## Overview
This application is designed to manage and store card information securely. It allows users to import card data from PDF files, perform BIN checks, and manage card entries through a user-friendly interface.

## Features
- Import card data from PDF documents.
- Perform BIN checks to validate card information.
- A context menu for managing card entries (remove, test, BIN check).
- A loading animation displayed during initialization.
- SQLite database for storing card information.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/L33TSP3AK/l33t-cc-storage.git
   cd l33t-cc-storage
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

## Usage
- To import card data, use the import function in the application.
- Right-click on a card entry to access the context menu for options like Remove, BIN Check, and Submit Test.



## Contact
For any inquiries, please open an issue in the GitHub repository.


Now, for the `requirements.txt` file, based on the imports in your provided code, here's an updated version:

```
PyQt5==5.15.6
pandas==1.5.3
```

Note that I've kept the versions as they were in the original requirements.txt you provided. You may want to update these to the latest compatible versions or the specific versions you're using in your development environment.

To create these files:

1. Save the markdown content above as `README.md` in your project's root directory.
2. Save the requirements content as `requirements.txt` in your project's root directory.

These files will provide a good starting point for documentation and dependency management for your project. Remember to keep them updated as your project evolves.
