# geometry_operations.py

import numpy as np

def column_list(matrix, indices_to_skip):
    result = []


    rows, cols, _ = matrix.shape


    for i in range(rows):
        for j in range(cols):
            # Verificăm dacă indicele curent trebuie să fie sărit
            if (i, j) in indices_to_skip:
                continue
            result.append(matrix[i, j])
            
    return result



def create_column_points(intersection_matrix, indices_to_skip, offset):
    """
    Creează puncte de coloană pe baza unei matrice de intersecție, sărind peste indicii specificați.

    Args:
        intersection_matrix (np.ndarray): Matricea de intersecție 3D.
        indices_to_skip (list of tuple): Lista de tuple care conține indicii pe care dorim să-i sărim.
        offset (float): Offset-ul pentru calculul coordonatelor punctelor coloanelor.

    Returns:
        np.ndarray: O matrice 2D cu punctele coloanelor, excluzând indicii specificați.
    """
    rows, cols, _ = intersection_matrix.shape
    result = np.empty((rows, cols), dtype=object)

    o1 = offset / 2

    for i in range(rows):
        for j in range(cols):
            # Verificăm dacă indicele curent trebuie să fie sărit
            if (i, j) in indices_to_skip:
                continue

            p = intersection_matrix[i, j]
            column_points = np.array([
                [[p[0] - o1, p[1] - o1, 0],
                 [p[0], p[1] - o1, 0],
                 [p[0] + o1, p[1] - o1, 0]],
                [[p[0] - o1, p[1], 0],
                 [p[0], p[1], 0],
                 [p[0] + o1, p[1], 0]],
                [[p[0] - o1, p[1] + o1, 0],
                 [p[0], p[1] + o1, 0],
                 [p[0] + o1, p[1] + o1, 0]]
            ])
            result[i, j] = column_points

    return result