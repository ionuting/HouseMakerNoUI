import sys
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, 
                             QGraphicsRectItem, QGraphicsTextItem, QMainWindow, QWidget, 
                             QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
                             QSlider, QDoubleSpinBox, QGroupBox, QGridLayout, QDockWidget)
from PyQt5.QtGui import QBrush, QColor, QPen, QFont
from PyQt5.QtCore import Qt, pyqtSignal

class DifferenceInputWithSlider(QWidget):
    valueChanged = pyqtSignal(float)

    def __init__(self, label, min_value, max_value, default_value, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label)
        self.label.setFont(QFont('Arial', 12))
        self.layout.addWidget(self.label)

        self.spinbox = QDoubleSpinBox()
        self.spinbox.setRange(min_value, max_value)
        self.spinbox.setValue(default_value)
        self.spinbox.setDecimals(2)
        self.spinbox.setSingleStep(0.05)
        self.spinbox.setFont(QFont('Arial', 12))
        self.layout.addWidget(self.spinbox)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(int(min_value * 20), int(max_value * 20))
        self.slider.setValue(int(default_value * 20))
        self.layout.addWidget(self.slider)

        self.setLayout(self.layout)

        self.slider.valueChanged.connect(self.slider_value_changed)
        self.spinbox.valueChanged.connect(self.spinbox_value_changed)

    def slider_value_changed(self, value):
        self.spinbox.setValue(value / 20)
        self.valueChanged.emit(value / 20)

    def spinbox_value_changed(self, value):
        self.slider.setValue(int(value * 20))
        self.valueChanged.emit(value)

    def value(self):
        return self.spinbox.value()

    def setValue(self, value):
        self.spinbox.setValue(value)

class RoomViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Room Viewer")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Graphic view setup
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.main_layout.addWidget(self.view)

        # Control panel setup
        self.control_panel = QWidget()
        self.control_layout = QVBoxLayout()
        self.control_panel.setLayout(self.control_layout)

        # Create a dock widget
        dock = QDockWidget("Control Panel", self)
        dock.setWidget(self.control_panel)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        # Set the background color of the control panel to light blue
        self.control_panel.setStyleSheet("background-color: #E6F3FF;")

        self.x_inputs = []
        self.y_inputs = []

        # Default coordinates
        self.x = [0., 3.5, 5.5, 9.5]
        self.y = [0., 4., 5.5, 9.]

        # X coordinates group
        x_group = QGroupBox("X Coordinates")
        x_group.setFont(QFont('Arial', 12))
        x_layout = QVBoxLayout()
        x_layout.addWidget(QLabel("x[0]: 0.00"))
        for i in range(1, 4):
            x_input = DifferenceInputWithSlider(f"x[{i}] - x[{i-1}]:", 0, 20, self.x[i] - self.x[i-1])
            x_layout.addWidget(x_input)
            self.x_inputs.append(x_input)
            x_input.valueChanged.connect(self.update_view)
        x_group.setLayout(x_layout)
        self.control_layout.addWidget(x_group)

        # Y coordinates group
        y_group = QGroupBox("Y Coordinates")
        y_group.setFont(QFont('Arial', 12))
        y_layout = QVBoxLayout()
        y_layout.addWidget(QLabel("y[0]: 0.00"))
        for i in range(1, 4):
            y_input = DifferenceInputWithSlider(f"y[{i}] - y[{i-1}]:", 0, 20, self.y[i] - self.y[i-1])
            y_layout.addWidget(y_input)
            self.y_inputs.append(y_input)
            y_input.valueChanged.connect(self.update_view)
        y_group.setLayout(y_layout)
        self.control_layout.addWidget(y_group)

        # Area information
        self.area_group = QGroupBox("Area Information")
        self.area_group.setFont(QFont('Arial', 12))
        area_layout = QVBoxLayout()
        self.useful_area_label = QLabel("Arie Utilă: ")
        self.useful_area_label.setFont(QFont('Arial', 12))
        self.total_area_label = QLabel("Arie Desfășurată: ")
        self.total_area_label.setFont(QFont('Arial', 12))
        area_layout.addWidget(self.useful_area_label)
        area_layout.addWidget(self.total_area_label)
        self.area_group.setLayout(area_layout)
        self.control_layout.addWidget(self.area_group)

        self.room_colors = [QColor("#ff9999"), QColor("#99ff99"), QColor("#9999ff"), 
                            QColor("#ffcc99"), QColor("#ccff99"), QColor("#99ccff")]

        self.update_view()

    def update_view(self):
        self.x = [0.]
        for input in self.x_inputs:
            self.x.append(self.x[-1] + input.value())

        self.y = [0.]
        for input in self.y_inputs:
            self.y.append(self.y[-1] + input.value())
        
        self.scene.clear()
        self.generate_room_data()
        self.draw_background_rect()
        self.draw_rooms()
        self.draw_vertices()
        self.update_area_information()

    def generate_room_data(self):
        offset = 0.125
        dim_reduc = 0.25

        self.date = [
            {
                "room": "room 01",
                "length": (self.x[1] - self.x[0]) - dim_reduc,
                "width": (self.y[1] - self.y[0]) - dim_reduc,
                "insertion_point": (self.x[0] + offset, self.y[0] + offset, 0)
            },
            {
                "room": "room 02",
                "length": (self.x[2] - self.x[1]) - dim_reduc,
                "width": (self.y[2] - self.y[0]) - dim_reduc,
                "insertion_point": (self.x[1] + offset, self.y[0] + offset, 0)
            },
            {
                "room": "room 03",
                "length": (self.x[3] - self.x[2]) - dim_reduc,
                "width": (self.y[1] - self.y[0]) - dim_reduc,
                "insertion_point": (self.x[2] + offset, self.y[0] + offset, 0)
            },
            {
                "room": "room 04",
                "length": (self.x[1] - self.x[0]) - dim_reduc,
                "width": (self.y[3] - self.y[1]) - dim_reduc,
                "insertion_point": (self.x[0] + offset, self.y[1] + offset, 0)
            },
            {
                "room": "room 05",
                "length": (self.x[2] - self.x[1]) - dim_reduc,
                "width": (self.y[3] - self.y[2]) - dim_reduc,
                "insertion_point": (self.x[1] + offset, self.y[2] + offset, 0)
            },
            {
                "room": "room 06",
                "length": (self.x[3] - self.x[2]) - dim_reduc,
                "width": (self.y[3] - self.y[1]) - dim_reduc,
                "insertion_point": (self.x[2] + offset, self.y[1] + offset, 0)
            },
        ]

        self.vertices = {}
        self.rooms = []
        vertex_index = 0

        for camera in self.date:
            room_name = camera["room"]
            length = camera["length"]
            width = camera["width"]
            x0, y0, z0 = camera["insertion_point"]

            v0 = (x0, y0)
            v1 = (x0 + length, y0)
            v2 = (x0 + length, y0 + width)
            v3 = (x0, y0 + width)

            for vertex in [v0, v1, v2, v3]:
                if vertex not in self.vertices:
                    self.vertices[vertex] = vertex_index
                    vertex_index += 1

            self.rooms.append({
                "name": room_name,
                "vertices": [v0, v1, v2, v3],
                "length": length,
                "width": width,
                "area": length * width
            })

    def draw_background_rect(self):
        offset = 0.125
        p0 = (self.x[0] - offset, self.y[0] - offset)
        p1 = (self.x[3] + offset, self.y[0] - offset)
        p2 = (self.x[3] + offset, self.y[3] + offset)
        p3 = (self.x[0] - offset, self.y[3] + offset)

        p0 = (p0[0], -p0[1])
        p1 = (p1[0], -p1[1])
        p2 = (p2[0], -p2[1])
        p3 = (p3[0], -p3[1])

        width = p1[0] - p0[0]
        height = p0[1] - p3[1]

        self.total_area = width * height  # Calculate total area

        rect = QGraphicsRectItem(p0[0] * 100, p3[1] * 100, width * 100, height * 100)
        brush = QBrush(QColor("lightgray"))
        rect.setBrush(brush)
        rect.setPen(QPen(Qt.black, 2))

        self.scene.addItem(rect)

    def draw_rooms(self):
        for i, room in enumerate(self.rooms):
            vertices = room["vertices"]
            x0, y0 = vertices[0]
            x1, y1 = vertices[2]

            y0, y1 = -y0, -y1

            rect = QGraphicsRectItem(x0 * 100, y0 * 100, (x1 - x0) * 100, (y1 - y0) * 100)
            brush = QBrush(self.room_colors[i % len(self.room_colors)])
            rect.setBrush(brush)
            rect.setPen(QPen(Qt.black, 2))

            self.scene.addItem(rect)

            text_x = (x0 + x1) / 2 * 100
            text_y = (y0 + y1) / 2 * 100

            room_info = f"{room['name']}\nL={room['length']:.2f}m, W={room['width']:.2f}m\nArea={room['area']:.2f}m²"
            text_item = QGraphicsTextItem(room_info)
            text_item.setPos(text_x - 50, text_y - 20)
            text_item.setDefaultTextColor(Qt.black)
            text_item.setFont(QFont('Arial', 12))

            self.scene.addItem(text_item)

    def draw_vertices(self):
        sorted_vertices = sorted(self.vertices.items(), key=lambda item: item[1])
        for vertex, index in sorted_vertices:
            x, y = vertex
            y = -y

            circle = QGraphicsEllipseItem(x * 100 - 5, y * 100 - 5, 10, 10)
            circle.setBrush(QBrush(QColor("lime")))
            circle.setPen(QPen(Qt.black))

            self.scene.addItem(circle)

            text = QGraphicsTextItem(str(index))
            text.setPos(x * 100 - 5, y * 100 - 20)
            text.setFont(QFont('Arial', 12))
            self.scene.addItem(text)

    def update_area_information(self):
        useful_area = sum(room['area'] for room in self.rooms)
        self.useful_area_label.setText(f"Arie Utilă: {useful_area:.2f} m²")
        self.total_area_label.setText(f"Arie Desfășurată: {self.total_area:.2f} m²")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = RoomViewer()
    viewer.show()
    sys.exit(app.exec_())