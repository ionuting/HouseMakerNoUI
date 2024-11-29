import numpy as np
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_Transform
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism
from OCC.Core.AIS import AIS_Shape, AIS_TextLabel
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from PyQt5.QtWidgets import QComboBox, QColorDialog
from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRepGProp import brepgprop_VolumeProperties

# Function to calculate the volume of a shape using pythonOCC
def calc_volume(shape):
    props = GProp_GProps()
    brepgprop_VolumeProperties(shape, props)
    return props.Mass()

def create_room_shape(intersection_pts, i1, i2, i3, i4, offset):
    return [
        [intersection_pts[i1[0], i1[1], 0] + offset, intersection_pts[i1[0], i1[1], 1] + offset],
        [intersection_pts[i2[0], i2[1], 0] - offset, intersection_pts[i2[0], i2[1], 1] + offset],
        [intersection_pts[i3[0], i3[1], 0] - offset, intersection_pts[i3[0], i3[1], 1] - offset],
        [intersection_pts[i4[0], i4[1], 0] + offset, intersection_pts[i4[0], i4[1], 1] - offset]
    ]

def create_face(base_points):
    polygon = BRepBuilderAPI_MakePolygon()
    for point in base_points:
        polygon.Add(gp_Pnt(point[0], point[1], 0))
    polygon.Close()
    face = BRepBuilderAPI_MakeFace(polygon.Shape())
    return face.Face()

def create_column(insertion_point):
    x, y = float(insertion_point[0]) - 0.125, float(insertion_point[1]) - 0.125
    column = BRepPrimAPI_MakeBox(gp_Pnt(x, y, 0), 0.25, 0.25, 2.8).Shape()
    return column

def create_axis_grid(self, x_interax, y_interax):
    axis_color = Quantity_Color(0.0, 1.0, 0.0, Quantity_TOC_RGB)  # Gray color for axes
    

        # Create X axes
    for y in y_interax:
        start_point = gp_Pnt(x_interax[0] - 2.5, y, 0)  # Extend 0.5m to the left
        end_point = gp_Pnt(x_interax[-1] + 2.5, y, 0)   # Extend 0.5m to the right
        edge = BRepBuilderAPI_MakeEdge(start_point, end_point).Edge()
        axis = AIS_Shape(edge)
        axis.SetColor(axis_color)
        self.canvas._display.Context.Display(axis, True)

    # Create Y axes
    for x in x_interax:
        start_point = gp_Pnt(x, y_interax[0] - 2.5, 0)  # Extend 0.5m downwards
        end_point = gp_Pnt(x, y_interax[-1] + 2.5, 0)   # Extend 0.5m upwards
        edge = BRepBuilderAPI_MakeEdge(start_point, end_point).Edge()
        axis = AIS_Shape(edge)
        axis.SetColor(axis_color)
        self.canvas._display.Context.Display(axis, True)


def create_grid(self):
    # Define the axis color (lime green)
    axis_color = Quantity_Color(0.2, 0.2, 0.2, Quantity_TOC_RGB)  # Lime green
    transparency_value = 0.9
    # Define the range for the grid
    x_intervals = range(-50, 51)  # X-axis range from -30 to 30
    y_intervals = range(-50, 51)  # Y-axis range from -30 to 30

    # Create X-axis grid lines (parallel to X axis)
    for y in y_intervals:
        start_point = gp_Pnt(-50, y, -0.45)  # Start at X=-30, Y=y
        end_point = gp_Pnt(50, y, -0.45)     # End at X=30, Y=y
        edge = BRepBuilderAPI_MakeEdge(start_point, end_point).Edge()
        axis = AIS_Shape(edge)
        axis.SetColor(axis_color)  # Set the color to lime green
        axis.SetTransparency(transparency_value)
        axis.SelectionMode(False)
        self.canvas._display.Context.Display(axis, True)

    # Create Y-axis grid lines (parallel to Y axis)
    for x in x_intervals:
        start_point = gp_Pnt(x, -50, -0.45)  # Start at X=x, Y=-30
        end_point = gp_Pnt(x, 50, -0.45)     # End at X=x, Y=30
        edge = BRepBuilderAPI_MakeEdge(start_point, end_point).Edge()
        axis = AIS_Shape(edge)
        axis.SetColor(axis_color)  # Set the color to lime green
        axis.SetTransparency(transparency_value)
        axis.SelectionMode(False)
        self.canvas._display.Context.Display(axis, True)
    
    

def translate_face(face, distance):
    translation = gp_Trsf()
    translation.SetTranslation(gp_Vec(0, 0, distance))
    transformed_shape = BRepBuilderAPI_Transform(face, translation).Shape()
    return transformed_shape


def toggle_clip_plane(self):
    """
    Activează sau dezactivează planul de tăiere
    """
    is_enabled = self.clip_plane_combo.currentText() == "Da"
    self.clip_plane.SetOn(is_enabled)
    
    # Actualizăm toate formele existente
    for shape in self.displayed_shapes:
        if is_enabled:
            self.canvas._display.Context.SetClipPlanes(shape, [self.clip_plane])
        else:
            self.canvas._display.Context.RemoveClipPlanes(shape)
            
    self.canvas._display.Context.UpdateCurrentViewer()



            # Define helper functions
def footprint_rectangle(matrix, i1, i2, i3, i4, offset):
    return [
        [matrix[i1[0], i1[1], 0] - offset, matrix[i1[0], i1[1], 1] - offset],
        [matrix[i2[0], i2[1], 0] + offset, matrix[i2[0], i2[1], 1] - offset],
        [matrix[i3[0], i3[1], 0] + offset, matrix[i3[0], i3[1], 1] + offset],
        [matrix[i4[0], i4[1], 0] - offset, matrix[i4[0], i4[1], 1] + offset]
    ]



def showColorDialog(self):
    color = QColorDialog.getColor()

    if color.isValid():
        # Obține valorile RGB
        r, g, b, _ = color.getRgbF()  # getRgbF returnează valorile normalizate (între 0 și 1)
        print(f"Color chosen: ({r:.2f}, {g:.2f}, {b:.2f})")
    return r, g, b      

        #DISPLAY CLIPING PLANE