import customtkinter as ctk
#from customtkinter import CTkSpinbox
import json
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import unicodedata
import shutil 
import math  # Agregar al inicio del archivo
import threading  # For backup threading
from datetime import datetime  # Importar datetime para registrar acciones
try:
    from git import Repo  # Asegúrate de tener gitpython instalado
    GIT_AVAILABLE = True
except ImportError:
    print("⚠️ Git no está disponible. La funcionalidad de Git estará deshabilitada.")
    GIT_AVAILABLE = False
    Repo = None
from modern_styles import modern_styles  # Import modern styling
from backup_system import BackupSystem  # Import backup system
from backup_gui_simple import BackupManagerDialog  # Import backup GUI

class ModernDialog(ctk.CTkToplevel):
	"""Base class for modern dialogs with consistent styling and behavior"""
	
	def __init__(self, parent, title="Dialog", size=(400, 300), resizable=True):
		super().__init__(parent)
		
		# Basic configuration
		self.title(title)
		self.geometry(f"{size[0]}x{size[1]}")
		self.resizable(resizable, resizable)
		
		# Modern styling
		self.styles = modern_styles
		
		# Center the dialog
		self.center_window()
		
		# Make modal
		self.transient(parent)
		self.grab_set()
		self.lift()
		self.focus_force()
		
		# Create main container
		self.main_container = ctk.CTkFrame(self, **self.styles.get_frame_style('card'))
		self.main_container.pack(fill="both", expand=True, padx=self.styles.spacing['md'], pady=self.styles.spacing['md'])
		
		# Initialize result
		self.result = None
		
		# Setup close behavior
		self.protocol("WM_DELETE_WINDOW", self.on_close)
		
		# Bind Escape key to close
		self.bind("<Escape>", lambda e: self.on_close())
	
	def center_window(self):
		"""Center the dialog on the parent window"""
		self.update_idletasks()
		
		# Get parent window position and size
		parent = self.master
		parent_x = parent.winfo_x()
		parent_y = parent.winfo_y()
		parent_width = parent.winfo_width()
		parent_height = parent.winfo_height()
		
		# Get dialog size
		dialog_width = self.winfo_reqwidth()
		dialog_height = self.winfo_reqheight()
		
		# Calculate center position
		x = parent_x + (parent_width // 2) - (dialog_width // 2)
		y = parent_y + (parent_height // 2) - (dialog_height // 2)
		
		# Ensure dialog is not off-screen
		x = max(0, x)
		y = max(0, y)
		
		self.geometry(f"+{x}+{y}")
	
	def create_header(self, title, subtitle=None, icon=None):
		"""Create a modern header section"""
		header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
		header_frame.pack(fill="x", pady=(0, self.styles.spacing['lg']))
		
		# Icon and title
		title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
		title_frame.pack(fill="x")
		
		title_text = f"{icon} {title}" if icon else title
		title_style = self.styles.get_label_style('heading')
		ctk.CTkLabel(title_frame, text=title_text, **title_style).pack(anchor="w")
		
		if subtitle:
			subtitle_style = self.styles.get_label_style('body')
			ctk.CTkLabel(
				title_frame, 
				text=subtitle, 
				**subtitle_style,
				text_color=self.styles.colors['text_secondary']
			).pack(anchor="w", pady=(self.styles.spacing['xs'], 0))
		
		return header_frame
	
	def create_form_field(self, parent, label, field_type="entry", **kwargs):
		"""Create a modern form field with label"""
		field_frame = ctk.CTkFrame(parent, fg_color="transparent")
		field_frame.pack(fill="x", pady=self.styles.spacing['sm'])
		
		# Label
		label_style = self.styles.get_label_style('body')
		ctk.CTkLabel(field_frame, text=label, **label_style).pack(anchor="w")
		
		# Field
		entry_style = self.styles.get_entry_style()
		entry_style.update(kwargs)
		
		if field_type == "entry":
			field = ctk.CTkEntry(field_frame, **entry_style)
		elif field_type == "textbox":
			field = ctk.CTkTextbox(field_frame, height=100, **entry_style)
		elif field_type == "optionmenu":
			values = kwargs.pop('values', [])
			field = ctk.CTkOptionMenu(field_frame, values=values, **entry_style)
		else:
			field = ctk.CTkEntry(field_frame, **entry_style)
		
		field.pack(fill="x", pady=(self.styles.spacing['xs'], 0))
		
		return field
	
	def create_button_bar(self, buttons):
		"""Create a modern button bar at the bottom"""
		button_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
		button_frame.pack(fill="x", pady=(self.styles.spacing['lg'], 0))
		
		# Right-aligned buttons
		button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
		button_container.pack(side="right")
		
		created_buttons = []
		for button_config in buttons:
			btn_style = self.styles.get_button_style(
				button_config.get('variant', 'primary'),
				button_config.get('size', 'medium')
			)
			
			btn = ctk.CTkButton(
				button_container,
				text=button_config['text'],
				command=button_config['command'],
				**btn_style
			)
			btn.pack(side="left", padx=(self.styles.spacing['sm'], 0))
			created_buttons.append(btn)
		
		return created_buttons
	
	def show_loading(self, message="Cargando..."):
		"""Show loading state"""
		# This could be enhanced with a progress bar or spinner
		pass
	
	def hide_loading(self):
		"""Hide loading state"""
		pass
	
	def on_close(self):
		"""Handle dialog close"""
		self.result = None
		self.destroy()
	
	def on_ok(self):
		"""Handle OK button - override in subclasses"""
		self.result = True
		self.destroy()
	
	def on_cancel(self):
		"""Handle Cancel button"""
		self.result = False
		self.destroy()

class ConfirmationDialog(ModernDialog):
	"""Modern confirmation dialog"""
	
	def __init__(self, parent, title="Confirmar", message="¿Está seguro?", icon="❓"):
		super().__init__(parent, title, (400, 200), False)
		
		# Create content
		self.create_header(title, icon=icon)
		
		# Message
		message_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
		message_frame.pack(fill="x", pady=self.styles.spacing['md'])
		
		message_style = self.styles.get_label_style('body')
		ctk.CTkLabel(message_frame, text=message, **message_style).pack()
		
		# Buttons
		self.create_button_bar([
			{'text': '❌ Cancelar', 'command': self.on_cancel, 'variant': 'secondary'},
			{'text': '✅ Confirmar', 'command': self.on_ok, 'variant': 'primary'}
		])

class InputDialog(ModernDialog):
	"""Modern input dialog"""
	
	def __init__(self, parent, title="Entrada", message="Ingrese el valor:", default_value="", icon="📝"):
		super().__init__(parent, title, (450, 250), False)
		
		self.value = None
		
		# Create content
		self.create_header(title, icon=icon)
		
		# Message and input
		content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
		content_frame.pack(fill="x", pady=self.styles.spacing['md'])
		
		if message:
			message_style = self.styles.get_label_style('body')
			ctk.CTkLabel(content_frame, text=message, **message_style).pack(anchor="w", pady=(0, self.styles.spacing['sm']))
		
		# Input field
		entry_style = self.styles.get_entry_style()
		self.entry = ctk.CTkEntry(content_frame, **entry_style)
		self.entry.pack(fill="x")
		
		if default_value:
			self.entry.insert(0, default_value)
			self.entry.select_range(0, 'end')
		
		# Focus on entry
		self.entry.focus()
		
		# Bind Enter key
		self.entry.bind("<Return>", lambda e: self.on_ok())
		
		# Buttons
		self.create_button_bar([
			{'text': '❌ Cancelar', 'command': self.on_cancel, 'variant': 'secondary'},
			{'text': '✅ Aceptar', 'command': self.on_ok, 'variant': 'primary'}
		])
	
	def on_ok(self):
		"""Handle OK button"""
		self.value = self.entry.get().strip()
		self.result = True
		self.destroy()

class FormDialog(ModernDialog):
	"""Modern form dialog with validation"""
	
	def __init__(self, parent, title="Formulario", fields=None, icon="📋"):
		super().__init__(parent, title, (500, 400), True)
		
		self.fields = fields or []
		self.field_widgets = {}
		self.values = {}
		
		# Create content
		self.create_header(title, icon=icon)
		
		# Create form
		self.create_form()
		
		# Buttons
		self.create_button_bar([
			{'text': '❌ Cancelar', 'command': self.on_cancel, 'variant': 'secondary'},
			{'text': '✅ Guardar', 'command': self.on_ok, 'variant': 'primary'}
		])
	
	def create_form(self):
		"""Create form fields"""
		form_frame = ctk.CTkScrollableFrame(self.main_container, **self.styles.get_frame_style('panel'))
		form_frame.pack(fill="both", expand=True, pady=self.styles.spacing['md'])
		
		for field in self.fields:
			field_name = field['name']
			field_label = field['label']
			field_type = field.get('type', 'entry')
			field_kwargs = field.get('kwargs', {})
			
			widget = self.create_form_field(form_frame, field_label, field_type, **field_kwargs)
			self.field_widgets[field_name] = widget
			
			# Set default value if provided
			if 'default' in field:
				if field_type == 'entry':
					widget.insert(0, str(field['default']))
				elif field_type == 'optionmenu':
					widget.set(str(field['default']))
	
	def validate_form(self):
		"""Validate form fields - override in subclasses"""
		return True
	
	def get_form_values(self):
		"""Get all form values"""
		values = {}
		for name, widget in self.field_widgets.items():
			if isinstance(widget, ctk.CTkEntry):
				values[name] = widget.get().strip()
			elif isinstance(widget, ctk.CTkTextbox):
				values[name] = widget.get("1.0", "end-1c").strip()
			elif isinstance(widget, ctk.CTkOptionMenu):
				values[name] = widget.get()
		return values
	
	def on_ok(self):
		"""Handle OK button with validation"""
		if self.validate_form():
			self.values = self.get_form_values()
			self.result = True
			self.destroy()
		else:
			# Validation failed - show error or highlight fields
			pass

def commit_y_push(repo_dir, mensaje_commit):
	if not GIT_AVAILABLE:
		print("⚠️ Git no está disponible. Saltando commit/push.")
		return
		
	try:
		repo = Repo(repo_dir)
		repo.git.add('html/JS/productos.json')
		repo.index.commit(mensaje_commit)
		repo.remote(name='origin').push()
		print("\u2705 Cambios subidos a GitHub correctamente.")
	except Exception as e:
		print(f"\u274c Error al hacer commit/push: {e}")

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

def filtrar_productos(self, *args):
	busqueda = self.entry_busqueda.get().strip().lower()
	categoria = self.combo_categoria.get()
	disciplina = self.combo_disciplina.get()

	# Si no hay cambios en la búsqueda, categoría o disciplina, no hacer nada
	if (
		busqueda == getattr(self, "last_search", "")
		and categoria == getattr(self, "last_category", "Todas")
		and disciplina == getattr(self, "last_disciplina", "Todas")
	):
		return

	# Actualizar los valores de búsqueda, categoría y disciplina
	self.last_search = busqueda
	self.last_category = categoria
	self.last_disciplina = disciplina

	productos_filtrados = []

	for p in self.cached_productos:
		titulo_lower = p['titulo'].lower()
		codigo = str(p.get('codigo_barras', ''))
		disciplina_p = p.get('disciplina', '').lower()

		# Verificar si la búsqueda coincide con el código exacto
		if busqueda.isdigit() and codigo.isdigit() and int(codigo) == int(busqueda):
			coincide_categoria = (
				categoria == "Todas"
				or categoria.upper() == p['categoria']['nombre'].upper()
				or categoria.lower() in p['categoria_general'].lower()
			)
			coincide_disciplina = (
				disciplina == "Todas"
				or disciplina.lower() == disciplina_p
			)
			if coincide_categoria and coincide_disciplina:
				productos_filtrados.append(p)
			continue

		# Si no es código exacto, buscar en título y código
		if busqueda in titulo_lower or busqueda in codigo:
			coincide_categoria = (
				categoria == "Todas"
				or categoria.upper() == p['categoria']['nombre'].upper()
				or categoria.lower() in p['categoria_general'].lower()
			)
			coincide_disciplina = (
				disciplina == "Todas"
				or disciplina.lower() == disciplina_p
			)
			if coincide_categoria and coincide_disciplina:
				productos_filtrados.append(p)

	# Ordenar los resultados numéricamente si es posible
	def get_sort_key(producto):
		try:
			return int(producto.get('codigo_barras', ''))
		except ValueError:
			return float('inf')

	productos_filtrados.sort(key=get_sort_key)

	# Actualizar la lista filtrada y mostrar los productos
	self.cached_filtrados = productos_filtrados
	self.mostrar_productos(productos_filtrados)

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

class LoginDialog(ctk.CTkToplevel):
	def __init__(self, parent):
		super().__init__(parent)
		self.title("🔐 Iniciar Sesión - Deportes Güemes")
		self.geometry("450x400")
		self.resizable(False, False)
		
		# Center the window
		self.transient(parent)
		self.grab_set()
		
		# Variables
		self.is_admin = False
		self.is_empleado = False
		self.styles = modern_styles
		
		# Main container with modern styling
		self.main_frame = ctk.CTkFrame(self, **self.styles.get_frame_style('card'))
		self.main_frame.pack(fill="both", expand=True, padx=self.styles.spacing['lg'], pady=self.styles.spacing['lg'])
		
		# Header section
		self.create_header()
		
		# Login form
		self.create_login_form()
		
		# Footer with help text
		self.create_footer()
		
		# Focus on username entry
		self.entry_usuario.focus()

	def create_header(self):
		"""Create modern header section"""
		header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
		header_frame.pack(fill="x", pady=(0, self.styles.spacing['lg']))
		
		# Title
		title_style = self.styles.get_label_style('heading')
		ctk.CTkLabel(
			header_frame,
			text="🏪 Deportes Güemes",
			**title_style
		).pack(pady=(0, self.styles.spacing['sm']))
		
		# Subtitle
		subtitle_style = self.styles.get_label_style('body')
		ctk.CTkLabel(
			header_frame,
			text="Sistema de Gestión de Inventario",
			**subtitle_style,
			text_color=self.styles.colors['text_secondary']
		).pack()

	def create_login_form(self):
		"""Create modern login form"""
		form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
		form_frame.pack(fill="x", pady=self.styles.spacing['md'])
		
		# Username section
		user_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
		user_frame.pack(fill="x", pady=self.styles.spacing['sm'])
		
		label_style = self.styles.get_label_style('body')
		ctk.CTkLabel(user_frame, text="👤 Usuario:", **label_style).pack(anchor="w")
		
		entry_style = self.styles.get_entry_style()
		self.entry_usuario = ctk.CTkEntry(
			user_frame,
			placeholder_text="Ingrese su usuario",
			**entry_style
		)
		self.entry_usuario.pack(fill="x", pady=(self.styles.spacing['xs'], 0))
		
		# Password section
		pass_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
		pass_frame.pack(fill="x", pady=self.styles.spacing['sm'])
		
		ctk.CTkLabel(pass_frame, text="🔒 Contraseña:", **label_style).pack(anchor="w")
		
		self.entry_password = ctk.CTkEntry(
			pass_frame,
			placeholder_text="Ingrese su contraseña",
			show="*",
			**entry_style
		)
		self.entry_password.pack(fill="x", pady=(self.styles.spacing['xs'], 0))
		
		# Bind Enter key to login
		self.entry_usuario.bind("<Return>", lambda e: self.entry_password.focus())
		self.entry_password.bind("<Return>", lambda e: self.login())
		
		# Login button - solución simplificada con altura fija
		login_button = ctk.CTkButton(
			form_frame,
			text="🚀 Iniciar Sesión",
			command=self.login,
			height=90,  # Altura fija más grande
			font=ctk.CTkFont(size=16, weight="bold"),
			fg_color="#1f538d",
			hover_color="#14396b",
			text_color="white",
			corner_radius=8
		)
		login_button.pack(fill="x", pady=(15, 15))  # Padding vertical más grande

	def create_footer(self):
		"""Create footer with help information"""
		footer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
		footer_frame.pack(fill="x", pady=(self.styles.spacing['lg'], 0))
		
		# Help text
		help_frame = ctk.CTkFrame(footer_frame, **self.styles.get_frame_style('panel'))
		help_frame.pack(fill="x")
		
		caption_style = self.styles.get_label_style('caption')
		ctk.CTkLabel(
			help_frame,
			text="💡 Credenciales de prueba:",
			**caption_style,
			text_color=self.styles.colors['text_secondary']
		).pack(pady=(self.styles.spacing['sm'], self.styles.spacing['xs']))
		
		ctk.CTkLabel(
			help_frame,
			text="👨‍💼 Administrador: usuario 'a', contraseña 'a'",
			**caption_style,
			text_color=self.styles.colors['text_secondary']
		).pack(pady=self.styles.spacing['xs'])
		
		ctk.CTkLabel(
			help_frame,
			text="👥 Empleado: usuario 'e', contraseña 'e'",
			**caption_style,
			text_color=self.styles.colors['text_secondary']
		).pack(pady=(self.styles.spacing['xs'], self.styles.spacing['sm']))

	def login(self):
		usuario = self.entry_usuario.get().strip()
		password = self.entry_password.get().strip()
		
		if not usuario or not password:
			messagebox.showerror("❌ Error", "Por favor complete todos los campos")
			return
		
		# Credenciales de admin
		if usuario == "a" and password == "a":
			self.is_admin = True
			self.is_empleado = False
			messagebox.showinfo("✅ Éxito", "¡Bienvenido Administrador!")
			self.destroy()
		# Credenciales de empleado
		elif usuario == "e" and password == "e":
			self.is_admin = False
			self.is_empleado = True
			messagebox.showinfo("✅ Éxito", "¡Bienvenido Empleado!")
			self.destroy()
		else:
			messagebox.showerror("❌ Error", "Usuario o contraseña incorrectos")
			self.entry_password.delete(0, 'end')
			self.entry_usuario.focus()

class App(ctk.CTk):
	def __init__(self):
		super().__init__()
		
		# Initialize modern styling
		self.styles = modern_styles
		self.styles.configure_theme("dark")
		
		# Initialize backup system
		try:
			self.backup_system = BackupSystem()
			print("Backup system initialized successfully")
		except Exception as e:
			print(f"Failed to initialize backup system: {e}")
			self.backup_system = None
		
		# Inicializar como no admin
		self.is_admin = False
		self.is_empleado = False

		# Inicializar modo_venta como None para evitar errores de atributo
		self.modo_venta = None
		
		# Configurar ventana principal
		self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
		self.title("Deportes Güemes - Sistema de Gestión")
		
		# Variable para controlar el tema
		self.tema_actual = "dark"
		
		# Use modern fonts from styling system
		self.font_title = self.styles.fonts['heading_medium']
		self.font_normal = self.styles.fonts['body_medium']
		self.font_small = self.styles.fonts['body_small']

		# Initialize responsive layout system
		self.current_layout = "desktop"  # desktop, tablet, mobile
		self.last_width = 0
		self.last_height = 0
		
		# Create main container with responsive design
		self.main_container = ctk.CTkFrame(self)
		self.main_container.pack(fill="both", expand=True)
		
		# Menu will be created after login
		self.menu_frame = None
		
		# Content area
		self.content_frame = ctk.CTkFrame(self.main_container)
		self.content_frame.pack(fill="both", expand=True)

		# Background frame for logo
		self.background_frame = ctk.CTkFrame(self.content_frame)
		self.background_frame.pack(fill="both", expand=True)

		# Crear Tabview para las pestañas principales (will be created after login)
		self.tab_view = None
		
		self.show_login()
		
		# Cargar imagen de fondo	
		try:
			self.original_image = Image.open("html/img/Logo.jpeg")
			self.actualizar_imagen_fondo()
			self.bind('<Configure>', self.on_window_resize)
		except Exception as e:
			print(f"Error al cargar la imagen de fondo: {e}")
		
		# Mostrar login al inicio
		self.state("zoomed")  # Iniciar maximizado	

	def actualizar_imagen_fondo(self):
		window_width = self.winfo_width()
		window_height = self.winfo_height()
		
		if window_width > 1 and window_height > 1:
			# Crear imagen que cubra toda la pantalla
			imagen_fondo = self.original_image.copy()
			
			# Calcular el tamaño para cubrir toda la ventana manteniendo proporción
			img_ratio = imagen_fondo.width / imagen_fondo.height
			window_ratio = window_width / window_height
			
			if img_ratio > window_ratio:
				# La imagen es más ancha, ajustar por altura
				new_height = window_height
				new_width = int(new_height * img_ratio)
			else:
				# La imagen es más alta, ajustar por ancho
				new_width = window_width
				new_height = int(new_width / img_ratio)
			
			imagen_fondo = imagen_fondo.resize((new_width, new_height), Image.Resampling.LANCZOS)
			
			self.bg_image = ctk.CTkImage(
				light_image=imagen_fondo,
				dark_image=imagen_fondo,
				size=(new_width, new_height)
			)
			
			if hasattr(self, 'bg_label'):
				self.bg_label.configure(image=self.bg_image)
			else:
				self.bg_label = ctk.CTkLabel(
					self.background_frame, 
					image=self.bg_image,
					text=""
				)
				# Colocar la imagen para que cubra toda la pantalla
				self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

	def on_resize(self, event=None):
		if event.widget == self:
			self.actualizar_imagen_fondo()

	def on_window_resize(self, event=None):
		"""Handle window resize with responsive layout updates"""
		if event and event.widget == self:
			current_width = self.winfo_width()
			current_height = self.winfo_height()
			
			# Only update if size changed significantly
			if abs(current_width - self.last_width) > 50 or abs(current_height - self.last_height) > 50:
				self.last_width = current_width
				self.last_height = current_height
				
				# Determine new layout
				new_layout = self.determine_layout(current_width)
				
				if new_layout != self.current_layout:
					self.current_layout = new_layout
					self.update_responsive_layout()
				
				# Update background image
				self.actualizar_imagen_fondo()
	
	def determine_layout(self, width):
		"""Determine layout type based on window width"""
		if width < self.styles.breakpoints['md']:
			return "mobile"
		elif width < self.styles.breakpoints['lg']:
			return "tablet"
		else:
			return "desktop"
	
	def update_responsive_layout(self):
		"""Update layout based on current responsive state"""
		if hasattr(self, 'menu_frame') and self.menu_frame:
			self.update_menu_layout()
		
		# Update any open dialogs
		for child in self.winfo_children():
			if isinstance(child, ctk.CTkToplevel):
				if hasattr(child, 'update_responsive_layout'):
					child.update_responsive_layout()
	
	def update_menu_layout(self):
		"""Update menu layout for responsive design"""
		if not self.menu_frame:
			return
		
		# Get current padding based on screen size
		responsive_padding = self.styles.get_responsive_padding(self.winfo_width())
		
		# Update menu frame padding
		self.menu_frame.pack_configure(pady=responsive_padding)
		
		# Update button spacing based on layout
		if self.current_layout == "mobile":
			# Stack buttons vertically on mobile
			for widget in self.menu_frame.winfo_children():
				if isinstance(widget, ctk.CTkButton):
					widget.pack_configure(side="top", fill="x", padx=self.styles.spacing['sm'], pady=self.styles.spacing['xs'])
		else:
			# Keep horizontal layout for tablet and desktop
			for widget in self.menu_frame.winfo_children():
				if isinstance(widget, ctk.CTkButton):
					if "Cerrar Sesión" in widget.cget("text") or "Cambiar Tema" in widget.cget("text"):
						widget.pack_configure(side="right", padx=self.styles.spacing['sm'])
					else:
						widget.pack_configure(side="left", padx=self.styles.spacing['sm'])

	def create_menu(self):
		# Destruir el menú anterior si existe
		if hasattr(self, 'menu_frame') and self.menu_frame is not None:
			self.menu_frame.destroy()

		# Crear un único frame para los botones con estilo moderno dentro del main_container
		self.menu_frame = ctk.CTkFrame(self.main_container, **self.styles.get_frame_style('panel'))
		self.menu_frame.pack(side="top", fill="x", pady=self.styles.spacing['md'], before=self.content_frame)

		# SOLO PARA ADMIN - Botón Nuevo Producto (primero)
		if self.is_admin:
			btn_style = self.styles.get_button_style('success', 'medium')
			ctk.CTkButton(
				self.menu_frame,
				text="➕ Nuevo Producto",
				command=self.show_nuevo_producto,
				**btn_style
			).pack(side="left", padx=self.styles.spacing['sm'])

		# Botón para abrir la pestaña "Lista de Productos"
		btn_style = self.styles.get_button_style('primary', 'medium')
		ctk.CTkButton(
			self.menu_frame,
			text="📋 Lista de Productos",
			command=self.show_ver_productos,
			**btn_style
		).pack(side="left", padx=self.styles.spacing['sm'])

		# Botón para abrir la pestaña "Venta"
		btn_style = self.styles.get_button_style('primary', 'medium')
		ctk.CTkButton(
			self.menu_frame,
			text="💰 Venta",
			command=self.toggle_modo_venta,
			**btn_style
		).pack(side="left", padx=self.styles.spacing['sm'])

		# Botón Lista de Precios (disponible para todos)
		btn_style = self.styles.get_button_style('secondary', 'medium')
		ctk.CTkButton(
			self.menu_frame,
			text="💲 Lista de Precios",
			command=self.show_lista_precios,
			**btn_style
		).pack(side="left", padx=self.styles.spacing['sm'])

		# SOLO PARA ADMIN - Botón Importar Precios Excel
		if self.is_admin:
			btn_style = self.styles.get_button_style('warning', 'medium')
			ctk.CTkButton(
				self.menu_frame,
				text="📊 Importar Precios Excel",
				command=self.show_excel_import,
				**btn_style
			).pack(side="left", padx=self.styles.spacing['sm'])

		# SOLO PARA ADMIN - Botón Historial
		if self.is_admin:
			btn_style = self.styles.get_button_style('secondary', 'medium')
			ctk.CTkButton(
				self.menu_frame,
				text="📊 Historial",
				command=self.show_historial,
				**btn_style
			).pack(side="left", padx=self.styles.spacing['sm'])

		# SOLO PARA ADMIN - Botón Respaldos (último)
		if self.is_admin:
			btn_style = self.styles.get_button_style('info', 'medium')
			ctk.CTkButton(
				self.menu_frame,
				text="💾 Respaldos",
				command=self.show_backup_manager,
				**btn_style
			).pack(side="left", padx=self.styles.spacing['sm'])

		# Botón de cambiar tema a la derecha
		btn_style = self.styles.get_button_style('outline', 'medium')
		btn_style['fg_color'] = self.styles.colors['warning']
		btn_style['hover_color'] = '#d97706'
		ctk.CTkButton(
			self.menu_frame,
			text="🎨 Cambiar Tema",
			command=self.toggle_tema,
			**btn_style
		).pack(side="right", padx=self.styles.spacing['sm'])

		# Botón de cerrar sesión a la derecha
		btn_style = self.styles.get_button_style('error', 'medium')
		ctk.CTkButton(
			self.menu_frame,
			text="🚪 Cerrar Sesión",
			command=self.logout,
			**btn_style
		).pack(side="right", padx=self.styles.spacing['sm'])

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

	def show_backup_manager(self):
		"""Show the backup management dialog"""
		if not self.is_admin:
			messagebox.showerror("Error", "Acceso denegado. Se requieren permisos de administrador.")
			return
		try:
			BackupManagerDialog(self)
		except Exception as e:
			messagebox.showerror("Error", f"Error al abrir el gestor de respaldos: {str(e)}")

	def show_excel_import(self):
		"""Show Excel price import dialog"""
		if not self.is_admin:
			messagebox.showerror("Error", "Acceso denegado. Se requieren permisos de administrador.")
			return
		
		try:
			# Initialize Excel importer
			excel_importer = ExcelPriceImporter(self)
			excel_importer.import_prices_from_excel()
		except Exception as e:
			messagebox.showerror("Error", f"Error al inicializar importador de Excel: {str(e)}")

	def trigger_backup_after_change(self, change_type="data_modified"):
		"""Trigger backup after data changes"""
		if hasattr(self, 'backup_system') and self.backup_system:
			try:
				# Create incremental backup in background thread
				def backup_thread():
					try:
						backup_info = self.backup_system.create_incremental_backup()
						if backup_info:
							print(f"Auto-backup created after {change_type}: {backup_info['id']}")
					except Exception as e:
						print(f"Auto-backup failed: {e}")
				
				# Run backup in separate thread to avoid blocking UI
				threading.Thread(target=backup_thread, daemon=True).start()
			except Exception as e:
				print(f"Failed to trigger backup: {e}")

	def save_products_with_backup(self, productos, commit_message="Product data updated"):
		"""Save products with automatic backup"""
		try:
			# Save products
			with open('html/JS/productos.json', 'w', encoding='utf-8') as archivo:
				json.dump(productos, archivo, indent=2, ensure_ascii=False)
			
			# Trigger backup
			self.trigger_backup_after_change("products_saved")
			
			# Git commit if available
			if GIT_AVAILABLE:
				try:
					repo = Repo('.')
					repo.index.add(['html/JS/productos.json'])
					repo.index.commit(commit_message)
					print(f"Git commit: {commit_message}")
				except Exception as e:
					print(f"Git commit failed: {e}")
			else:
				print("⚠️ Git no está disponible. Saltando commit.")
				
		except Exception as e:
			print(f"Failed to save products: {e}")
			raise

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
		self.state("zoomed")

	def update_interface(self):
		# Recrear el menú y limpiar pestañas si es necesario
		self.create_menu()
		# Si querés limpiar las pestañas al cambiar de usuario:
		if self.tab_view is not None and hasattr(self.tab_view, '_name_list'):
			for tab in self.tab_view._name_list[1:]:  # Mantener solo la pestaña principal si querés
				self.tab_view.delete(tab)

class VerProductosDialog(ctk.CTkToplevel):
	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent  # Guardar referencia al parent
		self.title("📋 Gestión de Productos - Deportes Güemes")
		self.geometry("1200x800")
		self.lift()  # Mantener ventana al frente
		self.transient(parent)  # Hacer la ventana dependiente del padre
		self.focus_force()  # Forzar el foco

		self.productos = []
		self.productos_seleccionados = []
		self.styles = modern_styles
		
		# Responsive layout variables
		self.current_columns = 4
		self.last_width = 0
		
		# Bind resize event
		self.bind('<Configure>', self.on_dialog_resize)

		# Main container with modern styling
		self.main_frame = ctk.CTkFrame(self, **self.styles.get_frame_style('default'))
		self.main_frame.pack(fill="both", expand=True, padx=self.styles.spacing['md'], pady=self.styles.spacing['md'])

		# Create header
		self.create_header()

		self.crear_filtros()

		# Products container with modern scrollable frame
		self.productos_frame = ctk.CTkScrollableFrame(
			self.main_frame,
			**self.styles.get_frame_style('card')
		)
		self.productos_frame.pack(fill="both", expand=True, padx=self.styles.spacing['sm'], pady=self.styles.spacing['sm'])

		# Guardar productos filtrados actuales
		self._productos_filtrados = []

		self.cargar_productos()

class ExcelPriceImporter:
	"""Handles importing prices from Excel files provided by brands"""
	
	def __init__(self, parent_app):
		self.parent_app = parent_app
		self.supported_formats = ['.xlsx', '.xls', '.csv']
	
	def import_prices_from_excel(self):
		"""Import prices from Excel file"""
		try:
			# Open file dialog
			file_path = filedialog.askopenfilename(
				title="Seleccionar archivo de precios de la marca",
				filetypes=[
					("Excel files", "*.xlsx *.xls"),
					("CSV files", "*.csv"),
					("All files", "*.*")
				]
			)
			
			if not file_path:
				return
			
			# Show import dialog
			import_dialog = ExcelImportDialog(self.parent_app, file_path)
			result = import_dialog.show()
			
			if result:
				self.process_import(result)
				
		except Exception as e:
			messagebox.showerror("Error", f"Error al importar precios: {str(e)}")
	
	def process_import(self, import_data):
		"""Process the imported data and update prices"""
		try:
			import pandas as pd
			
			# Read the Excel file
			if import_data['file_path'].endswith('.csv'):
				df = pd.read_csv(import_data['file_path'])
			else:
				df = pd.read_excel(import_data['file_path'])
			
			# Get column mappings
			id_column = import_data['id_column']
			price_column = import_data['price_column']
			
			# Load current products
			with open('html/JS/productos.json', 'r', encoding='utf-8') as f:
				productos = json.load(f)
			
			updated_count = 0
			errors = []
			
			# Update prices
			for index, row in df.iterrows():
				try:
					product_id = str(row[id_column]).strip()
					new_price = float(str(row[price_column]).replace(',', '.').replace('$', ''))
					
					# Find product and update price
					for producto in productos:
						if producto['id'] == product_id:
							old_price = producto['precio']
							producto['precio'] = new_price
							updated_count += 1
							
							# Log the change
							print(f"Updated {product_id}: ${old_price} -> ${new_price}")
							break
					
				except Exception as e:
					errors.append(f"Error en fila {index + 1}: {str(e)}")
			
			# Save updated products
			with open('html/JS/productos.json', 'w', encoding='utf-8') as f:
				json.dump(productos, f, ensure_ascii=False, indent=2)
			
			# Show results
			message = f"Precios actualizados exitosamente!\n\n"
			message += f"Productos actualizados: {updated_count}\n"
			
			if errors:
				message += f"Errores: {len(errors)}\n\n"
				message += "Primeros errores:\n" + "\n".join(errors[:5])
			
			messagebox.showinfo("Importación completada", message)
			
			# Refresh the product list in the main app
			if hasattr(self.parent_app, 'cargar_productos'):
				self.parent_app.cargar_productos()
			
			# Create backup after price update
			if hasattr(self.parent_app, 'backup_system') and self.parent_app.backup_system:
				try:
					self.parent_app.backup_system.create_incremental_backup()
					print("✅ Backup creado después de la importación de precios")
				except Exception as backup_error:
					print(f"⚠️ Error al crear backup: {backup_error}")
			
		except ImportError:
			messagebox.showerror("Error", "pandas no está instalado. Instala con: pip install pandas openpyxl")
		except Exception as e:
			messagebox.showerror("Error", f"Error al procesar importación: {str(e)}")


			
			# Configure columns
			tree['columns'] = list(df.columns)
			for col in df.columns:
				tree.heading(col, text=col)
				tree.column(col, width=100)
			
			# Add data
			for index, row in df.iterrows():
				tree.insert('', 'end', values=list(row))
			
			# Scrollbars
			v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
			h_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
			tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
			
			# Pack
			tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
			v_scrollbar.pack(side="right", fill="y", pady=10)
			h_scrollbar.pack(side="bottom", fill="x", padx=(10, 0))
			
			# Update column selection with detected columns
			columns = list(df.columns)
			print(f"📊 Actualizando OptionMenu con columnas: {columns}")
			self.create_column_selection(columns)
			
		except ImportError:
			error_label = ctk.CTkLabel(parent, text="pandas no está instalado.\nInstala con: pip install pandas openpyxl")
			error_label.pack(expand=True)
		except Exception as e:
			error_label = ctk.CTkLabel(parent, text=f"Error al cargar archivo:\n{str(e)}")
			error_label.pack(expand=True)
	
	def on_import(self):
		"""Handle import button click"""
		if not self.id_column_var.get() or not self.price_column_var.get():
			messagebox.showerror("Error", "Debe seleccionar las columnas de ID y Precio")
			return
		
		if self.id_column_var.get() == "Seleccionar columna..." or self.price_column_var.get() == "Seleccionar columna...":
			messagebox.showerror("Error", "Debe seleccionar columnas válidas")
			return
		
		self.result = {
			'file_path': self.file_path,
			'id_column': self.id_column_var.get(),
			'price_column': self.price_column_var.get()
		}
		self.destroy()
	
	def on_cancel(self):
		"""Handle cancel button click"""
		self.result = None
		self.destroy()
	
	def show(self):
		"""Show dialog and return result"""
		self.wait_window()
		return self.result


		if self.tab_view is not None and hasattr(self.tab_view, '_name_list'):
			for tab in self.tab_view._name_list[1:]:  # Mantener solo la pestaña principal si querés
				self.tab_view.delete(tab)

class VerProductosDialog(ctk.CTkToplevel):
	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent  # Guardar referencia al parent
		self.title("📋 Gestión de Productos - Deportes Güemes")
		self.geometry("1200x800")
		self.lift()  # Mantener ventana al frente
		self.transient(parent)  # Hacer la ventana dependiente del padre
		self.focus_force()  # Forzar el foco

		self.productos = []
		self.productos_seleccionados = []
		self.styles = modern_styles
		
		# Responsive layout variables
		self.current_columns = 4
		self.last_width = 0
		
		# Bind resize event
		self.bind('<Configure>', self.on_dialog_resize)

		# Main container with modern styling
		self.main_frame = ctk.CTkFrame(self, **self.styles.get_frame_style('default'))
		self.main_frame.pack(fill="both", expand=True, padx=self.styles.spacing['md'], pady=self.styles.spacing['md'])

		# Create header
		self.create_header()

		self.crear_filtros()

		# Products container with modern scrollable frame
		self.productos_frame = ctk.CTkScrollableFrame(
			self.main_frame,
			**self.styles.get_frame_style('card')
		)
		self.productos_frame.pack(fill="both", expand=True, padx=self.styles.spacing['sm'], pady=self.styles.spacing['sm'])

		# Guardar productos filtrados actuales
		self._productos_filtrados = []

		self.cargar_productos()
	
	def on_dialog_resize(self, event=None):
		"""Handle dialog resize with responsive layout updates"""
		if event and event.widget == self:
			current_width = self.winfo_width()
			
			# Only update if width changed significantly
			if abs(current_width - self.last_width) > 100:
				self.last_width = current_width
				
				# Calculate new column count based on width
				new_columns = self.calculate_responsive_columns(current_width)
				
				if new_columns != self.current_columns:
					self.current_columns = new_columns
					# Refresh product display with new column count
					if hasattr(self, '_productos_filtrados'):
						self.mostrar_productos(self._productos_filtrados)
	
	def calculate_responsive_columns(self, width):
		"""Calculate number of columns based on dialog width"""
		if width < 600:
			return 1  # Very small: 1 column
		elif width < 900:
			return 2  # Small: 2 columns
		elif width < 1200:
			return 3  # Medium: 3 columns
		elif width < 1500:
			return 4  # Large: 4 columns
		else:
			return 5  # Extra large: 5 columns
	
	def update_responsive_layout(self):
		"""Update layout for responsive design"""
		current_width = self.winfo_width()
		new_columns = self.calculate_responsive_columns(current_width)
		
		if new_columns != self.current_columns:
			self.current_columns = new_columns
			if hasattr(self, '_productos_filtrados'):
				self.mostrar_productos(self._productos_filtrados)

	def create_header(self):
		"""Create modern header section"""
		header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
		header_frame.pack(fill="x", pady=(0, self.styles.spacing['md']))
		
		# Title
		title_style = self.styles.get_label_style('heading')
		ctk.CTkLabel(
			header_frame,
			text="📋 Gestión de Productos",
			**title_style
		).pack(side="left")
		
		# Stats or info could go here
		info_style = self.styles.get_label_style('body')
		self.stats_label = ctk.CTkLabel(
			header_frame,
			text="Cargando productos...",
			**info_style,
			text_color=self.styles.colors['text_secondary']
		)
		self.stats_label.pack(side="right")

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
					#if not producto.get('es_variante', False):
					card = self.crear_producto_card(self.productos_frame, producto)
					card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
					col += 1
					if col >= columnas:
						col = 0
						row += 1
				except Exception as e:
					print(f"Error mostrando producto: {producto}\n{e}")

			# Actualizar el label de estadísticas
			total_productos = len(productos_filtrados)
			if total_productos == 0:
				self.stats_label.configure(text="No hay productos")
				label = ctk.CTkLabel(
					self.productos_frame,
					text="No hay productos para los filtros aplicados.",
					font=("", 16, "bold"),
					text_color="red"
				)
				label.grid(row=0, column=0, padx=10, pady=30, columnspan=columnas, sticky="nsew")
			else:
				self.stats_label.configure(text=f"📦 {total_productos} producto{'s' if total_productos != 1 else ''} encontrado{'s' if total_productos != 1 else ''}")
				
		except Exception as e:
			print(f"Error en mostrar_productos: {e}")
			self.stats_label.configure(text="❌ Error al cargar productos")

	def crear_filtros(self):
		"""Create modern collapsible filter section"""
		# Main filters container
		filtros_container = ctk.CTkFrame(self.main_frame, **self.styles.get_frame_style('panel'))
		filtros_container.pack(fill="x", padx=self.styles.spacing['sm'], pady=self.styles.spacing['sm'])
		
		# Filters header with toggle button
		header_frame = ctk.CTkFrame(filtros_container, fg_color="transparent")
		header_frame.pack(fill="x", pady=self.styles.spacing['sm'])
		
		# Toggle button for filters
		self.filtros_visible = False  # Start with filters hidden
		btn_style = self.styles.get_button_style('secondary', 'medium')
		self.toggle_filtros_btn = ctk.CTkButton(
			header_frame,
			text="🔍 Mostrar Filtros",
			command=self.toggle_filtros,
			**btn_style
		)
		self.toggle_filtros_btn.pack(side="left")
		
		# Admin buttons (only for admin users)
		if hasattr(self.parent, 'is_admin') and self.parent.is_admin:
			admin_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
			admin_frame.pack(side="left", padx=self.styles.spacing['md'])
			
			# Selection buttons
			btn_style_small = self.styles.get_button_style('secondary', 'small')
			ctk.CTkButton(
				admin_frame,
				text="✅ Seleccionar Todos",
				command=self.seleccionar_todos,
				**btn_style_small
			).pack(side="left", padx=self.styles.spacing['xs'])
			
			ctk.CTkButton(
				admin_frame,
				text="❌ Deseleccionar Todos",
				command=self.deseleccionar_todos,
				**btn_style_small
			).pack(side="left", padx=self.styles.spacing['xs'])
			
			# Mass action buttons
			btn_style_warning = self.styles.get_button_style('warning', 'small')
			ctk.CTkButton(
				admin_frame,
				text="💰 Cambiar Precio",
				command=self.actualizar_precios_seleccionados,
				**btn_style_warning
			).pack(side="left", padx=self.styles.spacing['xs'])
			
			btn_style_success = self.styles.get_button_style('success', 'small')
			ctk.CTkButton(
				admin_frame,
				text="📦 Cambiar Stock",
				command=self.actualizar_stock_seleccionados,
				**btn_style_success
			).pack(side="left", padx=self.styles.spacing['xs'])
		
		# Quick search (always visible)
		search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
		search_frame.pack(side="right", padx=self.styles.spacing['sm'])
		
		label_style = self.styles.get_label_style('body')
		ctk.CTkLabel(search_frame, text="🔎 Búsqueda rápida:", **label_style).pack(side="left", padx=(0, self.styles.spacing['xs']))
		
		entry_style = self.styles.get_entry_style()
		entry_style['width'] = 200
		self.filtro_nombre = ctk.CTkEntry(search_frame, placeholder_text="Buscar producto...", **entry_style)
		self.filtro_nombre.pack(side="left")
		self.filtro_nombre.bind('<KeyRelease>', lambda e: self.aplicar_filtros())
		
		# Collapsible filters content
		self.filtros_content = ctk.CTkFrame(filtros_container, **self.styles.get_frame_style('card'))
		# Don't pack initially - will be shown/hidden by toggle
		
		# Create all filter widgets inside the collapsible content
		self.crear_filtros_avanzados()
	
	def crear_filtros_avanzados(self):
		"""Create the advanced filter widgets inside the collapsible content"""
		label_style = self.styles.get_label_style('body')
		entry_style = self.styles.get_entry_style()
		
		# First row of filters
		filtro_row1 = ctk.CTkFrame(self.filtros_content, fg_color="transparent")
		filtro_row1.pack(fill="x", pady=self.styles.spacing['sm'])
		
		# Category filter
		cat_frame = ctk.CTkFrame(filtro_row1, fg_color="transparent")
		cat_frame.pack(side="left", padx=self.styles.spacing['sm'])
		
		ctk.CTkLabel(cat_frame, text="📂 Categoría:", **label_style).pack(anchor="w")
		self.filtro_categoria = ctk.CTkOptionMenu(
			cat_frame,
			values=["Todas", "Indumentaria", "Accesorios", "Remeras", "Pantalones", "Abrigos", "Marroquineria", "Bolsos", "Pelotas"],
			command=lambda x: self.aplicar_filtros(),
			width=140
		)
		self.filtro_categoria.pack(pady=(self.styles.spacing['xs'], 0))
		
		# Discipline filter
		disc_frame = ctk.CTkFrame(filtro_row1, fg_color="transparent")
		disc_frame.pack(side="left", padx=self.styles.spacing['sm'])
		
		ctk.CTkLabel(disc_frame, text="⚽ Disciplina:", **label_style).pack(anchor="w")
		self.filtro_disciplina = ctk.CTkOptionMenu(
			disc_frame,
			values=["Todas", "Futbol", "Basquet", "Tenis", "Natacion", "Running", 
					"Boxeo", "Voley", "Rugby", "Hockey", "Yoga", "Fitness", "Musculacion"],
			command=lambda x: self.aplicar_filtros(),
			width=140
		)
		self.filtro_disciplina.pack(pady=(self.styles.spacing['xs'], 0))
		
		# Gender filter
		gen_frame = ctk.CTkFrame(filtro_row1, fg_color="transparent")
		gen_frame.pack(side="left", padx=self.styles.spacing['sm'])
		
		ctk.CTkLabel(gen_frame, text="👤 Género:", **label_style).pack(anchor="w")
		self.filtro_genero = ctk.CTkOptionMenu(
			gen_frame,
			values=["Todos", "Femenino", "Masculino", "Niño", "Niña", "Unisex", "No"],
			command=lambda x: self.aplicar_filtros(),
			width=120
		)
		self.filtro_genero.pack(pady=(self.styles.spacing['xs'], 0))
		
		# Second row of filters
		filtro_row2 = ctk.CTkFrame(self.filtros_content, fg_color="transparent")
		filtro_row2.pack(fill="x", pady=self.styles.spacing['sm'])
		
		# Size filter
		size_frame = ctk.CTkFrame(filtro_row2, fg_color="transparent")
		size_frame.pack(side="left", padx=self.styles.spacing['sm'])
		
		ctk.CTkLabel(size_frame, text="📏 Talle:", **label_style).pack(anchor="w")
		self.filtro_talle = ctk.CTkOptionMenu(
			size_frame,
			values=["Todos", "No", "S", "M", "L", "XL"],
			command=lambda x: self.aplicar_filtros(),
			width=100
		)
		self.filtro_talle.pack(pady=(self.styles.spacing['xs'], 0))
		
		# Price range
		price_frame = ctk.CTkFrame(filtro_row2, fg_color="transparent")
		price_frame.pack(side="left", padx=self.styles.spacing['sm'])
		
		ctk.CTkLabel(price_frame, text="💰 Rango de Precio:", **label_style).pack(anchor="w")
		
		price_inputs = ctk.CTkFrame(price_frame, fg_color="transparent")
		price_inputs.pack(pady=(self.styles.spacing['xs'], 0))
		
		entry_style['width'] = 80
		self.filtro_precio_min = ctk.CTkEntry(price_inputs, placeholder_text="Mín", **entry_style)
		self.filtro_precio_min.pack(side="left", padx=(0, self.styles.spacing['xs']))
		self.filtro_precio_min.bind('<KeyRelease>', lambda e: self.aplicar_filtros())
		
		ctk.CTkLabel(price_inputs, text="-", **label_style).pack(side="left")
		
		self.filtro_precio_max = ctk.CTkEntry(price_inputs, placeholder_text="Máx", **entry_style)
		self.filtro_precio_max.pack(side="left", padx=(self.styles.spacing['xs'], 0))
		self.filtro_precio_max.bind('<KeyRelease>', lambda e: self.aplicar_filtros())
		
		# Clear filters button
		clear_frame = ctk.CTkFrame(filtro_row2, fg_color="transparent")
		clear_frame.pack(side="right", padx=self.styles.spacing['sm'])
		
		btn_style = self.styles.get_button_style('outline', 'medium')
		ctk.CTkButton(
			clear_frame,
			text="🗑️ Limpiar Filtros",
			command=self.limpiar_filtros,
			**btn_style
		).pack(pady=self.styles.spacing['sm'])
	
	def toggle_filtros(self):
		"""Toggle the visibility of advanced filters"""
		if self.filtros_visible:
			# Hide filters
			self.filtros_content.pack_forget()
			self.toggle_filtros_btn.configure(text="🔍 Mostrar Filtros")
			self.filtros_visible = False
		else:
			# Show filters
			self.filtros_content.pack(fill="x", pady=self.styles.spacing['sm'])
			self.toggle_filtros_btn.configure(text="🔼 Ocultar Filtros")
			self.filtros_visible = True

	def crear_botones_accion(self, parent):
		"""Create modern action buttons section"""
		botones_frame = ctk.CTkFrame(parent, fg_color="transparent")
		botones_frame.pack(fill="x", pady=self.styles.spacing['md'])
		
		# Selection buttons
		selection_frame = ctk.CTkFrame(botones_frame, fg_color="transparent")
		selection_frame.pack(side="left")
		
		btn_style = self.styles.get_button_style('secondary', 'small')
		ctk.CTkButton(
			selection_frame,
			text="✅ Seleccionar Todos",
			command=self.seleccionar_todos,
			**btn_style
		).pack(side="left", padx=self.styles.spacing['xs'])
		
		ctk.CTkButton(
			selection_frame,
			text="❌ Deseleccionar Todos",
			command=self.deseleccionar_todos,
			**btn_style
		).pack(side="left", padx=self.styles.spacing['xs'])
		
		# Mass action buttons
		actions_frame = ctk.CTkFrame(botones_frame, fg_color="transparent")
		actions_frame.pack(side="right")
		
		btn_style = self.styles.get_button_style('warning', 'small')
		ctk.CTkButton(
			actions_frame,
			text="💰 Actualizar Precios",
			command=self.actualizar_precios_seleccionados,
			**btn_style
		).pack(side="left", padx=self.styles.spacing['xs'])
		
		btn_style = self.styles.get_button_style('success', 'small')
		ctk.CTkButton(
			actions_frame,
			text="📦 Actualizar Stock",
			command=self.actualizar_stock_seleccionados,
			**btn_style
		).pack(side="left", padx=self.styles.spacing['xs'])

	def limpiar_filtros(self):
		"""Clear all filter values"""
		self.filtro_nombre.delete(0, 'end')
		if hasattr(self, 'filtro_categoria'):
			self.filtro_categoria.set("Todas")
		if hasattr(self, 'filtro_disciplina'):
			self.filtro_disciplina.set("Todas")
		if hasattr(self, 'filtro_genero'):
			self.filtro_genero.set("Todos")
		if hasattr(self, 'filtro_talle'):
			self.filtro_talle.set("Todos")
		if hasattr(self, 'filtro_precio_min'):
			self.filtro_precio_min.delete(0, 'end')
		if hasattr(self, 'filtro_precio_max'):
			self.filtro_precio_max.delete(0, 'end')
		
		# Apply filters to show all products
		self.aplicar_filtros()

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
		
		# Título con indicador de variante
		titulo_text = producto['titulo']
		if producto.get('es_variante', False):
			# Es una variante - agregar indicador
			variante_info = producto.get('variante', {})
			variante_valor = variante_info.get('valor', 'Variante')
			titulo_text = f"🔸 {titulo_text}"
			# Agregar label de variante
			ctk.CTkLabel(
				header_frame, 
				text=titulo_text, 
				font=("", 14, "bold"),
				text_color="#FF6B35"  # Color naranja para variantes
			).pack(side="left")
			# Mostrar de qué producto es variante
			producto_padre_id = producto.get('producto_padre', 'Desconocido')
			# Buscar el nombre del producto padre
			producto_padre_nombre = producto_padre_id
			for p in self.productos:
				if p['id'] == producto_padre_id:
					producto_padre_nombre = p['titulo']
					break
			ctk.CTkLabel(
				info_frame, 
				text=f"📎 Variante de: {producto_padre_nombre}",
				font=("", 10),
				text_color="#666666"
			).pack(anchor="w")
			ctk.CTkLabel(
				info_frame, 
				text=f"🎨 Tipo: {variante_valor}",
				font=("", 10),
				text_color="#666666"
			).pack(anchor="w")
		else:
			# Es un producto principal
			ctk.CTkLabel(
				header_frame, 
				text=f"🔹 {titulo_text}", 
				font=("", 14, "bold"),
				text_color="#4CAF50"  # Color verde para productos principales
			).pack(side="left")
			# Verificar si tiene variantes
			variantes_count = len([p for p in self.productos if p.get('producto_padre') == producto['id']])
			if variantes_count > 0:
				ctk.CTkLabel(
					info_frame, 
					text=f"🔗 Tiene {variantes_count} variante(s)",
					font=("", 10),
					text_color="#2196F3"
				).pack(anchor="w")
		
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
		# SOLO PARA ADMIN - Botones de Modificar y Eliminar
		if hasattr(self.parent, 'is_admin') and self.parent.is_admin:
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
		
		# Botón de Stock disponible para todos (admin y empleados)
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
		"""Modern stock update dialog"""
		class StockUpdateDialog(ModernDialog):
			def __init__(self, parent, producto):
				super().__init__(parent, "📦 Actualizar Stock", (450, 350), False)
				self.producto = producto
				self.parent_dialog = parent
				
				# Create header
				self.create_header(
					"Actualizar Stock",
					f"Gestionar inventario de: {producto['titulo']}",
					"📦"
				)
				
				# Product info section
				info_frame = ctk.CTkFrame(self.main_container, **self.styles.get_frame_style('panel'))
				info_frame.pack(fill="x", pady=self.styles.spacing['md'])
				
				info_style = self.styles.get_label_style('body')
				ctk.CTkLabel(info_frame, text=f"📋 Producto: {producto['titulo']}", **info_style).pack(anchor="w", padx=self.styles.spacing['md'], pady=self.styles.spacing['sm'])
				ctk.CTkLabel(info_frame, text=f"📊 Stock Actual: {producto.get('stock', 0)} unidades", **info_style).pack(anchor="w", padx=self.styles.spacing['md'], pady=(0, self.styles.spacing['sm']))
				
				# Input section
				self.entry_cantidad = self.create_form_field(
					self.main_container,
					"📈 Cantidad a agregar/quitar:",
					"entry",
					placeholder_text="Ej: +10 o -5"
				)
				
				# Help text
				help_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
				help_frame.pack(fill="x", pady=self.styles.spacing['sm'])
				
				help_style = self.styles.get_label_style('caption')
				ctk.CTkLabel(
					help_frame,
					text="💡 Ingrese un número positivo para agregar stock o negativo para quitar",
					**help_style,
					text_color=self.styles.colors['text_secondary']
				).pack()
				
				# Focus on entry
				self.entry_cantidad.focus()
				self.entry_cantidad.bind("<Return>", lambda e: self.on_ok())
				
				# Buttons
				self.create_button_bar([
					{'text': '❌ Cancelar', 'command': self.on_cancel, 'variant': 'secondary'},
					{'text': '✅ Actualizar Stock', 'command': self.on_ok, 'variant': 'success'}
				])
			
			def on_ok(self):
				cantidad_str = self.entry_cantidad.get().strip()
				if not cantidad_str:
					messagebox.showerror("❌ Error", "Por favor ingrese una cantidad")
					return
				
				try:
					cantidad = int(cantidad_str)
					nuevo_stock = self.producto.get('stock', 0) + cantidad
					
					# Verificar que el nuevo stock no sea menor a 0
					if nuevo_stock < 0:
						messagebox.showerror("❌ Error", "El stock no puede ser menor a 0")
						return
					
					self.producto['stock'] = nuevo_stock
					
					# Actualizar el archivo JSON
					with open('html/JS/productos.json', 'r') as archivo:
						productos = json.load(archivo)
					
					# Encontrar y actualizar el producto
					for i, p in enumerate(productos):
						if p['id'] == self.producto['id']:
							productos[i] = self.producto
							break
					
					with open('html/JS/productos.json', 'w') as archivo:
						json.dump(productos, archivo, indent=2)
					
					messagebox.showinfo("✅ Éxito", f"Stock actualizado correctamente.\nNuevo stock: {nuevo_stock} unidades")
					self.result = True
					self.destroy()
					
					# Recargar la vista de productos
					self.parent_dialog.cargar_productos()
					
				except ValueError:
					messagebox.showerror("❌ Error", "Por favor, ingrese un valor numérico válido.")
		
		# Show the dialog
		dialog = StockUpdateDialog(self, producto)

	def actualizar_precios_seleccionados(self):
		"""Modern price update dialog for selected products"""
		# Verificar si hay productos seleccionados
		productos_a_actualizar = [(p, v) for p, v in self.productos_seleccionados if v.get()]
		
		if not productos_a_actualizar:
			messagebox.showwarning("⚠️ Advertencia", "No hay productos seleccionados")
			return
		
		class PriceUpdateDialog(ModernDialog):
			def __init__(self, parent, productos_a_actualizar):
				super().__init__(parent, "💰 Actualizar Precios", (600, 500), True)
				self.productos_a_actualizar = productos_a_actualizar
				self.parent_dialog = parent
				
				# Create header
				self.create_header(
					"Actualizar Precios Masivamente",
					f"Actualizar precios de {len(productos_a_actualizar)} productos seleccionados",
					"💰"
				)
				
				# Create form
				self.create_price_form()
				
				# Show selected products
				self.create_products_list()
				
				# Buttons
				self.create_button_bar([
					{'text': '❌ Cancelar', 'command': self.on_cancel, 'variant': 'secondary'},
					{'text': '💰 Actualizar Precios', 'command': self.on_ok, 'variant': 'warning'}
				])
			
			def create_price_form(self):
				"""Create price update form"""
				form_frame = ctk.CTkFrame(self.main_container, **self.styles.get_frame_style('panel'))
				form_frame.pack(fill="x", pady=self.styles.spacing['md'])
				
				# Update type selection
				type_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
				type_frame.pack(fill="x", padx=self.styles.spacing['md'], pady=self.styles.spacing['sm'])
				
				label_style = self.styles.get_label_style('body')
				ctk.CTkLabel(type_frame, text="📊 Tipo de Actualización:", **label_style).pack(anchor="w")
				
				self.tipo_actualizacion = ctk.StringVar(value="porcentaje")
				
				radio_frame = ctk.CTkFrame(type_frame, fg_color="transparent")
				radio_frame.pack(fill="x", pady=(self.styles.spacing['xs'], 0))
				
				ctk.CTkRadioButton(
					radio_frame,
					text="📈 Porcentaje (%)",
					variable=self.tipo_actualizacion,
					value="porcentaje"
				).pack(side="left", padx=(0, self.styles.spacing['md']))
				
				ctk.CTkRadioButton(
					radio_frame,
					text="💵 Monto Fijo ($)",
					variable=self.tipo_actualizacion,
					value="monto"
				).pack(side="left")
				
				# Value input
				self.entry_valor = self.create_form_field(
					form_frame,
					"💲 Valor:",
					"entry",
					placeholder_text="Ej: 15 (para 15%) o 100 (para $100)"
				)
				
				# Focus on entry
				self.entry_valor.focus()
				self.entry_valor.bind("<Return>", lambda e: self.on_ok())
			
			def create_products_list(self):
				"""Create list of selected products"""
				list_frame = ctk.CTkFrame(self.main_container, **self.styles.get_frame_style('panel'))
				list_frame.pack(fill="both", expand=True, pady=self.styles.spacing['md'])
				
				# Title
				title_style = self.styles.get_label_style('subheading')
				ctk.CTkLabel(list_frame, text="📋 Productos Seleccionados:", **title_style).pack(
					anchor="w", padx=self.styles.spacing['md'], pady=(self.styles.spacing['sm'], 0)
				)
				
				# Scrollable products list
				products_scroll = ctk.CTkScrollableFrame(list_frame, height=150)
				products_scroll.pack(fill="both", expand=True, padx=self.styles.spacing['md'], pady=self.styles.spacing['sm'])
				
				body_style = self.styles.get_label_style('body')
				for producto, _ in self.productos_a_actualizar:
					product_frame = ctk.CTkFrame(products_scroll, fg_color="transparent")
					product_frame.pack(fill="x", pady=self.styles.spacing['xs'])
					
					ctk.CTkLabel(
						product_frame,
						text=f"• {producto['titulo']} - Precio actual: ${producto['precio']}",
						**body_style
					).pack(anchor="w")
			
			def on_ok(self):
				"""Apply price update"""
				valor_str = self.entry_valor.get().strip()
				if not valor_str:
					messagebox.showerror("❌ Error", "Por favor ingrese un valor")
					return
				
				try:
					valor = float(valor_str)
					
					# Confirm the action
					tipo_texto = "porcentaje" if self.tipo_actualizacion.get() == "porcentaje" else "monto fijo"
					confirm_msg = f"¿Confirma actualizar {len(self.productos_a_actualizar)} productos con {tipo_texto} de {valor}?"
					
					if not messagebox.askyesno("🤔 Confirmar", confirm_msg):
						return
					
					# Apply updates
					with open('html/JS/productos.json', 'r') as archivo:
						todos_productos = json.load(archivo)
					
					detalles_cambios = []
					for producto, _ in self.productos_a_actualizar:
						# Calcular nuevo precio
						precio_actual = float(producto['precio'])
						if self.tipo_actualizacion.get() == "porcentaje":
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
					try:
						HistorialDialog.registrar_accion(
							accion="Precio Actualizado",
							producto="Varios productos",
							detalles="\n".join(detalles_cambios)
						)
					except:
						pass  # Continue even if history fails
					
					# Commit changes
					try:
						commit_y_push(repo_dir='.', mensaje_commit="Actualización de precios masiva")
					except:
						pass  # Continue even if git fails
					
					messagebox.showinfo("✅ Éxito", f"Precios actualizados correctamente para {len(self.productos_a_actualizar)} productos")
					self.result = True
					self.destroy()
					
					# Reload products
					self.parent_dialog.cargar_productos()
					
				except ValueError:
					messagebox.showerror("❌ Error", "Por favor, ingrese un valor numérico válido.")
		
		# Show the dialog
		dialog = PriceUpdateDialog(self, productos_a_actualizar)
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
			try:
				# Guardar cambios
				with open('html/JS/productos.json', 'w') as archivo:
					json.dump(todos_productos, archivo, indent=2)
				
				# Registrar acción en el historial
				HistorialDialog.registrar_accion(
					accion="Precio Actualizado",
					producto="Varios productos",
					detalles="\n".join(detalles_cambios)
				)

				commit_y_push(repo_dir='.', mensaje_commit="Actualización de precios masiva")

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
		dialog.lift()
		dialog.transient(self)
		dialog.focus_force()
		dialog.grab_set() 
		
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

				commit_y_push(repo_dir='.', mensaje_commit="Actualización de stock masiva")
				
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
				commit_y_push(repo_dir='.', mensaje_commit=f"Producto eliminado: {producto['titulo']}")

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
		dialog.geometry("700x900")  # Aumentado de 600x800 a 700x900
		dialog.lift()
		dialog.transient(self)
		dialog.focus_force()
		dialog.grab_set()

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

		# Categoría
		ctk.CTkLabel(frame, text="Categoría").pack(pady=5)
		categorias = ["Indumentaria", "Accesorios", "Remeras", "Pantalones", "Abrigos", "Marroquineria", "Bolsos", "Pelotas"]
		variable_categoria = ctk.StringVar(value=producto['categoria']['nombre'].capitalize())
		categoria_menu = ctk.CTkOptionMenu(frame, values=categorias, variable=variable_categoria)
		categoria_menu.pack(pady=5)

		# Género
		ctk.CTkLabel(frame, text="Género").pack(pady=5)
		generos = ["Femenino", "Masculino", "Niño", "Niña", "Unisex", "No"]
		variable_genero = ctk.StringVar(value=producto.get('genero', 'No'))
		genero_menu = ctk.CTkOptionMenu(frame, values=generos, variable=variable_genero)
		genero_menu.pack(pady=5)

		# Talles
		ctk.CTkLabel(frame, text="Talles").pack(pady=5)
		talles = ["No", "S", "M", "L", "XL"]
		talle_vars = {}
		talles_frame = ctk.CTkFrame(frame)
		talles_frame.pack(pady=5)
		for talle in talles:
			var = ctk.BooleanVar(value=talle in producto.get('talles', []))
			talle_vars[talle] = var
			ctk.CTkCheckBox(talles_frame, text=talle, variable=var).pack(side="left", padx=5)

		# Disciplina
		ctk.CTkLabel(frame, text="Disciplina").pack(pady=5)
		disciplinas = ["Futbol", "Basquet", "Tenis", "Natacion", "Running", "Boxeo", "Voley", "Rugby", "Hockey", "Yoga", "Fitness", "Musculacion"]
		variable_disciplina = ctk.StringVar(value=producto.get('disciplina', ''))
		disciplina_menu = ctk.CTkOptionMenu(frame, values=disciplinas, variable=variable_disciplina)
		disciplina_menu.pack(pady=5)

		# Código de Barras
		ctk.CTkLabel(frame, text="Código de Barras").pack(pady=5)
		entry_codigo_barras = ctk.CTkEntry(frame, width=300)
		entry_codigo_barras.insert(0, str(producto.get('codigo_barras', '')))
		entry_codigo_barras.pack(pady=5)

		# Imagen actual
		ctk.CTkLabel(frame, text="Imagen actual:").pack(pady=5)
		img_label = ctk.CTkLabel(frame, text="")
		img_label.pack(pady=5)
		ruta_img = os.path.abspath(os.path.join('html', producto['imagen'].replace('./', ''))) if producto['imagen'] else ""
		if ruta_img and os.path.exists(ruta_img):
			pil_image = Image.open(ruta_img)
			pil_image.thumbnail((150, 150))
			ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(150, 150))
			img_label.configure(image=ctk_image)
			img_label.image = ctk_image

		# Botón para seleccionar nueva imagen
		nueva_imagen_path = [producto['imagen']]  # Usar lista para mutabilidad en closure

		def seleccionar_imagen():
			file_path = filedialog.askopenfilename(
				title="Seleccione una imagen",
				filetypes=[("Archivos de imagen", ".png .jpg .jpeg .gif .bmp")]
			)
			if file_path:
				imagen_nombre = os.path.basename(file_path)
				destino = os.path.join('html', 'img', imagen_nombre)
				try:
					os.makedirs(os.path.join('html', 'img'), exist_ok=True)
					shutil.copy2(file_path, destino)
					nueva_imagen_path[0] = f"./img/{imagen_nombre}"
					pil_image = Image.open(destino)
					pil_image.thumbnail((150, 150))
					ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(150, 150))
					img_label.configure(image=ctk_image)
					img_label.image = ctk_image
				except Exception as e:
					messagebox.showerror("Error", f"No se pudo copiar la imagen: {e}")

		ctk.CTkButton(frame, text="Cambiar Imagen", command=seleccionar_imagen).pack(pady=5)

		# Separador visual
		ctk.CTkFrame(frame, height=2, fg_color="gray").pack(fill="x", pady=20)

		# Botones de acción
		botones_frame = ctk.CTkFrame(frame, fg_color="transparent")
		botones_frame.pack(fill="x", pady=10)

		def guardar_cambios():
			try:
				# Obtener datos anteriores
				precio_anterior = producto['precio']
				titulo_anterior = producto['titulo']

				# Actualizar datos del producto
				producto['titulo'] = entry_nombre.get()
				producto['precio'] = redondear_precio(entry_precio.get())
				producto['categoria'] = {
					"nombre": variable_categoria.get().upper(),
					"id": variable_categoria.get().lower()
				}
				producto['categoria_general'] = "indumentaria" if variable_categoria.get().lower() in ["remeras", "pantalones", "abrigos"] else "accesorios"
				producto['genero'] = variable_genero.get()
				producto['talles'] = [talle for talle, var in talle_vars.items() if var.get()]
				producto['disciplina'] = variable_disciplina.get()
				producto['codigo_barras'] = int(entry_codigo_barras.get())
				producto['imagen'] = nueva_imagen_path[0]

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
				
				commit_y_push(repo_dir='.', mensaje_commit=f"Producto modificado: {producto['titulo']}")

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

		# Botón de Confirmar Cambios
		ctk.CTkButton(
			botones_frame,
			text="✅ Confirmar Cambios",
			command=guardar_cambios,
			height=40,
			font=ctk.CTkFont(size=14, weight="bold"),
			fg_color="#28a745",
			hover_color="#218838",
			text_color="white"
		).pack(side="left", padx=10, expand=True, fill="x")

		# Botón de Cancelar
		ctk.CTkButton(
			botones_frame,
			text="❌ Cancelar",
			command=dialog.destroy,
			height=40,
			font=ctk.CTkFont(size=14, weight="bold"),
			fg_color="#dc3545",
			hover_color="#c82333",
			text_color="white"
		).pack(side="right", padx=10, expand=True, fill="x")

class ModoVentaDialog(ctk.CTkToplevel):
	def __init__(self, parent):
		super().__init__(parent)
		self.title("Modo Venta")
		self.geometry("1000x600")  # Tamaño más razonable
		self.lift()  # Mantener ventana al frente
		self.transient(parent)  # Hacer la ventana dependiente del padre
		self.focus_force()  # Forzar el foco

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
				stock = producto.get('stock', 0)
				if stock > 0:
					stock_text = f"Stock: {stock}"
					stock_color = "green"
					checkbox_state = "normal"
				else:
					stock_text = "SIN STOCK"
					stock_color = "red"
					checkbox_state = "disabled"

				# Mostrar información del producto
				ctk.CTkLabel(item_frame, text=f"Código: {producto['codigo_barras']}", font=("", 12)).pack(side="left", padx=5)
				ctk.CTkLabel(item_frame, text=f"Producto: {producto['titulo']}", font=("", 12, "bold"), text_color="blue").pack(side="left", padx=5)
				ctk.CTkLabel(item_frame, text=f"${producto['precio']}", font=("", 12)).pack(side="right", padx=5)
				ctk.CTkLabel(item_frame, text=stock_text, font=("", 12), text_color=stock_color).pack(side="right", padx=5)

				# Campo para cantidad
				cantidad_var = ctk.IntVar(value=1)
				ctk.CTkLabel(item_frame, text="Cantidad:").pack(side="right", padx=2)
				frame_cantidad = ctk.CTkFrame(item_frame)
				frame_cantidad.pack(side="right", padx=2)

				def aumentar():
					if stock == 0:
						return
					cantidad_var.set(min(cantidad_var.get() + 1, stock))

				def disminuir():
					if cantidad_var.get() > 1:
						cantidad_var.set(cantidad_var.get() - 1)

				btn_menos = ctk.CTkButton(frame_cantidad, text="-", width=20, command=disminuir)
				btn_menos.pack(side="left")
				entry_cantidad = ctk.CTkEntry(frame_cantidad, width=30, textvariable=cantidad_var)
				entry_cantidad.pack(side="left")
				btn_mas = ctk.CTkButton(frame_cantidad, text="+", width=20, command=aumentar)
				btn_mas.pack(side="left")

				# Checkbox para seleccionar/deseleccionar el producto
				var = ctk.BooleanVar(value=stock > 0)
				checkbox = ctk.CTkCheckBox(
					item_frame,
					text="Seleccionar",
					variable=var,
					state=checkbox_state
				)
				checkbox.pack(side="right", padx=5)

				# Guardar la selección con cantidad SOLO si tiene stock
				if stock > 0:
					self.productos_seleccionados.append({
						"producto": producto,
						"var": var,
						"cantidad_var": cantidad_var
					})

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
		# Solo productos seleccionados y con cantidad > 0
		seleccionados = [
			(item["producto"], item["cantidad_var"].get())
			for item in self.productos_seleccionados
			if item["var"].get() and item["cantidad_var"].get() > 0
		]

		if not seleccionados:
			messagebox.showwarning("Advertencia", "No hay productos seleccionados para la venta.")
			return

		try:
			with open('html/JS/productos.json', 'r') as archivo:
				productos = json.load(archivo)

			detalles_venta = []
			for producto_sel, cantidad in seleccionados:
				for producto in productos:
					if producto['id'] == producto_sel['id']:
						if producto['stock'] >= cantidad:
							producto['stock'] -= cantidad
							detalles_venta.append(
								f"{producto['titulo']} (Código: {producto['codigo_barras']}, Cantidad: {cantidad}, Precio: ${producto['precio']})"
							)
							self._actualizar_stock_interfaz(producto)
						else:
							messagebox.showerror(
								"Error",
								f"El producto '{producto['titulo']}' no tiene suficiente stock."
							)
							return

			with open('html/JS/productos.json', 'w') as archivo:
				json.dump(productos, archivo, indent=2)

			HistorialDialog.registrar_accion(
				accion="Venta",
				producto="Productos vendidos",
				detalles="\n".join(detalles_venta)
			)

			messagebox.showinfo("Éxito", "Venta realizada correctamente.")
			self.total_venta = 0
			self.total_label.configure(text="Total: $0")

			# Deseleccionar productos si el switch está activado
			if self.deseleccionar_switch.get():
				self.productos_seleccionados.clear()
				for widget in self.lista_frame.winfo_children():
					if isinstance(widget, ctk.CTkFrame):
						checkbox = widget.winfo_children()[-1]
						if isinstance(checkbox, ctk.CTkCheckBox):
							checkbox.deselect()

		except Exception as e:
			messagebox.showerror("Error", f"Error al realizar la venta: {str(e)}")

	def _actualizar_stock_interfaz(self, producto):
		# Buscar el frame correspondiente al producto en la lista
		for widget in self.lista_frame.winfo_children():
			if isinstance(widget, ctk.CTkFrame):
				labels = widget.winfo_children()
				if labels and str(producto['codigo_barras']) in labels[0].cget("text"):
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
		self.lift()  # Mantener ventana al frente
		self.transient(parent)  # Hacer la ventana dependiente del padre
		self.focus_force()  # Forzar el foco

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
		opciones_unidades = ["Categoria Producto","Todas", "Indumentaria", "Accesorios", "Remeras", "Pantalones", "Abrigos", "Marroquineria", "Bolsos", "Pelotas"]
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
				print(f"Error copiando imagen: {e}")
				imagen_ruta = ""  # Si falla, deja la ruta vacía

		# Crear producto SIEMPRE, tenga o no imagen
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
			
			# Subir a GitHub
			commit_y_push(repo_dir='.', mensaje_commit=f"Nuevo producto agregado: {producto['titulo']}")


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
		self.lift()  # Mantener ventana al frente
		self.transient(parent)  # Hacer la ventana dependiente del padre
		self.focus_force()  # Forzar el foco

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

		# --- Agrega este bloque al final ---
		if not productos_filtrados:
			label = ctk.CTkLabel(
				self.tabla_frame,
				text="No se encontraron productos con los filtros aplicados.",
				font=("Helvetica", 16, "bold"),
				text_color="red"
			)
			label.grid(row=1, column=0, padx=10, pady=30, columnspan=6, sticky="nsew")

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
			label.pack(expand=True)
			label.bind("<Button-1>", lambda e, k=key: self.ordenar_por(k))

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

		# Mostrar el precio del producto seleccionado en el label
		self.precio_seleccionado_label.configure(
			text=f"Precio: ${producto['precio']}"
		)

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
		disciplina = self.combo_disciplina.get()

		# Si no hay cambios en la búsqueda, categoría o disciplina, no hacer nada
		if (
			busqueda == getattr(self, "last_search", "")
			and categoria == getattr(self, "last_category", "Todas")
			and disciplina == getattr(self, "last_disciplina", "Todas")
		):
			return

		# Actualizar los valores de búsqueda, categoría y disciplina
		self.last_search = busqueda
		self.last_category = categoria
		self.last_disciplina = disciplina

		productos_filtrados = []

		for p in self.cached_productos:
			titulo_lower = p['titulo'].lower()
			codigo = str(p.get('codigo_barras', ''))
			disciplina_p = p.get('disciplina', '').lower()

			# Verificar si la búsqueda coincide con el código exacto
			if busqueda.isdigit() and codigo.isdigit() and int(codigo) == int(busqueda):
				coincide_categoria = (
					categoria == "Todas"
					or categoria.upper() == p['categoria']['nombre'].upper()
					or categoria.lower() in p['categoria_general'].lower()
				)
				coincide_disciplina = (
					disciplina == "Todas"
					or disciplina.lower() == disciplina_p
				)
				if coincide_categoria and coincide_disciplina:
					productos_filtrados.append(p)
				continue

			# Si no es código exacto, buscar en título y código
			if busqueda in titulo_lower or busqueda in codigo:
				coincide_categoria = (
					categoria == "Todas"
					or categoria.upper() == p['categoria']['nombre'].upper()
					or categoria.lower() in p['categoria_general'].lower()
				)
				coincide_disciplina = (
					disciplina == "Todas"
					or disciplina.lower() == disciplina_p
				)
				if coincide_categoria and coincide_disciplina:
					productos_filtrados.append(p)

		# Ordenar los resultados numéricamente si es posible
		def get_sort_key(producto):
			try:
				return int(producto.get('codigo_barras', ''))
			except ValueError:
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
		busqueda_frame = ctk.CTkFrame(self.main_frame)
		busqueda_frame.pack(fill="x", padx=10, pady=5)

		# Nombre
		ctk.CTkLabel(busqueda_frame, text="Nombre").pack(side="left", padx=5)
		self.entry_busqueda = ctk.CTkEntry(busqueda_frame, width=200)
		self.entry_busqueda.pack(side="left", padx=5)
		self.entry_busqueda.bind('<KeyRelease>', self.filtrar_productos)

		# Filtro por categoría
		ctk.CTkLabel(busqueda_frame, text="Categoría:").pack(side="left", padx=5)
		self.combo_categoria = ctk.CTkOptionMenu(
			busqueda_frame,
			values=["Todas", "Indumentaria", "Accesorios", "Remeras", "Pantalones", "Abrigos", "Marroquineria", "Bolsos", "Pelotas"],
			command=self.filtrar_productos
		)
		self.combo_categoria.pack(side="left", padx=5)

		# Filtro por disciplina
		ctk.CTkLabel(busqueda_frame, text="Disciplina:").pack(side="left", padx=5)
		self.combo_disciplina = ctk.CTkOptionMenu(
			busqueda_frame,
			values=["Todas", "Futbol", "Basquet", "Tenis", "Natacion", "Running", 
					"Boxeo", "Voley", "Rugby", "Hockey", "Yoga", "Fitness", "Musculacion"],
			command=self.filtrar_productos
		)
		self.combo_disciplina.pack(side="left", padx=5)

		# Label para mostrar el precio seleccionado (arriba a la derecha)
		self.precio_seleccionado_label = ctk.CTkLabel(
			busqueda_frame,
			text="Precio: -",
			font=("Helvetica", 14, "bold"),
			text_color="green"
		)
		self.precio_seleccionado_label.pack(side="right", padx=10)

class HistorialDialog(ctk.CTkToplevel):
	def __init__(self, parent):
		super().__init__(parent)
		self.title("Historial de Cambios")
		self.geometry("1024x768")
		self.lift()  # Mantener ventana al frente
		self.transient(parent)  # Hacer la ventana dependiente del padre
		self.focus_force()  # Forzar el foco

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
		ctk.CTkLabel(self.tabla_frame, text="Fecha", font=("Helvetica", 14, "bold")).grid(row=0, column=0, padx=5, pady=2, sticky="ew")
		ctk.CTkLabel(self.tabla_frame, text="Acción", font=("Helvetica", 14, "bold")).grid(row=0, column=1, padx=5, pady=2, sticky="ew")
		ctk.CTkLabel(self.tabla_frame, text="Producto", font=("Helvetica", 14, "bold")).grid(row=0, column=2, padx=5, pady=2, sticky="ew")
		ctk.CTkLabel(self.tabla_frame, text="Detalles", font=("Helvetica", 14, "bold")).grid(row=0, column=3, padx=5, pady=2, sticky="ew")

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


class ExcelPriceImporter:
	"""Handles importing prices from Excel files provided by brands"""
	
	def __init__(self, parent_app):
		self.parent_app = parent_app
		self.supported_formats = ['.xlsx', '.xls', '.csv']
	
	def import_prices_from_excel(self):
		"""Import prices from Excel file"""
		try:
			# Open file dialog
			file_path = filedialog.askopenfilename(
				title="Seleccionar archivo de precios de la marca",
				filetypes=[
					("Excel files", "*.xlsx *.xls"),
					("CSV files", "*.csv"),
					("All files", "*.*")
				]
			)
			
			if not file_path:
				return
			
			# Show import dialog
			import_dialog = ExcelImportDialog(self.parent_app, file_path)
			result = import_dialog.show()
			
			if result:
				self.process_import(result)
				
		except Exception as e:
			messagebox.showerror("Error", f"Error al importar precios: {str(e)}")
	
	def process_import(self, import_data):
		"""Process the imported data and update prices"""
		try:
			import pandas as pd
			
			# Read the Excel file
			if import_data['file_path'].endswith('.csv'):
				df = pd.read_csv(import_data['file_path'])
			else:
				df = pd.read_excel(import_data['file_path'])
			
			# Get column mappings
			id_column = import_data['id_column']
			price_column = import_data['price_column']
			
			# Load current products
			with open('html/JS/productos.json', 'r', encoding='utf-8') as f:
				productos = json.load(f)
			
			updated_count = 0
			errors = []
			
			# Update prices
			for index, row in df.iterrows():
				try:
					product_id = str(row[id_column]).strip()
					new_price = float(str(row[price_column]).replace(',', '.').replace('$', ''))
					
					# Find product and update price
					for producto in productos:
						if producto['id'] == product_id:
							old_price = producto['precio']
							producto['precio'] = new_price
							updated_count += 1
							
							# Log the change
							print(f"Updated {product_id}: ${old_price} -> ${new_price}")
							break
					
				except Exception as e:
					errors.append(f"Error en fila {index + 1}: {str(e)}")
			
			# Save updated products
			with open('html/JS/productos.json', 'w', encoding='utf-8') as f:
				json.dump(productos, f, ensure_ascii=False, indent=2)
			
			# Show results
			message = f"Precios actualizados exitosamente!\n\n"
			message += f"Productos actualizados: {updated_count}\n"
			
			if errors:
				message += f"Errores: {len(errors)}\n\n"
				message += "Primeros errores:\n" + "\n".join(errors[:5])
			
			messagebox.showinfo("Importación completada", message)
			
			# Refresh the product list in the main app
			if hasattr(self.parent_app, 'cargar_productos'):
				self.parent_app.cargar_productos()
			
			# Create backup after price update
			if hasattr(self.parent_app, 'backup_system') and self.parent_app.backup_system:
				try:
					self.parent_app.backup_system.create_incremental_backup()
					print("✅ Backup creado después de la importación de precios")
				except Exception as backup_error:
					print(f"⚠️ Error al crear backup: {backup_error}")
			
		except ImportError:
			messagebox.showerror("Error", "pandas no está instalado. Instala con: pip install pandas openpyxl")
		except Exception as e:
			messagebox.showerror("Error", f"Error al procesar importación: {str(e)}")

class ExcelImportDialog(ModernDialog):
	"""Dialog for configuring Excel import settings"""
	
	def __init__(self, parent, file_path):
		super().__init__(parent, "Configurar Importación de Precios", (900, 700))
		self.file_path = file_path
		self.result = None
		self.setup_ui()
	
	def setup_ui(self):
		"""Setup the import configuration UI"""
		# Title
		title_label = ctk.CTkLabel(
			self.main_container,
			text="Configurar Importación de Precios",
			**self.styles.get_label_style('heading')
		)
		title_label.pack(pady=(0, self.styles.spacing['lg']))
		
		# File info
		file_info = ctk.CTkLabel(
			self.main_container,
			text=f"Archivo: {os.path.basename(self.file_path)}",
			**self.styles.get_label_style('body')
		)
		file_info.pack(pady=(0, self.styles.spacing['md']))
		
		# Preview frame
		preview_frame = ctk.CTkFrame(self.main_container)
		preview_frame.pack(fill="both", expand=True, pady=(0, self.styles.spacing['md']))
		
		# Configuration frame
		self.config_frame = ctk.CTkFrame(self.main_container)
		self.config_frame.pack(fill="x", pady=(0, self.styles.spacing['md']))
		
		# Create initial column selection (will be updated after loading file)
		self.create_column_selection()
		
		# Load and show preview (this will update the column selection)
		self.load_preview(preview_frame)
	
	def create_column_selection(self, columns=None):
		"""Create or update column selection widgets"""
		# Clear existing widgets if they exist
		for widget in self.config_frame.winfo_children():
			widget.destroy()
		
		if columns is None:
			columns = ["Seleccionar columna..."]
		
		# Column selection for ID
		ctk.CTkLabel(self.config_frame, text="Columna de ID del Producto:").pack(anchor="w", padx=10, pady=(10, 5))
		self.id_column_var = ctk.StringVar(value=columns[0])
		self.id_column_combo = ctk.CTkOptionMenu(
			self.config_frame, 
			variable=self.id_column_var, 
			values=columns
		)
		self.id_column_combo.pack(fill="x", padx=10, pady=(0, 10))
		
		# Column selection for Price
		ctk.CTkLabel(self.config_frame, text="Columna de Precio:").pack(anchor="w", padx=10, pady=(0, 5))
		self.price_column_var = ctk.StringVar(value=columns[0])
		self.price_column_combo = ctk.CTkOptionMenu(
			self.config_frame, 
			variable=self.price_column_var, 
			values=columns
		)
		self.price_column_combo.pack(fill="x", padx=10, pady=(0, 10))
		
		# Auto-detect columns if we have real column names
		if len(columns) > 1 and columns[0] != "Seleccionar columna...":
			for col in columns:
				col_lower = col.lower()
				if 'id' in col_lower or 'codigo' in col_lower or 'sku' in col_lower:
					self.id_column_var.set(col)
					self.id_column_combo.set(col)
					print(f"🔍 Auto-detectado ID: {col}")
				elif 'precio' in col_lower or 'price' in col_lower or 'valor' in col_lower:
					self.price_column_var.set(col)
					self.price_column_combo.set(col)
					print(f"💰 Auto-detectado Precio: {col}")
		
		# Buttons
		button_frame = ctk.CTkFrame(self.main_container)
		button_frame.pack(fill="x")
		
		cancel_btn = ctk.CTkButton(
			button_frame,
			text="Cancelar",
			command=self.on_cancel,
			**self.styles.get_button_style('secondary')
		)
		cancel_btn.pack(side="left", padx=(0, self.styles.spacing['sm']))
		
		import_btn = ctk.CTkButton(
			button_frame,
			text="Importar Precios",
			command=self.on_import,
			**self.styles.get_button_style('primary')
		)
		import_btn.pack(side="right")
	
	def load_preview(self, parent):
		"""Load and display file preview"""
		try:
			import pandas as pd
			
			# Read file with better CSV handling
			if self.file_path.endswith('.csv'):
				# Try different encodings and separators for CSV
				encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
				separators = [',', ';', '\t']
				
				df = None
				for encoding in encodings:
					for sep in separators:
						try:
							df = pd.read_csv(self.file_path, nrows=5, encoding=encoding, sep=sep)
							print(f"✅ CSV cargado con encoding={encoding}, sep='{sep}'")
							print(f"📊 Columnas detectadas: {list(df.columns)}")
							break
						except Exception as e:
							continue
					if df is not None:
						break
				
				if df is None:
					raise Exception("No se pudo leer el archivo CSV con ninguna configuración")
			else:
				df = pd.read_excel(self.file_path, nrows=5)
				print(f"📊 Columnas Excel detectadas: {list(df.columns)}")
			
			# Create treeview for preview
			tree = ttk.Treeview(parent, show='headings', height=6)
			
			# Configure columns
			tree['columns'] = list(df.columns)
			for col in df.columns:
				tree.heading(col, text=col)
				tree.column(col, width=100)
			
			# Add data
			for index, row in df.iterrows():
				tree.insert('', 'end', values=list(row))
			
			# Scrollbars
			v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
			h_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
			tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
			
			# Pack
			tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
			v_scrollbar.pack(side="right", fill="y", pady=10)
			h_scrollbar.pack(side="bottom", fill="x", padx=(10, 0))
			
			# Populate combo boxes with column names
			columns = list(df.columns)
			print(f"📊 Columnas encontradas: {columns}")
			
			# Update option menus with new values
			self.id_column_combo.configure(values=columns)
			self.price_column_combo.configure(values=columns)
			
			# Set default values
			if columns:
				self.id_column_combo.set(columns[0])
				self.price_column_combo.set(columns[0])
			
			# Try to auto-detect columns
			for col in columns:
				col_lower = col.lower()
				if 'id' in col_lower or 'codigo' in col_lower or 'sku' in col_lower:
					self.id_column_combo.set(col)
					self.id_column_var.set(col)
					print(f"🔍 Auto-detectado ID: {col}")
				elif 'precio' in col_lower or 'price' in col_lower or 'valor' in col_lower:
					self.price_column_combo.set(col)
					self.price_column_var.set(col)
					print(f"💰 Auto-detectado Precio: {col}")
			
		except ImportError:
			error_label = ctk.CTkLabel(parent, text="pandas no está instalado.\nInstala con: pip install pandas openpyxl")
			error_label.pack(expand=True)
		except Exception as e:
			error_label = ctk.CTkLabel(parent, text=f"Error al cargar archivo:\n{str(e)}")
			error_label.pack(expand=True)
	
	def on_import(self):
		"""Handle import button click"""
		if not self.id_column_var.get() or not self.price_column_var.get():
			messagebox.showerror("Error", "Debe seleccionar las columnas de ID y Precio")
			return
		
		self.result = {
			'file_path': self.file_path,
			'id_column': self.id_column_var.get(),
			'price_column': self.price_column_var.get()
		}
		self.destroy()
	
	def on_cancel(self):
		"""Handle cancel button click"""
		self.result = None
		self.destroy()
	
	def show(self):
		"""Show dialog and return result"""
		self.wait_window()
		return self.result

if __name__ == "__main__":
	try:
		app = App()
		app.mainloop()
	except TclError:
		pass  # Ignora el error al cerrar la app