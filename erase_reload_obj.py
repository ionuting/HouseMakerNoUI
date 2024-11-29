from OCC.Core.BRep import BRep_Builder
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
import uuid

class ObjectManager:
    def __init__(self, display):
        """
        Inițializează managerul de obiecte.
        
        Args:
            display: Obiectul display din pythonOCC
        """
        self.display = display
        self.objects = {}  # Dict pentru a ține evidența obiectelor {id: (shape, color, transparency)}
        self.builder = BRep_Builder()
        
    def add_object(self, shape, name=None, color=None, transparency=0):
        """
        Adaugă un obiect nou și îl afișează.
        
        Args:
            shape: Forma OCC de afișat
            name: Numele obiectului (opțional)
            color: Tuplu RGB (r, g, b) cu valori între 0 și 1
            transparency: Valoare între 0 și 1
            
        Returns:
            str: ID-ul obiectului adăugat
        """
        # Generăm un ID unic dacă nu este furnizat un nume
        obj_id = name if name else str(uuid.uuid4())
        
        # Convertim culoarea în format OCC dacă este specificată
        occ_color = None
        if color:
            occ_color = Quantity_Color(color[0], color[1], color[2], Quantity_TOC_RGB)
        
        # Stocăm obiectul și proprietățile sale
        self.objects[obj_id] = (shape, occ_color, transparency)
        
        # Afișăm obiectul
        ais_shape = self.display.DisplayShape(
            shape,
            color=occ_color if color else None,
            transparency=transparency,
            update=True
        )
        
        # Stocăm și referința AIS pentru ștergere ulterioară
        self.objects[obj_id] = (shape, occ_color, transparency, ais_shape[0])
        
        return obj_id
        
    def remove_object(self, obj_id):
        """
        Șterge un obiect specific din vizualizare.
        
        Args:
            obj_id: ID-ul obiectului de șters
            
        Returns:
            bool: True dacă obiectul a fost șters cu succes
        """
        if obj_id in self.objects:
            _, _, _, ais_shape = self.objects[obj_id]
            self.display.Context.Erase(ais_shape, True)
            del self.objects[obj_id]
            self.display.Repaint()
            return True
        return False
        
    def reload_object(self, obj_id, new_shape=None, new_color=None, new_transparency=None):
        """
        Reîncarcă un obiect cu proprietăți noi opționale.
        
        Args:
            obj_id: ID-ul obiectului de reîncărcat
            new_shape: Noua formă (opțional)
            new_color: Noua culoare (opțional)
            new_transparency: Noua transparență (opțional)
            
        Returns:
            bool: True dacă obiectul a fost reîncărcat cu succes
        """
        if obj_id in self.objects:
            old_shape, old_color, old_transparency, old_ais = self.objects[obj_id]
            
            # Folosim valorile vechi dacă nu sunt specificate altele noi
            shape = new_shape if new_shape is not None else old_shape
            color = new_color if new_color is not None else old_color
            transparency = new_transparency if new_transparency is not None else old_transparency
            
            # Ștergem vechiul obiect
            self.display.Context.Erase(old_ais, True)
            
            # Afișăm noul obiect
            ais_shape = self.display.DisplayShape(
                shape,
                color=color,
                transparency=transparency,
                update=True
            )
            
            # Actualizăm dicționarul
            self.objects[obj_id] = (shape, color, transparency, ais_shape[0])
            return True
        return False
        
    def get_object(self, obj_id):
        """
        Returnează datele unui obiect specific.
        
        Args:
            obj_id: ID-ul obiectului
            
        Returns:
            tuple: (shape, color, transparency) sau None dacă obiectul nu există
        """
        if obj_id in self.objects:
            shape, color, transparency, _ = self.objects[obj_id]
            return shape, color, transparency
        return None
        
    def clear_all(self):
        """
        Șterge toate obiectele din vizualizare.
        """
        for obj_id in list(self.objects.keys()):
            self.remove_object(obj_id)
        self.display.Repaint()

# Exemplu de utilizare
def main():
    display, start_display, add_menu, add_function_to_menu = init_display()
    
    # Creăm managerul de obiecte
    manager = ObjectManager(display)
    
    # Creăm câteva forme de test
    box1 = BRepPrimAPI_MakeBox(10, 10, 10).Shape()
    box2 = BRepPrimAPI_MakeBox(gp_Pnt(20, 0, 0), 10, 10, 10).Shape()
    cylinder = BRepPrimAPI_MakeCylinder(5, 15).Shape()
    
    # Adăugăm obiectele cu culori diferite
    box1_id = manager.add_object(box1, "box1", (1, 0, 0))  # roșu
    box2_id = manager.add_object(box2, "box2", (0, 1, 0))  # verde
    cyl_id = manager.add_object(cylinder, "cylinder", (0, 0, 1))  # albastru
    
    def remove_box1():
        manager.remove_object(box1_id)
        display.Repaint()
    
    def reload_box2():
        # Creăm o nouă cutie și o rotim
        trsf = gp_Trsf()
        trsf.SetRotation(gp_Vec(0, 0, 1).Normalized(), 0.5)  # rotație de ~30 grade
        new_box = BRepPrimAPI_MakeBox(gp_Pnt(20, 0, 0), 15, 15, 15).Shape()
        manager.reload_object(box2_id, new_box, (1, 1, 0))  # galben
        display.Repaint()
    
    def toggle_cylinder_transparency():
        _, color, transparency, _ = manager.objects[cyl_id]
        new_transparency = 0.8 if transparency < 0.5 else 0
        manager.reload_object(cyl_id, new_transparency=new_transparency)
        display.Repaint()
    
    # Adăugăm meniul și funcțiile
    add_menu('Operații')
    add_function_to_menu('Operații', remove_box1)
    add_function_to_menu('Operații', reload_box2)
    add_function_to_menu('Operații', toggle_cylinder_transparency)
    
    start_display()

if __name__ == '__main__':
    main()