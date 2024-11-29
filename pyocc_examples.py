import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QTableWidget, QTableWidgetItem, QPushButton, QLabel)
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect, QPoint
import ezdxf

class SquareWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.rect_width = 100  # Lungimea dreptunghiului
        self.rect_height = 100  # Lățimea dreptunghiului
        self.square_pos = QPoint(100, 100)  # Poziția inițială a dreptunghiului
        self.is_dragging = False
        self.drag_start_pos = None

    def paintEvent(self, event):
        """Funcția care desenează dreptunghiul."""
        painter = QPainter(self)
        painter.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))
        painter.setBrush(QColor(100, 150, 200))

        # Inversăm coordonatele pe axa Y pentru a simula sistemul de coordonate AutoCAD
        inv_y = self.height() - self.square_pos.y()

        # Desenează dreptunghiul la poziția actuală
        rect = QRect(self.square_pos.x(), inv_y - self.rect_height, self.rect_width, self.rect_height)
        painter.drawRect(rect)

    def mousePressEvent(self, event):
        """Funcția care detectează apăsarea mouse-ului."""
        inv_y = self.height() - self.square_pos.y()
        if event.button() == Qt.LeftButton:
            rect = QRect(self.square_pos.x(), inv_y - self.rect_height, self.rect_width, self.rect_height)
            if rect.contains(event.pos()):
                self.is_dragging = True
                self.drag_start_pos = event.pos() - self.square_pos  # Calculăm diferența dintre click și poziția dreptunghiului

    def mouseMoveEvent(self, event):
        """Funcția care permite mutarea dreptunghiului în timpul dragării."""
        if self.is_dragging:
            self.square_pos = QPoint(event.pos().x(), self.height() - event.pos().y() + self.drag_start_pos.y())
            self.update()  # Reîmprospătează ecranul pentru a redesena dreptunghiul la noua poziție

    def mouseReleaseEvent(self, event):
        """Funcția care finalizează mutarea dreptunghiului."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False

    def update_rectangle(self, x, y, width, height):
        """Actualizează dimensiunile dreptunghiului în funcție de inputurile din tabel."""
        self.square_pos = QPoint(x, self.height() - y)  # Transformăm coordonata Y
        self.rect_width = width
        self.rect_height = height
        self.update()  # Reîmprospătează ecranul pentru a redesena dreptunghiul la noile dimensiuni

    def export_to_dxf(self, filename="rectangle.dxf"):
        """Funcția care exportă dreptunghiul într-un fișier DXF folosind ezdxf."""
        doc = ezdxf.new()
        msp = doc.modelspace()

        # Coordonații dreptunghiului, în coordonatele inversate pentru DXF
        x1, y1 = self.square_pos.x(), self.height() - self.square_pos.y()
        x2, y2 = x1 + self.rect_width, y1 - self.rect_height

        # Adaugă dreptunghiul la modelul DXF
        msp.add_lwpolyline([(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)], close=True)

        # Salvează fișierul DXF
        doc.saveas(filename)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Setează titlul și dimensiunea ferestrei
        self.setWindowTitle('PyQt5 Parametric Rectangle with Editable Table')
        self.setGeometry(100, 100, 800, 600)

        # Layout principal pe orizontală
        main_layout = QHBoxLayout()

        # Creează widgetul central pentru desen
        self.square_widget = SquareWidget()

        # Creează un layout vertical pentru panoul lateral
        side_layout = QVBoxLayout()

        # Creează un tabel pentru a afișa dimensiunile dreptunghiului
        self.table_widget = QTableWidget(4, 2)  # 4 rânduri, 2 coloane (X, Y, Width, Height)
        self.table_widget.setHorizontalHeaderLabels(['Parametru', 'Valoare'])
        self.table_widget.setVerticalHeaderLabels(['X', 'Y', 'Lungime', 'Lățime'])
        self.update_table_values()

        # Creează un buton pentru actualizarea dimensiunilor
        update_button = QPushButton('Actualizează Dimensiuni')
        update_button.clicked.connect(self.update_rectangle)

        # Creează un buton pentru export în DXF
        export_button = QPushButton('Exportă în DXF')
        export_button.clicked.connect(self.export_rectangle_to_dxf)

        # Adaugă tabelul și butoanele la layout-ul lateral
        side_layout.addWidget(QLabel("Parametrii dreptunghiului"))
        side_layout.addWidget(self.table_widget)
        side_layout.addWidget(update_button)
        side_layout.addWidget(export_button)

        # Adaugă widget-ul lateral și cel principal la layout-ul principal
        main_layout.addWidget(self.square_widget, stretch=3)
        main_layout.addLayout(side_layout, stretch=1)

        # Creează un container pentru layout-ul principal
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def update_table_values(self):
        """Actualizează valorile din tabel cu cele curente ale dreptunghiului."""
        self.table_widget.setItem(0, 1, QTableWidgetItem(str(self.square_widget.square_pos.x())))
        self.table_widget.setItem(1, 1, QTableWidgetItem(str(self.height() - self.square_widget.square_pos.y())))  # Conversia Y
        self.table_widget.setItem(2, 1, QTableWidgetItem(str(self.square_widget.rect_width)))
        self.table_widget.setItem(3, 1, QTableWidgetItem(str(self.square_widget.rect_height)))

    def update_rectangle(self):
        """Actualizează dimensiunile dreptunghiului pe baza valorilor din tabel."""
        try:
            x = int(self.table_widget.item(0, 1).text())
            y = int(self.table_widget.item(1, 1).text())
            width = int(self.table_widget.item(2, 1).text())
            height = int(self.table_widget.item(3, 1).text())
            self.square_widget.update_rectangle(x, y, width, height)
        except ValueError:
            print("Valori invalide introduse în tabel.")

    def export_rectangle_to_dxf(self):
        """Exportă dreptunghiul în fișier DXF."""
        self.square_widget.export_to_dxf()
        print("Dreptunghiul a fost exportat în rectangle.dxf")

# Rulează aplicația PyQt5
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
