import os
import tkinter
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk, ImageEnhance, ImageFilter


widgets = []

def mainmenu_window(): # Es el menú principal hecho funcion, no se puede volver al original asi que esta es la alternativa 
    # Labels Locales
    label = Label(root, text="Main menu", font='arial 15')
    label.place(x=20, y=150)
    widgets.append(label)
    # ---- Descripcion ----
    '''
    label_widget = Label(root, text="", height=8, width=110, font='minecraft 6', background="#000000")
    label_widget.place(x=40, y=210)  
    widgets.append(label_widget)
    '''



## ---------------- Window ----------------------
# Creamos la ventana
root = Tk()
root.tk.call('tk', 'scaling', 2.0)
root.geometry('640x360')
root.resizable(0, 0)
root.title("Anime-Term")
root.configure(bg='#FFFFFF')



'''
# Aplicamos fondo
bg_image = Image.open(r"resources\background_1080.jpg")
bg_image = bg_image.filter(ImageFilter.GaussianBlur(radius=6))
enhancer = ImageEnhance.Brightness(bg_image)
bg_image_darker = enhancer.enhance(0.5)
bg_photo = ImageTk.PhotoImage(bg_image_darker)
canvas = tkinter.Canvas(root, width=1080, height=720)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor="nw")
root.image = bg_photo
'''
## ----------------------------------------------
mainmenu_window()

root.mainloop()