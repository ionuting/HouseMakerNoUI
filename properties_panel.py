from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from property_item import PropertiesTree, PropertyItem


class PropertiesPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Properties Panel")
        self.setMinimumWidth(150)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

       
        
                # Create Tree Widget
        self.properties_tree = PropertiesTree()
        self.properties_tree.propertyChanged.connect(self.update_property)
        self.layout.addWidget(self.properties_tree)

        # Add Rectangle button
        self.add_button = QPushButton("Add Rectangle")
        self.layout.addWidget(self.add_button)

        # Delete Rectangle button
        self.delete_button = QPushButton("Delete Rectangle")
        self.layout.addWidget(self.delete_button)

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
    
    def clear_properties(self):
        self.properties_tree.clear()  # Clear existing properties

    def set_current_guid(self, guid):
        self.properties_tree.current_guid = guid
