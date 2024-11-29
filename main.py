import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from building_generator import BuildingGenerator  # Asigură-te că acest modul există
from Viewer_dxf import CADViewerWidget

# Creează un widget de tip tab-uri
class MainApp(QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Creează instanțele pentru cele două feronare principale
        self.window1 = BuildingGenerator()  # Asigură-te că clasa BuildingGenerator este corect implementată
        self.window2 = CADViewerWidget()  # Asigură-te că clasa BuildingGenerator este corect implementată

        # Adaugă feronarele în widget-ul de tip tab
        self.tab_widget.addTab(self.window1, "3D Viewer")
        self.tab_widget.addTab(self.window2, "Dxf Viewer")

if __name__ == '__main__':
    app = QApplication(sys.argv)  # Creează aplicația
    main_window = MainApp()  # Creează fereastra principală
    main_window.show()  # Afișează fereastra principală
    sys.exit(app.exec_())  # Execută aplicația
