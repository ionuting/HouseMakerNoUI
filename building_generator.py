import numpy as np
from PyQt5.QtWidgets import  QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSlider, QCheckBox, QPushButton, QLabel, QLineEdit, QScrollArea
from PyQt5.QtCore import Qt
from OCC.Display.backend import load_backend
load_backend("pyqt5")
from OCC.Display.qtDisplay import qtViewer3d
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf, gp_Ax1, gp_Dir, gp_Pln
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_Transform
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.AIS import AIS_Shape, AIS_TextLabel
from OCC.Core.TCollection import TCollection_ExtendedString
from PyQt5.QtWidgets import QComboBox, QColorDialog
from OCC.Core.Graphic3d import Graphic3d_ClipPlane
from OCC.Core.AIS import AIS_Manipulator
from OCC.Extend.LayerManager import Layer
from OCC.Core.Quantity import (
    Quantity_Color,
    Quantity_NOC_ALICEBLUE,
    Quantity_NOC_ANTIQUEWHITE,
)

import json
import matplotlib.pyplot as plt

from fenestration import Fenestration
from geometry_utils import showColorDialog, footprint_rectangle, create_face, toggle_clip_plane, create_room_shape, calc_volume, create_column, translate_face, create_grid, create_axis_grid
from visualization import read_volumes_from_json, create_matplotlib_charts
from beams import create_beam_pairs, create_beam_contours, beam_points, drop_list_at_indexes
from map_builder import create_column_points, column_list
from roofs import roof_01
from ClipPlane import create_clip_plane
import ezdxf
from dxf import columns_dxf
from BlenderImportJson import read_json, build_faces_from_json

class BuildingGenerator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.show_interior_covering = True
        self.show_exterior_covering = True
        self.show_roof = True
        self.show_blender = True

        # Initialize lists for displayed shapes
        self.displayed_shapes = []
        self.ais_shapes = []
        
        # Initialize the display first
        self.canvas = qtViewer3d(self)
        
        
        # Initialize clip plane with improved settings
        self.clip_plane = Graphic3d_ClipPlane()
        self.clip_plane.SetCapping(True)
        self.clip_plane.SetCappingHatch(True)
        
        # Set color and material for cutting surface
        color = Quantity_Color(0.8, 0.8, 0.8, Quantity_TOC_RGB)
        material = self.clip_plane.CappingMaterial()
        material.SetAmbientColor(color)
        material.SetDiffuseColor(color)
        self.clip_plane.SetCappingMaterial(material)
        
        # Add the clip plane to the view
        self.canvas._display.View.AddClipPlane(self.clip_plane)
        
        # Initialize manipulator
        self.current_manip = None
        
        # Disable clip plane initially
        self.clip_plane.SetOn(False)
        
        self.initUI()

    def initUI(self):
        
        self.setWindowTitle('Building Generator')
        self.setGeometry(100, 100, 1200, 800)

        # Main layout
        main_layout = QHBoxLayout()
        
        # 3D viewer
        self.canvas = qtViewer3d(self)
        # Setare culoare fundal la alb
        self.canvas._display.View.SetBackgroundColor(Quantity_Color(0.828, 0.828, 0.828, Quantity_TOC_RGB))
        main_layout.addWidget(self.canvas, 4)
        
        # Side panel
        side_panel = QWidget()
        side_panel.setFixedWidth(200)
        side_layout = QVBoxLayout(side_panel)
        
        # Scroll area for side panel
        scroll = QScrollArea()
        scroll.setWidget(side_panel)
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(220)
        main_layout.addWidget(scroll, 1)
        
        # X interax inputs
        self.x_inputs = []
        side_layout.addWidget(QLabel('X Interax:'))
        for i, val in enumerate([0, 4, 7, 10]):
            layout = QHBoxLayout()
            layout.addWidget(QLabel(f'X{i}:'))
            line_edit = QLineEdit(str(val))
            self.x_inputs.append(line_edit)
            layout.addWidget(line_edit)
            side_layout.addLayout(layout)
        
        # Y interax inputs
        self.y_inputs = []
        side_layout.addWidget(QLabel('Y Interax:'))
        for i, val in enumerate([0, 5, 6.5, 10]):
            layout = QHBoxLayout()
            layout.addWidget(QLabel(f'Y{i}:'))
            line_edit = QLineEdit(str(val))
            self.y_inputs.append(line_edit)
            layout.addWidget(line_edit)
            side_layout.addLayout(layout)
        
                # Checkboxes for coverings
        self.interior_checkbox = QCheckBox('Show Interior Covering')
        self.interior_checkbox.setChecked(True)
        side_layout.addWidget(self.interior_checkbox)
        
        self.exterior_checkbox = QCheckBox('Show Exterior Covering')
        self.exterior_checkbox.setChecked(True)
        side_layout.addWidget(self.exterior_checkbox)

        self.roof_checkbox = QCheckBox('Show Roof')
        self.roof_checkbox.setChecked(True)
        side_layout.addWidget(self.roof_checkbox)

        self.blender_checkbox = QCheckBox('Show Blender')
        self.blender_checkbox.setChecked(False)
        side_layout.addWidget(self.blender_checkbox)

        # Update button
        update_button = QPushButton('Update Geometry')
        update_button.clicked.connect(self.update_geometry)
        side_layout.addWidget(update_button)
        
         # Creează un buton pentru a deschide color picker-ul
        self.btn = QPushButton('Pick a Color', self)
        self.btn.clicked.connect(showColorDialog)

                # Show graphs
        graph_button = QPushButton('show_graphs')
        graph_button.clicked.connect(self.show_graphs)
        side_layout.addWidget(graph_button)


        side_layout.addWidget(self.btn)
        self.setLayout(side_layout)

        layout_v = QVBoxLayout()

        self.activate_manip_button = QPushButton("Activate Manipulator", self)
        self.activate_manip_button.setCheckable(True)
        self.activate_manip_button.clicked.connect(self.activate_manipulator)
        side_layout.addWidget(self.activate_manip_button)
        

        # Spacer
        side_layout.addStretch(1)
        
        # Set main widget
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
      
        # Initialize geometry
        self.update_geometry()
        
        # Modificăm partea cu clip plane
        clip_plane_layout = QHBoxLayout()
        clip_plane_label = QLabel("Activează plan tăiere:")
        clip_plane_layout.addWidget(clip_plane_label)
        
        self.clip_plane_combo = QComboBox()
        self.clip_plane_combo.addItems(["Nu", "Da"])
        self.clip_plane_combo.currentIndexChanged.connect(toggle_clip_plane)
        clip_plane_layout.addWidget(self.clip_plane_combo)
        
        side_layout.addLayout(clip_plane_layout)
        
        elevation_plane_layout = QHBoxLayout()
        elevation_plane_label = QLabel("Cota plan tăiere:")
        elevation_plane_layout.addWidget(elevation_plane_label)
        side_layout.addLayout(elevation_plane_layout)
        
        self.z_slider = QSlider(Qt.Horizontal)
        self.z_slider.setMinimum(-100)
        self.z_slider.setMaximum(600)
        self.z_slider.setValue(0)
        self.z_slider.setTickPosition(QSlider.TicksBelow)
        self.z_slider.setTickInterval(10)
        self.z_slider.valueChanged.connect(self.update_clip_plane_position)
        side_layout.addWidget(self.z_slider)
        self.clip_plane_combo.currentIndexChanged.connect(self.toggle_clip_plane)
        self.z_slider.valueChanged.connect(self.update_clip_plane_position)

        #Add selection mode for manipulator
        #self.canvas._display.Context.Activate(AIS_Shape, True)
    
    def activate_manipulator(self):
        """Function to activate/deactivate the manipulator"""
        if self.activate_manip_button.isChecked():
            selected_shapes = self.canvas._display.GetSelectedShapes()
            if selected_shapes:
                selected = selected_shapes[0]  # Get the first selected shape
                if selected:
                    # Find corresponding AIS_Shape
                    for ais_shape in self.ais_shapes:
                        if ais_shape.Shape().IsEqual(selected):
                            # Detach previous manipulator if exists
                            if self.current_manip:
                                self.current_manip.Detach()
                            
                            # Create and attach new manipulator
                            self.current_manip = AIS_Manipulator()
                            self.current_manip.IsAttached(ais_shape)
                            self.canvas._display.Context.Display(self.current_manip, True)
                            self.canvas._display.View.Redraw()
                            break
            else:
                self.activate_manip_button.setChecked(False)
        else:
            # Detach manipulator when button is deactivated
            if self.current_manip:
                self.current_manip.Detach()
                self.canvas._display.Remove(self.current_manip, True)
                self.current_manip = None
                self.canvas._display.View.Redraw()

    def display_shape(self, shape, color=None, transparency=0.0):
        """Modified method to keep references to AIS_Shape"""
        ais_shape = AIS_Shape(shape)
        if color:
            ais_shape.SetColor(color)
        if transparency > 0:
            ais_shape.SetTransparency(transparency)
        
        # Add clip plane to the shape
        ais_shape.AddClipPlane(self.clip_plane)
        
        self.canvas._display(ais_shape, True)
        self.displayed_shapes.append(shape)
        self.ais_shapes.append(ais_shape)
        return ais_shape

    def clear_display(self):
        """Modified method to clean up both shapes and AIS_Shapes"""
        if self.current_manip:
            self.current_manip.Detach()
            self.canvas._display(self.current_manip, True)
            self.current_manip = None
        
        self.canvas._display.EraseAll(True)
        self.displayed_shapes.clear()
        self.ais_shapes.clear()
        self.canvas._display.Redraw()

    def toggle_clip_plane(self, index):
        """Toggle clip plane on/off"""
        is_enabled = index == 1
        self.clip_plane.SetOn(is_enabled)
        self.canvas._display.Redraw()
    
    def update_clip_plane_position(self):
        """
        Actualizează poziția planului de tăiere bazată pe valoarea slider-ului
        """
        z_value = self.z_slider.value() / 100.0  # Convertim la metri
        plane = gp_Pln(gp_Pnt(0, 0, z_value), gp_Dir(0, 0, -1))
        self.clip_plane.SetEquation(plane)
        
        # Actualizăm toate formele
        if self.clip_plane.IsOn():
            for shape in self.displayed_shapes:
                self.canvas._display.Context.SetClipPlanes(shape, [self.clip_plane])
                
        self.canvas._display.Context.UpdateCurrentViewer()
      
    def update_geometry(self):
         
        # Detașăm manipulatorul existent înainte de a actualiza geometria
        if self.current_manip:
            self.current_manip.Detach()
            self.current_manip = None

        # Curățăm lista de forme afișate
        self.displayed_shapes.clear()

        # Get updated interax values
        x_interax = [float(x.text()) for x in self.x_inputs]
        y_interax = [float(y.text()) for y in self.y_inputs]
                
        # Update covering visibility
        self.show_interior_covering = self.interior_checkbox.isChecked()
        self.show_exterior_covering = self.exterior_checkbox.isChecked()
        self.show_roof = self.roof_checkbox.isChecked()
        self.show_blender = self.blender_checkbox.isChecked()
        
        # Clear previous display
        self.canvas._display.EraseAll()
        
        # Generate and display new geometry
        self.generate_building(x_interax, y_interax)

        # Fit all objects in the viewer
        self.canvas._display.FitAll()
                 
    
    def window_placement(self, intersection_matrix, i, j, angle, offset, z_height=0):
        if angle not in [0, 90, 180, 270]:
            raise ValueError("Angle must be 0, 90, 180, or 270.")
        
        base_point = intersection_matrix[i, j]
        x, y = base_point[0], base_point[1]
        
        if angle == 0:
            x += offset
        elif angle == 90:
            y += offset
        elif angle == 180:
            x -= offset
        elif angle == 270:
            y -= offset
        
        return gp_Pnt(x, y, z_height), angle
     

    def generate_building(self, x_interax, y_interax):
        # Generate the grid of intersection points
        X, Y = np.meshgrid(x_interax, y_interax)
        
        # Create a list of coordinates (x, y)
        coordinates_list = [[X[i, j], Y[i, j]] for i in range(X.shape[0]) for j in range(X.shape[1])]
        
        # Create the intersection matrix
        intersection_matrix = np.dstack((X, Y))

               # Add this new method to create and display the axis grid
        create_axis_grid(self, x_interax, y_interax)
        #create_grid(self)
    
        def cut_with_bounding_boxes(resulting_shape, fenestration_params):
            for params in fenestration_params:
                fenestration = Fenestration(*params)
                fenestration.create_frame()
                fenestration.create_openings()
                fenestration.create_panels()
                fenestration.create_bounding_box()
                
                transformed_bounding_box = fenestration.apply_transformation(fenestration.bounding_box)
                resulting_shape = BRepAlgoAPI_Cut(resulting_shape, transformed_bounding_box).Shape()
            
            return resulting_shape

            # Creăm un plan de tăiere
        clip_plane = create_clip_plane()

    # Adăugăm planul de tăiere la un obiect, de exemplu, o formă
    # Aici ar trebui să aveți un obiect 3D existent la care să adăugați planul de tăiere.
    # Presupunem că aveți un obiect numit `some_shape`.
    # some_shape.AddClipPlane(clip_plane)  # Exemplu de utilizare

    # Activăm planul de tăiere (de exemplu, la cererea utilizatorului)
    # clip_plane.SetOn(True)

        # Constants
        height = 2.8

        # Generate rooms
        rooms = [
            create_room_shape(intersection_matrix, [0, 0], [0, 1], [1, 1], [1, 0], 0.125),
            create_room_shape(intersection_matrix, [0, 1], [0, 2], [2, 2], [2, 1], 0.125),
            create_room_shape(intersection_matrix, [0, 2], [0, 3], [1, 3], [1, 2], 0.125),
            create_room_shape(intersection_matrix, [1, 0], [1, 1], [3, 1], [3, 0], 0.125),
            create_room_shape(intersection_matrix, [2, 1], [2, 2], [3, 2], [3, 1], 0.125),
            create_room_shape(intersection_matrix, [1, 2], [1, 3], [3, 3], [3, 2], 0.125)
        ]

        # Generate foundation cells
        foundation_cells = [
            create_room_shape(intersection_matrix, [0, 0], [0, 1], [1, 1], [1, 0], 0.3),
            create_room_shape(intersection_matrix, [0, 1], [0, 2], [2, 2], [2, 1], 0.3),
            create_room_shape(intersection_matrix, [0, 2], [0, 3], [1, 3], [1, 2], 0.3),
            create_room_shape(intersection_matrix, [1, 0], [1, 1], [3, 1], [3, 0], 0.3),
            create_room_shape(intersection_matrix, [2, 1], [2, 2], [3, 2], [3, 1], 0.3),
            create_room_shape(intersection_matrix, [1, 2], [1, 3], [3, 3], [3, 2], 0.3)
        ]


                # Generate interiour coverings
        int_coverings = [
            create_room_shape(intersection_matrix, [0, 0], [0, 1], [1, 1], [1, 0], 0.13),
            create_room_shape(intersection_matrix, [0, 1], [0, 2], [2, 2], [2, 1], 0.13),
            create_room_shape(intersection_matrix, [0, 2], [0, 3], [1, 3], [1, 2], 0.13),
            create_room_shape(intersection_matrix, [1, 0], [1, 1], [3, 1], [3, 0], 0.13),
            create_room_shape(intersection_matrix, [2, 1], [2, 2], [3, 2], [3, 1], 0.13),
            create_room_shape(intersection_matrix, [1, 2], [1, 3], [3, 3], [3, 2], 0.13)
        ]


        # Create background face and prism
        background_face = create_face(footprint_rectangle(intersection_matrix, [0, 0], [0, 3], [3, 3], [3, 0], 0.125))
        background_prism = BRepPrimAPI_MakePrism(background_face, gp_Vec(0, 0, height)).Shape()

        # Create outside covering face and prism
        out_covering_face = create_face(footprint_rectangle(intersection_matrix, [0, 0], [0, 3], [3, 3], [3, 0], 0.225))
        out_covering_prism = BRepPrimAPI_MakePrism(out_covering_face, gp_Vec(0, 0, height)).Shape()

  
        resulting_shape_out = BRepAlgoAPI_Cut(out_covering_prism, background_prism).Shape()
        
        # Create room prisms and cut from background
        resulting_shape = background_prism
        for room in rooms:
            room_face = create_face(room)
            room_prism = BRepPrimAPI_MakePrism(room_face, gp_Vec(0, 0, height)).Shape()
            resulting_shape = BRepAlgoAPI_Cut(resulting_shape, room_prism).Shape()
        
        test = create_column_points(intersection_matrix, [(2, 0), (2, 3)], 0.25)

        # Create room coverings and cut from background
        resulting_coverings = []
        for room, int_covering in zip(rooms, int_coverings):
            room_face = create_face(room)
            int_covering_face = create_face(int_covering)
            room_prism = BRepPrimAPI_MakePrism(room_face, gp_Vec(0, 0, height)).Shape()
            int_covering_prism = BRepPrimAPI_MakePrism(int_covering_face, gp_Vec(0, 0, height)).Shape()
            resulting_shape_cov = BRepAlgoAPI_Cut(room_prism, int_covering_prism).Shape()
            resulting_coverings.append(resulting_shape_cov)


        cp = column_list(intersection_matrix, [(2, 0), (2, 3)])
        print("coordinates columns", cp)
        # Create columns
        columns = [create_column(point) for point in cp]


        for c in cp:
            columns_dxf(c)

        # Cut columns from the resulting shape
        for col in columns:
            resulting_shape = BRepAlgoAPI_Cut(resulting_shape, col).Shape()

        
        # Display columns
        column_color = Quantity_Color(0.3, 0.3, 0.2, Quantity_TOC_RGB)
        columns_volume = 0
        for col in columns:
            ais_col = self.canvas._display.DisplayShape(col, update=True, color=column_color)
            columns_volume = columns_volume + calc_volume(col)
            ais_col[0].AddClipPlane(clip_plane)

        beam_matrix = beam_points(intersection_matrix, 0.25)
        # Exemplu de utilizare:
        # Presupunând că aveți deja columns_points definit
        skipx = [(2,0), (2,2), (1, 1)]
        skipy =[(1,0), (1,3)]
        x_beams, y_beams = create_beam_pairs(beam_matrix, skipx, skipy)

                # Exemplu de utilizare:
        # Presupunând că aveți deja x_beams și y_beams definite
        x_beam_contours = create_beam_contours(x_beams)
        y_beam_contours = create_beam_contours(y_beams)

        
        beam_list =[]
        drop_index = []
        drop_index_y = [2, 11]
        # Create beams
        for i, beam in enumerate(x_beam_contours):
            if i in drop_index:
                continue
              
            x_beams_face = create_face(beam)
            translated_x_beam_face = translate_face(x_beams_face, 2.55)
            x_beam_prism = BRepPrimAPI_MakePrism(translated_x_beam_face, gp_Vec(0, 0, 0.25)).Shape()
            beam_list.append(x_beam_prism)
        
        for i, beam in enumerate(y_beam_contours):
            if i in drop_index_y:
                continue
            y_beams_face = create_face(beam)
            translated_y_beam_face = translate_face(y_beams_face, 2.55)
            y_beam_prism = BRepPrimAPI_MakePrism(translated_y_beam_face, gp_Vec(0, 0, 0.25)).Shape()
            beam_list.append(y_beam_prism)


        # Create outside covering face and prism
        grass = create_face(footprint_rectangle(intersection_matrix, [0, 0], [0, 3], [3, 3], [3, 0], 10.0))
        translated_grass = translate_face(grass, -0.45)
        translated_grass_prism = BRepPrimAPI_MakePrism(translated_grass, gp_Vec(0, 0, 0.1)).Shape()

        # Create and display slabs
        slab_color = Quantity_Color(0.8, 0.8, 0.8, Quantity_TOC_RGB)
        room_slabs = []
        for room in rooms:
            room_face = create_face(room)
            room_slab = BRepPrimAPI_MakePrism(room_face, gp_Vec(0, 0, 0.1)).Shape()
            room_slabs.append(room_slab)
            self.canvas._display.DisplayShape(room_slab, update=True, color=slab_color)

    # Note: Fenestration and foundation elements are omitted for brevity
    # You can add them following a similar pattern if needed

        depth = -1.2
        f_thickness = 0.45

        # Boolean operation to cut rooms from the background prism and create foundations elevations

        # Create background face and then prism
        background_face = create_face(footprint_rectangle(intersection_matrix, [0, 0], [0, 3], [3, 3], [3, 0], 0.125))
        background_prism_el = BRepPrimAPI_MakePrism(background_face, gp_Vec(0, 0, depth)).Shape()

        resulting_shape_el = background_prism_el
        for room in rooms:
            room_face = create_face(room)
            # Mutăm room_face cu -1.2 metri mai jos pe axa Z
            translated_room_face = translate_face(room_face, -1.2)

            elevation_prisme = BRepPrimAPI_MakePrism(room_face, gp_Vec(0, 0, depth)).Shape()
            resulting_shape_el = BRepAlgoAPI_Cut(resulting_shape_el, elevation_prisme).Shape()

        # Create exterior foundation contour
        foundation_face = create_face(footprint_rectangle(intersection_matrix, [0, 0], [0, 3], [3, 3], [3, 0], 0.3))
        translated_foundation_face = translate_face(foundation_face, -1.65)
        foundation_prism = BRepPrimAPI_MakePrism(translated_foundation_face, gp_Vec(0, 0, f_thickness)).Shape()

        resulting_shape_f = foundation_prism
        for cell in foundation_cells:
            f_face = create_face(cell)
            translated_cell_face = translate_face(f_face, -1.65)
            foundation_cell = BRepPrimAPI_MakePrism(translated_cell_face, gp_Vec(0, 0, f_thickness)).Shape()
            resulting_shape_f = BRepAlgoAPI_Cut(resulting_shape_f, foundation_cell).Shape()

        foundation_color = Quantity_Color(0.1, 0.1, 0.1, Quantity_TOC_RGB)
        self.canvas._display.DisplayShape(resulting_shape_f, update=True, color=foundation_color)
        foundation_volume = calc_volume(resulting_shape_f)


        foundation_color = Quantity_Color(0.1, 0.1, 0.1, Quantity_TOC_RGB)
        self.canvas._display.DisplayShape(resulting_shape_el, update=True, color=foundation_color)
        elevation_volume = calc_volume (resulting_shape_el)
        

        fenestration_params = [
            (*self.window_placement(intersection_matrix, 0, 1, 0, 0.5, 0.), 0.9, 2.1, 0.05, "double"),
            (*self.window_placement(intersection_matrix, 0, 1, 90, 0.5, 0.), 0.9, 2.1, 0.05, "double"),
            (*self.window_placement(intersection_matrix, 0, 2, 90, 0.5, 0.), 0.9, 2.1, 0.05, "double"),
            (*self.window_placement(intersection_matrix, 1, 1, 90, 0.25, 0.), 0.9, 2.1, 0.05, "double"),
            (*self.window_placement(intersection_matrix, 0, 2, 90, 0.5, 0.), 0.9, 2.1, 0.05, "double"),
            (*self.window_placement(intersection_matrix, 1, 2, 90, 0.25, 0.), 0.9, 2.1, 0.05, "double"),
            (*self.window_placement(intersection_matrix, 2, 1, 0, 0.5, 0.), 0.9, 2.1, 0.05, "double"),
            (*self.window_placement(intersection_matrix, 0, 0, 0, 1.2, 0.9), 1.5, 1.2, 0.05, "single"),
            (*self.window_placement(intersection_matrix, 0, 2, 0, 1.2, 0.9), 1.5, 1.2, 0.05, "single"),
            (*self.window_placement(intersection_matrix, 1, 0, 90, 1.8, 0.9), 1.2, 1.2, 0.05, "single"),
            (*self.window_placement(intersection_matrix, 1, 3, 90, 1.8, 0.9), 1.2, 1.2, 0.05, "single"),
            (*self.window_placement(intersection_matrix, 3, 1, 0, 0.5, 1.2), 0.6, 0.9, 0.05, "single")
        ]

        for params in fenestration_params:
            fenestration = Fenestration(*params)
            fenestration.create_frame()
            fenestration.create_openings()
            fenestration.create_panels()
            fenestration.create_bounding_box()
         
        resulting_shape1 = resulting_shape
            # Tăiem resulting_shape cu boundingbox-urile ferestrelor
        resulting_shape1 = cut_with_bounding_boxes(resulting_shape1, fenestration_params)

        resulting_shape_out = cut_with_bounding_boxes(resulting_shape_out, fenestration_params)
        resulting_shape_cov = cut_with_bounding_boxes(resulting_shape_cov, fenestration_params)

        resulting_coverings1 = []
        # Tăiem acoperirile cu boundingbox-urile ferestrelor
        for covering in resulting_coverings:
            result = cut_with_bounding_boxes(covering, fenestration_params)
            resulting_coverings1.append(result)
        
        for params in fenestration_params:
            fenestration = Fenestration(*params)
            fenestration.create_frame()
            fenestration.create_openings()
            fenestration.create_panels()

            
            for shape in fenestration.get_shapes():
                self.canvas._display.Context.Display(shape, True)
         
        for b in beam_list:
            resulting_shape1 = BRepAlgoAPI_Cut(resulting_shape1, b).Shape()

        # Display the resulting shape
        resulting_shape_color = Quantity_Color(0.796, 0.255, 0.329, Quantity_TOC_RGB)
        self.canvas._display.DisplayShape(resulting_shape1, update=True, color=resulting_shape_color)
        wall_volume = calc_volume(resulting_shape1)


         # Display beams
        beam_volumes = 0
        beam_color = Quantity_Color(0.3, 0.3, 0.3, Quantity_TOC_RGB)
        for b in beam_list:
            self.canvas._display.DisplayShape(b, update=True, color=beam_color)
            beam_volumes = beam_volumes + calc_volume(b)


        # Display outside covering 
        if self.show_exterior_covering:
            out_covering_color = Quantity_Color(1, 1, 0.5, Quantity_TOC_RGB)
           #self.display_shape_with_clip(resulting_shape_out, out_covering_color)
            self.canvas._display.DisplayShape(resulting_shape_out, update=True, color=out_covering_color)

        # Display interior coverings
        if self.show_interior_covering:
            covering_color = Quantity_Color(0.9, 0.9, 0.9, Quantity_TOC_RGB)
            for covering in resulting_coverings1:
                #self.display_shape_with_clip(covering, covering_color)
                self.canvas._display.DisplayShape(covering, update=True, color=covering_color)


        point_01 = intersection_matrix[-1,-1]
        point_max = [point_01[0]+1.8, point_01[1] + 1.8]
        insert_01 = intersection_matrix[0, 0]
        height_r = 2.8
        insertion_point_r = [insert_01[0]-0.9, insert_01[1]-0.9, height_r]

        roof_height = 2
        extruded_compound = roof_01(point_max, insertion_point_r, height_r, roof_height, 0.3)
        # Setarea culorii și transparenței acoperișului extrudat
        roof_color = Quantity_Color(0.647, 0.165, 0.165, Quantity_TOC_RGB)  
        extruded_shape_r = AIS_Shape(extruded_compound)
        extruded_shape_r.SetColor(roof_color)
        extruded_shape_r.SetTransparency(0.6)  # Fără transparență

        grass_color = Quantity_Color(0, 1, 0, Quantity_TOC_RGB)
        self.canvas._display.DisplayShape(translated_grass_prism, update=True, color=grass_color)
        self.canvas._display.View.SetBgGradientColors(Quantity_Color(Quantity_NOC_ALICEBLUE), Quantity_Color(Quantity_NOC_ANTIQUEWHITE), 2, True,
)
              
        #self.canvas._display.DisplayShape(extruded_compound, update=True, color=roof_color)
        # Display roof
        if self.show_roof:
            self.canvas._display.DisplayShape(extruded_compound, update=True, color=roof_color)
        

        if self.show_blender:
                            # Calea către fișierul JSON
            filepath = "C:\\Users\\ciunt\\OneDrive\\Desktop\\exports\\mesh_export.json"
            
            # Citește fișierul JSON
            print("Se citește fișierul JSON...")
            mesh_data = read_json(filepath)
            print("Fișierul a fost citit cu succes")
            
            # Creează obiectul din fețele JSON
            print("Se construiește obiectul 3D doar din fețe...")
            compound = build_faces_from_json(mesh_data)
            print("Obiectul a fost construit cu succes")

           
            # Afișăm obiectul
            self.canvas._display.DisplayShape(compound, transparency=0.5, update=True)
            print("Obiectul a fost afișat cu succes")
        

        # Function to calculate the volume of a shape using pythonOCC
        volumes_dict = {
            'Foundation': foundation_volume,        # Replace with your actual shapes
            'Elevation': elevation_volume, 
            'Beams': beam_volumes,
            'Columns': columns_volume,
            'Walls': wall_volume
            }
        # Step 2: Save the dictionary to a JSON file
        def save_volumes_to_json(volumes_dict, filename):
            with open(filename, 'w') as json_file:
                json.dump(volumes_dict, json_file)

        # Save the volumes to a JSON file
        save_volumes_to_json(volumes_dict, 'volumes.json')

    def show_graphs(self):
        filename = 'volumes.json'
        volumes = read_volumes_from_json(filename)
    
        if volumes:
        
            # Create and display Matplotlib charts
            fig, axes = create_matplotlib_charts(volumes)
            plt.show()


 


