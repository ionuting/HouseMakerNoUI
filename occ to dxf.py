import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QLabel, QGridLayout, QPushButton, QHBoxLayout, QLineEdit
)
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QRectF

class Square:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.is_selected = False

    def get_area(self):
        return self.size ** 2

    def get_coordinates(self):
        return f"({self.x}, {self.y})"

    def contains(self, point):
        return QRectF(self.x, self.y, self.size, self.size).contains(point)


class SquareWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.square = None  # Pătratul desenat
        self.selected_square = None  # Pătratul selectat
        self.setMinimumSize(400, 400)

    def set_square(self, square):
        self.square = square
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.square:
            # Desenăm pătratul
            pen = QPen(QColor(0, 0, 0), 3)
            painter.setPen(pen)
            painter.setBrush(QColor(200, 200, 255))
            painter.drawRect(self.square.x, self.square.y, self.square.size, self.square.size)

            # Dacă pătratul este selectat, îl evidențiem
            if self.square.is_selected:
                pen.setStyle(Qt.DotLine)
                painter.setPen(pen)
                painter.drawRect(self.square.x, self.square.y, self.square.size, self.square.size)

    def mousePressEvent(self, event):
        if self.square and self.square.contains(event.pos()):
            self.square.is_selected = True
            self.parent().show_properties(self.square)
        else:
            self.square.is_selected = False
        self.update()


class PropertyTable(QTableWidget):
    def __init__(self, square, parent=None):
        super().__init__(parent)
        self.square = square
        self.setRowCount(3)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Proprietate", "Valoare"])
        self.init_table()

    def init_table(self):
        # Inițializăm tabelul de proprietăți
        self.setItem(0, 0, QTableWidgetItem("Coordonate"))
        self.setItem(0, 1, QTableWidgetItem(self.square.get_coordinates()))
        
        self.setItem(1, 0, QTableWidgetItem("Dimensiune"))
        self.setItem(1, 1, QTableWidgetItem(f"{self.square.size} cm"))

        self.setItem(2, 0, QTableWidgetItem("Arie"))
        self.setItem(2, 1, QTableWidgetItem(f"{self.square.get_area()} cm²"))

    def update_properties(self):
        # Actualizăm dimensiunile pătratului în funcție de modificările utilizatorului
        size_item = self.item(1, 1)
        try:
            new_size = int(size_item.text().replace(" cm", ""))
            self.square.size = new_size
        except ValueError:
            pass
        self.init_table()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Desenează și selectează un pătrat")

        # Cream widgetul pentru desen
        self.square_widget = SquareWidget(self)

        # Layout principal
        layout = QVBoxLayout()

        # Form pentru introducerea coordonatelor și dimensiunii pătratului
        form_layout = QGridLayout()
        self.x_input = QLineEdit("50")
        self.y_input = QLineEdit("50")
        self.size_input = QLineEdit("100")
        form_layout.addWidget(QLabel("X:"), 0, 0)
        form_layout.addWidget(self.x_input, 0, 1)
        form_layout.addWidget(QLabel("Y:"), 1, 0)
        form_layout.addWidget(self.y_input, 1, 1)
        form_layout.addWidget(QLabel("Dimensiune:"), 2, 0)
        form_layout.addWidget(self.size_input, 2, 1)

        # Butonul pentru a desena pătratul
        draw_button = QPushButton("Desenează pătratul")
        draw_button.clicked.connect(self.draw_square)

        # Layout pentru fereastra de proprietăți
        self.property_table = None

        layout.addLayout(form_layout)
        layout.addWidget(draw_button)
        layout.addWidget(self.square_widget)

        # Widget central
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.addLayout(layout)

        # Adăugăm la layout-ul principal și fereastra de proprietăți
        self.properties_widget = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_widget)
        central_layout.addWidget(self.properties_widget)

        self.setCentralWidget(central_widget)

    def draw_square(self):
        # Citim coordonatele și dimensiunea
        x = int(self.x_input.text())
        y = int(self.y_input.text())
        size = int(self.size_input.text())

        # Cream pătratul și îl desenăm
        square = Square(x, y, size)
        self.square_widget.set_square(square)

    def show_properties(self, square):
        if self.property_table:
            self.property_table.deleteLater()
        self.property_table = PropertyTable(square, self)
        self.properties_layout.addWidget(self.property_table)
        self.property_table.cellChanged.connect(self.property_table.update_properties)


# Funcția principală care rulează aplicația
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
