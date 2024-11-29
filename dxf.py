import ezdxf

def columns_dxf(insertion_points):
    # Deschide fișierul DXF existent
    filename = "dreptunghi_cu_hatch.dxf"
    doc = ezdxf.readfile(filename)

    # Adaugă un layer nou, dacă nu există deja
    layer_name = 'stalpi'
    if layer_name not in doc.layers:
        doc.layers.add(name=layer_name, lineweight=40)  # Grosimea liniei 0.4 mm

    # Adaugă un model space
    msp = doc.modelspace()

    # Definim punctele dreptunghiului (coordonate pentru cele 4 colțuri)
    insertion_point = insertion_points
    width = 0.25
    height = 0.25

    # Calculăm coordonatele colțurilor dreptunghiului
    x1, y1 = insertion_point
    x2, y2 = x1 + width, y1 + height

    # Creăm conturul dreptunghiului folosind o polilinie
    msp.add_lwpolyline([(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)],
                        close=True, dxfattribs={'layer': layer_name})

        # Calculăm coordonatele colțurilor dreptunghiului
    x1, y1 = insertion_point
    x2, y2 = x1 + width, y1 + height

    # Creăm conturul dreptunghiului folosind o polilinie
    lwpolyline= msp.add_lwpolyline([(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)], close=True, dxfattribs={'layer': 'stalpi'})

    # Adaugă un hatch (hașurare) pentru dreptunghi
    hatch = msp.add_hatch(color=7, dxfattribs={'layer': 'stalpi'})  # Color=7 (alb/negru)
    #hatch.paths.add_polyline_path([(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)], is_closed=True)

    hatch = msp.add_hatch(color=7)
    path = hatch.paths.add_polyline_path(
    # get path vertices from associated LWPOLYLINE entity
    lwpolyline.get_points(format="xyb"),
    # get closed state also from associated LWPOLYLINE entity
    is_closed=lwpolyline.closed,
)
    #Hatch set pattern
    hatch.set_pattern_fill("ANSI31", scale=0.5)

    # Set association between boundary path and LWPOLYLINE
    hatch.associate(path, [lwpolyline])

    # Salvează fișierul DXF
    doc.saveas("dreptunghi_cu_hatch.dxf")

    print("Geometria a fost adăugată cu succes!")

def dxf (insertion_point, width, height, file):
    # Crează un document nou DXF
    doc = ezdxf.new('R2010')

    # Adaugă un nou layer numit 'stalpi' cu grosimea de linie 0.4
    doc.layers.add(name='stalpi', lineweight=40)  # 0.4 mm în ezdxf se setează ca 40 (în 1/100 mm)

    # Adaugă un model space
    msp = doc.modelspace()

    # Definim punctele dreptunghiului (coordonate pentru cele 4 colțuri)
    insertion_point = [0, 1]
    width = 0.25
    height = 0.25

    # Calculăm coordonatele colțurilor dreptunghiului
    x1, y1 = insertion_point
    x2, y2 = x1 + width, y1 + height

    # Creăm conturul dreptunghiului folosind o polilinie
    lwpolyline= msp.add_lwpolyline([(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)], close=True, dxfattribs={'layer': 'stalpi'})

    # Adaugă un hatch (hașurare) pentru dreptunghi
    hatch = msp.add_hatch(color=7, dxfattribs={'layer': 'stalpi'})  # Color=7 (alb/negru)
    #hatch.paths.add_polyline_path([(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)], is_closed=True)

    hatch = msp.add_hatch(color=7)
    path = hatch.paths.add_polyline_path(
    # get path vertices from associated LWPOLYLINE entity
    lwpolyline.get_points(format="xyb"),
    # get closed state also from associated LWPOLYLINE entity
    is_closed=lwpolyline.closed,
)
    #Hatch set pattern
    hatch.set_pattern_fill("ANSI31", scale=0.5)

    # Set association between boundary path and LWPOLYLINE
    hatch.associate(path, [lwpolyline])

    # Salvează fișierul DXF
    doc.saveas(file)

