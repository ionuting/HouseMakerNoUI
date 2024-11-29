from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox, QVBoxLayout, QHBoxLayout, QWidget, QGraphicsView, QDockWidget
from grid import Grid
from properties_panel import PropertiesPanel
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rectangle Intersection Tool")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a horizontal layout
        self.layout = QHBoxLayout(self.central_widget)

        # Create properties panel as a dockable widget
        self.properties_panel = PropertiesPanel()
        self.properties_dock = QDockWidget("Properties", self)
        self.properties_dock.setWidget(self.properties_panel)
        self.properties_dock.setFixedWidth(250)  # Set a fixed width for the side panel
        self.properties_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)  # Disable undocking
        self.addDockWidget(Qt.LeftDockWidgetArea, self.properties_dock)  # Place it on the left edge

         # Connect buttons in properties panel to functions
        self.properties_panel.add_button.clicked.connect(self.add_rectangle)
        self.properties_panel.delete_button.clicked.connect(self.delete_selected_rectangle)


        # Create central widget for the grid
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Set layout for the central widget (for grid)
        self.layout = QVBoxLayout(self.central_widget)
        self.grid = Grid(x_coords=[0, 4, 6, 10], y_coords=[0, 4, 6, 8])
        self.layout.addWidget(self.grid)

        # Set stretch factors to control resizing behavior
        self.layout.setStretch(0, 0)  # PropertiesPanel - fixed size (no stretch)
        self.layout.setStretch(1, 1)  # Grid - expandable (stretches to fill space)

        self.create_menu()
        self.grid.load_json_file()  # Load rectangles from JSON

        self.grid.rectangles  # Example use of rectangles

    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        add_rect_action = QAction("Add Rectangle", self)
        add_rect_action.triggered.connect(self.add_rectangle)
        file_menu.addAction(add_rect_action)

        delete_rect_action = QAction("Delete Selected Rectangle", self)
        delete_rect_action.triggered.connect(self.delete_selected_rectangle)
        file_menu.addAction(delete_rect_action)

        # Fullscreen action
        fullscreen_action = QAction("Toggle Fullscreen", self)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        file_menu.addAction(fullscreen_action)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def add_rectangle(self):
        self.grid.add_rectangle()

    def delete_selected_rectangle(self):
        selected_rectangle = self.grid.get_selected_rectangle()
        if selected_rectangle:
            self.grid.delete_selected_rectangle()
            self.properties_panel.clear_properties()  # Clear properties after deletion
        else:
            QMessageBox.warning(self, "Warning", "No rectangle selected!")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_selected_rectangle()  # Call delete function when Delete key is pressed
        super().keyPressEvent(event)  # Call the parent keyPressEvent for other events
    
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
