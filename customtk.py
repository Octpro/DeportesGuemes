import customtkinter as ctk
import json
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import unicodedata
import shutil 
import math  # Agregar al inicio del archivo
from datetime import datetime  # Importar datetime para registrar acciones

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
		
		# Inicializar como no admin
		self.is_admin = False
		self.is_empleado = False

		# Inicializar modo_venta como None para evitar errores de atributo
		self.modo_venta = None
		
		# Configurar ventana principal
		self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
		self.title("Deportes Güemes")
		
		# Variable para controlar el tema
		self.tema_actual = "dark"
		
		# Configurar fuentes primero
		self.font_title = ("Helvetica", 16, "bold")
		self.font_normal = ("Helvetica", 12)
		self.font_small = ("Helvetica", 10)

		self.menu_frame = ctk.CTkFrame(self)
		self.menu_frame.pack(side="top", fill="x")  # Empaquetar arriba
		self.create_menu()
		
		# Crear contenedor para la imagen
		self.background_frame = ctk.CTkFrame(self)
		self.background_frame.pack(fill="both", expand=True)  # Empaquetar después del menú

		# Crear Tabview para las pestañas principales
		self.tab_view = ctk.CTkTabview(self.background_frame)
		self.tab_view.pack(fill="both", expand=True)

		# Cargar imagen de fondo
		try:
			self.original_image = Image.open("html/img/Logo.jpeg")
			self.actualizar_imagen_fondo()
			self.bind('<Configure>', self.on_resize)
		except Exception as e:
			print(f"Error al cargar la imagen de fondo: {e}")
		
		# Mostrar login al inicio
		self.show_login()

	def actualizar_imagen_fondo(self):
		window_width = self.background_frame.winfo_width()
		window_height = self.background_frame.winfo_height()
		
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
		# Destruir el menú anterior si existe
		if hasattr(self, 'menu_frame'):
			self.menu_frame.destroy()

		# Crear un único frame para los botones
		self.menu_frame = ctk.CTkFrame(self)
		self.menu_frame.pack(side="top", fill="x", pady=10)

		# Botón para abrir la pestaña "Lista de Productos"
		ctk.CTkButton(
			self.menu_frame,
			text="Lista de Productos",
			command=self.show_ver_productos,
			font=self.font_normal
		).pack(side="left", padx=5)

		# Botón para abrir la pestaña "Venta"
		ctk.CTkButton(
			self.menu_frame,
			text="Venta",
			command=self.toggle_modo_venta,
			font=self.font_normal
		).pack(side="left", padx=5)

		# SOLO PARA ADMIN
		if self.is_admin:
			ctk.CTkButton(
				self.menu_frame,
				text="Ingresar Nuevo Producto",
				command=self.show_nuevo_producto,
				font=self.font_normal
			).pack(side="left", padx=5)

			ctk.CTkButton(
				self.menu_frame,
				text="Historial",
				command=self.show_historial,
				font=self.font_normal
			).pack(side="left", padx=5)

			ctk.CTkButton(
				self.menu_frame,
				text="Lista de Precios",
				command=self.show_lista_precios,
				font=self.font_normal
			).pack(side="left", padx=5)

		# Botón de cambiar tema a la derecha
		ctk.CTkButton(
			self.menu_frame,
			text="Cambiar Tema",
			command=self.toggle_tema,
			font=self.font_normal,
			fg_color="purple",
			hover_color="darkviolet"
		).pack(side="right", padx=5)

		# Botón de cerrar sesión a la derecha
		ctk.CTkButton(
			self.menu_frame,
			text="Cerrar Sesión",
			command=self.logout,
			fg_color="red"
		).pack(side="right", padx=5)

	def logout(self):
		self.is_admin = False
		self.is_empleado = False
		self.menu_frame.destroy()  # Destruir el menú actual
		self.show_login()          # Volver a mostrar el login

	def toggle_tema(self):
		if self.tema_actual == "dark":
			ctk.set_appearance_mode("light")
			self.tema_actual = "light"
		else:
			ctk.set_appearance_mode("dark")
			self.tema_actual = "dark"

	def show_nuevo_producto(self):
		if not self.is_admin:
			messagebox.showerror("Error", "Acceso denegado. Se requieren permisos de administrador.")
			return
		ProductoDialog(self)

	def show_ver_productos(self):
		VerProductosDialog(self)
			
	def toggle_modo_venta(self):
		#if self.modo_venta.get():
		ModoVentaDialog(self)

	def show_lista_precios(self):
		ListaPreciosDialog(self)

	def show_historial(self):
		if not self.is_admin:
			messagebox.showerror("Error", "Acceso denegado. Se requieren permisos de administrador.")
			return
		HistorialDialog(self)

	def show_login(self):
		dialog = LoginDialog(self)
		dialog.grab_set()
		self.wait_window(dialog)
		# Si el usuario no se autenticó, cerrar la app principal
		if not (dialog.is_admin or dialog.is_empleado):
			self.destroy()
			return  # Return immediately to prevent further code execution
		self.is_admin = dialog.is_admin
		self.is_empleado = dialog.is_empleado
		self.update_interface()  # Esto recrea el menú según el usuario

	def update_interface(self):
		# Recrear el menú y limpiar pestañas si es necesario
		self.create_menu()
		# Si querés limpiar las pestañas al cambiar de usuario:
		for tab in self.tab_view._name_list[1:]:  # Mantener solo la pestaña principal si querés
			self.tab_view.delete(tab)
			
		# # Solo intentar configurar self.modo_venta si ya fue creado
		# if self.modo_venta is not None:
		# 	if self.is_admin:
		# 		# Habilitar modo venta para admin
		# 		self.modo_venta.configure(state="normal")
		# 	else:
		# 		# Deshabilitar modo venta para usuarios normales
		# 		self.modo_venta.configure(state="disabled")
		# else:
		# 	# Deshabilitar modo venta para usuarios normales
		# 	self.modo_venta.configure(state="normal")

class VerProductosDialog(ctk.CTkToplevel):
	def __init__(self, parent):
		super().__init__(parent)
		self.title("Ver Productos")
		self.geometry("1024x768")
		self.productos = []
		self.productos_seleccionados = []

		self.main_frame = ctk.CTkFrame(self)
		self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

		self.crear_filtros()

		self.productos_frame = ctk.CTkScrollableFrame(self.main_frame)
		self.productos_frame.pack(fill="both", expand=True, padx=10, pady=5)

		# Guardar productos filtrados actuales
		self._productos_filtrados = []

		self.cargar_productos()

	def cargar_productos(self):
		try:
			with open('html/JS/productos.json', 'r') as archivo:
				self.productos = json.load(archivo)
				self._productos_filtrados = self.productos
				self.mostrar_productos(self.productos)
		except FileNotFoundError:
			self.productos = []
			messagebox.showerror("Error", "No se encontró el archivo de productos")

	def mostrar_productos(self, productos_filtrados):
		try:
			# Limpiar el frame anterior
			for widget in self.productos_frame.winfo_children():
				widget.destroy()

			# Guardar productos filtrados actuales
			self._productos_filtrados = productos_filtrados

			columnas = 4  # Fijo: 4 columnas
			for col in range(columnas):
				self.productos_frame.grid_columnconfigure(col, weight=1, uniform="column")
			self.productos_seleccionados = []
			row = 0
			col = 0

			for producto in productos_filtrados:
				try:
					if not producto.get('es_variante', False):
						card = self.crear_producto_card(self.productos_frame, producto)
						card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
						col += 1
						if col >= columnas:
							col = 0
							row += 1
				except Exception as e:
					print(f"Error mostrando producto: {producto}\n{e}")

		except Exception as e:
			print(f"Error en mostrar_productos: {e}")

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
			disciplina = self.filtro_disciplina.get()
			genero = self.filtro_genero.get()
			talle = self.filtro_talle.get()
			
			# Obtener precios con valores por defecto
			precio_min = self.filtro_precio_min.get() or "0"  # Si está vacío, usa "0"
			precio_max = self.filtro_precio_max.get() or "999999999"  # Si está vacío, usa "999999999"
			
			# Filtrar productos
			productos_filtrados = [p for p in self.productos if
				nombre in p['titulo'].lower() and
				(categoria == "Todas" or 
				 categoria.upper() == p['categoria']['nombre'] or 
				 categoria.lower() in p['categoria_general'].lower()) and
				(disciplina == "Todas" or disciplina.lower() == p.get('disciplina', '').lower()) and
				(genero == "Todos" or genero.lower() == p.get('genero', '').lower()) and
				(talle == "Todos" or talle in p.get('talles', [])) and
				float(p['precio']) >= float(precio_min) and
				float(p['precio']) <= float(precio_max)]
				
			# Actualizar vista
			self.mostrar_productos(productos_filtrados)
			
		except ValueError as e:
			print(f"Error al aplicar filtros: {e}")

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
		dialog.lift()  # Mantener ventana al frente
		dialog.transient(self)  # Hacer la ventana dependiente del padre
		dialog.focus_force()  # Forzar el foco
		dialog.grab_set()  # Hacer la ventana modal

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
				
				detalles_cambios = []
				for producto, _ in productos_a_actualizar:
					# Calcular nuevo precio
					precio_actual = float(producto['precio'])
					if tipo_actualizacion.get() == "porcentaje":
						nuevo_precio = precio_actual * (1 + valor/100)
						tipo_cambio = f"{valor}%"
					else:  # monto
						nuevo_precio = precio_actual + valor
						tipo_cambio = f"${valor}"
					
					# Redondear y actualizar precio
					producto['precio'] = redondear_precio(str(nuevo_precio))
					
					# Registrar detalle del cambio
					detalles_cambios.append(
						f"{producto['titulo']}: ${precio_actual} -> ${producto['precio']} ({tipo_cambio})"
					)
					
					# Actualizar en la lista completa
					for i, p in enumerate(todos_productos):
						if p['id'] == producto['id']:
							todos_productos[i] = producto
							break
				
				# Guardar cambios
				with open('html/JS/productos.json', 'w') as archivo:
					json.dump(todos_productos, archivo, indent=2)
				
				# Registrar acción en el historial
				HistorialDialog.registrar_accion(
					accion="Precio Actualizado",
					producto="Varios productos",
					detalles="\n".join(detalles_cambios)
				)
				
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
		dialog.lift()  # Mantener ventana al frente
		dialog.transient(self)  # Hacer la ventana dependiente del padre
		dialog.focus_force()  # Forzar el foco
		dialog.grab_set()  # Hacer la ventana modal
		
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
				
				 # Registrar acción en el historial
				HistorialDialog.registrar_accion(
					accion="Eliminado",
					producto=producto['titulo'],
					detalles=f"Producto eliminado con código: {producto['codigo_barras']}"
				)

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
		dialog.lift()  # Mantener ventana al frente
		dialog.transient(self)  # Hacer la ventana dependiente del padre
		dialog.focus_force()  # Forzar el foco
		dialog.grab_set()  # Hacer la ventana modal
		
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
				# Obtener datos anteriores
				precio_anterior = producto['precio']
				titulo_anterior = producto['titulo']

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

				# Registrar acción en el historial
				HistorialDialog.registrar_accion(
					accion="Modificado",
					producto=producto['titulo'],
					detalles=f"Nombre: {titulo_anterior} -> {producto['titulo']}, "
							 f"Precio: ${precio_anterior} -> ${producto['precio']}"
				)

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
		self.geometry("1000x600")  # Tamaño más razonable

		# Variables
		self.productos_seleccionados = []  # Lista de productos seleccionados
		self.total_venta = 0  # Total acumulado

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

		# Total acumulado
		self.total_label = ctk.CTkLabel(self.input_frame, 
										text="Total: $0",
										font=("", 16, "bold"),
										text_color="green")
		self.total_label.pack(pady=10)

		# Botón "Restablecer Lista" al lado del título
		productos_label_frame = ctk.CTkFrame(self.list_frame)
		productos_label_frame.pack(fill="x", padx=10, pady=5)

		ctk.CTkLabel(
			productos_label_frame,
			text="Productos Escaneados",
			font=("", 14, "bold")
		).pack(side="left", padx=5)

		self.restablecer_button = ctk.CTkButton(
			productos_label_frame,
			text="Restablecer Lista",
			command=self.restablecer_lista,
			fg_color="red"
		)
		self.restablecer_button.pack(side="right", padx=5)

		# Lista de productos escaneados
		self.lista_frame = ctk.CTkScrollableFrame(self.list_frame)
		self.lista_frame.pack(fill="both", expand=True)

		# Frame inferior para el botón "Vender"
		self.bottom_frame = ctk.CTkFrame(self)
		self.bottom_frame.pack(side="bottom", fill="x", padx=20, pady=10, anchor="se")

		# Botón "Vender"
		self.vender_button = ctk.CTkButton(
			self.bottom_frame,
			text="Vender",
			command=self.vender_productos,
			fg_color="blue"
		)
		self.vender_button.pack(side="right", padx=10)

		# Slide switch para deseleccionar productos después de vender
		self.deseleccionar_switch = ctk.CTkSwitch(
			self.input_frame,
			text="Deseleccionar después de vender",
			onvalue=True,
			offvalue=False,
			font=("", 12)
		)
		self.deseleccionar_switch.pack(pady=10)

	def procesar_codigo(self, event=None):
		codigo = self.entry_codigo_barras.get().strip()
		if not codigo:
			messagebox.showwarning("Advertencia", "Ingrese un código de barras.")
			return

		# Limpiar entrada
		self.entry_codigo_barras.delete(0, 'end')

		try:
			# Cargar todos los productos
			with open('html/JS/productos.json', 'r') as archivo:
				productos = json.load(archivo)

			# Buscar producto con ese código
			producto = None
			for p in productos:
				if str(p.get('codigo_barras')) == codigo:
					producto = p
					break

			if producto:
				# Crear un frame para mostrar el producto escaneado
				item_frame = ctk.CTkFrame(self.lista_frame)
				item_frame.pack(fill="x", padx=5, pady=2)

				# Verificar stock
				if producto.get('stock', 0) > 0:
					stock_text = f"Stock: {producto['stock']}"
					stock_color = "green"
					checkbox_state = "normal"  # Habilitar checkbox
				else:
					stock_text = "SIN STOCK"
					stock_color = "red"
					checkbox_state = "disabled"  # Deshabilitar checkbox

				# Mostrar información del producto
				ctk.CTkLabel(item_frame, text=f"Código: {producto['codigo_barras']}", font=("", 12)).pack(side="left", padx=5)
				ctk.CTkLabel(item_frame, text=f"Producto: {producto['titulo']}", font=("", 12, "bold"), text_color="blue").pack(side="left", padx=5)
				ctk.CTkLabel(item_frame, text=f"${producto['precio']}", font=("", 12)).pack(side="right", padx=5)
				ctk.CTkLabel(item_frame, text=stock_text, font=("", 12), text_color=stock_color).pack(side="right", padx=5)

				# Checkbox para seleccionar/desseleccionar el producto
				var = ctk.BooleanVar()
				checkbox = ctk.CTkCheckBox(
					item_frame,
					text="Seleccionar",
					variable=var,
					command=lambda: self.actualizar_total(var, producto),
					state=checkbox_state  # Habilitar o deshabilitar según el stock
				)
				checkbox.pack(side="right", padx=5)

				# Desplazar el scroll hacia el final
				self.lista_frame._parent_canvas.yview_moveto(1.0)

			else:
				# Producto no encontrado
				messagebox.showerror("Error", f"No se encontró un producto con el código de barras: {codigo}")

		except Exception as e:
			messagebox.showerror("Error", f"Error al procesar el código de barras: {str(e)}")

	def actualizar_total(self, var, producto):
		if var.get():
			# Seleccionar producto
			self.productos_seleccionados.append(producto)
			self.total_venta += float(producto['precio'])
		else:
			# Deseleccionar producto
			self.productos_seleccionados.remove(producto)
			self.total_venta -= float(producto['precio'])

		# Actualizar el total en la etiqueta
		self.total_label.configure(text=f"Total: ${self.total_venta:.2f}")

	def restablecer_lista(self):
			# Limpiar la lista de productos seleccionados y el total
			self.productos_seleccionados.clear()
			self.total_venta = 0
			self.total_label.configure(text="Total: $0")

			# Limpiar la lista de productos escaneados en la interfaz
			for widget in self.lista_frame.winfo_children():
				widget.destroy()

	def vender_productos(self):
		if not self.productos_seleccionados:
			messagebox.showwarning("Advertencia", "No hay productos seleccionados para la venta.")
			return

		try:
			# Cargar todos los productos
			with open('html/JS/productos.json', 'r') as archivo:
				productos = json.load(archivo)

			# Actualizar el stock de los productos seleccionados
			detalles_venta = []
			for producto_seleccionado in self.productos_seleccionados:
				for producto in productos:
					if producto['id'] == producto_seleccionado['id']:
						if producto['stock'] > 0:
							producto['stock'] -= 1
							detalles_venta.append(
								f"{producto['titulo']} (Código: {producto['codigo_barras']}, Precio: ${producto['precio']})"
								)
							# Actualizar el stock en la interfaz
							self._actualizar_stock_interfaz(producto)
						else:
							messagebox.showerror(
								"Error",
								f"El producto '{producto['titulo']}' no tiene suficiente stock."
							)
							return

			# Guardar los cambios en el archivo JSON
			with open('html/JS/productos.json', 'w') as archivo:
				json.dump(productos, archivo, indent=2)

			# Registrar la acción en el historial
			HistorialDialog.registrar_accion(
				accion="Venta",
				producto="Productos vendidos",
				detalles="\n".join(detalles_venta)
			)

			# Mostrar mensaje de éxito
			messagebox.showinfo("Éxito", "Venta realizada correctamente.")
			self.total_venta = 0
			self.total_label.configure(text="Total: $0")

			# Deseleccionar productos si el switch está activado
			if self.deseleccionar_switch.get():
				self.productos_seleccionados.clear()
				for widget in self.lista_frame.winfo_children():
					if isinstance(widget, ctk.CTkFrame):
						checkbox = widget.winfo_children()[-1]  # El último widget es el checkbox
						if isinstance(checkbox, ctk.CTkCheckBox):
							checkbox.deselect()

		except Exception as e:
			messagebox.showerror("Error", f"Error al realizar la venta: {str(e)}")

	def _actualizar_stock_interfaz(self, producto):
		# Buscar el frame correspondiente al producto en la lista
		for widget in self.lista_frame.winfo_children():
			if isinstance(widget, ctk.CTkFrame):
				labels = widget.winfo_children()
				if labels and producto['codigo_barras'] in labels[0].cget("text"):
					# Actualizar el texto del stock
					for label in labels:
						if "Stock:" in label.cget("text"):
							label.configure(text=f"Stock: {producto['stock']}")
							break

class ProductoDialog(ctk.CTkToplevel):
	def __init__(self, parent, codigo_barras=None):
		super().__init__(parent)
		self.title("Ingresar Nuevo Producto")
		#self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
		self.geometry("800x800")  # Tamaño más razonable para el diálogo

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
		# Validar campos requeridos
		nombre_producto = self.entry_nombre.get().strip()
		categoria_producto = self.variable_unidad.get()
		precio = self.entry_precio.get().strip()
		es_variante = self.var_es_variante.get()
		genero = self.variable_gen.get()
		disciplina = self.variable_disciplina.get()
		codigo_barras = self.entry_codigo_barras.get().strip()
		
		# Validaciones básicas
		if not nombre_producto:
			messagebox.showerror("Error", "El nombre del producto es obligatorio")
			return
			
		if not precio:
			messagebox.showerror("Error", "El precio es obligatorio")
			return
			
		if categoria_producto == "Categoria Producto":
			messagebox.showerror("Error", "Seleccione una categoría")
			return
		
		if not codigo_barras:
			messagebox.showerror("Error", "El código de barras es obligatorio")
			return
			
		# Cargar productos existentes
		try:
			with open('html/JS/productos.json', 'r') as archivo:
				contenido = archivo.read().strip()
				productos = json.loads(contenido) if contenido else []
		except (FileNotFoundError, json.JSONDecodeError):
			productos = []

		# Clasificar categorías
		categoria_general = "Indumentaria" if categoria_producto.lower() in ["remeras", "pantalones", "abrigos"] else "Accesorios"

		# Generar ID único
		base_id = f"{categoria_producto.lower()}_{nombre_producto.replace(' ', '_').lower()}"
		id_producto = generate_unique_id(base_id, productos)

		# Procesar imagen
		imagen_ruta = ""
		if hasattr(self, 'selected_image_path') and self.selected_image_path:
			imagen_nombre = os.path.basename(self.selected_image_path)
			destino = os.path.join('html', 'img', imagen_nombre)
			
			try:
				os.makedirs(os.path.join('html', 'img'), exist_ok=True)
				shutil.copy2(self.selected_image_path, destino)
				imagen_ruta = f"./img/{imagen_nombre}"
			except Exception as e:

				# Crear producto
				producto = {
					"id": id_producto,
					"titulo": nombre_producto,
					"imagen": imagen_ruta,
					"categoria": {"nombre": categoria_producto.upper(), "id": categoria_producto.lower()},
					"categoria_general": categoria_general.lower(),
					"precio": redondear_precio(precio),
					"es_variante": es_variante,
					"genero": genero,
					"talles": [talle for talle, var in self.talle_vars.items() if var.get()],
					"color": self.color_label.cget("text") if hasattr(self, 'color_label') else "No especificado",
					"disciplina": disciplina,
					"stock": 0,
					"codigo_barras": int(codigo_barras)
				}

		# Normalizar producto
		producto = normalizar_diccionario(producto)

		# Guardar producto
		try:
			productos.append(producto)
			with open('html/JS/productos.json', 'w') as archivo:
				json.dump(productos, archivo, indent=2)

			# Registrar acción en el historial
			HistorialDialog.registrar_accion(
				accion="Agregado",
				producto=producto['titulo'],
				detalles=f"Producto agregado con código: {producto['codigo_barras']}, Precio: ${producto['precio']}"
			)

			messagebox.showinfo("Éxito", "Producto guardado correctamente")
			
			# Limpiar formulario
			self.entry_nombre.delete(0, 'end')
			self.entry_precio.delete(0, 'end')
			self.entry_codigo_barras.delete(0, 'end')
			self.variable_unidad.set("Categoria Producto")
			self.variable_gen.set("Genero")
			self.variable_disciplina.set("Deportes")
			self.var_es_variante.set(False)
			if hasattr(self, 'image_label'):
				self.image_label.configure(image='')
			self.color_label.configure(text="Color")
			for var in self.talle_vars.values():
				var.set(False)
				
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar el producto: {str(e)}")

class ListaPreciosDialog(ctk.CTkToplevel):
	def __init__(self, parent):
		super().__init__(parent)
		self.title("Lista de Precios")
		self.geometry("1024x768")

		# Inicializar variables primero
		self.columna_orden = None
		self.orden_actual = None
		self.cached_productos = []
		self.cached_filtrados = []
		self.last_search = ""
		self.last_category = "Todas"
		self.seleccion = {}
		self.productos = []

		# Frame principal
		self.main_frame = ctk.CTkFrame(self)
		self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

		# Crear barra de búsqueda
		self.crear_barra_busqueda()

		# Frame para la tabla con scroll
		self.tabla_frame = ctk.CTkScrollableFrame(self.main_frame)
		self.tabla_frame.pack(fill="both", expand=True, padx=10, pady=5)
		self.tabla_frame.grid_columnconfigure((0,1,2,3,4,5), weight=1, uniform="column")

		# Cargar productos y mostrar
		self.cargar_productos()

	def mostrar_productos(self, productos_filtrados):
		# Limpiar tabla primero
		for widget in self.tabla_frame.winfo_children():
			widget.destroy()

		# Crear headers
		self._crear_headers()

		# Mostrar productos
		for row, producto in enumerate(productos_filtrados, start=1):
			self._crear_nueva_fila(producto, row)

	def _crear_headers(self):
		headers = {
			"codigo": "Código",
			"titulo": "Producto", 
			"categoria": "Categoría",
			"talle": "Talle",
			"color": "Color",
			"precio": "Precio"
		}
		
		for i, (key, header) in enumerate(headers.items()):
			header_frame = ctk.CTkFrame(self.tabla_frame)
			header_frame.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
			
			# Texto del header con flecha si está ordenado
			texto = header
			if self.columna_orden == key:
				texto = f"{header} {'▼' if self.orden_actual == 'desc' else '▲'}"
			
			label = ctk.CTkLabel(
				header_frame, 
				text=texto,
				font=("Helvetica", 14, "bold"),
				cursor="hand2"
			)


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
				self.cached_filtrados = self.productos  # Inicializar cached_filtrados
				self.mostrar_productos(self.productos)
		except FileNotFoundError:
			self.productos = []
			self.cached_productos = []
			self.cached_filtrados = []

	def filtrar_productos(self, *args):
		busqueda = self.entry_busqueda.get().strip().lower()
		categoria = self.combo_categoria.get()

		# Si no hay cambios en la búsqueda o categoría, no hacer nada
		if busqueda == self.last_search and categoria == self.last_category:
			return

		# Actualizar los valores de búsqueda y categoría
		self.last_search = busqueda
		self.last_category = categoria

		productos_filtrados = []

		for p in self.cached_productos:
			titulo_lower = p['titulo'].lower()
			codigo = str(p.get('codigo_barras', ''))

			# Verificar si la búsqueda coincide con el código exacto
			if busqueda.isdigit() and codigo.isdigit() and int(codigo) == int(busqueda):
				productos_filtrados.append(p)
				continue

			# Si no es código exacto, buscar en título y código
			if busqueda in titulo_lower or busqueda in codigo:
				# Si la categoría es "Todas", incluir todos los productos
				if categoria == "Todas" or (
					categoria.upper() == p['categoria']['nombre'].upper() or
					categoria.lower() in p['categoria_general'].lower()
				):
					productos_filtrados.append(p)

		# Ordenar los resultados numéricamente si es posible
		def get_sort_key(producto):
			try:
				# Intentar convertir el código de barras a un número
				return int(producto.get('codigo_barras', ''))
			except ValueError:
				# Si no es un número, usar un valor alto para colocarlo al final
				return float('inf')

		productos_filtrados.sort(key=get_sort_key)

		# Actualizar la lista filtrada y mostrar los productos
		self.cached_filtrados = productos_filtrados
		self.mostrar_productos(productos_filtrados)

	def _crear_headers(self):
		# Método auxiliar para crear headers con ordenamiento
		headers = {
			"codigo": "Código",
			"titulo": "Producto", 
			"categoria": "Categoría",
			"talle": "Talle",
			"color": "Color",
			"precio": "Precio"
		}
		
		for i, (key, header) in enumerate(headers.items()):
			header_frame = ctk.CTkFrame(self.tabla_frame)
			header_frame.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
			
			label = ctk.CTkLabel(
				header_frame, 
				text=f"{header} ▼" if self.columna_orden == key and self.orden_actual == "desc"
				else f"{header} ▲" if self.columna_orden == key and self.orden_actual == "asc"
				else header,
				font=("Helvetica", 14, "bold"),
				cursor="hand2"  # Cambiar cursor a mano
			)
			label.pack(expand=True)
			label.bind("<Button-1>", lambda e, k=key: self.ordenar_por(k))

	def ordenar_por(self, columna):
		if not self.cached_filtrados:
			self.cached_filtrados = self.cached_productos.copy()
			
		if self.columna_orden == columna:
			self.orden_actual = "desc" if self.orden_actual == "asc" else "asc"
		else:
			self.columna_orden = columna
			self.orden_actual = "asc"
		
		productos_ordenados = self.cached_filtrados.copy()
		
		def get_valor_ordenamiento(producto):
			try:
				if columna == "codigo":
					# Convertir código de barras a entero
					return int(str(producto.get('codigo_barras', '0')))
				elif columna == "titulo":
					return producto['titulo'].lower()
				elif columna == "categoria":
					return producto['categoria']['nombre'].lower()
				elif columna == "talle":
					return ",".join(producto.get('talles', []))
				elif columna == "color":
					return producto.get('color', '')
				elif columna == "precio":
					# Convertir precio a entero
					return int(float(producto['precio']))
				return ""
			except (ValueError, TypeError):
				# Si hay error de conversión, retornar 0
				if columna in ["codigo", "precio"]:
					return 0
				return ""
		
		try:
			productos_ordenados.sort(
				key=get_valor_ordenamiento,
				reverse=(self.orden_actual == "desc")
			)
		except Exception as e:
			print(f"Error al ordenar: {e}")
		
		self.mostrar_productos(productos_ordenados)

	def _crear_nueva_fila(self, producto, row):
		# Crear frame para la fila
		row_frame = ctk.CTkFrame(self.tabla_frame)
		row_frame.grid(row=row, column=0, columnspan=6, sticky="ew", padx=2, pady=1)
		row_frame.grid_columnconfigure((0,1,2,3,4,5), weight=1, uniform="column")
		
		# Guardar el ID del producto en el frame para referencia
		row_frame.producto_id = producto['id']
		
		 # Código de barras convertido a string
		codigo_barras = str(producto.get('codigo_barras', ''))
		if len(codigo_barras) > 8:
			codigo_barras = codigo_barras[:8]
		
		# Código de barras con nueva fuente
		ctk.CTkLabel(
			row_frame, 
			text=codigo_barras,
			font=("Helvetica", 12)
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
		
		# Bind para el clic
		row_frame.bind("<Button-1>", lambda e, p=producto, rf=row_frame: self.seleccionar_fila(rf, p))
		
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

	def crear_barra_busqueda(self):
		# Frame para la barra de búsqueda
		busqueda_frame = ctk.CTkFrame(self.main_frame)
		busqueda_frame.pack(fill="x", padx=10, pady=5)

		# Búsqueda por nombre
		ctk.CTkLabel(
			busqueda_frame, 
			text="Buscar:",
			font=self.master.font_normal
		).pack(side="left", padx=5)
		
		self.entry_busqueda = ctk.CTkEntry(busqueda_frame, width=200)
		self.entry_busqueda.pack(side="left", padx=5)
		self.entry_busqueda.bind('<KeyRelease>', self.filtrar_productos)

		# Filtro por categoría
		ctk.CTkLabel(
			busqueda_frame, 
			text="Categoría:",
			font=self.master.font_normal
		).pack(side="left", padx=5)
		
		self.combo_categoria = ctk.CTkOptionMenu(
			busqueda_frame,
			values=["Todas", "Indumentaria", "Accesorios", "REMERAS", "PANTALONES", "ABRIGOS"],
			command=self.filtrar_productos
		)
		self.combo_categoria.pack(side="left", padx=5)

class HistorialDialog(ctk.CTkToplevel):
	def __init__(self, parent):
		super().__init__(parent)
		self.title("Historial de Cambios")
		self.geometry("1024x768")

		# Inicializar variables
		self.historial = []
		self.filtrado = []

		# Frame principal
		self.main_frame = ctk.CTkFrame(self)
		self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

		# Crear barra de búsqueda
		self.crear_barra_busqueda()

		# Frame para la tabla con scroll
		self.tabla_frame = ctk.CTkScrollableFrame(self.main_frame)
		self.tabla_frame.pack(fill="both", expand=True, padx=10, pady=5)
		self.tabla_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="column")

		# Cargar historial
		self.cargar_historial()

	def crear_barra_busqueda(self):
		# Frame para la barra de búsqueda
		busqueda_frame = ctk.CTkFrame(self.main_frame)
		busqueda_frame.pack(fill="x", padx=10, pady=5)

		# Filtro por tipo de acción
		ctk.CTkLabel(busqueda_frame, text="Tipo de Acción:").pack(side="left", padx=5)
		self.combo_tipo_accion = ctk.CTkOptionMenu(
			busqueda_frame,
			values=["Todos", "Agregado", "Eliminado", "Modificado", "Precio Actualizado", "Venta"],
			command=self.filtrar_historial
		)
		self.combo_tipo_accion.pack(side="left", padx=5)

		# Filtro por fecha
		ctk.CTkLabel(busqueda_frame, text="Fecha:").pack(side="left", padx=5)
		self.entry_fecha = ctk.CTkEntry(busqueda_frame, width=200)
		self.entry_fecha.pack(side="left", padx=5)
		self.entry_fecha.bind('<KeyRelease>', lambda e: self.filtrar_historial())

	def cargar_historial(self):
		try:
			# Leer el historial desde un archivo JSON
			with open('html/JS/historial.json', 'r') as archivo:
				self.historial = json.load(archivo)
		except FileNotFoundError:
			self.historial = []

		# Mostrar el historial completo
		self.mostrar_historial(self.historial)

	def mostrar_historial(self, registros):
		# Limpiar la tabla
		for widget in self.tabla_frame.winfo_children():
			widget.destroy()

		# Crear encabezados
		headers = ["Fecha", "Tipo de Acción", "Producto", "Detalles"]
		for i, header in enumerate(headers):
			ctk.CTkLabel(
				self.tabla_frame,
				text=header,
				font=("Helvetica", 14, "bold")
			).grid(row=0, column=i, padx=5, pady=5, sticky="ew")

		# Mostrar registros
		for row, registro in enumerate(registros, start=1):
			ctk.CTkLabel(self.tabla_frame, text=registro["fecha"]).grid(row=row, column=0, padx=5, pady=2, sticky="ew")
			ctk.CTkLabel(self.tabla_frame, text=registro["accion"]).grid(row=row, column=1, padx=5, pady=2, sticky="ew")
			ctk.CTkLabel(self.tabla_frame, text=registro["producto"]).grid(row=row, column=2, padx=5, pady=2, sticky="ew")
			ctk.CTkLabel(self.tabla_frame, text=registro["detalles"]).grid(row=row, column=3, padx=5, pady=2, sticky="ew")

	def filtrar_historial(self, *args):
		tipo_accion = self.combo_tipo_accion.get()
		fecha = self.entry_fecha.get().strip()

		# Filtrar por tipo de acción y fecha
		self.filtrado = [
			registro for registro in self.historial
			if (tipo_accion == "Todos" or registro["accion"] == tipo_accion) and
			   (not fecha or fecha in registro["fecha"])
		]

		# Mostrar los registros filtrados
		self.mostrar_historial(self.filtrado)

	@staticmethod
	def registrar_accion(accion, producto, detalles):
		# Crear un registro
		registro = {
			"fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
			"accion": accion,
			"producto": producto,
			"detalles": detalles
		}

		# Leer el historial existente
		try:
			with open('html/JS/historial.json', 'r') as archivo:
				historial = json.load(archivo)
		except FileNotFoundError:
			historial = []

		# Agregar el nuevo registro
		historial.append(registro)

		# Guardar el historial actualizado
		with open('html/JS/historial.json', 'w') as archivo:
			json.dump(historial, archivo, indent=2)

class LoginDialog(ctk.CTkToplevel):
	def __init__(self, parent):
		super().__init__(parent)
		self.title("Iniciar Sesión")
		self.geometry("400x300")
		
		# Variables
		self.is_admin = False
		self.is_empleado = False
		
		# Frame principal
		self.main_frame = ctk.CTkFrame(self)
		self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
		
		# Usuario
		ctk.CTkLabel(self.main_frame, text="Usuario:").pack(pady=5)
		self.entry_usuario = ctk.CTkEntry(self.main_frame)
		self.entry_usuario.pack(pady=5)
		
		# Contraseña
		ctk.CTkLabel(self.main_frame, text="Contraseña:").pack(pady=5)
		self.entry_password = ctk.CTkEntry(self.main_frame, show="*")
		self.entry_password.pack(pady=5)
		
		# Botón login
		ctk.CTkButton(
			self.main_frame,
			text="Iniciar Sesión",
			command=self.login
		).pack(pady=20)

	def login(self):
		usuario = self.entry_usuario.get()
		password = self.entry_password.get()
		
		# Credenciales de admin
		if usuario == "a" and password == "a":
			self.is_admin = True
			self.is_empleado = False
			messagebox.showinfo("Éxito", "Bienvenido Administrador")
			self.destroy()
		# Credenciales de empleado
		elif usuario == "e" and password == "e":
			self.is_admin = False
			self.is_empleado = True
			messagebox.showinfo("Éxito", "Bienvenido Empleado")
			self.destroy()
		else:
			messagebox.showerror("Error", "Usuario o contraseña incorrectos")

if __name__ == "__main__":
	try:
		app = App()
		app.mainloop()
	except TclError:
		pass  # Ignora el error al cerrar la app