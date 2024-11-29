import json
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QPainter
from intersection_point import IntersectionPoint
from rectangle_item import RectangleItem
from properties_panel import PropertiesPanel
from property_item import PropertyItem


class Grid(QGraphicsView):
    def __init__(self, x_coords, y_coords, scale_factor=20):
        super().__init__()
        self.setScene(QGraphicsScene())
        self.setRenderHint(QPainter.Antialiasing)

        self.x_coords = x_coords
        self.y_coords = y_coords
        self.scale_factor = scale_factor
        self.scale_factor_multiplier = 1.1  # Zoom factor

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


    def wheelEvent(self, event):
        """Handle zooming in and out with the mouse wheel."""
        zoom_in = event.angleDelta().y() > 0
        if zoom_in:
            self.scale(self.scale_factor_multiplier, self.scale_factor_multiplier)
        else:
            self.scale(1 / self.scale_factor_multiplier, 1 / self.scale_factor_multiplier)

    def resizeEvent(self, event):
        """Ensure the grid view fits the new size."""
        super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

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
            self.update_json_file()
            self.refresh_properties()
    
    def clear_properties(self):
        self.clear()  # Clear existing properties

    def set_current_guid(self, guid):
        self.current_guid = guid    
    
    def refresh_properties(self):
        selected_rect = self.get_selected_rectangle()
        self.update_properties(selected_rect)

    def add_rectangle(self):
        # Create a rectangle item
        rect_item = RectangleItem(0, 0, 15, 15)  # Default size of 50x30
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
                i = 0
                for guid, props in data.items():
                    i += 1
                    rect_item = RectangleItem(0, 0, 5, 5)  # Default size
                    rect_item.guid = guid
                    rect_item.name = props.get("name", "Rectangle" + str(i))  # Use default name if not found
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
