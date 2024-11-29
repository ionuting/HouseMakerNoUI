from OCC.Core.gp import gp_Pnt, gp_Trsf, gp_Ax1, gp_Dir
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.AIS import AIS_Shape
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Display.SimpleGui import init_display

class Fenestration:
    def __init__(self, width, height, depth, insertion_point=gp_Pnt(0, 0, 0), rotation_angle=0.0, window_type="double"):
        self.width = width
        self.height = height
        self.depth = depth
        self.insertion_point = insertion_point
        self.rotation_angle = rotation_angle
        self.window_type = window_type
        self.frame = None
        self.window = None
        self.glass_panels = []
        self.wood_panels = []
        self.bounding_box = None

    def create_frame(self):
        self.frame = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), self.width, self.depth, self.height).Shape()

    def create_openings(self):
        if self.window_type == "double":
            opening_width = self.width / 2 - 100
            opening_height = self.height / 2 - 100
            opening_depth = self.depth + 1.0
            
            left_bottom_opening = BRepPrimAPI_MakeBox(gp_Pnt(50, -1, 50), opening_width, opening_depth, opening_height).Shape()
            right_bottom_opening = BRepPrimAPI_MakeBox(gp_Pnt(self.width / 2 + 25, -1, 50), opening_width, opening_depth, opening_height).Shape()
            left_top_opening = BRepPrimAPI_MakeBox(gp_Pnt(50, -1, opening_height + 50), opening_width, opening_depth, opening_height).Shape()
            right_top_opening = BRepPrimAPI_MakeBox(gp_Pnt(self.width / 2 + 25, -1, opening_height + 50), opening_width, opening_depth, opening_height).Shape()

            self.window = BRepAlgoAPI_Cut(self.frame, left_bottom_opening).Shape()
            self.window = BRepAlgoAPI_Cut(self.window, right_bottom_opening).Shape()
            self.window = BRepAlgoAPI_Cut(self.window, left_top_opening).Shape()
            self.window = BRepAlgoAPI_Cut(self.window, right_top_opening).Shape()
        else:  # "single"
            opening_width = 500.0
            opening_height = 1100.0
            opening_depth = self.depth + 1.0

            left_opening = BRepPrimAPI_MakeBox(gp_Pnt(50, -1, 50), opening_width, opening_depth, opening_height).Shape()
            right_opening = BRepPrimAPI_MakeBox(gp_Pnt(self.width / 2 + 25, -1, 50), opening_width, opening_depth, opening_height).Shape()

            self.window = BRepAlgoAPI_Cut(self.frame, left_opening).Shape()
            self.window = BRepAlgoAPI_Cut(self.window, right_opening).Shape()

    def create_panels(self):
        if self.window_type == "double":
            opening_width = self.width / 2 - 100
            opening_height = self.height / 2 - 100
            
            left_top_glass = BRepPrimAPI_MakeBox(gp_Pnt(50, self.depth / 2, opening_height + 50), opening_width, 5.0, opening_height).Shape()
            right_top_glass = BRepPrimAPI_MakeBox(gp_Pnt(self.width / 2 + 25, self.depth / 2, opening_height + 50), opening_width, 5.0, opening_height).Shape()
            self.glass_panels.extend([left_top_glass, right_top_glass])
            
            left_bottom_panel = BRepPrimAPI_MakeBox(gp_Pnt(50, self.depth / 2, 50), opening_width, 5.0, opening_height).Shape()
            right_bottom_panel = BRepPrimAPI_MakeBox(gp_Pnt(self.width / 2 + 25, self.depth / 2, 50), opening_width, 5.0, opening_height).Shape()
            self.wood_panels.extend([left_bottom_panel, right_bottom_panel])
        else:  # "single"
            opening_width = 500.0
            opening_height = 1100.0
            
            left_glass = BRepPrimAPI_MakeBox(gp_Pnt(50, self.depth / 2, 50), opening_width, 5.0, opening_height).Shape()
            right_glass = BRepPrimAPI_MakeBox(gp_Pnt(self.width / 2 + 25, self.depth / 2, 50), opening_width, 5.0, opening_height).Shape()
            self.glass_panels.extend([left_glass, right_glass])

    def create_bounding_box(self):
        bounding_box_width = self.width + 20
        bounding_box_height = self.height + 20
        bounding_box_depth = 600.0
        bounding_box_position = gp_Pnt(-10, self.depth - 300, -10)
        self.bounding_box = BRepPrimAPI_MakeBox(bounding_box_position, bounding_box_width, bounding_box_depth, bounding_box_height).Shape()

    def apply_transformation(self, shape):
        trsf = gp_Trsf()
        trsf.SetTranslation(gp_Pnt(0, 0, 0), self.insertion_point)
        if self.rotation_angle != 0:
            axis = gp_Ax1(self.insertion_point, gp_Dir(0, 0, 1))
            trsf.SetRotation(axis, self.rotation_angle * 3.14159265359 / 180)
        transformer = BRepBuilderAPI_Transform(shape, trsf)
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

def create_and_display_fenestrations(fenestration_params):
    display, start_display, add_menu, add_function_to_menu = init_display()
    
    for params in fenestration_params:
        fenestration = Fenestration(*params)
        fenestration.create_frame()
        fenestration.create_openings()
        fenestration.create_panels()
        fenestration.create_bounding_box()
        
        for shape in fenestration.get_shapes():
            display.Context.Display(shape, True)
    
    start_display()

# Definirea parametrilor pentru fiecare feronerie
fenestration_params = [
    # Patru ferestre de tip "double"
    (900.0, 2100.0, 50.0, gp_Pnt(100, 200, 0), 0.0, "double"),
    (900.0, 2100.0, 50.0, gp_Pnt(1100, 200, 0), 30.0, "double"),
    (900.0, 2100.0, 50.0, gp_Pnt(2100, 200, 0), 60.0, "double"),
    (900.0, 2100.0, 50.0, gp_Pnt(3100, 200, 0), 90.0, "double"),
    
    # Patru ferestre de tip "single"
    (1200.0, 1200.0, 50.0, gp_Pnt(100, 2500, 0), 0.0, "single"),
    (1200.0, 1200.0, 50.0, gp_Pnt(1400, 2500, 0), 30.0, "single"),
    (1200.0, 1200.0, 50.0, gp_Pnt(2700, 2500, 0), 60.0, "single"),
    (1200.0, 1200.0, 50.0, gp_Pnt(4000, 2500, 0), 90.0, "single")
]

# Crearea și afișarea feroneriilor
create_and_display_fenestrations(fenestration_params)