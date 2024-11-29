import dotbimpy
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCC.Core.gp import gp_Pnt, gp_Trsf, gp_Vec
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Display.SimpleGui import init_display
import numpy as np

class DotBimConverter:
    def __init__(self):
        self.builder = BRep_Builder()
        self.compound = TopoDS_Compound()
        self.builder.MakeCompound(self.compound)

    def read_dotbim(self, filepath):
        """
        Citește fișierul .bim și returnează obiectul dotbimpy
        """
        try:
            bim_file = dotbimpy.File.read(filepath)
            print(f"Fișierul .bim a fost citit cu succes.")
            print(f"Număr de mesh-uri: {len(bim_file.meshes)}")
            print(f"Număr de elemente: {len(bim_file.elements)}")
            return bim_file
        except Exception as e:
            print(f"Eroare la citirea fișierului .bim: {str(e)}")
            return None

    def create_transform(self, rotation, translation):
        """
        Creează o transformare din rotație și translație
        """
        transform = gp_Trsf()
        
        # Setăm translația
        if translation is not None:
            transform.SetTranslation(gp_Vec(*translation))
        
        # Setăm rotația (dacă este furnizată)
        if rotation is not None:
            # Aici ar trebui adăugată logica pentru rotație
            # În funcție de formatul rotației din fișierul .bim
            pass
            
        return transform

    def process_mesh(self, mesh, transform=None):
        """
        Procesează un singur mesh și îl convertește în format OCC
        """
        try:
            vertices = []
            # Convertim vertecșii
            for i in range(0, len(mesh.coordinates), 3):
                x = mesh.coordinates[i]
                y = mesh.coordinates[i + 1]
                z = mesh.coordinates[i + 2]
                point = gp_Pnt(x, y, z)
                
                # Aplicăm transformarea dacă există
                if transform is not None:
                    point.Transform(transform)
                    
                vertices.append(point)

            # Procesăm fețele
            for i in range(0, len(mesh.indices), 3):
                # Luăm cei trei indecși pentru triunghi
                idx1 = mesh.indices[i]
                idx2 = mesh.indices[i + 1]
                idx3 = mesh.indices[i + 2]

                # Creăm poligonul
                polygon = BRepBuilderAPI_MakePolygon()
                polygon.Add(vertices[idx1])
                polygon.Add(vertices[idx2])
                polygon.Add(vertices[idx3])
                polygon.Close()

                if polygon.IsDone():
                    try:
                        # Creăm fața
                        face_maker = BRepBuilderAPI_MakeFace(polygon.Wire())
                        if face_maker.IsDone():
                            face = face_maker.Face()
                            self.builder.Add(self.compound, face)
                    except Exception as e:
                        print(f"Eroare la crearea feței: {str(e)}")

            return True
        except Exception as e:
            print(f"Eroare la procesarea mesh-ului: {str(e)}")
            return False

    def convert_file(self, bim_file):
        """
        Convertește întregul fișier .bim în format OCC
        """
        try:
            # Procesăm fiecare element
            for element in bim_file.elements:
                # Găsim mesh-ul corespunzător
                mesh = next((m for m in bim_file.meshes if m.mesh_id == element.mesh_id), None)
                
                if mesh is not None:
                    # Creăm transformarea pentru acest element
                    transform = self.create_transform(element.rotation, element.vector)
                    
                    # Procesăm mesh-ul cu transformarea
                    self.process_mesh(mesh, transform)
                else:
                    print(f"Nu s-a găsit mesh-ul cu ID-ul {element.mesh_id}")

            return self.compound
        except Exception as e:
            print(f"Eroare la conversia fișierului: {str(e)}")
            return None

def main():
    try:
        # Inițializăm display-ul
        display, start_display, add_menu, add_function_to_menu = init_display()

        # Creăm convertorul
        converter = DotBimConverter()

        # Citim fișierul .bim
        filepath = "C:\\#BIMChess\\dotbim\\dotbim_file.bim"  # Înlocuiește cu calea reală
        bim_file = converter.read_dotbim(filepath)

        if bim_file is not None:
            # Convertim fișierul
            compound = converter.convert_file(bim_file)

            if compound is not None:
                # Afișăm rezultatul
                display.DisplayShape(compound, update=True)
                print("Modelul a fost convertit și afișat cu succes")
                
                # Opțional, putem adăuga informații suplimentare din fișierul .bim
                print("\nInformații despre model:")
                print(f"Versiune schema: {bim_file.schema_version}")
                if hasattr(bim_file, 'info'):
                    print(f"Informații: {bim_file.info}")

                start_display()
            else:
                print("Eroare la conversia modelului")
        else:
            print("Eroare la citirea fișierului .bim")

    except Exception as e:
        print(f"Eroare generală: {str(e)}")

if __name__ == "__main__":
    main()
    
    