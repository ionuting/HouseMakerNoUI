import numpy as np
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_Transform
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism
from OCC.Core.AIS import AIS_Shape, AIS_TextLabel
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from map_builder import create_column_points

def drop_list_at_indexes(list, indexes):
    new_list = []
    for i in range(list):
        for j in indexes:
            if i == j:
                continue
            new_list.append(list[i])
    return new_list
            

def beam_points(intersection_matrix, offset):
    rows, cols, _ = intersection_matrix.shape
    result = np.empty((rows, cols), dtype=object)
    
    o1 = offset/2
    
    for i in range(rows):
        for j in range(cols):
            p = intersection_matrix[i, j]
            column_points = np.array([
                [[p[0]-o1, p[1]-o1, 0],
                [p[0], p[1]-o1, 0],
                [p[0] + o1, p[1]-o1, 0]],
                [[p[0] - o1, p[1], 0],
                [p[0], p[1], 0],
                [p[0] + o1, p[1], 0]],
                [[p[0] - o1, p[1] + o1, 0],
                [p[0], p[1] + o1, 0],
                [p[0] + o1, p[1] + o1, 0]]
            ])
            result[i, j] = column_points
    
    return result


def create_beam_pairs(beam_points, skipx, skipy):
    rows, cols = beam_points.shape
    x_beams = []
    y_beams = []

    # Generare perechi pe axa X
    for i in range(rows):
        for j in range(cols - 1):
            if (i, j) in skipx:
                if j ==0 and j < (cols - 2):  
                    x_beam = (
                        beam_points[i, j+1][[0, 1, 2], 2],  # [0,2], [1,2], [2,2] din stâlpul i
                        beam_points[i, j+2][[0, 1, 2], 0]  # [0,0], [1,0], [2,0] din stâlpul i+1
                    )

                elif j == (cols -1):
                    continue
            else:
                    x_beam = (
                beam_points[i, j][[0, 1, 2], 2],  # [0,2], [1,2], [2,2] din stâlpul i
                beam_points[i, j+1][[0, 1, 2], 0]  # [0,0], [1,0], [2,0] din stâlpul i+1
            )
            x_beams.append(x_beam)

    # Generare perechi pe axa Y
    for j in range(cols):
        for i in range(rows - 1):

            if (i, j) in skipy:
                if i ==0 and i < (rows - 2):  
                    y_beam = (
                        beam_points[i+1, j][2, [0, 1, 2]],  # [2,0], [2,1], [2,2] din stâlpul j
                        beam_points[i+2, j][0, [0, 1, 2]]  # [0,0], [0,1], [0,2] din stâlpul j+1
                    )
                elif i == (rows-1):
                    continue
                
                else:
                    y_beam = (
                        beam_points[i, j][2, [0, 1, 2]],  # [2,0], [2,1], [2,2] din stâlpul j
                        beam_points[i+2, j][0, [0, 1, 2]]  # [0,0], [0,1], [0,2] din stâlpul j+1
                    )
                    i = i+2
            else:
                 
                y_beam = (
                    beam_points[i, j][2, [0, 1, 2]],  # [2,0], [2,1], [2,2] din stâlpul j
                    beam_points[i+1, j][0, [0, 1, 2]]  # [0,0], [0,1], [0,2] din stâlpul j+1
                )
            
        
            y_beams.append(y_beam)

    return x_beams, y_beams

# Funcție pentru a vizualiza structura rezultată
def print_beam_structure(x_beams, y_beams):
    print("Structura grinzilor pe axa X:")
    for idx, beam in enumerate(x_beams):
        print(f"Grinda X {idx}:")
        print("  Puncte Stâlp 1:", beam[0])
        print("  Puncte Stâlp 2:", beam[1])
        print()

    print("\nStructura grinzilor pe axa Y:")
    for idx, beam in enumerate(y_beams):
        print(f"Grinda Y {idx}:")
        print("  Puncte Stâlp 1:", beam[0])
        print("  Puncte Stâlp 2:", beam[1])
        print()


def create_beam_contours(beam_pairs):
    beam_contours = []
    
    for beam in beam_pairs:
        start_points, end_points = beam
        
        # Creăm conturul în ordine inversă acelor de ceasornic
        contour = [
            start_points[2],  # Punctul din dreapta jos al primului stâlp
            start_points[1],  # Punctul din mijloc jos al primului stâlp
            start_points[0],  # Punctul din stânga jos al primului stâlp
            end_points[0],    # Punctul din stânga sus al celui de-al doilea stâlp
            end_points[1],    # Punctul din mijloc sus al celui de-al doilea stâlp
            end_points[2],    # Punctul din dreapta sus al celui de-al doilea stâlp
            start_points[2]   # Înapoi la punctul de start pentru a închide conturul
        ]
        
        beam_contours.append(np.array(contour))
    
    return beam_contours

# Funcție pentru a vizualiza contururile rezultate
def print_beam_contours(beam_contours):
    for idx, contour in enumerate(beam_contours):
        print(f"Contur Grindă {idx}:")
        for point in contour:
            print(f"  {point}")
        print()
# Add any other geometry utility functions here