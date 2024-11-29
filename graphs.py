import sys
import json
import uuid
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsTextItem,
    QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel,
    QDockWidget, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPen, QBrush, QPainter


class IntersectionPoint(QGraphicsEllipseItem):
    def __init__(self, x, y, index, radius=4):
        super().__init__(x - radius, y - radius, radius * 2, radius * 2)
        self.setBrush(QBrush(Qt.red))
        self.setFlags(QGraphicsEllipseItem.ItemIsSelectable)
        self.setZValue(2)
        self.index = index

        # Create label for the index
        self.label = QGraphicsTextItem(str(index), self)
        self.label.setPos(x - radius, y - radius - 10)  # Position label above the point

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.setPen(QPen(Qt.blue, 2))
            painter.drawEllipse(self.rect())


class RectangleItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.setBrush(QBrush(Qt.blue))
        self.setFlags(QGraphicsRectItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable)

        # Initialize additional properties
        self.guid = str(uuid.uuid4())  # Unique identifier for each rectangle
        self.name = ""
        self.point_indices = []  # List of intersection point indices

    def update_points(self, intersection_points):
        """Update rectangle's corner points based on intersection point indices."""
        self.points = [intersection_points[i] for i in self.point_indices]

    def get_properties(self):
        return self.guid, self.name, self.point_indices


class Grid(QGraphicsView):
    def __init__(self, x_coords, y_coords, scale_factor=20):
        super().__init__()
        self.setScene(QGraphicsScene())
        self.setRenderHint(QPainter.Antialiasing)
        self.setFixedSize(800, 600)

        self.x_coords = x_coords
        self.y_coords = y_coords
        self.scale_factor = scale_factor
        self.intersection_points = [(x * self.scale_factor, max(y_coords) * self.scale_factor - (y * self.scale_factor))
                                    for x in x_coords for y in y_coords]  # Store the actual intersection points
        self.rectangles = []  # List to hold rectangle items

        # Draw grid based on the provided coordinates
        self.draw_grid()

        # Set the scene rectangle to encompass the grid
        self.setSceneRect(0, 0, max(x_coords) * self.scale_factor, max(y_coords) * self.scale_factor)
        self.fitInView(0, 0, max(x_coords) * self.scale_factor, max(y_coords) * self.scale_factor, Qt.KeepAspectRatio)

    def draw_grid(self):
        grid_pen = QPen(Qt.lightGray, 0.5)  # Pen for grid lines
        grid_pen.setStyle(Qt.DashLine)

        # Draw vertical lines based on x coordinates
        for x in self.x_coords:
            self.scene().addLine(x * self.scale_factor, 0, x * self.scale_factor, max(self.y_coords) * self.scale_factor, grid_pen)

        # Draw horizontal lines based on y coordinates (invert y direction)
        for y in self.y_coords:
            self.scene().addLine(0, max(self.y_coords) * self.scale_factor - (y * self.scale_factor),
                                 max(self.x_coords) * self.scale_factor, max(self.y_coords) * self.scale_factor - (y * self.scale_factor), grid_pen)

        # Draw intersection points (invert y direction) and make them selectable
        for i, x in enumerate(self.x_coords):
            for j, y in enumerate(self.y_coords):
                intersection_point = IntersectionPoint(x * self.scale_factor,
                                                       max(self.y_coords) * self.scale_factor - (y * self.scale_factor),
                                                       index=(i, j))
                self.scene().addItem(intersection_point)

    def add_rectangle(self):
        # Create a rectangle item
        rect_item = RectangleItem(0, 0, 50, 30)  # Default size of 50x30
        self.scene().addItem(rect_item)
        self.rectangles.append(rect_item)  # Keep track of created rectangles

        # Automatically select the new rectangle
        rect_item.setSelected(True)

    def get_selected_rectangle(self):
        for item in self.scene().selectedItems():
            if isinstance(item, RectangleItem):
                return item
        return None

    def delete_selected_rectangle(self):
        selected_rect = self.get_selected_rectangle()
        if selected_rect:
            self.scene().removeItem(selected_rect)
            self.rectangles.remove(selected_rect)
            self.update_json_file()  # Update JSON after deletion

    def update_json_file(self):
        """Updates the JSON file with the current rectangles' properties."""
        data = {
            rect.guid: {
                "name": rect.name,
                "point_indices": rect.point_indices,
                **{k: v for k, v in rect.__dict__.items() if not k.startswith('_') and k not in ["guid", "name", "point_indices"]},
            }
            for rect in self.rectangles
        }
        with open('rectangles.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def clear_json_file(self):
        """Clear existing data in the JSON file on startup."""
        with open('rectangles.json', 'w') as json_file:
            json.dump({}, json_file)  # Write an empty dictionary to clear the file

    def load_json_file(self):
        """Loads rectangles from a JSON file."""
        try:
            with open('rectangles.json', 'r') as json_file:
                data = json.load(json_file)
                i=0
                for guid, props in data.items():
                    i=i+1
                    rect_item = RectangleItem(0, 0, 50, 30)  # Default size
                    rect_item.guid = guid
                    rect_item.name = props.get("name", "Rectangle" + i)  # Use default name if not found
                    rect_item.point_indices = props.get("point_indices", [])  # Initialize point_indices
                    rect_item.update_points(self.intersection_points)  # Update rectangle points based on indices

                    # Set other properties from JSON
                    for k, v in props.items():
                        if k not in ["name", "point_indices"]:
                            rect_item.__dict__[k] = v

                    self.scene().addItem(rect_item)
                    self.rectangles.append(rect_item)
        except FileNotFoundError:
            # If the file does not exist, just continue
            pass


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
        for idx, point_index in enumerate(rect_item.point_indices):
            PropertyItem(points_group, f"Point {idx + 1}", str(point_index))

        # Connect item change signal to update_property method
        self.itemChanged.connect(self.on_item_changed)

    def on_item_changed(self, item, column):
        if column == 1 and item.parent():  # If value changed
            property_name = item.text(0)
            value = item.text(1)
            if self.current_guid:
                self.propertyChanged.emit(property_name, value, self.current_guid)


class PropertiesPanel(QWidget):
    def __init__(self, grid):
        super().__init__()
        self.grid = grid
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Create Tree Widget
        self.properties_tree = PropertiesTree()
        self.properties_tree.propertyChanged.connect(self.update_property)

        # Add controls for adding properties
        add_property_layout = QHBoxLayout()

        self.new_property_name = QLineEdit(self)
        self.new_property_name.setPlaceholderText("Property Name")
        add_property_layout.addWidget(self.new_property_name)

        self.new_property_value = QLineEdit(self)
        self.new_property_value.setPlaceholderText("Property Value")
        add_property_layout.addWidget(self.new_property_value)

        self.add_property_btn = QPushButton("Add Property")
        self.add_property_btn.clicked.connect(self.add_property)
        add_property_layout.addWidget(self.add_property_btn)

        # Button to update properties
        self.update_properties_btn = QPushButton("Update Properties")
        self.update_properties_btn.clicked.connect(self.update_properties)
        add_property_layout.addWidget(self.update_properties_btn)

        # Add controls for rectangle actions
        controls_layout = QHBoxLayout()
        self.add_rectangle_btn = QPushButton("Add Rectangle")
        self.add_rectangle_btn.clicked.connect(self.add_rectangle)
        self.delete_btn = QPushButton("Delete Rectangle")
        self.delete_btn.clicked.connect(self.delete_rectangle)

        for btn in [self.add_rectangle_btn, self.delete_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    background-color: #0078d7;
                    color: white;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #0063b1;
                }
                QPushButton:pressed {
                    background-color: #004e8c;
                }
            """)
            controls_layout.addWidget(btn)

        layout.addWidget(self.properties_tree)
        layout.addLayout(add_property_layout)
        layout.addLayout(controls_layout)

        self.setMinimumWidth(300)

    def refresh_properties(self):
        selected_rect = self.grid.get_selected_rectangle()
        self.properties_tree.update_properties(selected_rect)

    def update_property(self, property_name, value, guid):
        selected_rect = self.grid.get_selected_rectangle()
        if not selected_rect or selected_rect.guid != guid:
            return

        if property_name == "Name":
            selected_rect.name = value
        elif property_name == "Position X":
            try:
                x = float(value)
                selected_rect.setPos(x, selected_rect.pos().y())
            except ValueError:
                pass
        elif property_name == "Position Y":
            try:
                y = float(value)
                selected_rect.setPos(selected_rect.pos().x(), y)
            except ValueError:
                pass
        elif property_name == "Width":
            try:
                width = float(value)
                selected_rect.setRect(0, 0, width, selected_rect.rect().height())
            except ValueError:
                pass
        elif property_name == "Height":
            try:
                height = float(value)
                selected_rect.setRect(0, 0, selected_rect.rect().width(), height)
            except ValueError:
                pass
        elif property_name.startswith("Point "):
            try:
                idx = int(property_name.split(" ")[1]) - 1
                point_value = int(value)
                if 0 <= idx < len(selected_rect.point_indices):
                    selected_rect.point_indices[idx] = point_value
                    selected_rect.update_points(self.grid.intersection_points)
            except (ValueError, IndexError):
                pass

        self.grid.update_json_file()
        self.refresh_properties()

    def add_property(self):
        selected_rect = self.grid.get_selected_rectangle()
        if selected_rect:
            property_name = self.new_property_name.text().strip()
            property_value = self.new_property_value.text().strip()

            if property_name and property_value:
                # Add the new property to the rectangle's properties
                PropertyItem(self.properties_tree, property_name, property_value)
                # Optionally store this in the rectangle for later use
                selected_rect.__dict__[property_name] = property_value

                # Clear input fields
                self.new_property_name.clear()
                self.new_property_value.clear()

                # Refresh the properties view
                self.refresh_properties()

    def update_properties(self):
        """Update all properties of the selected rectangle and save to JSON."""
        selected_rect = self.grid.get_selected_rectangle()
        if selected_rect:
            # Update properties based on the properties tree
            for idx in range(self.properties_tree.topLevelItemCount()):
                group_item = self.properties_tree.topLevelItem(idx)
                for j in range(group_item.childCount()):
                    property_item = group_item.child(j)
                    property_name = property_item.text(0)
                    property_value = property_item.text(1)

                    # Update rectangle attributes
                    if property_name == "Name":
                        selected_rect.name = property_value
                    elif property_name == "Position X":
                        try:
                            selected_rect.setPos(float(property_value), selected_rect.pos().y())
                        except ValueError:
                            pass
                    elif property_name == "Position Y":
                        try:
                            selected_rect.setPos(selected_rect.pos().x(), float(property_value))
                        except ValueError:
                            pass
                    elif property_name == "Width":
                        try:
                            selected_rect.setRect(0, 0, float(property_value), selected_rect.rect().height())
                        except ValueError:
                            pass
                    elif property_name == "Height":
                        try:
                            selected_rect.setRect(0, 0, selected_rect.rect().width(), float(property_value))
                        except ValueError:
                            pass

            # Update JSON after properties have been modified
            self.grid.update_json_file()
            self.refresh_properties()

    def add_rectangle(self):
        self.grid.add_rectangle()
        self.refresh_properties()

    def delete_rectangle(self):
        self.grid.delete_selected_rectangle()
        self.refresh_properties()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.grid = Grid(x_coords=(0, 4, 6, 10), y_coords=(0, 4, 6, 8))  # Example grid
        self.setCentralWidget(self.grid)

        self.properties_panel = PropertiesPanel(self.grid)
        self.dock = QDockWidget("Properties", self)
        self.dock.setWidget(self.properties_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)

        self.setWindowTitle("Rectangle Manager")
        self.setGeometry(100, 100, 1024, 768)

        self.grid.clear_json_file()  # Clear the JSON file at startup
        self.grid.load_json_file()  # Load rectangles from JSON on startup


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
