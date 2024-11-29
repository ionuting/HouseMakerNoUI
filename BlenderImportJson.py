import json
import os
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCC.Core.gp import gp_Pnt
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Display.SimpleGui import init_display
import uuid
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB

def read_json(filepath):
    """Citește datele din fișierul JSON."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fișierul {filepath} nu există!")
        
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

def build_faces_from_json(data):
    """
    Creează un obiect compound pe baza datelor despre fețele din JSON.
    
    Args:
        data (dict): Dicționar cu datele mesh-ului
        
    Returns:
        TopoDS_Compound: Obiectul 3D creat
    """
    builder = BRep_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)

    vertices = data["vertices"]
    faces = data["faces"]

    # Convertim vertecșii în puncte gp_Pnt
    points = [gp_Pnt(v[0], v[1], v[2]) for v in vertices]

    for face_indices in faces:
        if len(face_indices) < 3:
            print(f"Avertisment: Fața are mai puțin de 3 vertecși, se va ignora: {face_indices}")
            continue
        
        polygon = BRepBuilderAPI_MakePolygon()
        
        for index in face_indices:
            if 0 <= index < len(points):
                polygon.Add(points[index])
            else:
                print(f"Avertisment: Index de vertex invalid: {index}")
                continue
        
        polygon.Close()

        if polygon.IsDone():
            face_maker = BRepBuilderAPI_MakeFace(polygon.Wire())
            if face_maker.IsDone():
                face_shape = face_maker.Face()
                builder.Add(compound, face_shape)
            else:
                print(f"Avertisment: Nu s-a putut crea fața pentru poligonul: {face_indices}")
        else:
            print(f"Avertisment: Poligonul nu a putut fi construit pentru indicii: {face_indices}")

    return compound


