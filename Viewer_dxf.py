#!/usr/bin/env python3
# Copyright (c) 2020-2023, Matthew Broadway
# License: MIT License
import argparse
import logging
import signal
import sys

from ezdxf.addons.xqt import QtWidgets as qw
from PyQt5.QtCore import Qt  # Import corect pentru Qt

import ezdxf
from ezdxf import recover
from ezdxf.addons.drawing.qtviewer import CADViewer
from ezdxf.addons.drawing.config import Configuration
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QVBoxLayout, QPushButton, QLabel

# ------------------------------------------------------------------------------
# IMPORTANT: This example is just a remaining skeleton, the implementation
# details moved into module: ezdxf.addon.drawing.qtviewer
#
# The CAD viewer can be executed by the new ezdxf command line launcher:
# C:\> ezdxf view FILE
#
# # docs: https://ezdxf.mozman.at/docs/addons/drawing.html
# ------------------------------------------------------------------------------
class CADViewerWidget(QWidget):
    def __init__(self):
        super(CADViewerWidget, self).__init__()

        # Setare layout
        layout = QVBoxLayout(self)

        # Configurarea vizualizatorului CAD
        self.viewer = CADViewer.from_config(Configuration())
        layout.addWidget(self.viewer)

        # Variabile pentru panoramare
        self._is_panning = False  # Variabilă pentru a urmări dacă panning-ul este activ
        self._last_mouse_position = None  # Poziția inițială a mouse-ului

        # Setăm un mouse event filter pentru a intercepta evenimentele mouse-ului
        self.viewer.setMouseTracking(True)

        # Conectăm semnalele mouse-ului
        self.viewer.mousePressEvent = self.mouse_press_event
        self.viewer.mouseMoveEvent = self.mouse_move_event
        self.viewer.mouseReleaseEvent = self.mouse_release_event

    def mouse_press_event(self, event):
        if event.button() == qw.Qt.LeftButton:  # Verifică dacă butonul stâng al mouse-ului este apăsat
            self._is_panning = True
            self._last_mouse_position = event.pos()  # Salvează poziția inițială a mouse-ului
            self.viewer.setCursor(qw.Qt.ClosedHandCursor)  # Schimbă cursorul pentru a indica panning-ul

    def mouse_move_event(self, event):
        if self._is_panning:  # Verifică dacă panning-ul este activ
            delta = event.pos() - self._last_mouse_position  # Calculează diferența dintre poziția curentă și cea anterioară a mouse-ului
            # Translatază scena în funcție de mișcarea mouse-ului
            self.viewer.horizontalScrollBar().setValue(self.viewer.horizontalScrollBar().value() - delta.x())
            self.viewer.verticalScrollBar().setValue(self.viewer.verticalScrollBar().value() - delta.y())
            self._last_mouse_position = event.pos()  # Actualizează poziția anterioară a mouse-ului

    def mouse_release_event(self, event):
        if event.button() == qw.Qt.LeftButton:  # Verifică dacă butonul stâng al mouse-ului a fost eliberat
            self._is_panning = False  # Resetează starea de panning
            self.viewer.setCursor(qw.Qt.ArrowCursor)  # Schimbă cursorul înapoi la săgeată

    def load_dxf_file(self):
        # Deschidem un dialog pentru a selecta fișierul DXF
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Selectează fișierul DXF", "", "DXF Files (*.dxf);;All Files (*)", options=options)
        if file_name:
            self.show_dxf_file(file_name)

    def show_dxf_file(self, filename):
        try:
            doc, auditor = recover.readfile(filename)
            self.viewer.set_document(doc, auditor, draw=False)
            self.viewer.draw_layout("Model")  # Poate fi adaptat în funcție de layout
        except IOError:
            logging.error(f"Nu este un fișier DXF sau o eroare I/O generică: {filename}")
        except Exception as e:
            logging.error(f"Eroare la deschiderea fișierului: {e}")