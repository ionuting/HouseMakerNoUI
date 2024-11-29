import numpy as np
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf, gp_Ax1, gp_Dir
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.AIS import AIS_Shape
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB

class Fenestration:
    def __init__(self, insertion_point, rotation_angle, width, height, depth, window_type="double"):
        self.width = float(width)
        self.height = float(height)
        self.depth = float(depth)
        self.insertion_point = insertion_point
        self.rotation_angle = float(rotation_angle)
        self.window_type = window_type
        self.frame = None
        self.window = None
        self.glass_panels = []
        self.wood_panels = []
        self.bounding_box = None

    def create_frame(self):
        self.frame = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 
                                         self.width, 
                                         self.depth, 
                                         self.height).Shape()

    def create_openings(self):
        if self.window_type == "double":
            opening_width = self.width / 2 - 0.1
            opening_height = self.height / 2 - 0.1
            opening_depth = self.depth + 0.001
            
            left_bottom_opening = BRepPrimAPI_MakeBox(gp_Pnt(0.05, -0.001, 0.05), opening_width, opening_depth, opening_height).Shape()
            right_bottom_opening = BRepPrimAPI_MakeBox(gp_Pnt(self.width / 2 + 0.025, -0.001, 0.05), opening_width, opening_depth, opening_height).Shape()
            left_top_opening = BRepPrimAPI_MakeBox(gp_Pnt(0.05, -0.001, opening_height + 0.05), opening_width, opening_depth, opening_height).Shape()
            right_top_opening = BRepPrimAPI_MakeBox(gp_Pnt(self.width / 2 + 0.025, -0.001, opening_height + 0.05), opening_width, opening_depth, opening_height).Shape()

            self.window = BRepAlgoAPI_Cut(self.frame, left_bottom_opening).Shape()
            self.window = BRepAlgoAPI_Cut(self.window, right_bottom_opening).Shape()
            self.window = BRepAlgoAPI_Cut(self.window, left_top_opening).Shape()
            self.window = BRepAlgoAPI_Cut(self.window, right_top_opening).Shape()
        else:  # "single"
            opening_width = self.width - 0.1
            opening_height = self.height - 0.1
            opening_depth = self.depth + 0.001

            opening = BRepPrimAPI_MakeBox(gp_Pnt(0.05, -0.001, 0.05), opening_width, opening_depth, opening_height).Shape()
            self.window = BRepAlgoAPI_Cut(self.frame, opening).Shape()

    def create_panels(self):
        if self.window_type == "double":
            opening_width = self.width / 2 - 0.1
            opening_height = self.height / 2 - 0.1
            
            left_top_glass = BRepPrimAPI_MakeBox(gp_Pnt(0.05, self.depth / 2, opening_height + 0.05), opening_width, 0.005, opening_height).Shape()
            right_top_glass = BRepPrimAPI_MakeBox(gp_Pnt(self.width / 2 + 0.025, self.depth / 2, opening_height + 0.05), opening_width, 0.005, opening_height).Shape()
            self.glass_panels.extend([left_top_glass, right_top_glass])
            
            left_bottom_panel = BRepPrimAPI_MakeBox(gp_Pnt(0.05, self.depth / 2, 0.05), opening_width, 0.005, opening_height).Shape()
            right_bottom_panel = BRepPrimAPI_MakeBox(gp_Pnt(self.width / 2 + 0.025, self.depth / 2, 0.05), opening_width, 0.005, opening_height).Shape()
            self.wood_panels.extend([left_bottom_panel, right_bottom_panel])
        else:  # "single"
            opening_width = self.width - 0.1
            opening_height = self.height - 0.1
            
            glass = BRepPrimAPI_MakeBox(gp_Pnt(0.05, self.depth / 2, 0.05), opening_width, 0.005, opening_height).Shape()
            self.glass_panels.append(glass)

    def create_bounding_box(self):
        bounding_box_width = self.width + 0.02
        bounding_box_height = self.height + 0.02
        bounding_box_depth = 0.6
        bounding_box_position = gp_Pnt(-0.01, self.depth - 0.3, -0.01)
        self.bounding_box = BRepPrimAPI_MakeBox(bounding_box_position, bounding_box_width, bounding_box_depth, bounding_box_height).Shape()

    def apply_transformation(self, shape):
        translation_trsf = gp_Trsf()
        translation_trsf.SetTranslation(gp_Pnt(0, 0, 0), self.insertion_point)
        
        rotation_trsf = gp_Trsf()
        if self.rotation_angle != 0:
            axis = gp_Ax1(self.insertion_point, gp_Dir(0, 0, 1))
            rotation_trsf.SetRotation(axis, self.rotation_angle * np.pi / 180)
        
        combined_trsf = gp_Trsf()
        combined_trsf.Multiply(rotation_trsf)
        combined_trsf.Multiply(translation_trsf)
        
        transformer = BRepBuilderAPI_Transform(shape, combined_trsf)
        return transformer.Shape()

    def get_shapes(self):
        shapes = []
        
        window_shape = AIS_Shape(self.apply_transformation(self.window))
        frame_color = Quantity_Color(0.5, 0.5, 0.5, Quantity_TOC_RGB)
        window_shape.SetColor(frame_color)
        shapes.append(window_shape)
        
        glass_color = Quantity_Color(0.0, 0.0, 1.0, Quantity_TOC_RGB)
        for glass_panel in self.glass_panels:
            glass_shape = AIS_Shape(self.apply_transformation(glass_panel))
            glass_shape.SetColor(glass_color)
            glass_shape.SetTransparency(0.5)
            shapes.append(glass_shape)
        
        wood_color = Quantity_Color(0.33, 0.22, 0.14, Quantity_TOC_RGB)
        for wood_panel in self.wood_panels:
            wood_shape = AIS_Shape(self.apply_transformation(wood_panel))
            wood_shape.SetColor(wood_color)
            shapes.append(wood_shape)
        
        if self.bounding_box:
            bounding_box_shape = AIS_Shape(self.apply_transformation(self.bounding_box))
            bounding_box_color = Quantity_Color(1.0, 1.0, 1.0, Quantity_TOC_RGB)
            bounding_box_shape.SetColor(bounding_box_color)
            bounding_box_shape.SetTransparency(0.7)
            shapes.append(bounding_box_shape)
        
        return shapes