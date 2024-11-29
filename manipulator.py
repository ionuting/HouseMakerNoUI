import os
import sys
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere
from OCC.Core.gp import gp_Pnt
from OCC.Core.AIS import AIS_Manipulator
from OCC.Extend.LayerManager import Layer
from OCC.Display.backend import load_backend

load_backend("pyqt5")
import OCC.Display.qtDisplay as qtDisplay

from PyQt5.QtWidgets import (
    QApplication,
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QDialog,
)


class TranslationManipulator(AIS_Manipulator):
    def __init__(self):
        super().__init__()

    def Move(self, dx, dy, dz):
        # Permitem doar translatii pe axa Z
        self.SetTranslation(gp_Vec(0, 0, dz))
        self.Update()


class App(QDialog):
    def __init__(self):
        super().__init__()
        self.title = "PyQt5 / pythonOCC / Manipulator"
        self.left = 500
        self.top = 300
        self.width = 1600
        self.height = 800
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.createLayout()

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)
        self.show()
        self.createGeometry()

    def createGeometry(self):
        self.canvas.InitDriver()
        self.display = self.canvas._display

        # Crearea geometriei
        box = BRepPrimAPI_MakeBox(15.0, 15.0, 15.0).Shape()
        self.layer = Layer(self.display, box)
        sphere = BRepPrimAPI_MakeSphere(gp_Pnt(25, 25, 25), 5).Shape()
        self.layer.add_shape(sphere)
        self.show_layer()

    def createLayout(self):
        self.horizontalGroupBox = QGroupBox("Display PythonOCC")
        layout_h = QHBoxLayout()
        layout_v = QVBoxLayout()

        self.activate_manip_button = QPushButton("Activate Manipulator", self)
        self.activate_manip_button.setCheckable(True)
        self.activate_manip_button.clicked.connect(self.activate_manipulator)
        layout_v.addWidget(self.activate_manip_button)

        self.show_layer_button = QPushButton("Show Layer", self)
        self.show_layer_button.setCheckable(True)
        self.show_layer_button.setChecked(True)
        self.show_layer_button.clicked.connect(self.show_layer)
        layout_v.addWidget(self.show_layer_button)
        layout_h.addLayout(layout_v)

        self.canvas = qtDisplay.qtViewer3dWithManipulator(self)
        layout_h.addWidget(self.canvas)
        self.horizontalGroupBox.setLayout(layout_h)

    def show_layer(self):
        if self.show_layer_button.isChecked():
            self.layer.show()
            self.display.FitAll()
        else:
            self.layer.hide()
            self.display.FitAll()

    def activate_manipulator(self):
        if self.activate_manip_button.isChecked():
            selected = self.display.GetSelectedShape()
            if selected is not None:
                (
                    self.ais_element_manip,
                    self.index_element_manip,
                ) = self.layer.get_aisshape_from_topodsshape(selected)
                self.shape_element_manip = selected
                
                # Utilizează manipulantul personalizat
                self.manip = TranslationManipulator()
                self.manip.Attach(self.ais_element_manip)
                self.canvas.set_manipulator(self.manip)
                self.display.View.Redraw()
            else:
                self.activate_manip_button.setChecked(False)
        else:
            # Obține transformările efectuate cu manipulantul
            trsf = self.canvas.get_trsf_from_manip()
            # Aplică transformarea la TopoDS_Shape
            self.layer.update_trsf_shape(
                self.shape_element_manip, self.index_element_manip, trsf
            )
            self.manip.Detach()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    if os.getenv("APPVEYOR") is None:
        sys.exit(app.exec_())
