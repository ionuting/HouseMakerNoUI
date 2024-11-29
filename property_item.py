from PyQt5.QtWidgets import QTreeWidgetItem, QTreeWidget
from PyQt5.QtCore import Qt, pyqtSignal


class PropertyItem(QTreeWidgetItem):
    def __init__(self, parent, name, value=""):
        super().__init__(parent)
        self.setText(0, name)
        self.setText(1, str(value))
        self.setFlags(self.flags() | Qt.ItemIsEditable)


class PropertiesTree(QTreeWidget):
    propertyChanged = pyqtSignal(str, str, str)  # property_name, value, guid

    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["Property", "Value"])
        self.setColumnWidth(0, 150)
        self.setAlternatingRowColors(True)
        self.current_guid = None

        # Style the tree
        self.setStyleSheet(""" 
            QTreeWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #f5f5f5;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ccc;
            }
        """)

    def add_property(self, guid, name, value):
        item = PropertyItem(self, name, value)
        item.guid = guid  # Associate the GUID with the property item
        item.setFlags(item.flags() | Qt.ItemIsEditable)  # Make it editable
        item.setData(0, Qt.UserRole, guid)  # Store GUID in the UserRole data
        self.addTopLevelItem(item)

    def itemChanged(self, item, column):
        super().itemChanged(item, column)
        if column == 1 and item.data(0, Qt.UserRole):
            guid = item.data(0, Qt.UserRole)
            self.propertyChanged.emit(item.text(0), item.text(1), guid)  # Emit signal when item changes
