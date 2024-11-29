from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal


class PropertyItem(QTreeWidgetItem):
    def __init__(self, parent, name, value):
        super().__init__(parent, [name, value])
        self.setFlags(self.flags() | Qt.ItemIsEditable)  # Allow editing of the value


class PropertiesTree(QTreeWidget):
    propertyChanged = pyqtSignal(str, str, str)  # property_name, value, guid
    ignore_changes = False  # Flag to ignore changes during updates

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

    def update_properties(self, rect_item):
        self.clear()
        if not rect_item:
            return

        self.current_guid = rect_item.guid

        # General Properties Group
        general_group = QTreeWidgetItem(self, ["General"])
        general_group.setExpanded(True)

        PropertyItem(general_group, "GUID", rect_item.guid)  # Non-editable
        PropertyItem(general_group, "Name", rect_item.name)

        # Geometry Properties Group
        geometry_group = QTreeWidgetItem(self, ["Geometry"])
        geometry_group.setExpanded(True)

        x, y = rect_item.pos().x(), rect_item.pos().y()
        PropertyItem(geometry_group, "Position X", x)
        PropertyItem(geometry_group, "Position Y", y)
        PropertyItem(geometry_group, "Width", rect_item.rect().width())
        PropertyItem(geometry_group, "Height", rect_item.rect().height())

        # Points Properties Group
        points_group = QTreeWidgetItem(self, ["Points"])
        points_group.setExpanded(True)

        # Display points as a string representation of the list of indices
        points_string = str(rect_item.point_indices)
        PropertyItem(points_group, "Point Indices", points_string)

        # Connect item change signal to update_property method
        self.itemChanged.connect(self.on_item_changed)

    def on_item_changed(self, item, column):
        if self.ignore_changes:
            return  # Prevent recursion
        if column == 1 and item.parent():  # If value changed
            property_name = item.text(0)
            value = item.text(1)
            if self.current_guid:
                self.propertyChanged.emit(property_name, value, self.current_guid)
