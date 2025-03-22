import customtkinter as ctk
import json
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import unicodedata
import shutil 
import math  # Agregar al inicio del archivo

def eliminar_acentos(cadena):
	return ''.join(
		c for c in unicodedata.normalize('NFD', cadena)
		if unicodedata.category(c) != 'Mn'
	)

def select_image():
	global root
	root = Tk()
	file_path = filedialog.askopenfilename(
		title="Seleccione una imagen",
		filetypes=[("Archivos de imagen", ".png .jpg .jpeg .gif .bmp")]
	)
	if file_path:
		display_image(file_path)

def display_image(file_path):
	global selected_image_path, img, photo, color_label, image_label
	selected_image_path = file_path
	img = Image.open(file_path)
	new_size = (300, 300)
	img.thumbnail(new_size)
	photo = ImageTk.PhotoImage(img)
	image_label = Label(root)
	image_label.config(image=photo)
	image_label.image = photo
	image_label.bind("<Button-1>", get_color)
	image_label.pack()
	color_label = Label(root, text="Color", bg="white")
	color_label.pack()

def mostrar_imagen_producto(frame, imagen_ruta):
	# Ajustar la ruta relativa para que busque en la carpeta html/img
	ruta_absoluta = os.path.abspath(os.path.join('html', imagen_ruta))
	if imagen_ruta and os.path.exists(ruta_absoluta):
		try:
			img = Image.open(ruta_absoluta)
			img.thumbnail((100, 100))
			photo = ImageTk.PhotoImage(img)
			label = Label(frame, image=photo)
			label.image = photo  # Keep a reference to avoid garbage collection
			label.pack(anchor='w')
		except Exception as e:
			print(f"Error al cargar la imagen {imagen_ruta}: {e}")

color_hex_map = {
	"Negro": "#000000",
	"Blanco": "#FFFFFF",
	"Rojo": "#FF0000",
	"Verde": "#00FF00",
	"Azul": "#0000FF",
	"Amarillo": "#FFFF00",
	"Naranja": "#FFA500",
	"Cian": "#00FFFF",
	"Magenta": "#FF00FF",
	"Plata": "#C0C0C0",
	"Gris": "#808080",
	"Marron": "#800000",
	"Oliva": "#808000",
	"Verde Oscuro": "#008000",
	"Violeta": "#800080",
	"Verde Azulado": "#008080",
	"Azul Marino": "#000080"
}
	
def closest_color(rgb):
	colors = {
		"Negro": (0, 0, 0),
		"Blanco": (255, 255, 255),
		"Rojo": (255, 0, 0),
		"Verde": (0, 255, 0),
		"Azul": (0, 0, 255),
		"Amarillo": (255, 255, 0),
		"Naranja": (255, 165, 0),
		"Cian": (0, 255, 255),
		"Magenta": (255, 0, 255),
		"Plata": (192, 192, 192),
		"Gris": (128, 128, 128),
		"Marron": (128, 0, 0),
		"Oliva": (128, 128, 0),
		"Verde Oscuro": (0, 128, 0),
		"Violeta": (128, 0, 128),
		"Verde Azulado": (0, 128, 128),
		"Azul Marino": (0, 0, 128)
	}
	closest_color_name = min(colors, key=lambda color: sum((sc - rc) ** 2 for sc, rc in zip(colors[color], rgb)))
	return closest_color_name, colors[closest_color_name]

def get_color(event):
	x, y = event.x, event.y
	if img:
		rgb = img.getpixel((x, y))
		color_name, color_rgb = closest_color(rgb)
		color_hex = color_hex_map[color_name]
		color_label.config(bg=color_hex, text=color_name)
		return color_name
	return None

def reset_image():
	global selected_image_path
	selected_image_path = None

def generate_unique_id(base_id, productos):
	counter = 1
	unique_id = base_id
	existing_ids = {producto['id'] for producto in productos}
	while unique_id in existing_ids:
		unique_id = f"{base_id}_{counter}"
		counter += 1
	return unique_id

def redondear_precio(precio):
	"""Redondea el precio al número superior"""
	try:
		# Convertir a float y redondear hacia arriba
		return str(math.ceil(float(precio)))
	except ValueError:
		return precio

def eliminar_acentos(cadena):
	"""Elimina tildes y caracteres especiales de un texto"""
	if not isinstance(cadena, str):
		return cadena
	return ''.join(
		c for c in unicodedata.normalize('NFD', cadena)
		if unicodedata.category(c) != 'Mn'
	)

def normalizar_diccionario(diccionario):
	"""Normaliza todas las cadenas de texto en un diccionario"""
	for key, value in diccionario.items():
		if isinstance(value, dict):
			diccionario[key] = normalizar_diccionario(value)
		elif isinstance(value, list):
			diccionario[key] = [eliminar_acentos(item) if isinstance(item, str) else item for item in value]
		elif isinstance(value, str):
			diccionario[key] = eliminar_acentos(value)
	return diccionario

def agregar_variante(nombre_producto, categoria_producto, precio):
	if messagebox.askyesno("Agregar Variante", "¿Desea agregar una variante?"):
		select_image()
		
		# Actualizar el texto de los widgets existentes para cambiar el precio y el color
		# Entry_1.delete(0, END)
		# Entry_1.insert(0, nombre_producto)
		# Entry_3.delete(0, END)
		# Entry_3.insert(0, precio)
	else:
		messagebox.showinfo("Información", "No se agregó ninguna variante.")

def filtrar_productos(productos, nombre=None, categoria=None, precio_min=None, precio_max=None, disciplina=None, genero=None):
	filtrados = productos
	if nombre:
		nombre = eliminar_acentos(nombre.lower())
		filtrados = [p for p in filtrados if nombre in eliminar_acentos(p['titulo'].lower())]
	if categoria and categoria != "Todas":
		categoria = eliminar_acentos(categoria.lower())
		filtrados = [p for p in filtrados if categoria in eliminar_acentos(p['categoria_general'].lower()) or categoria in eliminar_acentos(p['categoria']['id'])]
	if precio_min is not None:
		filtrados = [p for p in filtrados if float(p['precio']) >= float(precio_min)]
	if precio_max is not None:
		filtrados = [p for p in filtrados if float(p['precio']) <= float(precio_max)]
	if disciplina and disciplina != "Todas":
		disciplina = eliminar_acentos(disciplina.lower())
		filtrados = [p for p in filtrados if disciplina in eliminar_acentos(p.get('disciplina', '').lower())]
	if genero and genero != "Todos":
		genero = eliminar_acentos(genero.lower())
		filtrados = [p for p in filtrados if genero in eliminar_acentos((p['genero'] or "").lower())]
	return filtrados

# Crear una clase gestora de datos:
class DataManager:
    def __init__(self):
        self.file_path = 'html/JS/productos.json'
        self.productos = []
        self.load_data()

    def load_data(self):
        try:
            with open(self.file_path, 'r') as file:
                self.productos = json.load(file)
        except FileNotFoundError:
            self.productos = []

    def save_data(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.productos, file, indent=2)

# Configurar tema y color
ctk.set_appearance_mode("dark")  # Temas: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # Temas: "blue", "dark-blue", "green"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configurar ventana principal
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        self.title("Deportes Güemes")
        
        # Variable para controlar el tema
        self.tema_actual = "dark"
        
        # Configurar fuentes
        self.font_title = ("Helvetica", 16, "bold")
        self.font_normal = ("Helvetica", 12)
        self.font_small = ("Helvetica", 10)
        
        # Crear menú primero (para que aparezca arriba)
        self.create_menu()
        
        # Modo venta switch
        self.modo_venta = ctk.CTkSwitch(
            self, 
            text="Modo Venta",
            command=self.toggle_modo_venta,
            font=self.font_normal
        )
        self.modo_venta.pack(pady=10)
        
        # Crear frame principal para el fondo
        self.background_frame = ctk.CTkFrame(self)
        self.background_frame.pack(fill="both", expand=True)
        
        # Cargar imagen de fondo
        try:
            self.original_image = Image.open("html/img/Logo.jpeg")
            self.actualizar_imagen_fondo()
            self.bind('<Configure>', self.on_resize)
        except Exception as e:
            print(f"Error al cargar la imagen de fondo: {e}")

    def actualizar_imagen_fondo(self):
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        
        if window_width > 1 and window_height > 1:
            imagen_fondo = self.original_image.copy()
            imagen_fondo.thumbnail((window_width, window_height))
            
            self.bg_image = ctk.CTkImage(
                light_image=imagen_fondo,
                dark_image=imagen_fondo,
                size=(window_width, window_height)
            )
            
            if hasattr(self, 'bg_label'):
                self.bg_label.configure(image=self.bg_image)
            else:
                self.bg_label = ctk.CTkLabel(
                    self.background_frame, 
                    image=self.bg_image,
                    text=""
                )
                self.bg_label.place(relx=0.5, rely=0.5, anchor="center")

    def on_resize(self, event=None):
        if event.widget == self:
            self.actualizar_imagen_fondo()

    def create_menu(self):
        menu_frame = ctk.CTkFrame(self)
        menu_frame.pack(side="top", fill="x", pady=10)
        
        ctk.CTkButton(
            menu_frame,
            text="Ingresar Nuevo Producto",
            command=self.show_nuevo_producto,
            font=self.font_normal
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            menu_frame,
            text="Ver Productos",
            command=self.show_ver_productos,
            font=self.font_normal
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            menu_frame,
            text="Lista de Precios",
            command=self.show_lista_precios,
            font=self.font_normal
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            menu_frame,
            text="Cambiar Tema",
            command=self.toggle_tema,
            fg_color="gray40"
        ).pack(side="right", padx=5)

    def toggle_tema(self):
        if self.tema_actual == "dark":
            ctk.set_appearance_mode("light")
            self.tema_actual = "light"
        else:
            ctk.set_appearance_mode("dark")
            self.tema_actual = "dark"

    def show_nuevo_producto(self):
        dialog = ProductoDialog(self)
        dialog.grab_set()

    def show_ver_productos(self):
        dialog = VerProductosDialog(self)
        dialog.grab_set()
            
    def toggle_modo_venta(self):
        if self.modo_venta.get():
            dialog = ModoVentaDialog(self)
            dialog.grab_set()

    def show_lista_precios(self):
        dialog = ListaPreciosDialog(self)
        dialog.grab_set()

class VerProductosDialog(ctk.CTkToplevel):
	def __init__(self, parent):
		super().__init__(parent)
		self.title("Ver Productos")
		self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
		
		# Inicializar variables
		self.productos_seleccionados = []
		self.productos = []
		self.productos_frame = None
		
		# Frame principal
		self.main_frame = ctk.CTkFrame(self)
		self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
		
		# Crear frame de filtros
		self.crear_filtros()
		
		# Crear frame scrollable inicial
		self.productos_frame = ctk.CTkScrollableFrame(self.main_frame)
		self.productos_frame.pack(fill="both", expand=True, padx=10, pady=5)
		
		# Cargar productos
		self.cargar_productos()

	def mostrar_productos(self, productos_filtrados):
		# Limpiar el frame anterior
		if self.productos_frame:
			for widget in self.productos_frame.winfo_children():
				widget.destroy()
		
		# Configurar el grid
		self.productos_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="column")
		
		# Reiniciar lista de productos seleccionados
		self.productos_seleccionados = []
		
		# Variables para el grid
		row = 0
		col = 0
		
		# Mostrar productos
		for producto in productos_filtrados:
			if not producto.get('es_variante', False):
				card = self.crear_producto_card(self.productos_frame, producto)
				card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
				
				col += 1
				if col >= 3:
					col = 0
					row += 1

	def crear_filtros(self):
		filtro_frame = ctk.CTkFrame(self.main_frame)
		filtro_frame.pack(fill="x", padx=10, pady=5)
		
		# Nombre
		ctk.CTkLabel(filtro_frame, text="Nombre").pack(side="left", padx=5)
		self.filtro_nombre = ctk.CTkEntry(filtro_frame)
		self.filtro_nombre.pack(side="left", padx=5)
		self.filtro_nombre.bind('<KeyRelease>', lambda e: self.aplicar_filtros())
		
		# Categoría
		ctk.CTkLabel(filtro_frame, text="Categoría").pack(side="left", padx=5)
		self.filtro_categoria = ctk.CTkOptionMenu(
			filtro_frame,
			values=["Todas", "Indumentaria", "Accesorios", "REMERAS", "PANTALONES", "ABRIGOS"],
			command=lambda x: self.aplicar_filtros()
		)
		self.filtro_categoria.pack(side="left", padx=5)
		
		# Disciplina
		ctk.CTkLabel(filtro_frame, text="Disciplina").pack(side="left", padx=5)
		self.filtro_disciplina = ctk.CTkOptionMenu(
			filtro_frame,
			values=["Todas", "Futbol", "Basquet", "Tenis", "Natacion", "Running", 
					"Boxeo", "Voley", "Rugby", "Hockey", "Yoga", "Fitness", "Musculacion"],
			command=lambda x: self.aplicar_filtros()
		)
		self.filtro_disciplina.pack(side="left", padx=5)
		
		# Género
		ctk.CTkLabel(filtro_frame, text="Género").pack(side="left", padx=5)
		self.filtro_genero = ctk.CTkOptionMenu(
			filtro_frame,
			values=["Todos", "Femenino", "Masculino", "Niño", "Niña", "Unisex", "No"],
			command=lambda x: self.aplicar_filtros()
		)
		self.filtro_genero.pack(side="left", padx=5)
		
		 # Talles (después del filtro de género)
		ctk.CTkLabel(filtro_frame, text="Talle").pack(side="left", padx=5)
		self.filtro_talle = ctk.CTkOptionMenu(
			filtro_frame,
			values=["Todos", "No", "S", "M", "L", "XL"],
			command=lambda x: self.aplicar_filtros()
		)
		self.filtro_talle.pack(side="left", padx=5)
		
		# Precio Mínimo
		ctk.CTkLabel(filtro_frame, text="Precio Mínimo").pack(side="left", padx=5)
		self.filtro_precio_min = ctk.CTkEntry(filtro_frame)
		self.filtro_precio_min.pack(side="left", padx=5)
		self.filtro_precio_min.bind('<KeyRelease>', lambda e: self.aplicar_filtros())
		
		# Precio Máximo
		ctk.CTkLabel(filtro_frame, text="Precio Máximo").pack(side="left", padx=5)
		self.filtro_precio_max = ctk.CTkEntry(filtro_frame)
		self.filtro_precio_max.pack(side="left", padx=5)
		self.filtro_precio_max.bind('<KeyRelease>', lambda e: self.aplicar_filtros())

		# Frame para botones de acción
		botones_frame = ctk.CTkFrame(self.main_frame)
		botones_frame.pack(fill="x", padx=10, pady=5)
		
		# Botones de selección
		ctk.CTkButton(
			botones_frame,
			text="Seleccionar Todos",
			command=self.seleccionar_todos,
			fg_color="gray40"
		).pack(side="left", padx=5)
		
		ctk.CTkButton(
			botones_frame,
			text="Deseleccionar Todos",
			command=self.deseleccionar_todos,
			fg_color="gray40"
		).pack(side="left", padx=5)
		
		# Botones de acciones masivas
		ctk.CTkButton(
			botones_frame,
			text="Actualizar Precios Seleccionados",
			command=self.actualizar_precios_seleccionados,
			fg_color="blue"
		).pack(side="left", padx=5)
		
		ctk.CTkButton(
			botones_frame,
			text="Actualizar Stock Seleccionados",
			command=self.actualizar_stock_seleccionados,
			fg_color="green"
		).pack(side="left", padx=5)

	def aplicar_filtros(self, *args):
		try:
			nombre = self.filtro_nombre.get().lower()
			categoria = self.filtro_categoria.get()
			disciplina = self.filtro_disciplina.get()  # Obtener valor del filtro de disciplina
			genero = self.filtro_genero.get()
			talle = self.filtro_talle.get()
			precio_min = self.filtro_precio_min.get() or "0"
			precio_max = self.filtro_precio_max.get() or "999999999"
			
			# Filtrar productos
			productos_filtrados = [p for p in self.productos if
				nombre in p['titulo'].lower() and
				(categoria == "Todas" or 
				 categoria.upper() == p['categoria']['nombre'] or 
				 categoria.lower() in p['categoria_general'].lower()) and
				(disciplina == "Todas" or disciplina.lower() == p.get('disciplina', '').lower()) and  # Agregar filtro de disciplina
				(genero == "Todos" or genero.lower() == p.get('genero', '').lower()) and
				(talle == "Todos" or talle in p.get('talles', [])) and
				float(p['precio']) >= float(precio_min) and
				float(p['precio']) <= float(precio_max)]
				
			# Actualizar vista
			self.mostrar_productos(productos_filtrados)
			
		except ValueError as e:
			print(f"Error al aplicar filtros: {e}")

	def cargar_productos(self):
		try:
			with open('html/JS/productos.json', 'r') as archivo:
				self.productos = json.load(archivo)
		except FileNotFoundError:
			self.productos = []
			
		self.mostrar_productos(self.productos)
		
	def crear_producto_card(self, parent, producto):
		# Crear frame para la card
		card = ctk.CTkFrame(parent)
		
		# Frame para imagen
		img_frame = ctk.CTkFrame(card)
		img_frame.pack(fill="x", padx=5, pady=5)
		
		# Imagen del producto
		if producto['imagen']:
			try:
				ruta_absoluta = os.path.abspath(os.path.join('html', producto['imagen'].replace('./', '')))
				if os.path.exists(ruta_absoluta):
					# Usar CTkImage en lugar de PhotoImage
					pil_image = Image.open(ruta_absoluta)
					pil_image.thumbnail((200, 200))
					ctk_image = ctk.CTkImage(
						light_image=pil_image,
						dark_image=pil_image,
						size=(200, 200)
					)
					imagen_label = ctk.CTkLabel(
						img_frame, 
						image=ctk_image, 
						text=""
					)
					imagen_label.pack(expand=True, fill="both")
			except Exception as e:
				print(f"Error al cargar la imagen {producto['imagen']}: {e}")
		
		# Frame para información
		info_frame = ctk.CTkFrame(card)
		info_frame.pack(fill="x", padx=5, pady=5)
		
		# Checkbox y título en la misma línea
		header_frame = ctk.CTkFrame(info_frame)
		header_frame.pack(fill="x", pady=2)
		
		var = ctk.BooleanVar()
		self.productos_seleccionados.append((producto, var))
		ctk.CTkCheckBox(header_frame, text="", variable=var).pack(side="left", padx=5)
		ctk.CTkLabel(header_frame, text=producto['titulo'], font=("", 14, "bold")).pack(side="left")
		
		# Información del producto
		ctk.CTkLabel(info_frame, text=f"Precio: ${producto['precio']}").pack(anchor="w")
		ctk.CTkLabel(info_frame, text=f"Stock: {producto.get('stock', 0)}").pack(anchor="w")
		
		# Color con indicador visual
		color_frame = ctk.CTkFrame(info_frame)
		color_frame.pack(fill="x", pady=2)
		color_name = producto.get('color', 'No especificado')
		color_label = ctk.CTkLabel(color_frame, text=f"Color: {color_name}")
		color_label.pack(side="left")
		
		# Frame para botones
		botones_frame = ctk.CTkFrame(card)
		botones_frame.pack(fill="x", padx=5, pady=5)
		
		# Botones con iconos o colores diferentes
		ctk.CTkButton(
			botones_frame,
			text="Modificar",
			command=lambda p=producto: self.modificar_producto(p),
			fg_color="green"
		).pack(side="left", padx=2, expand=True)
		
		ctk.CTkButton(
			botones_frame,
			text="Eliminar",
			command=lambda p=producto: self.eliminar_producto(p),
			fg_color="red"
		).pack(side="left", padx=2, expand=True)
		
		ctk.CTkButton(
			botones_frame,
			text="Stock",
			command=lambda p=producto: self.actualizar_stock(p),
			fg_color="blue"
		).pack(side="left", padx=2, expand=True)
		
		return card

	def seleccionar_todos(self):
		for _, var in self.productos_seleccionados:
			var.set(True)

	def deseleccionar_todos(self):
		for _, var in self.productos_seleccionados:
			var.set(False)

	def actualizar_stock(self, producto):
		dialog = ctk.CTkToplevel(self)
		dialog.title("Actualizar Stock")
		dialog.geometry("400x300")

		# Frame principal
		frame = ctk.CTkFrame(dialog)
		frame.pack(fill="both", expand=True, padx=20, pady=20)

		# Información del producto
		ctk.CTkLabel(frame, text=f"Producto: {producto['titulo']}").pack(pady=5)
		ctk.CTkLabel(frame, text=f"Stock Actual: {producto.get('stock', 0)}").pack(pady=5)

		# Entrada para cantidad
		ctk.CTkLabel(frame, text="Cantidad stock agregado").pack(pady=5)
		entry_cantidad = ctk.CTkEntry(frame)
		entry_cantidad.pack(pady=10)

		def aplicar_ajuste():
			cantidad = entry_cantidad.get()
			if cantidad:
				try:
					cantidad = int(cantidad)
					nuevo_stock = producto.get('stock', 0) + cantidad
					
					# Verificar que el nuevo stock no sea menor a 0
					if nuevo_stock < 0:
						messagebox.showerror("Error", "El stock no puede ser menor a 0")
						return
					
					producto['stock'] = nuevo_stock
					
					# Actualizar el archivo JSON
					with open('html/JS/productos.json', 'r') as archivo:
						productos = json.load(archivo)
					
					# Encontrar y actualizar el producto
					for i, p in enumerate(productos):
						if p['id'] == producto['id']:
							productos[i] = producto
							break
					
					with open('html/JS/productos.json', 'w') as archivo:
						json.dump(productos, archivo, indent=2)
					
					messagebox.showinfo("Información", "Stock actualizado correctamente.")
					dialog.destroy()
					# Recargar la vista de productos
					self.cargar_productos()
					
				except ValueError:
					messagebox.showerror("Error", "Por favor, ingrese un valor numérico válido.")
		
		# Botón de actualizar
		ctk.CTkButton(
			frame,
			text="Actualizar Stock",
			command=aplicar_ajuste
		).pack(pady=10)

	def actualizar_precios_seleccionados(self):
		# Verificar si hay productos seleccionados
		productos_a_actualizar = [(p, v) for p, v in self.productos_seleccionados if v.get()]
		
		if not productos_a_actualizar:
			messagebox.showwarning("Advertencia", "No hay productos seleccionados")
			return
		
		# Crear ventana de actualización
		dialog = ctk.CTkToplevel(self)
		dialog.title("Actualizar Precios Seleccionados")
		dialog.geometry("500x300")  # Altura reducida
		
		# Frame superior para controles
		control_frame = ctk.CTkFrame(dialog)
		control_frame.pack(fill="x", padx=20, pady=10)
		
		# Frame izquierdo para tipo de actualización
		tipo_frame = ctk.CTkFrame(control_frame)
		tipo_frame.pack(side="left", padx=10)
		
		ctk.CTkLabel(tipo_frame, text="Tipo de Actualización").pack(pady=2)
		tipo_actualizacion = ctk.StringVar(value="porcentaje")
		
		ctk.CTkRadioButton(
			tipo_frame, 
			text="Porcentaje",
			variable=tipo_actualizacion,
			value="porcentaje"
		).pack(pady=2)
		
		ctk.CTkRadioButton(
			tipo_frame, 
			text="Monto Fijo",
			variable=tipo_actualizacion,
			value="monto"
		).pack(pady=2)
		
		# Frame derecho para valor y botón
		valor_frame = ctk.CTkFrame(control_frame)
		valor_frame.pack(side="left", padx=10)
		
		ctk.CTkLabel(valor_frame, text="Valor").pack(pady=2)
		entry_valor = ctk.CTkEntry(valor_frame)
		entry_valor.pack(pady=2)
		
		# Botón de actualizar
		ctk.CTkButton(
			valor_frame,
			text="Actualizar Precios",
			command=lambda: aplicar_actualizacion(),
			fg_color="blue"
		).pack(pady=5)
		
		# Lista de productos en frame separado
		ctk.CTkLabel(dialog, text="Productos seleccionados:").pack(pady=5)
		productos_frame = ctk.CTkFrame(dialog)
		productos_frame.pack(fill="both", expand=True, padx=20, pady=5)
		
		# Mostrar productos seleccionados
		for producto, _ in productos_a_actualizar:
			ctk.CTkLabel(
				productos_frame, 
				text=f"{producto['titulo']} - Precio actual: ${producto['precio']}"
			).pack(anchor="w", pady=2)

		def aplicar_actualizacion():
			valor = entry_valor.get()
			if not valor:
				messagebox.showerror("Error", "Ingrese un valor")
				return
				
			try:
				valor = float(valor)
				with open('html/JS/productos.json', 'r') as archivo:
					todos_productos = json.load(archivo)
				
				for producto, _ in productos_a_actualizar:
					# Calcular nuevo precio
					precio_actual = float(producto['precio'])
					if tipo_actualizacion.get() == "porcentaje":
						nuevo_precio = precio_actual * (1 + valor/100)
					else:  # monto
						nuevo_precio = precio_actual + valor
					
					# Redondear y actualizar precio
					producto['precio'] = redondear_precio(str(nuevo_precio))
					
					# Actualizar en la lista completa
					for i, p in enumerate(todos_productos):
						if p['id'] == producto['id']:
							todos_productos[i] = producto
							break
				
				# Guardar cambios
				with open('html/JS/productos.json', 'w') as archivo:
					json.dump(todos_productos, archivo, indent=2)
				
				messagebox.showinfo("Éxito", "Precios actualizados correctamente")
				dialog.destroy()
				self.cargar_productos()  # Recargar vista
				
			except ValueError:
				messagebox.showerror("Error", "Ingrese un valor numérico válido")

	def actualizar_stock_seleccionados(self):
		# Verificar si hay productos seleccionados
		productos_a_actualizar = [(p, v) for p, v in self.productos_seleccionados if v.get()]
		
		if not productos_a_actualizar:
			messagebox.showwarning("Advertencia", "No hay productos seleccionados")
			return
		
		# Crear ventana de actualización
		dialog = ctk.CTkToplevel(self)
		dialog.title("Actualizar Stock Seleccionados")
		dialog.geometry("500x400")
		
		# Frame principal
		frame = ctk.CTkFrame(dialog)
		frame.pack(fill="both", expand=True, padx=20, pady=20)
		
		# Cantidad a agregar/restar
		ctk.CTkLabel(frame, text="Cantidad de stock a agregar/restar").pack(pady=5)
		entry_cantidad = ctk.CTkEntry(frame)
		entry_cantidad.pack(pady=10)
		
		# Lista de productos seleccionados
		productos_frame = ctk.CTkScrollableFrame(frame)
		productos_frame.pack(fill="both", expand=True, pady=10)
		
		for producto, _ in productos_a_actualizar:
			producto_frame = ctk.CTkFrame(productos_frame)
			producto_frame.pack(fill="x", pady=2)
			ctk.CTkLabel(producto_frame, 
						text=f"{producto['titulo']} - Stock actual: {producto.get('stock', 0)}"
			).pack(pady=2)
		
		def aplicar_actualizacion():
			cantidad = entry_cantidad.get()
			if not cantidad:
				messagebox.showerror("Error", "Ingrese una cantidad")
				return
				
			try:
				cantidad = int(cantidad)
				error_productos = []
				
				# Verificar primero si algún producto quedaría con stock negativo
				for producto, _ in productos_a_actualizar:
					nuevo_stock = producto.get('stock', 0) + cantidad
					if nuevo_stock < 0:
						error_productos.append(producto['titulo'])
				
				if error_productos:
					messagebox.showerror(
						"Error", 
						"Los siguientes productos quedarían con stock negativo:\n" + 
						"\n".join(error_productos)
					)
					return
				
				# Si todo está bien, actualizar
				with open('html/JS/productos.json', 'r') as archivo:
					todos_productos = json.load(archivo)
				
				for producto, _ in productos_a_actualizar:
					producto['stock'] = producto.get('stock', 0) + cantidad
					
					# Actualizar en la lista completa
					for i, p in enumerate(todos_productos):
						if p['id'] == producto['id']:
							todos_productos[i] = producto
							break
				
				# Guardar cambios
				with open('html/JS/productos.json', 'w') as archivo:
					json.dump(todos_productos, archivo, indent=2)
				
				messagebox.showinfo("Éxito", "Stock actualizado correctamente")
				dialog.destroy()
				self.cargar_productos()  # Recargar vista
				
			except ValueError:
				messagebox.showerror("Error", "Ingrese un valor numérico válido")
		
		# Botón de actualizar
		ctk.CTkButton(
			frame,
			text="Actualizar Stock",
			command=aplicar_actualizacion,
			fg_color="green"
		).pack(pady=10)

	def eliminar_producto(self, producto):
		"""Eliminar producto usando CustomTkinter con diálogo Sí/No"""
		# Crear diálogo de confirmación personalizado
		dialog = ctk.CTkToplevel(self)
		dialog.title("Confirmar eliminación")
		dialog.geometry("400x150")
		dialog.transient(self)  # Hacer el diálogo modal
		
		# Frame principal
		frame = ctk.CTkFrame(dialog)
		frame.pack(fill="both", expand=True, padx=20, pady=20)
		
		# Mensaje
		ctk.CTkLabel(
			frame,
			text="¿Está seguro de que desea eliminar este producto?",
			font=("", 12)
		).pack(pady=10)
		
		# Frame para botones
		button_frame = ctk.CTkFrame(frame)
		button_frame.pack(pady=10)
		
		def confirmar():
			try:
				# Leer productos actuales
				with open('html/JS/productos.json', 'r') as archivo:
					productos = json.load(archivo)
				
				# Filtrar el producto a eliminar
				productos = [p for p in productos if p['id'] != producto['id']]
				
				# Guardar la lista actualizada
				with open('html/JS/productos.json', 'w') as archivo:
					json.dump(productos, archivo, indent=2)
				
				# Actualizar la vista
				self.productos = productos
				self.cargar_productos()
				
				# Mostrar mensaje de éxito
				messagebox.showinfo("Éxito", "Producto eliminado correctamente")
				
			except Exception as e:
				messagebox.showerror("Error", f"No se pudo eliminar el producto: {str(e)}")
			finally:
				dialog.destroy()
		
		# Botones
		ctk.CTkButton(
			button_frame,
			text="Sí",
			command=confirmar,
			fg_color="red"
		).pack(side="left", padx=10)
		
		ctk.CTkButton(
			button_frame,
			text="No",
			command=dialog.destroy
		).pack(side="left", padx=10)
		
		# Centrar el diálogo
		dialog.update()
		dialog_width = dialog.winfo_width()
		dialog_height = dialog.winfo_height()
		screen_width = dialog.winfo_screenwidth()
		screen_height = dialog.winfo_screenheight()
		x = (screen_width - dialog_width) // 2
		y = (screen_height - dialog_height) // 2
		dialog.geometry(f"+{x}+{y}")
		
		dialog.grab_set()  # Hacer el diálogo modal

	def modificar_producto(self, producto):
		# Crear ventana de modificación
		dialog = ctk.CTkToplevel(self)
		dialog.title("Modificar Producto")
		dialog.geometry("400x300")
		
		# Frame principal
		frame = ctk.CTkFrame(dialog)
		frame.pack(fill="both", expand=True, padx=20, pady=20)
		
		# Nombre del producto
		ctk.CTkLabel(frame, text="Nombre Producto").pack(pady=5)
		entry_nombre = ctk.CTkEntry(frame, width=300)
		entry_nombre.insert(0, producto['titulo'])
		entry_nombre.pack(pady=5)
		
		# Precio
		ctk.CTkLabel(frame, text="Precio").pack(pady=5)
		entry_precio = ctk.CTkEntry(frame, width=300)
		entry_precio.insert(0, producto['precio'])
		entry_precio.pack(pady=5)
		
		def guardar_cambios():
			try:
				# Actualizar datos del producto
				producto['titulo'] = entry_nombre.get()
				producto['precio'] = redondear_precio(entry_precio.get())
				
				# Leer todos los productos
				with open('html/JS/productos.json', 'r') as archivo:
					productos = json.load(archivo)
				
				# Encontrar y actualizar el producto
				for i, p in enumerate(productos):
					if p['id'] == producto['id']:
						productos[i] = producto
						break
				
				# Guardar cambios
				with open('html/JS/productos.json', 'w') as archivo:
					json.dump(productos, archivo, indent=2)
				
				messagebox.showinfo("Éxito", "Producto modificado correctamente")
				dialog.destroy()
				self.cargar_productos()  # Recargar vista
				
			except Exception as e:
				messagebox.showerror("Error", f"No se pudo modificar el producto: {str(e)}")
		
		# Botón de guardar
		ctk.CTkButton(
			frame,
			text="Guardar Cambios",
			command=guardar_cambios,
			fg_color="blue"
		).pack(pady=20)

class ModoVentaDialog(ctk.CTkToplevel):
	def __init__(self, parent):
		super().__init__(parent)
		self.title("Modo Venta")
		self.geometry("800x600")  # Tamaño más razonable

		# Frame principal con dos columnas
		self.main_frame = ctk.CTkFrame(self)
		self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

		# Frame izquierdo para entrada
		self.input_frame = ctk.CTkFrame(self.main_frame)
		self.input_frame.pack(side="left", fill="both", expand=True, padx=10)

		# Frame derecho para lista
		self.list_frame = ctk.CTkFrame(self.main_frame)
		self.list_frame.pack(side="right", fill="both", expand=True, padx=10)

		# Entrada de código
		ctk.CTkLabel(self.input_frame, 
					text="Ingrese Código de Barras",
					font=("", 14, "bold")).pack(pady=10)
		self.entry_codigo_barras = ctk.CTkEntry(self.input_frame, width=200)
		self.entry_codigo_barras.pack(pady=5)
		self.entry_codigo_barras.bind("<Return>", self.procesar_codigo)
		self.entry_codigo_barras.focus()  # Foco automático

		# Lista de códigos escaneados
		ctk.CTkLabel(self.list_frame, 
					text="Códigos Escaneados",
					font=("", 14, "bold")).pack(pady=10)
		
		# Frame scrollable para la lista
		self.lista_frame = ctk.CTkScrollableFrame(self.list_frame)
		self.lista_frame.pack(fill="both", expand=True)

		# Lista para mantener registro de códigos escaneados
		self.codigos_escaneados = []

	def procesar_codigo(self, event=None):
		codigo = self.entry_codigo_barras.get()
		if not codigo:
			return

		# Limpiar entrada
		self.entry_codigo_barras.delete(0, 'end')

		try:
			# Cargar todos los productos
			with open('html/JS/productos.json', 'r') as archivo:
				productos = json.load(archivo)

			# Buscar producto con ese código
			producto = None
			producto_index = -1
			for i, p in enumerate(productos):
				if p.get('codigo_barras') == codigo:
					producto = p
					producto_index = i
					break

			# Crear frame para el código escaneado
			item_frame = ctk.CTkFrame(self.lista_frame)
			item_frame.pack(fill="x", padx=5, pady=2)

			if producto:
				# Verificar stock
				if producto.get('stock', 0) > 0:
					# Restar stock
					productos[producto_index]['stock'] -= 1
					
					# Guardar cambios en el archivo
					with open('html/JS/productos.json', 'w') as archivo:
						json.dump(productos, archivo, indent=2)
					
					# Mostrar información del producto
					ctk.CTkLabel(item_frame, 
							   text=f"Código: {codigo}",
							   font=("", 12)).pack(side="left", padx=5)
					ctk.CTkLabel(item_frame,
							   text=f"Producto: {producto['titulo']}",
							   font=("", 12, "bold"),
							   text_color="green").pack(side="left", padx=5)
					ctk.CTkLabel(item_frame,
							   text=f"${producto['precio']}",
							   font=("", 12)).pack(side="right", padx=5)
					ctk.CTkLabel(item_frame,
							   text=f"Stock restante: {producto['stock']}",
							   font=("", 12)).pack(side="right", padx=5)
				else:
					# Producto sin stock
					ctk.CTkLabel(item_frame, 
							   text=f"Código: {codigo}",
							   font=("", 12)).pack(side="left", padx=5)
					ctk.CTkLabel(item_frame,
							   text=f"Producto: {producto['titulo']} - SIN STOCK",
							   font=("", 12),
							   text_color="orange").pack(side="left", padx=5)
			else:
				# Producto no encontrado
				ctk.CTkLabel(item_frame, 
						   text=f"Código: {codigo}",
						   font=("", 12)).pack(side="left", padx=5)
				ctk.CTkLabel(item_frame,
						   text="Producto no encontrado",
						   font=("", 12),
						   text_color="red").pack(side="left", padx=5)

			# Agregar botón para eliminar y restaurar stock
			def eliminar_item():
				if producto and hasattr(item_frame, 'stock_restado'):
					# Restaurar stock
					with open('html/JS/productos.json', 'r') as archivo:
						productos_actuales = json.load(archivo)
					for i, p in enumerate(productos_actuales):
						if p['id'] == producto['id']:
							productos_actuales[i]['stock'] += 1
							break
					with open('html/JS/productos.json', 'w') as archivo:
						json.dump(productos_actuales, archivo, indent=2)
				item_frame.destroy()

			ctk.CTkButton(
				item_frame,
				text="X",
				width=30,
				command=eliminar_item,
				fg_color="red"
			).pack(side="right", padx=5)

			# Marcar que se restó stock
			if producto and producto.get('stock', 0) > 0:
				item_frame.stock_restado = True

		except Exception as e:
			messagebox.showerror("Error", f"Error al procesar código: {str(e)}")

class ProductoDialog(ctk.CTkToplevel):
	def __init__(self, parent, codigo_barras=None):
		super().__init__(parent)
		self.title("Ingresar Nuevo Producto")
		self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")

		# Crear frame principal scrollable
		self.main_frame = ctk.CTkScrollableFrame(self)
		self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

		# Nombre Producto
		ctk.CTkLabel(self.main_frame, text="Nombre Producto").pack(pady=5)
		self.entry_nombre = ctk.CTkEntry(self.main_frame, width=300)
		self.entry_nombre.pack(pady=5)

		# Botón Seleccionar Imagen
		self.button_imagen = ctk.CTkButton(
			self.main_frame, 
			text="Seleccionar Imagen",
			command=self.select_image
		)
		self.button_imagen.pack(pady=10)
		
		# Frame para imagen y color
		self.image_frame = ctk.CTkFrame(self.main_frame)
		self.image_frame.pack(pady=10)
		
		# Label para la imagen
		self.image_label = ctk.CTkLabel(self.image_frame, text="")
		self.image_label.pack(pady=10)
		
		# Label para el color
		self.color_frame = ctk.CTkFrame(self.image_frame)
		self.color_frame.pack(pady=5)
		self.color_label = ctk.CTkLabel(self.color_frame, text="Color")
		self.color_label.pack(pady=5)

		# Categoría Producto
		opciones_unidades = ["Categoria Producto", "Remeras", "Abrigos", "Pantalones", "Accesorios"]
		self.variable_unidad = ctk.StringVar(value=opciones_unidades[0])
		self.categoria_menu = ctk.CTkOptionMenu(
			self.main_frame,
			values=opciones_unidades,
			variable=self.variable_unidad
		)
		self.categoria_menu.pack(pady=10)

		# Precio
		ctk.CTkLabel(self.main_frame, text="Precio").pack(pady=5)
		self.entry_precio = ctk.CTkEntry(self.main_frame, width=300)
		self.entry_precio.pack(pady=5)

		# Género
		opciones_gen = ["Genero", "Femenino", "Masculino", "Niño", "Niña", "Unisex", "No"]
		self.variable_gen = ctk.StringVar(value=opciones_gen[0])
		self.genero_menu = ctk.CTkOptionMenu(
			self.main_frame,
			values=opciones_gen,
			variable=self.variable_gen
		)
		self.genero_menu.pack(pady=10)

		# Talles
		ctk.CTkLabel(self.main_frame, text="Talles").pack(pady=5)
		self.talles_frame = ctk.CTkFrame(self.main_frame)
		self.talles_frame.pack(pady=10)
		
		self.talle_vars = {}
		talles = ["No", "S", "M", "L", "XL"]
		for talle in talles:
			var = ctk.BooleanVar()
			self.talle_vars[talle] = var
			ctk.CTkCheckBox(
				self.talles_frame, 
				text=talle,
				variable=var
			).pack(side="left", padx=5)

		# Disciplina
		opciones_disciplinas = ["Deportes", "Futbol", "Basquet", "Tenis", "Natacion", 
							  "Running", "Boxeo", "Voley", "Rugby", "Hockey", "Yoga", 
							  "Fitness", "Musculacion"]
		self.variable_disciplina = ctk.StringVar(value=opciones_disciplinas[0])
		self.disciplina_menu = ctk.CTkOptionMenu(
			self.main_frame,
			values=opciones_disciplinas,
			variable=self.variable_disciplina
		)
		self.disciplina_menu.pack(pady=10)

		# Es variante
		self.var_es_variante = ctk.BooleanVar()
		self.check_variante = ctk.CTkCheckBox(
			self.main_frame,
			text="Es variante de otro producto",
			variable=self.var_es_variante
		)
		self.check_variante.pack(pady=10)

		# Código de Barras
		ctk.CTkLabel(self.main_frame, text="Código de Barras").pack(pady=5)
		self.entry_codigo_barras = ctk.CTkEntry(self.main_frame, width=300)
		self.entry_codigo_barras.pack(pady=5)
		if codigo_barras:
			self.entry_codigo_barras.insert(0, codigo_barras)

		# Botón Guardar
		self.button_guardar = ctk.CTkButton(
			self.main_frame,
			text="Guardar",
			command=self.guardar
		)
		self.button_guardar.pack(pady=20)

	def select_image(self):
		file_path = filedialog.askopenfilename(
			title="Seleccione una imagen",
			filetypes=[("Archivos de imagen", ".png .jpg .jpeg .gif .bmp")]
		)
		if file_path:
			self.display_image(file_path)

	def display_image(self, file_path):
		self.selected_image_path = file_path
		self.original_image = Image.open(file_path)
		
		# Redimensionar para mostrar
		display_size = (300, 300)
		self.display_image = self.original_image.copy()
		self.display_image.thumbnail(display_size)
		
		# Usar CTkImage en lugar de PhotoImage
		ctk_image = ctk.CTkImage(
			light_image=self.display_image,
			dark_image=self.display_image,
			size=display_size
		)
		self.image_label.configure(image=ctk_image)
		self.image_label.image = ctk_image
		
		# Bind el click del ratón para selección de color
		self.image_label.bind("<Button-1>", self.get_color)

	def get_color(self, event):
		if hasattr(self, 'original_image'):
			# Calcular las coordenadas relativas
			img_width = self.display_image.width
			img_height = self.display_image.height
			
			# Convertir coordenadas del evento a coordenadas de la imagen
			x = int((event.x / self.image_label.winfo_width()) * img_width)
			y = int((event.y / self.image_label.winfo_height()) * img_height)
			
			# Asegurarse de que las coordenadas estén dentro de los límites
			x = max(0, min(x, img_width - 1))
			y = max(0, min(y, img_height - 1))
			
			# Obtener el color RGB del pixel
			rgb = self.display_image.getpixel((x, y))
			if isinstance(rgb, int):  # Si es imagen en escala de grises
				rgb = (rgb, rgb, rgb)
			
			# Encontrar el color más cercano
			color_name, _ = closest_color(rgb)
			color_hex = color_hex_map[color_name]
			
			# Actualizar el label de color
			self.color_label.configure(text=color_name)
			try:
				self.color_frame.configure(fg_color=color_hex)
			except:
				pass  # Si no se puede cambiar el color de fondo

	def guardar(self):
		# Obtener los valores
		nombre_producto = self.entry_nombre.get()
		categoria_producto = self.variable_unidad.get()
		precio = redondear_precio(self.entry_precio.get())
		es_variante = self.var_es_variante.get()
		genero = self.variable_gen.get()
		talles = [talle for talle, var in self.talle_vars.items() if var.get()]
		disciplina = self.variable_disciplina.get()
		codigo_barras = self.entry_codigo_barras.get()

		try:
			with open('html/JS/productos.json', 'r') as archivo:
				contenido = archivo.read().strip()
				productos = json.loads(contenido) if contenido else []
		except (FileNotFoundError, json.JSONDecodeError):
			productos = []

		# Clasificar las categorías
		categoria_general = "Indumentaria" if categoria_producto.lower() in ["remeras", "pantalones", "abrigos"] else "Accesorios"

		# Generar ID único
		base_id = f"{categoria_producto.lower()}_{nombre_producto.replace(' ', '_').lower()}"
		id_producto = generate_unique_id(base_id, productos)

		# Procesar imagen si fue seleccionada
		imagen_ruta = ""
		if hasattr(self, 'selected_image_path') and self.selected_image_path:
			imagen_nombre = os.path.basename(self.selected_image_path)
			destino = os.path.join('html', 'img', imagen_nombre)

			if not os.path.exists(destino):
				try:
					os.makedirs(os.path.join('html', 'img'), exist_ok=True)
					shutil.copy2(self.selected_image_path, destino)
				except Exception as e:
					messagebox.showerror("Error", f"No se pudo copiar la imagen: {str(e)}")
					return

			imagen_ruta = f"./img/{imagen_nombre}"

		producto = {
			"id": id_producto,
			"titulo": nombre_producto,
			"imagen": imagen_ruta,
			"categoria": {"nombre": categoria_producto.upper(), "id": categoria_producto.lower()},
			"categoria_general": categoria_general.lower(),
			"precio": precio,
			"es_variante": es_variante,
			"genero": genero,
			"talles": talles,
			"color": self.color_label.cget("text") if hasattr(self, 'color_label') else "No especificado",
			"disciplina": disciplina,
			"stock": 0,
			"codigo_barras": codigo_barras
		}

		# Normalizar el producto
		producto = normalizar_diccionario(producto)

		# Verificar si es variante y si existe producto principal
		if es_variante:
			producto_principal_existe = any(p['titulo'] == nombre_producto and p['es_variante'] for p in productos)
			if not producto_principal_existe:

				if hasattr(self, 'image_label'):
					self.image_label.configure(image='')
				self.color_label.configure(text="Color")
				for var in self.talle_vars.values():
					var.set(False)

class ListaPreciosDialog(ctk.CTkToplevel):
	def __init__(self, parent):
		super().__init__(parent)
		self.title("Lista de Precios")
		
		# Optimización 1: Usar geometría más pequeña por defecto
		self.geometry("1024x768")
		
		# Optimización 2: Cachear productos y filtrados
		self.cached_productos = []
		self.cached_filtrados = []
		self.last_search = ""
		self.last_category = "Todas"
		
		# Inicializar variables antes de crear los frames
		self.selected_row = None
		self.seleccion = {}  # Diccionario para mantener el estado de selección
		self.productos = []  # Lista de productos
		
		# Frame principal
		self.main_frame = ctk.CTkFrame(self)
		self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
		
		# Crear barra de búsqueda
		self.crear_barra_busqueda()
		
		# Crear tabla de productos
		self.crear_tabla()
		
		# Cargar productos
		self.cargar_productos()

		# Agregar bind al frame principal para deseleccionar
		self.main_frame.bind("<Button-1>", self.deseleccionar_todo)
		self.tabla_frame.bind("<Button-1>", self.deseleccionar_todo)

	def deseleccionar_todo(self, event=None):
		# Solo deseleccionar si el clic fue directamente en el frame y no en una fila
		if event and event.widget in (self.main_frame, self.tabla_frame):
			for producto_id in list(self.seleccion.keys()):
				for widget in self.tabla_frame.winfo_children():
					if isinstance(widget, ctk.CTkFrame) and hasattr(widget, 'producto_id'):
						if widget.producto_id == producto_id:
							widget.configure(fg_color=("gray86", "gray17"))
			self.seleccion.clear()

	def crear_barra_busqueda(self):
		busqueda_frame = ctk.CTkFrame(self.main_frame)
		busqueda_frame.pack(fill="x", padx=10, pady=5)
		
		# Búsqueda por nombre
		ctk.CTkLabel(busqueda_frame, text="Buscar:").pack(side="left", padx=5)
		self.entry_busqueda = ctk.CTkEntry(busqueda_frame, width=200)
		self.entry_busqueda.pack(side="left", padx=5)
		self.entry_busqueda.bind('<KeyRelease>', self.filtrar_productos)
		
		# Filtro por categoría
		ctk.CTkLabel(busqueda_frame, text="Categoría:").pack(side="left", padx=5)
		self.combo_categoria = ctk.CTkOptionMenu(
			busqueda_frame,
			values=["Todas", "Indumentaria", "Accesorios", "REMERAS", "PANTALONES", "ABRIGOS"],
			command=self.filtrar_productos
		)
		self.combo_categoria.pack(side="left", padx=5)

	def crear_tabla(self):
		# Frame para la tabla con scroll
		self.tabla_frame = ctk.CTkScrollableFrame(self.main_frame)
		self.tabla_frame.pack(fill="both", expand=True, padx=10, pady=5)
		
		# Configurar grid para columnas uniformes
		self.tabla_frame.grid_columnconfigure((0,1,2,3,4,5), weight=1, uniform="column")
		
		# Cabecera de la tabla
		self._crear_headers()

	def mostrar_productos(self, productos_filtrados):
		# Optimización 3: Limitar número de productos mostrados
		PRODUCTOS_POR_PAGINA = 50
		productos_mostrar = productos_filtrados[:PRODUCTOS_POR_PAGINA]
		
		# Optimización 4: Reusar widgets existentes
		existing_frames = [w for w in self.tabla_frame.winfo_children() 
						 if isinstance(w, ctk.CTkFrame)]
		
		for widget in self.tabla_frame.winfo_children():
			widget.destroy()
			
		# Headers
		self._crear_headers()
		
		# Optimización 5: Crear frames solo cuando sea necesario
		for row, producto in enumerate(productos_mostrar, start=1):
			if row < len(existing_frames):
				row_frame = existing_frames[row]
				self._actualizar_frame(row_frame, producto, row)
			else:
				self._crear_nueva_fila(producto, row)

	def seleccionar_fila(self, row_frame, producto, event=None):
		# Detener la propagación del evento
		if event:
			event.widget.focus_set()
			event.widget.grab_current()
		
		# Deseleccionar fila anterior si existe y es diferente
		for widget in self.tabla_frame.winfo_children():
			if isinstance(widget, ctk.CTkFrame) and hasattr(widget, 'producto_id'):
				if widget != row_frame and widget.producto_id in self.seleccion:
					widget.configure(fg_color=("gray86", "gray17"))
					del self.seleccion[widget.producto_id]
		
		# Seleccionar o deseleccionar la fila actual
		if producto['id'] in self.seleccion:
			row_frame.configure(fg_color=("gray86", "gray17"))
			del self.seleccion[producto['id']]
		else:
			row_frame.configure(fg_color=("gray70", "gray30"))
			self.seleccion[producto['id']] = producto

	def cargar_productos(self):
		try:
			with open('html/JS/productos.json', 'r') as archivo:
				self.productos = json.load(archivo)
			self.cached_productos = self.productos
			self.mostrar_productos(self.productos)
		except FileNotFoundError:
			self.productos = []

	def filtrar_productos(self, *args):
		# Optimización 6: Throttling de búsqueda
		busqueda = self.entry_busqueda.get().lower()
		categoria = self.combo_categoria.get()
		
		if busqueda == self.last_search and categoria == self.last_category:
			return
			
		self.last_search = busqueda
		self.last_category = categoria
		
		# Optimización 7: Caching de resultados
		productos_filtrados = [p for p in self.cached_productos if
			busqueda in p['titulo'].lower() and
			(categoria == "Todas" or 
			 categoria.upper() == p['categoria']['nombre'] or 
			 categoria.lower() in p['categoria_general'].lower())]
		
		self.cached_filtrados = productos_filtrados
		self.mostrar_productos(productos_filtrados)

	def _crear_headers(self):
		# Método auxiliar para crear headers
		headers = ["Código", "Producto", "Categoría", "Talle", "Color", "Precio"]
		for i, header in enumerate(headers):
			ctk.CTkLabel(
				self.tabla_frame, 
				text=header,
				font=("Helvetica", 14, "bold")  # Fuente más grande para headers
			).grid(row=0, column=i, padx=5, pady=5, sticky="ew")

	def _crear_nueva_fila(self, producto, row):
		# Crear frame para la fila
		row_frame = ctk.CTkFrame(self.tabla_frame)
		row_frame.grid(row=row, column=0, columnspan=6, sticky="ew", padx=2, pady=1)
		row_frame.grid_columnconfigure((0,1,2,3,4,5), weight=1, uniform="column")
		
		# Guardar el ID del producto en el frame para referencia
		row_frame.producto_id = producto['id']
		
		# Bind para el clic con stop propagation
		row_frame.bind("<Button-1>", lambda e, p=producto, rf=row_frame: self.seleccionar_fila(rf, p, e))
		
		# Aplicar color si estaba seleccionado
		if producto['id'] in self.seleccion:
			row_frame.configure(fg_color=("gray70", "gray30"))
		
		# Bind para el clic
		row_frame.bind("<Button-1>", lambda e, p=producto, rf=row_frame: self.seleccionar_fila(rf, p))
		
		# Código de barras con nueva fuente
		ctk.CTkLabel(
			row_frame, 
			text=producto.get('codigo_barras', '')[:8],
			font=("Helvetica", 12)  # Fuente normal para el contenido
		).grid(row=0, column=0, padx=5, pady=2, sticky="ew")
		
		# Nombre del producto
		ctk.CTkLabel(
			row_frame, 
			text=producto['titulo']
		).grid(row=0, column=1, padx=5, pady=2, sticky="ew")
		
		# Categoría
		ctk.CTkLabel(
			row_frame, 
			text=producto['categoria']['nombre']
		).grid(row=0, column=2, padx=5, pady=2, sticky="ew")
		
		# Talles
		ctk.CTkLabel(
			row_frame, 
			text=", ".join(producto.get('talles', []))
		).grid(row=0, column=3, padx=5, pady=2, sticky="ew")
		
		# Color
		ctk.CTkLabel(
			row_frame, 
			text=producto.get('color', '')
		).grid(row=0, column=4, padx=5, pady=2, sticky="ew")
		
		# Precio
		ctk.CTkLabel(
			row_frame, 
			text=f"${producto['precio']}"
		).grid(row=0, column=5, padx=5, pady=2, sticky="ew")
		
		# Bind para todos los labels dentro del frame
		for child in row_frame.winfo_children():
			child.bind("<Button-1>", lambda e, p=producto, rf=row_frame: self.seleccionar_fila(rf, p, e))

	def _actualizar_frame(self, row_frame, producto, row):
		# Actualizar el ID del producto en el frame para referencia
		row_frame.producto_id = producto['id']
		
		# Aplicar color si estaba seleccionado
		if producto['id'] in self.seleccion:
			row_frame.configure(fg_color=("gray70", "gray30"))
		else:
			row_frame.configure(fg_color=("gray86", "gray17"))
		
		# Código de barras
		row_frame.winfo_children()[0].configure(text=producto.get('codigo_barras', '')[:8])
		
		# Nombre del producto
		row_frame.winfo_children()[1].configure(text=producto['titulo'])
		
		# Categoría
		row_frame.winfo_children()[2].configure(text=producto['categoria']['nombre'])
		
		# Talles
		row_frame.winfo_children()[3].configure(text=", ".join(producto.get('talles', [])))
		
		# Color
		row_frame.winfo_children()[4].configure(text=producto.get('color', ''))
		
		# Precio
		row_frame.winfo_children()[5].configure(text=f"${producto['precio']}")
		
		# Bind para todos los labels dentro del frame
		for child in row_frame.winfo_children():
			child.bind("<Button-1>", lambda e, p=producto, rf=row_frame: self.seleccionar_fila(rf, p, e))

if __name__ == "__main__":
	app = App()
	app.mainloop()
