import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def select_image():
    file_path = filedialog.askopenfilename(
        title="Seleccione una imagen",
        filetypes=[("Archivos de imagen", ".png .jpg .jpeg .gif .bmp")]
    )
    if file_path:
        display_image(file_path)

def display_image(file_path):
    print(file_path)
    image = Image.open(file_path)
    photo = ImageTk.PhotoImage(image)
    image_label.config(image=photo)
    image_label.image = photo  # Mantener la referencia para evitar que se recicle

root = tk.Tk()
root.title("Selector de Imágenes")

button = tk.Button(root, text="Seleccionar Imagen", command=select_image)
button.pack(pady=10)

image_label = tk.Label(root)
image_label.pack()

root.mainloop()
