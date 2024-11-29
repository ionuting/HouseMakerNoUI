import sys
import os
from OCC.Core.gp import gp_Pln, gp_Pnt, gp_Dir
from OCC.Core.Graphic3d import Graphic3d_ClipPlane
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB


def create_clip_plane():
    # Creăm un obiect Graphic3d_ClipPlane
    clip_plane = Graphic3d_ClipPlane()

    # Activăm umplerea planului de tăiere
    clip_plane.SetCapping(True)
    clip_plane.SetCappingHatch(True)

    # Dezactivăm planul de tăiere inițial
    clip_plane.SetOn(False)

    # Setăm culoarea planului de tăiere
    aMat = clip_plane.CappingMaterial()
    aColor = Quantity_Color(0.5, 0.6, 0.7, Quantity_TOC_RGB)  # RGB între 0 și 1
    aMat.SetAmbientColor(aColor)
    aMat.SetDiffuseColor(aColor)
    clip_plane.SetCappingMaterial(aMat)

    # Definim planul ca fiind la z = 0
    plane_definition = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(0, 0, -1))
    clip_plane.SetEquation(plane_definition)

    return clip_plane



