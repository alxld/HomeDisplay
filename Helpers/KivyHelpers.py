from kivymd.uix.dialog import MDDialog
from kivy.core.window.window_sdl2 import WindowSDL

def FindDialogRoot(instance):
    while(type(instance) != MDDialog):
        if hasattr(instance, 'parent'):
            instance = instance.parent
        else:
            raise Exception("Unable to find dialog in instance hierachy")
        
    return instance

def FindChildByID(instance, id):
    if(hasattr(instance, "children")):
        for child in instance.children:
            if hasattr(child, "id") and child.id == id:
                return child
            else:
                if hasattr(child, "children"):
                    returned = FindChildByID(child, id)
                    if returned:
                        return returned

    return None

def FindWindowFromWidget(instance):
    while(hasattr(instance, 'parent')):
        instance = instance.parent
        if type(instance) == WindowSDL:
            return instance
        
    return instance