from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Dir, gp_Ax2
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeEdge
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.TopoDS import TopoDS_Compound, TopoDS_Shape
from OCC.Core.BRep import BRep_Builder
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.AIS import AIS_Shape
from OCC.Display.SimpleGui import init_display
from OCC.Core.BRepCheck import BRepCheck_Analyzer
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_SOLID

def roof_01(point_max, insertion_point, height, roof_height, thickness):
    width = point_max[0]
    depth = point_max[1]
    if width < depth:
         b = width/2
    else:
         b = depth/2
    height = height - 0.9 * height/(b)
    def roof_style1_points(point_max, height, roof_height, insertion_point):
        width = point_max[0]
        depth = point_max[1]
        ip = insertion_point
        xip = ip[0]
        yip = ip[1]
        zip = ip[2]

        if depth < width:
            # Definirea punctelor pentru acoperișul în 4 ape
            roof_points = [
                gp_Pnt(xip, yip, height),               # Punct A (stânga față)
                gp_Pnt(xip + width, yip, height),          # Punct B (dreapta față)
                gp_Pnt(xip + width, yip + depth, height),      # Punct C (dreapta spate)
                gp_Pnt(xip, yip + depth, height),          # Punct D (stânga spate)
                gp_Pnt(xip+depth / 2, yip + depth / 2, height + roof_height),  # Punct E (vârful acoperișului
                gp_Pnt(xip+width - depth/2, yip + depth / 2, height + roof_height)  # Punct F (vârful acoperișului)
            ]
        else:
            roof_points = [
                gp_Pnt(xip, yip, height),               # Punct A (stânga față)
                gp_Pnt(xip + width, yip, height),          # Punct B (dreapta față)
                gp_Pnt(xip + width, yip + depth, height),      # Punct C (dreapta spate)
                gp_Pnt(xip, yip + depth, height),          # Punct D (stânga spate)
                gp_Pnt(xip + width / 2, yip + width / 2, height + roof_height),  # Punct E (vârful acoperișului
                gp_Pnt(xip + width / 2, yip + depth - width / 2, height + roof_height)  # Punct F (vârful acoperișului)
            ]
        return roof_points

    # Funcție pentru crearea unei fețe a acoperișului
    def make_roof_face(*points):
        polygon = BRepBuilderAPI_MakePolygon()
        for point in points:
            polygon.Add(point)
        polygon.Close()
        return BRepBuilderAPI_MakeFace(polygon.Wire()).Face()


    roof_points = roof_style1_points(point_max, height, roof_height, insertion_point)
    # Crearea celor 4 fețe ale acoperișului
    if width > depth:
        roof_faces = [
            make_roof_face(roof_points[0], roof_points[1], roof_points[5], roof_points[4]),
            make_roof_face(roof_points[1], roof_points[2], roof_points[5]),
            make_roof_face(roof_points[2], roof_points[3], roof_points[4], roof_points[5]),
            make_roof_face(roof_points[3], roof_points[0], roof_points[4])
        ]
    else:
        roof_faces = [
            make_roof_face(roof_points[0], roof_points[1], roof_points[4]),
            make_roof_face(roof_points[1], roof_points[2], roof_points[5], roof_points[4]),
            make_roof_face(roof_points[2], roof_points[3], roof_points[5]),
            make_roof_face(roof_points[3], roof_points[0], roof_points[4], roof_points[5])
        ]


    thickness = thickness
    # Extrudarea fețelor pe axa Z cu valoarea specificată
    extruded_faces = []
    for face in roof_faces:
        vector = gp_Vec(0, 0, thickness)  # Extrudăm pe axa Z
        extruded_face = BRepPrimAPI_MakePrism(face, vector).Shape()
        extruded_faces.append(extruded_face)

    # Combinarea fețelor extrudate într-un compus
    extruded_compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(extruded_compound)
    for extruded_face in extruded_faces:
        builder.Add(extruded_compound, extruded_face)
    return extruded_compound

