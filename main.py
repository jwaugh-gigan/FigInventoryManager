import sys
from PyQt5.QtCore import Qt, QModelIndex, QItemSelectionModel, QSortFilterProxyModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QTextEdit
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
from PyQt5.QtWidgets import QPushButton, QComboBox
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QDateEdit
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QTableView, QInputDialog
from PyQt5.QtWidgets import QAction, QMessageBox
from PyQt5.QtGui import QColor
import random, json
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QDateEdit, QMessageBox
from PyQt5.QtCore import QDate


def generate_soft_dark_color():
    """Generate a soft dark hex color."""
    # Adjust the range to pick softer dark colors (e.g., 50 to 100)
    return f"#{random.randint(0, 50):02x}{random.randint(0, 50):02x}{random.randint(0, 50):02x}"

def generate_light_color():
    return f"#{random.randint(200, 255):02x}{random.randint(200, 255):02x}{random.randint(200, 255):02x}"


class AddInventoryDialog(QDialog):
    def __init__(self, parent=None):
        super(AddInventoryDialog, self).__init__(parent)
        
        self.setWindowTitle("Add New Inventory Item")
        self.setGeometry(100, 100, 400, 400)

        layout = QVBoxLayout()

        # Combo box for Purchase Location
        self.itemNameCombo = QComboBox(self)
        self.loadItemNames()
        self.itemNameCombo.currentIndexChanged.connect(self.onItemNameSelected)
        layout.addWidget(QLabel("Item Name"))
        layout.addWidget(self.itemNameCombo)

        self.expirationDateEdit = QDateEdit(self)
        self.expirationDateEdit.setDate(QDate.currentDate())
        self.expirationDateEdit.setCalendarPopup(True)
        layout.addWidget(QLabel("Expiration Date"))
        layout.addWidget(self.expirationDateEdit)

        # Combo box for Purchase Location
        self.purchaseLocationCombo = QComboBox(self)
        self.loadVendors()
        self.purchaseLocationCombo.currentIndexChanged.connect(self.onVendorSelected)
        layout.addWidget(QLabel("Vendor"))
        layout.addWidget(self.purchaseLocationCombo)

        self.purchaseDateEdit = QDateEdit(self)
        self.purchaseDateEdit.setDate(QDate.currentDate())
        self.purchaseDateEdit.setCalendarPopup(True)
        layout.addWidget(QLabel("Purchase Date"))
        layout.addWidget(self.purchaseDateEdit)
        
        self.purchaseLotNumberEdit = QLineEdit(self)
        layout.addWidget(QLabel("Purchase Lot Number"))
        layout.addWidget(self.purchaseLotNumberEdit)

        # Set Date Added to current date and make it read-only
        self.dateAddedEdit = QDateEdit(self)
        self.dateAddedEdit.setDate(QDate.currentDate())
        self.dateAddedEdit.setReadOnly(True)  # Make the date edit read-only
        self.dateAddedEdit.setButtonSymbols(QDateEdit.NoButtons)  # Hide the calendar and arrows
        layout.addWidget(QLabel("Date Added"))
        layout.addWidget(self.dateAddedEdit)

        # Add buttons
        buttonsLayout = QHBoxLayout()
        addButton = QPushButton("Add")
        addButton.clicked.connect(self.accept)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)
        buttonsLayout.addWidget(addButton)
        buttonsLayout.addWidget(cancelButton)
        layout.addLayout(buttonsLayout)

        self.setLayout(layout)
        
    def loadItemNames(self):
        try:    
            with open("item_names.json", "r") as file:
                itemNames = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            itemNames = ["Green Grapes"]  # Default item names

        itemNames.append("Other")  # Always add "Other" at the end
        self.itemNameCombo.clear()  # Clear existing items
        self.itemNameCombo.addItems(itemNames)
        
    def onItemNameSelected(self, index):
        if self.itemNameCombo.currentText() == "Other":
            self.promptNewItemName()

    def promptNewItemName(self):
        text, ok = QInputDialog.getText(self, "New Item Name", "Enter Item Name:")
        if ok and text:
            self.itemNameCombo.addItem(text)
            self.itemNameCombo.setCurrentText(text)
            self.saveItemNameToFile()

    def saveItemNameToFile(self):
        itemNames = [self.itemNameCombo.itemText(i) for i in range(self.itemNameCombo.count()) if self.itemNameCombo.itemText(i) != "Other"]

        with open("item_names.json", "w") as file:
            json.dump(itemNames, file)
            
    def loadVendors(self):
        try:
            with open("vendors.json", "r") as file:
                vendors = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            vendors = ["Sam's Club"]  # Default vendors

        vendors.append("Other")  # Always add "Other" at the end
        self.purchaseLocationCombo.clear()  # Clear existing items
        self.purchaseLocationCombo.addItems(vendors)
        
    def onVendorSelected(self, index):
        if self.purchaseLocationCombo.currentText() == "Other":
            self.promptNewVendor()

    def promptNewVendor(self):
        text, ok = QInputDialog.getText(self, "New Vendor", "Enter vendor name:")
        if ok and text:
            self.purchaseLocationCombo.addItem(text)
            self.purchaseLocationCombo.setCurrentText(text)
            self.saveVendorsToFile()

    def saveVendorsToFile(self):
        vendors = []
        for i in range(self.purchaseLocationCombo.count()):
            vendor = self.purchaseLocationCombo.itemText(i)
            if vendor != "Other":
                vendors.append(vendor)

        with open("vendors.json", "w") as file:
            json.dump(vendors, file)
        
    def accept(self):
        # Check if all fields have valid input
        if self.itemNameCombo.currentText() == "Other":
            QMessageBox.warning(self, "Input Error", "Name field is required.")
            return
        if self.purchaseLocationCombo.currentText() == "Other":
            QMessageBox.warning(self, "Input Error", "Vendor field is required.")
            return
        if not self.purchaseLotNumberEdit.text().strip():
            QMessageBox.warning(self, "Input Error", "Purchase Lot Number field is required.")
            return

        # If all checks pass, accept the dialog
        super(AddInventoryDialog, self).accept()

    def getData(self):
        # Return only the relevant fields
        return {
            "name": self.itemNameCombo.currentText(),
            "expiration_date": self.expirationDateEdit.date().toString("MM-dd-yyyy"),
            "purchase_location": self.purchaseLocationCombo.currentText(),
            "purchase_date": self.purchaseDateEdit.date().toString("MM-dd-yyyy"),
            "purchase_lot_number": self.purchaseLotNumberEdit.text(),
            "date_added": self.dateAddedEdit.date().toString("MM-dd-yyyy")
        }

#####
# Edit class
#####

class EditInventoryDialog(QDialog):
    def __init__(self, data, parent=None):
        super(EditInventoryDialog, self).__init__(parent)

        self.setWindowTitle("Edit Inventory Item")
        self.setGeometry(100, 100, 400, 400)

        layout = QVBoxLayout()

        # Initialize labels and line edits with existing data
        self.nameEdit = QLineEdit(data['name'], self)
        layout.addWidget(QLabel("Name"))
        layout.addWidget(self.nameEdit)

        self.expirationDateEdit = QDateEdit(QDate.fromString(data['expiration_date'], "MM-dd-yyyy"), self)
        self.expirationDateEdit.setCalendarPopup(True)
        layout.addWidget(QLabel("Expiration Date"))
        layout.addWidget(self.expirationDateEdit)

        self.purchaseLocationEdit = QLineEdit(data['purchase_location'], self)
        layout.addWidget(QLabel("Vendor"))
        layout.addWidget(self.purchaseLocationEdit)

        self.purchaseDateEdit = QDateEdit(QDate.fromString(data['purchase_date'], "MM-dd-yyyy"), self)
        self.purchaseDateEdit.setCalendarPopup(True)
        layout.addWidget(QLabel("Purchase Date"))
        layout.addWidget(self.purchaseDateEdit)

        self.dateAddedEdit = QDateEdit(QDate.fromString(data['date_added'], "MM-dd-yyyy"), self)
        self.dateAddedEdit.setCalendarPopup(True)
        layout.addWidget(QLabel("Date Added"))
        layout.addWidget(self.dateAddedEdit)

        # Date Opened Field
        self.dateOpenedEdit = QDateEdit(self)
        self.dateOpenedEdit.setCalendarPopup(True)
        self.dateOpenedEdit.setDate(QDate.currentDate())  # Default to current date
        # Check if a "date_opened" key exists and it is not empty

        # If there's a "date_opened" value, set it
        if 'date_opened' in data and data['date_opened']:
            self.dateOpenedEdit.setDate(QDate.fromString(data['date_opened'], "MM-dd-yyyy"))
        else:
            # Optional: For new entries or if not opened, you might want to indicate it's not set yet
            # This line is optional, depending on how you want to handle new or unopened items
            self.dateOpenedEdit.setSpecialValueText("Not Opened")
            # If you want the field to be editable even if not previously opened, remove the next line
            self.dateOpenedEdit.setEnabled(True)  # Ensure it's enabled for editing
        layout.addWidget(QLabel("Date Opened"))
        layout.addWidget(self.dateOpenedEdit)

        # Add buttons
        buttonsLayout = QHBoxLayout()
        saveButton = QPushButton("Save")
        saveButton.clicked.connect(self.accept)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)
        buttonsLayout.addWidget(saveButton)
        buttonsLayout.addWidget(cancelButton)
        layout.addLayout(buttonsLayout)

        self.setLayout(layout)

    def getData(self):
        # Return the updated data from the form
        return {
            "name": self.nameEdit.text(),
            "expiration_date": self.expirationDateEdit.date().toString("MM-dd-yyyy"),
            "purchase_location": self.purchaseLocationEdit.text(),
            "purchase_date": self.purchaseDateEdit.date().toString("MM-dd-yyyy"),
            "date_added": self.dateAddedEdit.date().toString("MM-dd-yyyy"),
            "date_opened": self.dateOpenedEdit.date().toString("MM-dd-yyyy") if self.dateOpenedEdit.isEnabled() else ""
        }

class CreateBatchDialog(QDialog):
    def __init__(self, batch_size, parent=None):
        super(CreateBatchDialog, self).__init__(parent)

        self.setWindowTitle("Create New Batch")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # Sell Date Field
        self.sellDateEdit = QDateEdit(self)
        self.sellDateEdit.setDate(QDate.currentDate())
        self.sellDateEdit.setCalendarPopup(True)
        layout.addWidget(QLabel("Sell Date"))
        layout.addWidget(self.sellDateEdit)

        # Sell Location Field
        self.sellLocationEdit = QLineEdit(self)
        layout.addWidget(QLabel("Sell Location"))
        layout.addWidget(self.sellLocationEdit)

        # Batch Size (Read-Only)
        self.batchSizeEdit = QLineEdit(self)
        self.batchSizeEdit.setText(str(batch_size))
        layout.addWidget(QLabel("Number of Outgoing Boxes in the Batch"))
        layout.addWidget(self.batchSizeEdit)

        # Add buttons
        buttonsLayout = QHBoxLayout()
        saveButton = QPushButton("Create Batch")
        saveButton.clicked.connect(self.validateAndAccept)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)
        buttonsLayout.addWidget(saveButton)
        buttonsLayout.addWidget(cancelButton)
        layout.addLayout(buttonsLayout)

        self.setLayout(layout)

    def getBatchData(self):
        return {
            "sell_date": self.sellDateEdit.date().toString("MM-dd-yyyy"),
            "sell_location": self.sellLocationEdit.text(),
            "batch_size": self.batchSizeEdit.text(),
        }


    def validateAndAccept(self):
        # Validate Sell Location field
        if not self.sellLocationEdit.text().strip():
            QMessageBox.warning(self, "Input Error", "Sell Location field is required.")
            return

        # Validate Batch Size field
        try:
            batch_size = int(self.batchSizeEdit.text())
            if batch_size <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Invalid number of items in the batch.")
            return

        # If validation passes, accept the dialog
        self.accept()
        
#####
# Table Management
#####

class CheckableSqlInventoryModel(QSqlQueryModel):
    def __init__(self, parent=None):
        super(CheckableSqlInventoryModel, self).__init__(parent)
        self.checks = {}

    def load_data(self):
        self.setQuery("""
            SELECT 
                inventory.id, 
                inventory.name, 
                inventory.date_opened,  -- Include the 'date opened' column
                inventory.expiration_date, 
                inventory.purchase_location, 
                inventory.purchase_date, 
                inventory.purchase_lot_number, 
                inventory.date_added, 
                inventory.status,
                batches.sell_date, 
                batches.sell_location, 
                batches.fig_and_brie_batch_number, 
                batches.batch_color
            FROM inventory 
            LEFT JOIN batches ON inventory.batch_id = batches.batch_id
            ORDER BY 
                CASE WHEN inventory.status = 'Available' THEN 1 ELSE 2 END,
                inventory.batch_id
        """)

    def rowCount(self, parent=QModelIndex()):
        return super().rowCount()

    def columnCount(self, parent=QModelIndex()):
        return super().columnCount() + 1  # Add one for the checkbox column

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.CheckStateRole and index.column() == 0:  # Checkbox column
            return self.checks.get(index.row(), Qt.Unchecked)

        if role == Qt.DisplayRole and index.column() == 0:  # Prevent displaying any data in checkbox column
            return ""

        if role == Qt.BackgroundRole:
            # Fetch the batch color from the 13th column (index 12)
            color_index = self.createIndex(index.row(), 12)
            color_value = super().data(color_index, Qt.DisplayRole)
            if color_value:  # If color value is present, set the background color
                return QColor(color_value)

        # Use shifted index for original data columns if beyond the checkbox column
        if index.column() > 0:
            return super().data(self.index(index.row(), index.column() - 1), role)
        return super().data(index, role)

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole and index.column() == 0:  # Checkbox column
            self.checks[index.row()] = value
            self.dataChanged.emit(index, index, [role])
            return True
        return False  # Editing other data through this model is not allowed

    def flags(self, index):
        if index.column() == 0:  # Checkbox column
            return Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        return super(CheckableSqlInventoryModel, self).flags(index) | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            # Update headers list to include 'Date Opened' before 'Expiration Date'
            headers = [
                "Inventory", 
                "Item ID", 
                "Item Name", 
                "Date Opened",  # New column header
                "Expiration Date", 
                "Vendor",
                "Purchase Date", 
                "Purchase Lot Number", 
                "Date Added", 
                "Status", 
                "Sell Date", 
                "Sell Location", 
                "Fig and Brie Batch Code", 
                "Batch Color"
            ]
            if 0 <= section < len(headers):
                return headers[section]
        return super().headerData(section, orientation, role)

    def uncheckAll(self):
        for row in range(self.rowCount()):
            self.checks[row] = Qt.Unchecked
            index = self.index(row, 0)  # Assuming the checkbox is in the first column
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])

class CheckableSqlBatchesModel(QSqlQueryModel):
    def __init__(self, parent=None):
        super(CheckableSqlBatchesModel, self).__init__(parent)
        self.checks = {}

    def load_data(self):
            self.setQuery("""
                SELECT 
                    batches.batch_id, 
                    batches.sell_date, 
                    batches.sell_location, 
                    batches.batch_size, 
                    batches.fig_and_brie_batch_number,
                    batch_color,
                    GROUP_CONCAT(inventory.name, '\n') AS inventory_items,  -- Separator is newline for names
                    GROUP_CONCAT(inventory.id, '\n') AS inventory_ids      -- Separator is newline for IDs
                FROM batches
                LEFT JOIN inventory ON batches.batch_id = inventory.batch_id
                GROUP BY batches.batch_id
            """)

    def rowCount(self, parent=QModelIndex()):
        return super().rowCount()

    def columnCount(self, parent=QModelIndex()):
        return super().columnCount() + 1  # Add one for the checkbox column

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.CheckStateRole and index.column() == 0:  # Checkbox column
            return self.checks.get(index.row(), Qt.Unchecked)
        
        if role == Qt.DisplayRole and index.column() == 0:  # Prevent displaying any data in checkbox column
            return ""

        if role == Qt.BackgroundRole:
            # Adjust this index to the column where batch_color is stored in your dataset
            batch_color_column_index = 5
            color_index = self.createIndex(index.row(), batch_color_column_index)
            color_value = super().data(color_index, Qt.DisplayRole)
            if color_value:  # If color value is present, set the background color
                return QColor(color_value)

        # Use shifted index for original data columns if beyond the checkbox column
        if index.column() > 0:
            return super().data(self.index(index.row(), index.column() - 1), role)
        return super().data(index, role)

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole and index.column() == 0:  # Checkbox column
            if value == Qt.Checked:
                # Uncheck all other rows
                for row in range(self.rowCount()):
                    if row != index.row():
                        self.checks[row] = Qt.Unchecked
                        self.dataChanged.emit(self.index(row, 0), self.index(row, 0), [role])

            # Set the value for the current row
            self.checks[index.row()] = value
            self.dataChanged.emit(index, index, [role])
            return True

        return False  # Editing other data through this model is not allowed


    def flags(self, index):
        if index.column() == 0:  # Checkbox column
            return Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        return super(CheckableSqlBatchesModel, self).flags(index) | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            headers = ["", "Batch ID", "Sell Date", "Sell Location", "Batch Size", "Fig and Brie Batch Code",
                       "Batch Color", "Inventory Items", "Inventory Item ID" ]
            if 0 <= section < len(headers):
                return headers[section]
        return super().headerData(section, orientation, role)
    
    def uncheckAll(self):
        for row in range(self.rowCount()):
            self.checks[row] = Qt.Unchecked
            index = self.index(row, 0)  # Assuming the checkbox is in the first column
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])

#####
# Main App Window
#####

class InventoryApp(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initDb()
        self.initInventoryTable()
        self.initBatchTable()
        self.selectedItems = []
        self.proxyModel = QSortFilterProxyModel(self)
        self.proxyModel.setSourceModel(self.model)  # self.model is your CheckableSqlTableModel
        self.inventoryTableView.setModel(self.proxyModel)

    def initUI(self):
        self.setWindowTitle('Inventory Management')
        self.setGeometry(100, 100, 2100, 820)
        # self.setStyleSheet("""
        # QWidget {
        #     background-color: #2E2E2E; /* Dark gray background for most widgets */
        #     color: #FFFFFF; /* White text color for most widgets */
        #     }
        #     QLineEdit, QDateEdit, QComboBox, QPushButton {
        #         background-color: #383838; /* Slightly lighter gray for input fields and buttons */
        #         color: #FFFFFF; /* White text */
        #         border-radius: 5px; /* Rounded corners */
        #         padding: 2px; /* Padding for text inside input fields */
        #         border: 1px solid #4F4F4F; /* Subtle border for depth */
        #     }
        #     QPushButton:hover {
        #         background-color: #626262;
        #     }
        #     QPushButton:pressed {
        #         background-color: #707070;
        #     }
        #     QMenuBar {
        #         background-color: #383838;
        #     }
        #     QMenuBar::item {
        #         spacing: 3px; /* spacing between menu bar items */
        #         padding: 2px 10px;
        #         background: transparent;
        #         border-radius: 4px;
        #     }
        #     QMenuBar::item:selected { /* when selected */
        #         background: #505050;
        #     }
        #     QMenu {
        #         background-color: #383838;
        #         border: 1px solid #4F4F4F;
        #     }
        #     QMenu::item {
        #         color: #FFFFFF;
        #     }
        #     QMenu::item:selected {
        #         background-color: #505050;
        #     }
        #     QTableView {
        #         gridline-color: #585858; /* Darker grid lines for tables */
        #     }        
        #     QTextEdit {
        #     background-color: #FFFFFF; /* Keep label box background light */
        #     color: #000000; /* Black text color for label box */
        #     }
        # """)
        darkerLineColor = "#b0b0b0"

        menuBar = self.menuBar()
        # Add "Preferences" Menu
        preferencesMenu = menuBar.addMenu('Preferences')

        # Add actions for editing JSON files
        editVendorAction = QAction('Edit Vendor JSON', self)
        editVendorAction.triggered.connect(self.editVendorJson)
        preferencesMenu.addAction(editVendorAction)

        editFoodItemAction = QAction('Edit Food Item JSON', self)
        editFoodItemAction.triggered.connect(self.editFoodItemJson)
        preferencesMenu.addAction(editFoodItemAction)

        # Main horizontal layout
        mainLayout = QHBoxLayout()

        # Vertical layout for buttons
        buttonsLayout = QVBoxLayout()

        
        # Inventory buttons
        self.addButton = QPushButton('Add Inventory Item\n+', self)
        self.addButton.clicked.connect(self.addInventory)
        self.addButton.setFixedSize(150, 60)
        # Styling the add button
        self.addButton.setStyleSheet("""
            QPushButton {
                background-color: #98FB98; /* Light green background */
                color: black; /* Text color */
                border-radius: 12px; /* Rounded corners */
                padding: 6px; /* Padding around text */
                border: 1px solid #5FBC5F; /* Slightly darker border for depth */
                font-weight: bold; /* Making the text bold */
                font-size: 14px; /* Font size */
            }
            QPushButton:hover {
                background-color: #90EE90; /* Slightly darker green when hovered */
            }
            QPushButton:pressed {
                background-color: #7CCD7C; /* Even darker green when pressed */
            }
        """)
        buttonsLayout.addWidget(self.addButton)
        
        # Open Inventory buttons
        self.openButton = QPushButton('Open Checked\nInventory Items', self)
        self.openButton.clicked.connect(self.setDateOpenedForSelected)
        self.openButton.setFixedSize(150, 60)
        # Styling the add button
        self.openButton.setStyleSheet("""
            QPushButton {
                background-color: #98FB98; /* Light green background */
                color: black; /* Text color */
                border-radius: 12px; /* Rounded corners */
                padding: 6px; /* Padding around text */
                border: 1px solid #5FBC5F; /* Slightly darker border for depth */
                font-weight: bold; /* Making the text bold */
                font-size: 14px; /* Font size */
            }
            QPushButton:hover {
                background-color: #90EE90; /* Slightly darker green when hovered */
            }
            QPushButton:pressed {
                background-color: #7CCD7C; /* Even darker green when pressed */
            }
        """)
        buttonsLayout.addWidget(self.openButton)
        
        # Batch buttons
        self.createBatchButton = QPushButton('Create Batch', self)
        self.createBatchButton.clicked.connect(self.createBatch)
        self.createBatchButton.setFixedSize(150, 60)
        self.createBatchButton.setStyleSheet("""
            QPushButton {
                background-color: #98FB98; /* Light green background */
                color: black; /* Text color */
                border-radius: 12px; /* Rounded corners */
                padding: 6px; /* Padding around text */
                border: 1px solid #5FBC5F; /* Slightly darker border for depth */
                font-weight: bold; /* Making the text bold */
                font-size: 14px; /* Font size */
            }
            QPushButton:hover {
                background-color: #90EE90; /* Slightly darker green when hovered */
            }
            QPushButton:pressed {
                background-color: #7CCD7C; /* Even darker green when pressed */
            }
        """)
        buttonsLayout.addWidget(self.createBatchButton) 
        
        self.addInventoryToBatchButton = QPushButton("Add Checked\nItems to Batch", self)
        self.addInventoryToBatchButton.clicked.connect(self.addCheckedItemsToBatch)
        self.addInventoryToBatchButton.setFixedSize(150, 60)
        self.addInventoryToBatchButton.setStyleSheet("""
            QPushButton {
                background-color: #98FB98; /* Light green background */
                color: black; /* Text color */
                border-radius: 12px; /* Rounded corners */
                padding: 6px; /* Padding around text */
                border: 1px solid #5FBC5F; /* Slightly darker border for depth */
                font-weight: bold; /* Making the text bold */
                font-size: 14px; /* Font size */
            }
            QPushButton:hover {
                background-color: #90EE90; /* Slightly darker green when hovered */
            }
            QPushButton:pressed {
                background-color: #7CCD7C; /* Even darker green when pressed */
            }
        """)
        buttonsLayout.addWidget(self.addInventoryToBatchButton)
        
        
        self.editButton = QPushButton('Edit Selected\nInventory Item', self)
        self.editButton.clicked.connect(self.editCheckedRow)
        self.editButton.setFixedSize(150, 60)
        # Styling the add button
        self.editButton.setStyleSheet("""
            QPushButton {
                background-color: #FFFACD; /* Light green background */
                color: black; /* Text color */
                border-radius: 12px; /* Rounded corners */
                padding: 6px; /* Padding around text */
                border: 1px solid #EEE8AA; /* Slightly darker border for depth */
                font-weight: bold; /* Making the text bold */
                font-size: 14px; /* Font size */
            }
            QPushButton:hover {
                background-color: #90EE90; /* Slightly darker green when hovered */
            }
            QPushButton:pressed {
                background-color: #7CCD7C; /* Even darker green when pressed */
            }
        """)
        buttonsLayout.addWidget(self.editButton)
    

        self.unbatchInventoryItemsButton = QPushButton("Unbatch\nSelected Items", self)
        self.unbatchInventoryItemsButton.clicked.connect(self.unbatchCheckedInventoryItems)
        self.unbatchInventoryItemsButton.setFixedSize(150, 60)
        self.unbatchInventoryItemsButton.setStyleSheet("""
            QPushButton {
                background-color: #FFA07A; /* Light salmon red background */
                color: black; /* Text color */
                border-radius: 10px; /* Rounded corners */
                padding: 6px; /* Padding around text */
                border: 1px solid #FA8072; /* Slightly darker border for depth */
                font-weight: bold; /* Making the text bold */
                font-size: 14px; /* Font size */
            }
            QPushButton:hover {
                background-color: #FA8072; /* Slightly darker salmon when hovered */
            }
            QPushButton:pressed {
                background-color: #E9967A; /* Dark salmon for pressed state */
            }
        """)
        buttonsLayout.addWidget(self.unbatchInventoryItemsButton)

        self.removeButton = QPushButton('Delete Checked\nInventory Items', self)
        self.removeButton.clicked.connect(self.removeCheckedRows)
        self.removeButton.setFixedSize(150, 60)
        self.removeButton.setStyleSheet("""
            QPushButton {
                background-color: #FFA07A; /* Light salmon red background */
                color: black; /* Text color */
                border-radius: 10px; /* Rounded corners */
                padding: 6px; /* Padding around text */
                border: 1px solid #FA8072; /* Slightly darker border for depth */
                font-weight: bold; /* Making the text bold */
                font-size: 14px; /* Font size */
            }
            QPushButton:hover {
                background-color: #FA8072; /* Slightly darker salmon when hovered */
            }
            QPushButton:pressed {
                background-color: #E9967A; /* Dark salmon for pressed state */
            }
        """)
        buttonsLayout.addWidget(self.removeButton)
        
        self.deleteBatchButton = QPushButton('Delete Batch', self)
        self.deleteBatchButton.clicked.connect(self.deleteBatch)
        self.deleteBatchButton.setFixedSize(150, 60)
        self.deleteBatchButton.setStyleSheet("""
            QPushButton {
                background-color: #FFA07A; /* Light salmon red background */
                color: black; /* Text color */
                border-radius: 10px; /* Rounded corners */
                padding: 6px; /* Padding around text */
                border: 1px solid #FA8072; /* Slightly darker border for depth */
                font-weight: bold; /* Making the text bold */
                font-size: 14px; /* Font size */
            }
            QPushButton:hover {
                background-color: #FA8072; /* Slightly darker salmon when hovered */
            }
            QPushButton:pressed {
                background-color: #E9967A; /* Dark salmon for pressed state */
            }
        """)
        buttonsLayout.addWidget(self.deleteBatchButton)
        
        self.toggleVisibilityButton = QPushButton("Show Batched\nInventory Items", self)
        self.toggleVisibilityButton.clicked.connect(self.toggleUnavailableRows)
        self.toggleVisibilityButton.setFixedSize(150, 60)
        self.toggleVisibilityButton.setStyleSheet("""
            QPushButton {
                background-color: #ADD8E6; /* Light blue background */
                color: black; /* Text color */
                border-radius: 10px; /* Rounded corners */
                padding: 6px; /* Padding around text */
                border: 1px solid #87CEEB; /* Slightly darker border for depth */
                font-weight: bold; /* Making the text bold */
                font-size: 14px; /* Font size */
            }
            QPushButton:hover {
                background-color: #87CEFA; /* Slightly darker blue when hovered */
            }
            QPushButton:pressed {
                background-color: #6495ED; /* Cornflower blue for pressed state */
            }
        """)
        buttonsLayout.addWidget(self.toggleVisibilityButton)

        # Horizontal layout for Label Buttons
        labelMakerLayout = QVBoxLayout()
        labelMakerContainer = QWidget()
                
        LabelbuttonLayout = QHBoxLayout()
        self.printLabelButton = QPushButton('Print Label', self)
        self.printLabelButton.clicked.connect(self.printLabel)
        LabelbuttonLayout.addWidget(self.printLabelButton)
        self.cancelButton = QPushButton('Cancel Label', self)
        self.cancelButton.clicked.connect(self.cancelLabel)
        LabelbuttonLayout.addWidget(self.cancelButton)
        labelMakerContainer.setFixedWidth(600)
        
        # Label Maker Layout
        self.labelTextBox = QTextEdit(self)
        self.labelTextBox.setReadOnly(True)
        labelMakerLayout.addWidget(self.labelTextBox)
        labelMakerLayout.addLayout(LabelbuttonLayout)
        labelMakerContainer.setLayout(labelMakerLayout)
        labelMakerContainer.setFixedWidth(600)

        batchAndLabelLayout = QHBoxLayout()
        batchAndLabelContainer = QWidget()
        tableLayout = QVBoxLayout()
        tableContainer = QWidget()
        # Inventory Table
        self.inventoryTableView = QTableView(self)
        self.inventoryTableView.setStyleSheet(f"QTableView {{ gridline-color: {darkerLineColor}; }}")
        tableLayout.addWidget(self.inventoryTableView)

        # Batch Table
        self.batchTableView = QTableView(self)
        self.batchTableView.setStyleSheet(f"QTableView {{ gridline-color: {darkerLineColor}; }}")
        batchAndLabelLayout.addWidget(self.batchTableView)
        batchAndLabelLayout.addWidget(labelMakerContainer)
        batchAndLabelContainer.setLayout(batchAndLabelLayout)
        tableLayout.addWidget(batchAndLabelContainer)
        tableContainer.setLayout(tableLayout)
        

        # Main layout setup
        mainLayout.addLayout(buttonsLayout)
        mainLayout.addWidget(tableContainer)

        # Set the main layout to a central widget
        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)
        
    def initInventoryTable(self):
        # Set up the model
        self.model = CheckableSqlInventoryModel(self)
        self.model.load_data()  # Load data using the custom query

        # Set the model on the table view
        self.inventoryTableView.setModel(self.model)
        self.printModelColumns(self.model)
        
        # Connect the model's dataChanged signal (if needed)
        # self.model.dataChanged.connect(self.createLabelForSelectedBatch)
        # Depending on your implementation, you may not need this signal connection

        # Hide the ID Column
        self.inventoryTableView.hideColumn(13)
        
        # Set Alignment
        header = self.inventoryTableView.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.inventoryTableView.horizontalHeader().setStretchLastSection(True)
        self.inventoryTableView.resizeColumnsToContents()
        
    def initBatchTable(self):
        # Set up the batch model
        self.batchModel = CheckableSqlBatchesModel(self)
        self.batchModel.load_data()  # Load data using the custom query

        # Assuming you have a separate QTableView for batches
        self.batchTableView.setModel(self.batchModel)
        self.printModelColumns(self.batchModel)
        self.adjustRowHeights(self.batchTableView, textColumnIndex=5)
        
        # Optional: Connect the model's dataChanged signal if needed
        self.batchModel.dataChanged.connect(self.onBatchCheckboxClicked)
        # Depending on your implementation, you may not need this signal connection

        # Optional: Hide specific columns if necessary
        self.batchTableView.hideColumn(6)

        # Set Alignment and other properties for the batch table view
        header = self.batchTableView.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.batchTableView.horizontalHeader().setStretchLastSection(True)
        self.batchTableView.resizeColumnsToContents()
    
    def addInventory(self):
        dialog = AddInventoryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            inventoryData = dialog.getData()
            print("Adding Inventory:")
            print(inventoryData)
            self.addInventoryToDb(inventoryData)
            # Refresh your grid view here to show the new data
            self.model.load_data()
            self.inventoryTableView.resizeColumnsToContents()
            
    def setDateOpenedForSelected(self):
        selectedRows = self.getSelectedRows()  # Get selected item IDs
        todayDate = QDate.currentDate().toString("MM-dd-yyyy")  # Format today's date as a string
        openedItems = []  # To track items that are already opened by name

        for inventory_id in selectedRows:
            # Check if the opened date is already set and fetch the item name
            check_query = QSqlQuery()
            check_query.prepare("SELECT name, date_opened FROM inventory WHERE id = :inventory_id")
            check_query.bindValue(":inventory_id", inventory_id)
            check_query.exec_()
            
            if check_query.next() and check_query.value(1):
                # If there's already a date set, add the item name to the list and skip updating
                openedItems.append(check_query.value(0))  # Using item name instead of ID
                continue  # Skip this item
            
            # Update the opened date for items that don't have it set
            update_query = QSqlQuery()
            update_query.prepare("UPDATE inventory SET date_opened = :date_opened WHERE id = :inventory_id")
            update_query.bindValue(":date_opened", todayDate)
            update_query.bindValue(":inventory_id", inventory_id)
            if not update_query.exec_():
                QMessageBox.critical(self, "Database Error", update_query.lastError().text())

        # If there are opened items, show a modal popup
        if openedItems:
            QMessageBox.information(self, "Package Already Opened",
                                    "The following items are already opened and cannot be opened again: " + ", ".join(openedItems) + 
                                    ". To modify, please use the edit functionality.",
                                    QMessageBox.Ok)

        self.model.load_data()  # Refresh the table view to show the updated dates
            
    def editVendorJson(self):
        self.editJsonFile("vendors.json")

    def editFoodItemJson(self):
        self.editJsonFile("item_names.json")

    def editJsonFile(self, filename):
        try:
            with open(filename, "r") as file:
                data = json.load(file)
            textData = json.dumps(data, indent=4)
        except (FileNotFoundError, json.JSONDecodeError):
            textData = "[]"

        # Create and display the dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit {filename}")
        dialog.setLayout(QVBoxLayout())

        textEdit = QTextEdit()
        textEdit.setText(textData)
        dialog.layout().addWidget(textEdit)

        saveButton = QPushButton("Save")
        saveButton.clicked.connect(lambda: self.saveJsonFile(filename, textEdit.toPlainText(), dialog))
        dialog.layout().addWidget(saveButton)

        dialog.exec_()

    def saveJsonFile(self, filename, textData, dialog):
        try:
            data = json.loads(textData)
            with open(filename, "w") as file:
                json.dump(data, file, indent=4)
            dialog.close()
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "Invalid JSON format.")

    def adjustRowHeights(self, inventoryTableView, textColumnIndex):
        inventoryTableView.resizeRowsToContents()
        for row in range(inventoryTableView.model().rowCount()):
            text = inventoryTableView.model().data(inventoryTableView.model().index(row, textColumnIndex))
            # Calculate required height based on the text
            # This is a simple approximation. You might need a more complex calculation.
            lines = text.count('\n') + 1
            rowHeight = inventoryTableView.rowHeight(row) * lines
            inventoryTableView.setRowHeight(row, rowHeight)
        
    def createBatch(self):
        selectedRows = []
        alreadyBatchedItems = []

        for row in range(self.model.rowCount()):
            if self.model.data(self.model.index(row, 0), Qt.CheckStateRole) == Qt.Checked:
                inventory_id = self.model.data(self.model.index(row, 1))  # Assuming ID is in column 1
                name = self.model.data(self.model.index(row, 2))  # Assuming name is in column 2

                # Check if the inventory item is part of a batch
                batch_check_query = QSqlQuery()
                batch_check_query.exec_(f"SELECT batch_id FROM inventory WHERE id = {inventory_id}")
                if batch_check_query.next():
                    batch_id = batch_check_query.value(0)
                    if batch_id:  # This checks if batch_id is not None and not empty
                        alreadyBatchedItems.append(name)
                    else:
                        selectedRows.append(inventory_id)

        if alreadyBatchedItems:
            QMessageBox.warning(self, "Warning", "The following items are already in a batch and cannot be added to a new batch:\n" + "\n".join(alreadyBatchedItems))
            return

        if not selectedRows:
            QMessageBox.warning(self, "Warning", "No items selected to create a batch.")
            return

        # Open the batch creation dialog
        dialog = CreateBatchDialog(len(selectedRows), self)
        if dialog.exec_() == QDialog.Accepted:
            batch_data = dialog.getBatchData()
            batch_color = generate_light_color()  # Make sure this function is defined and returns a color string

            # Insert the new batch record with batch_color
            batch_query = QSqlQuery()
            batch_query.prepare("INSERT INTO batches (sell_date, sell_location, batch_size, batch_color) VALUES (?, ?, ?, ?)")
            batch_query.addBindValue(batch_data['sell_date'])
            batch_query.addBindValue(batch_data['sell_location'])
            batch_query.addBindValue(batch_data['batch_size'])
            batch_query.addBindValue(batch_color)  # Adding batch_color

            if not batch_query.exec_():
                QMessageBox.critical(self, "Database Error", batch_query.lastError().text())
                return

            batch_id = batch_query.lastInsertId()

            # Generate fig_and_brie_batch_number using the batch_id
            date_str = batch_data['sell_date'].replace('-', '')
            batch_number = f"{batch_id}-{date_str}-{batch_data['batch_size']}-LC"

            # Update the batch record with the generated batch number
            update_batch_query = QSqlQuery()
            update_batch_query.prepare("UPDATE batches SET fig_and_brie_batch_number = ? WHERE batch_id = ?")
            update_batch_query.addBindValue(batch_number)
            update_batch_query.addBindValue(batch_id)

        if not update_batch_query.exec_():
            QMessageBox.critical(self, "Database Error", update_batch_query.lastError().text())
            return

        batch_id = batch_query.lastInsertId()

        # Associate selected inventory items with the new batch
        for inventory_id in selectedRows:
            update_query = QSqlQuery()
            update_query.prepare("UPDATE inventory SET batch_id = ?, status = 'Batched' WHERE id = ?")
            update_query.addBindValue(batch_id)
            update_query.addBindValue(inventory_id)
            if not update_query.exec_():
                QMessageBox.critical(self, "Database Error", update_query.lastError().text())

        self.model.load_data()  # Refresh the inventory model
        self.model.uncheckAll()
        self.batchModel.load_data() 
        self.adjustRowHeights(self.batchTableView, textColumnIndex=5)

    def toggleUnavailableRows(self):
        if self.proxyModel.filterRegExp().isEmpty():
            # Show only rows without 'Unavailable' status
            self.proxyModel.setFilterRegExp('^(?!.*Batched).*$')
            self.proxyModel.setFilterKeyColumn(8)  # Replace 5 with the actual index of your status column
        else:
            # Show all rows
            self.proxyModel.setFilterRegExp('')

    def cancelLabel(self):
        # Logic to handle "Cancel Label" action, like clearing the text box
        self.labelTextBox.clear()
    
    def getSelectedRows(self):
        selectedRows = []
        for row in range(self.model.rowCount()):
            if self.model.data(self.model.index(row, 0), Qt.CheckStateRole) == Qt.Checked:
                inventory_id = self.model.data(self.model.index(row, 1))  # Assuming ID is in column 1
                selectedRows.append(inventory_id)
        return selectedRows

    def removeCheckedRows(self):
        rows_to_remove = []
        cannot_remove = False

        for row in range(self.model.rowCount()):
            if self.model.data(self.model.index(row, 0), Qt.CheckStateRole) == Qt.Checked:
                inventory_id = self.model.data(self.model.index(row, 1))  # Assuming ID is in column 1

                # Perform a query to check the batch_id for this inventory item
                query = QSqlQuery(f"SELECT batch_id FROM inventory WHERE id = {inventory_id}")
                if query.exec_() and query.first():
                    batch_id = query.value(0)
                    if batch_id:  # This checks if batch_id is not None and not empty
                        cannot_remove = True
                        continue
                    rows_to_remove.append(row)

        if cannot_remove:
            QMessageBox.warning(self, "Warning", "Some selected items are associated with a batch and cannot be removed.")
            return

        if not rows_to_remove:
            QMessageBox.warning(self, "Warning", "No eligible items selected for removal.")
            return

        # Confirmation dialog before removal - outside of any loop
        reply = QMessageBox.question(self, 'Confirm Removal', 'Are you sure you want to remove the selected items?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            for row in reversed(rows_to_remove):  # Remove rows in reverse order to not mess up the indices
                inventory_id = self.model.data(self.model.index(row, 1))  # Assuming ID is in column 1
                delete_query = QSqlQuery()
                if not delete_query.exec_(f"DELETE FROM inventory WHERE id = {inventory_id}"):
                    QMessageBox.critical(self, "Database Error", delete_query.lastError().text())
                    return  # Exit if the delete operation fails

            self.model.load_data()  # Reload the data
            self.batchModel.load_data() 
            self.adjustRowHeights(self.batchTableView, textColumnIndex=5)

    def editCheckedRow(self):
        checked_indexes = []
        for row in range(self.model.rowCount()):
            index = self.model.index(row, 0)  # Assuming the checkbox is in column 0
            if self.model.data(index, Qt.CheckStateRole) == Qt.Checked:
                checked_indexes.append(row)

        if len(checked_indexes) != 1:
            QMessageBox.warning(self, "Warning", "Please select exactly one row to edit.")
            return

        row_to_edit = checked_indexes[0]
        self.openEditDialog(row_to_edit)
        
    def openEditDialog(self, row):
        data_to_edit = {
            'name': self.model.data(self.model.index(row, 2)),
            'date_opened': self.model.data(self.model.index(row, 3)),
            'expiration_date': self.model.data(self.model.index(row, 4)),
            'purchase_location': self.model.data(self.model.index(row, 5)),
            'purchase_date': self.model.data(self.model.index(row, 6)),
            'date_added': self.model.data(self.model.index(row, 7))
            # Add other fields if necessary
        }
        dialog = EditInventoryDialog(data_to_edit, self)
        if dialog.exec_() == QDialog.Accepted:
            updated_data = dialog.getData()
            self.updateRowInDb(row, updated_data)

    def updateRowInDb(self, row, data):
        inventory_id = self.model.data(self.model.index(row, 1))  # Assuming ID is in column 1

        query = QSqlQuery()
        query.prepare("""
            UPDATE inventory 
            SET name = ?, date_opened = ?, expiration_date = ?, purchase_location = ?, 
                purchase_date = ?, date_added = ?
            WHERE id = ?
        """)

        query.addBindValue(data['name'])
        query.addBindValue(data['date_opened'])
        query.addBindValue(data['expiration_date'])
        query.addBindValue(data['purchase_location'])
        query.addBindValue(data['purchase_date'])
        query.addBindValue(data['date_added'])
        query.addBindValue(inventory_id)

        if not query.exec_():
            QMessageBox.critical(self, "Database Error", query.lastError().text())
        else:
            self.model.load_data()  # Refresh the model to update the view


    def onBatchCheckboxClicked(self, topLeft, bottomRight, roles):
        if Qt.CheckStateRole in roles and topLeft.column() == 0:  # Check if the checkbox state changed
            batchId = self.batchModel.data(self.batchModel.index(topLeft.row(), 1), Qt.DisplayRole)  # Get the batch ID
            FigAndBrie_BatchCode = self.batchModel.data(self.batchModel.index(topLeft.row(), 5), Qt.DisplayRole)  # Get the fig batch code
            foodsAndItems = self.batchModel.data(self.batchModel.index(topLeft.row(), 7), Qt.DisplayRole)  # Get ingredients
            foodsAndItemsInline = foodsAndItems.replace('\n', ', ')  # Format ingredients for inline display
            sellDateStr = self.batchModel.data(self.batchModel.index(topLeft.row(), 2), Qt.DisplayRole)  # Get the sell date

            # Convert sell date string to QDate object and calculate use-by date
            sellDate = QDate.fromString(sellDateStr, "MM-dd-yyyy")
            useByDate = sellDate.addDays(4).toString("MM-dd-yyyy")


            # Base64 encoded image (replace with your logo's base64)
            # logo_base64 = "data:image/png;base64,..."  # Replace with your logo's base64 string
            # <img class="logo" src="{logo_base64}" alt="Logo">

            # Construct HTML content
            html_content = f"""
            <html>
                <head>
                    <style>
                        .label-container {{
                            font-family: Arial, sans-serif;
                        }}
                        .logo {{
                            width: 100px;
                            height: auto;
                        }}
                        .title {{
                            font-size: 18px;
                            font-weight: bold;
                        }}
                        .ingredients {{
                            font-size: 14px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="label-container">
                        
                        <div class="title">Fig and Brie</div>
                        <div class="ingredients">Ingredients: {foodsAndItemsInline}</div>
                        <div>Fig and Brie Batch Code: {FigAndBrie_BatchCode}</div>
                        <div>Please consume within 4 days days days of the creation date</div>
                        <div>Use By: {useByDate}</div>
                    </div>
                </body>
            </html>
            """

            # Set the HTML content to the labelTextBox
            self.labelTextBox.setHtml(html_content)
   
    def handleRowSelection(self, topLeft, bottomRight, roles):
        if Qt.CheckStateRole in roles and topLeft.column() == 0:
            row = topLeft.row()
            if self.model.data(topLeft, Qt.CheckStateRole) == Qt.Checked:
                self.inventoryTableView.selectRow(row)
            else:
                self.inventoryTableView.selectionModel().select(self.model.index(row, 0), 
                                                       QItemSelectionModel.Deselect | QItemSelectionModel.Rows)
    
    def getSelectedBatchId(self):
        for row in range(self.batchModel.rowCount()):
            if self.batchModel.data(self.batchModel.index(row, 0), Qt.CheckStateRole) == Qt.Checked:
                # Assuming batch_id is in the second column
                return self.batchModel.data(self.batchModel.index(row, 1), Qt.DisplayRole)
        return None  # Return None if no batch is selected
    
    def getCheckedInventoryItems(self):
        checkedItems = []
        for row in range(self.model.rowCount()):
            # Check if the checkbox in the first column is checked
            if self.model.data(self.model.index(row, 0), Qt.CheckStateRole) == Qt.Checked:
                # Retrieve the inventory item's ID from the second column
                inventory_id = self.model.data(self.model.index(row, 1))
                checkedItems.append(inventory_id)
        return checkedItems
    
    
    def addCheckedItemsToBatch(self):
        selectedBatchId = self.getSelectedBatchId()
        print("Selected Batch ID:", selectedBatchId)
        if not selectedBatchId:
            QMessageBox.warning(self, "Warning", "No batch selected.")
            return

        checkedItems = self.getCheckedInventoryItems()
        print("Checked Items:", checkedItems)
        if not checkedItems:
            QMessageBox.warning(self, "Warning", "No inventory items selected.")
            return

        for itemId in checkedItems:
            if not self.isItemAlreadyBatched(itemId):
                self.addInventoryItemToBatch(itemId, selectedBatchId)
            else:
                print(f"Item {itemId} is already batched.")

        self.model.load_data()  # Refresh the inventory model
        self.model.uncheckAll()
        self.batchModel.load_data() 
        self.adjustRowHeights(self.batchTableView, textColumnIndex=5)
        
    def isItemAlreadyBatched(self, itemId):
        query = QSqlQuery()
        query.prepare("SELECT batch_id FROM inventory WHERE id = :itemId")
        query.bindValue(":itemId", itemId)
        if query.exec_() and query.next():
            batch_id = query.value(0)
            # Check if batch_id is not None and not an empty string
            return batch_id is not None and batch_id != ""
        else:
            QMessageBox.critical(self, "Database Error", query.lastError().text())
            return False

    def addInventoryItemToBatch(self, itemId, batchId):
        update_query = QSqlQuery()
        update_query.prepare("UPDATE inventory SET batch_id = :batchId, status = 'Batched' WHERE id = :itemId")
        update_query.bindValue(":batchId", batchId)
        update_query.bindValue(":itemId", itemId)
        
        if not update_query.exec_():
            QMessageBox.critical(self, "Database Error", update_query.lastError().text())
            print("Error updating item:", itemId, "Batch ID:", batchId, "Error:", update_query.lastError().text())         
    
    def deleteBatch(self):
        selectedBatchIds = []
        for row in range(self.batchModel.rowCount()):
            if self.batchModel.data(self.batchModel.index(row, 0), Qt.CheckStateRole) == Qt.Checked:
                batchId = self.batchModel.data(self.batchModel.index(row, 1), Qt.DisplayRole)  # Assuming batch_id is in the second column
                selectedBatchIds.append(batchId)

        if not selectedBatchIds:
            QMessageBox.warning(self, "Warning", "Please select a batch to delete.")
            return

        # Confirm deletion for all selected batches
        reply = QMessageBox.question(self, 'Confirm Deletion', 'Are you sure you want to delete the selected batch(es)?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            for batchId in selectedBatchIds:
                # Update inventory items, set batch_id to NULL and status to 'Available'
                update_query = QSqlQuery()
                update_query.exec_(f"UPDATE inventory SET batch_id = NULL, status = 'Available' WHERE batch_id = {batchId}")
                if update_query.lastError().isValid():
                    QMessageBox.critical(self, "Update Error", update_query.lastError().text())
                    continue  # Skip the deletion of this batch due to error in updating inventory items

                # Delete the batch
                delete_query = QSqlQuery()
                delete_query.exec_(f"DELETE FROM batches WHERE batch_id = {batchId}")
                if delete_query.lastError().isValid():
                    QMessageBox.critical(self, "Deletion Error", delete_query.lastError().text())
                    continue

        # Refresh the models to reflect changes
        self.model.load_data()  # Refresh inventory model
        self.batchModel.load_data()  # Refresh batch model
        self.batchModel.uncheckAll()

    def unbatchCheckedInventoryItems(self):
        checkedItems = self.getCheckedInventoryItems()
        if not checkedItems:
            QMessageBox.warning(self, "Warning", "No inventory items selected.")
            return

        for itemId in checkedItems:
            self.setInventoryItemAsAvailable(itemId)

        # Reload data to reflect the changes
        self.model.load_data()
        self.model.uncheckAll()
        self.batchModel.load_data()
        self.batchModel.uncheckAll()

    def setInventoryItemAsAvailable(self, itemId):
        update_query = QSqlQuery()
        update_query.prepare("UPDATE inventory SET batch_id = NULL, status = 'Available' WHERE id = :itemId")
        update_query.bindValue(":itemId", itemId)
        
        if not update_query.exec_():
            QMessageBox.critical(self, "Database Error", update_query.lastError().text())
            print("Error setting item as available:", itemId, "Error:", update_query.lastError().text())

    def printLabel(self):
        printer = QPrinter(QPrinter.HighResolution)
        printDialog = QPrintDialog(printer, self)

        if printDialog.exec_() == QPrintDialog.Accepted:
            self.labelTextBox.print_(printer)
    
    def initDb(self):
        # Connect to the database
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('inventory.db')

        if not self.db.open():
            QMessageBox.critical(self, "Database Error", self.db.lastError().text())
            return

        # Create or modify the inventory table
        query = QSqlQuery()
        if not query.exec_("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                name TEXT,
                expiration_date TEXT,
                purchase_location TEXT,
                purchase_date TEXT,
                purchase_lot_number TEXT,
                date_added TEXT,
                date_opened TEXT,
                status TEXT DEFAULT 'Available',
                batch_id INTEGER,
                FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
            )
        """):
            QMessageBox.critical(self, "Database Error", query.lastError().text())

        # Ensure the batches table is also correctly created
        if not query.exec_("""
            CREATE TABLE IF NOT EXISTS batches (
                batch_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                sell_date TEXT,
                sell_location TEXT,
                batch_size TEXT,
                fig_and_brie_batch_number TEXT,
                batch_color TEXT
            )
        """):
            QMessageBox.critical(self, "Database Error", query.lastError().text())

    # Additional database initialization if needed
        
    def addInventoryToDb(self, data):
        print("Data to be inserted:", data)

        # Explicitly set batch_id to None in the data dictionary
        data['batch_id'] = None

        query = QSqlQuery()
        query.prepare("""
            INSERT INTO inventory (
                name, expiration_date, purchase_location, 
                purchase_date, purchase_lot_number, date_added, batch_id
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """)

        query.addBindValue(data['name'])
        query.addBindValue(data['expiration_date'])
        query.addBindValue(data['purchase_location'])
        query.addBindValue(data['purchase_date'])
        query.addBindValue(data['purchase_lot_number'])
        query.addBindValue(data['date_added'])
        query.addBindValue(data['batch_id'])  # Bind batch_id as well

        print("Prepared Query:", query.lastQuery())
        print("Bound Values:", data['name'], data['expiration_date'], data['purchase_location'], data['purchase_date'], 
              data['purchase_lot_number'], data['date_added'], data['batch_id'])

        if not query.exec_():
            QMessageBox.critical(self, "Database Error", query.lastError().text())

        self.model.load_data()
        self.inventoryTableView.resizeColumnsToContents()
        self.inventoryTableView.resizeRowsToContents()
        
    def printModelColumns(self, model):
        num_columns = model.columnCount()
        print("Model Columns:")
        for col in range(num_columns):
            column_name = model.headerData(col, Qt.Horizontal)
            print(f"Column {col}: {column_name}")

# Run the application
def main():
    app = QApplication(sys.argv)
    ex = InventoryApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

#####
# Inventory Adding
#####

