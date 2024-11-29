import numpy as np

# Definirea axelor cladirii
# Definirea distanțelor interax
x_interax = [0, 3, 5, 9]
y_interax = [0, 4, 5.5, 9]

# Generarea grilei de puncte de intersecție folosind meshgrid
X, Y = np.meshgrid(x_interax, y_interax)

# Crearea matricei de puncte de intersecție
intersection_matrix = np.dstack((X, Y))

# Definirea unei camere dreptunghiulare cu offset de colțuri
def footprint_rectangle(matrix, i1, i2, i3, i4, offset):
    return [
        [matrix[i1[0], i1[1], 0] - offset, matrix[i1[0], i1[1], 1] - offset],
        [matrix[i2[0], i2[1], 0] + offset, matrix[i2[0], i2[1], 1] - offset],
        [matrix[i3[0], i3[1], 0] + offset, matrix[i3[0], i3[1], 1] + offset],
        [matrix[i4[0], i4[1], 0] - offset, matrix[i4[0], i4[1], 1] + offset]
    ]

print("This is the footprint:", footprint_rectangle(intersection_matrix, [0, 0], [0, 3], [3, 3], [3, 0], 0.125), "end")


# Definirea unei camere dreptunghiulare cu offset de colțuri
def room(intersection_pts, i1, i2, i3, i4, offset):
    return [
        [intersection_pts[i1[0], i1[1], 0] + offset, intersection_pts[i1[0], i1[1], 1] + offset],
        [intersection_pts[i2[0], i2[1], 0] - offset, intersection_pts[i2[0], i2[1], 1] + offset],
        [intersection_pts[i3[0], i3[1], 0] - offset, intersection_pts[i3[0], i3[1], 1] - offset],
        [intersection_pts[i4[0], i4[1], 0] + offset, intersection_pts[i4[0], i4[1], 1] - offset]
    ]

print("This is one room:", room(intersection_matrix, [0, 0], [0, 1], [1, 1], [1, 0], 0.125), "end")


# Plasarea unei feronier pe baza unghiului și offsetului
def window_placement(room_points, angle, offset):
    offsets = {
        0: (offset, 0),
        90: (0, offset),
        180: (-offset, 0),
        270: (0, -offset)
    }
    
    if angle in offsets:
        dx, dy = offsets[angle]
        window_point = [room_points[0][0] + dx, room_points[0][1] + dy]
        return angle, window_point
    else:
        raise ValueError("Unghiul trebuie să fie 0, 90, 180 sau 270.")

# Definirea unei coloane și poziționarea ei
def create_column_matrix(c_l, c_w, insertion_point):
    return [
        [[insertion_point[0] - c_l / 2, insertion_point[1] - c_w / 2],
         [insertion_point[0], insertion_point[1] - c_w / 2],
         [insertion_point[0] + c_l / 2, insertion_point[1] - c_w / 2]],
        
        [[insertion_point[0] - c_l / 2, insertion_point[1]],
         [insertion_point[0], insertion_point[1]],
         [insertion_point[0] + c_l / 2, insertion_point[1]]],
        
        [[insertion_point[0] - c_l / 2, insertion_point[1] + c_w / 2],
         [insertion_point[0], insertion_point[1] + c_w / 2],
         [insertion_point[0] + c_l / 2, insertion_point[1] + c_w / 2]]
    ]

# Indecșii pe care vrem să-i sărim (coordonate 2D, nu unidimensional)
skip_indices = {(1, 2), (2, 1)}

# Iterăm prin punctele matricei, excluzând punctele din skip_indices
col_points_list = []
ny, nx = intersection_matrix.shape[:2]  # Dimensiuni pe direcția y și x

for i in range(ny):  # Rânduri
    for j in range(nx):  # Coloane
        if (i, j) in skip_indices:
            continue  # Sărim peste acest punct
        col_points_list.append(intersection_matrix[i, j])  # Adăugăm punctul valid

matrix_of_matrix = []
# Afișarea coordonatelor de inserție a stâlpilor
for point in col_points_list:
    column_matrix = create_column_matrix(0.25, 0.25, point)
    matrix_of_matrix.append(column_matrix)

# Afișăm matrix_of_matrix înainte de stacking
print("Matrix of matrix înainte de stacking:")
for matrix in matrix_of_matrix:
    print(matrix)

# Facem stacking pe o nouă axă (axă 0, de exemplu)
stacked_matrix = np.stack(matrix_of_matrix, axis=0)

# Afișăm rezultatul după stacking
print("\nMatrix of matrix după stacking:")
print(stacked_matrix)

def create_point_pairs(intersection_matrix, val, valy, skip_indices=None):
    pairs = []
    ny, nx = intersection_matrix.shape[:2]
    
    skip_indices = set() if skip_indices is None else set(skip_indices)
    
    def should_skip(i, j):
        return (i, j) in skip_indices
    
    # Crearea perechilor pe direcția x
    for i in range(ny):
        for j in range(nx - 1):
            if should_skip(i, j) or should_skip(i, j + 1):
                continue
            pair = (
                [intersection_matrix[i, j, 0] + val, intersection_matrix[i, j, 1]],
                [intersection_matrix[i, j + 1, 0] - val, intersection_matrix[i, j + 1, 1]]
            )
            pairs.append(("x", i, j, pair))
    
    # Crearea perechilor pe direcția y
    for i in range(ny - 1):
        for j in range(nx):
            if should_skip(i, j) or should_skip(i + 1, j):
                continue
            pair = (
                [intersection_matrix[i, j, 0], intersection_matrix[i, j, 1] + valy],
                [intersection_matrix[i + 1, j, 0], intersection_matrix[i + 1, j, 1] - valy]
            )
            pairs.append(("y", i, j, pair))
    
    return pairs

# Valori pentru offset
val = 0.125  # Exemplu de valoare pentru offset pe x
valy = 0.125  # Exemplu de valoare pentru offset pe y

# Afișarea perechilor fără puncte de sărit
skip_indices = {(1, 2), (2, 1)}
point_pairs = create_point_pairs(intersection_matrix, val, valy, skip_indices)

for direction, i, j, pair in point_pairs:
    if direction == "x":
        print(f"Pereche pe direcția x între punctele ({i},{j}) și ({i},{j+1}): {pair}")
    else:
        print(f"Pereche pe direcția y între punctele ({i},{j}) și ({i+1},{j}): {pair}")

# Afișarea punctelor sărite
print("\nPuncte sărite:")
for i, j in skip_indices:
    print(f"Punct sărit: ({i},{j}) cu coordonatele {intersection_matrix[i, j]}")

# Exista si posibilitatea de a ne folosi de diferite faze ale proiectarii
# De exemplu:
# Concept - gasit forma ideala - S.F. - calcul statistic oarecum, sau umflat.
# Design - exportat si mapat in detaliu in dxf de exemplu cu linii specifice.
# sau folosit solvere speciale pentru grinzi, placi samd