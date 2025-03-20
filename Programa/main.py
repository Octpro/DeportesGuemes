#validar entrada de datos
#si pones cargar producto desde modo venta, que quede en el entry el codigo de barras
#verificar si pones que no es variante que cargue correctamente el producto
#que cargue bien los talles

import json
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import unicodedata

def eliminar_acentos(cadena):
    return ''.join(
        c for c in unicodedata.normalize('NFD', cadena)
        if unicodedata.category(c) != 'Mn'
    )

def select_image():
	file_path = filedialog.askopenfilename(
		title="Seleccione una imagen",
		filetypes=[("Archivos de imagen", ".png .jpg .jpeg .gif .bmp")]
	)
	if file_path:
		display_image(file_path)

def display_image(file_path):
	global selected_image_path, img, photo
	selected_image_path = file_path
	img = Image.open(file_path)
	new_size = (300, 300)
	img.thumbnail(new_size)
	photo = ImageTk.PhotoImage(img)
	image_label.config(image=photo)
	image_label.image = photo
	image_label.bind("<Button-1>", get_color)

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
	image_label.config(image='')
	image_label.image = None

def generate_unique_id(base_id, productos):
	counter = 1
	unique_id = base_id
	existing_ids = {producto['id'] for producto in productos}
	while unique_id in existing_ids:
		unique_id = f"{base_id}_{counter}"
		counter += 1
	return unique_id

def guardar():
	nombre_producto = Entry_1.get()
	categoria_producto = variable_unidad.get()
	precio = Entry_3.get()
	es_variante = var_es_variante.get()
	genero = variable_gen.get()
	talles = [listbox_talles.get(i) for i in listbox_talles.curselection()]
	disciplina = variable_disciplina.get()  # Obtener la disciplina seleccionada
	codigo_barras = entry_codigo_barras.get()  # Obtener el código de barras
	
	try:
		with open('html/JS/productos.json', 'r') as archivo:
			contenido = archivo.read().strip()
			if contenido:
				productos = json.loads(contenido)
			else:
				productos = []
	except FileNotFoundError:
		productos = []
	except json.JSONDecodeError:
		productos = []
	
	# Clasificar las categorías correctamente
	categoria_general = "Indumentaria" if categoria_producto.lower() in ["remeras", "pantalones", "abrigos"] else "Accesorios"
	
	base_id = f"{categoria_producto.lower()}_{nombre_producto.replace(' ', '_').lower()}"
	id_producto = generate_unique_id(base_id, productos)
	
	imagen_ruta = selected_image_path
	if imagen_ruta:
		imagen_nombre = os.path.basename(imagen_ruta)
		imagen_ruta = f"./img/{imagen_nombre}"
	else:
		imagen_ruta = ""
	
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
		"color": color_label.cget("text"),  # Usar el nombre del color en lugar del código hexadecimal
		"disciplina": disciplina,  # Agregar la disciplina al producto
		"stock": 0,  # Inicializar el stock a 0
		"codigo_barras": codigo_barras  # Agregar el código de barras al producto
	}
	
	productos.append(producto)
	
	with open('html/JS/productos.json', 'w') as archivo:
		json.dump(productos, archivo, indent=2)

	reset_image()
	color_label.config(bg="white", text="Color")
	
	messagebox.showinfo("Información", "Producto agregado correctamente.")
	
	if es_variante:
		agregar_variante(nombre_producto, categoria_producto, precio)

def agregar_variante(nombre_producto, categoria_producto, precio):
	if messagebox.askyesno("Agregar Variante", "¿Desea agregar una variante?"):
		select_image()
		
		# Actualizar el texto de los widgets existentes para cambiar el precio y el color
		Entry_1.delete(0, END)
		Entry_1.insert(0, nombre_producto)
		Entry_3.delete(0, END)
		Entry_3.insert(0, precio)
	else:
		messagebox.showinfo("Información", "No se agregó ninguna variante.")

def guardar_variante(nombre_producto, categoria_producto, precio, color):
    global selected_image_path
    talles = [listbox_talles.get(i) for i in listbox_talles.curselection()]
    disciplina = variable_disciplina.get()  # Obtener la disciplina seleccionada
    codigo_barras = entry_codigo_barras.get()  # Obtener el código de barras
    
    try:
        with open('html/JS/productos.json', 'r') as archivo:
            productos = json.load(archivo)
    except FileNotFoundError:
        productos = []
    
    # Clasificar las categorías correctamente
    categoria_general = "Indumentaria" if categoria_producto.lower() in ["remeras", "pantalones", "abrigos"] else "Accesorios"
    
    base_id = f"{categoria_producto.lower()}_{nombre_producto.replace(' ', '_').lower()}_variante"
    id_producto = generate_unique_id(base_id, productos)
    
    imagen_ruta = selected_image_path
    if imagen_ruta:
        imagen_nombre = os.path.basename(imagen_ruta)
        imagen_ruta = f"./img/{imagen_nombre}"
    else:
        imagen_ruta = ""
    
    producto = {
        "id": id_producto,
        "titulo": nombre_producto,
        "imagen": imagen_ruta,
        "categoria": {"nombre": categoria_producto.upper(), "id": categoria_producto.lower()},
        "categoria_general": categoria_general.lower(),
        "precio": precio,
        "es_variante": True,
        "genero": variable_gen.get(),
        "talles": talles,
        "color": color,
        "disciplina": disciplina,  # Agregar la disciplina al producto
        "stock": 0,  # Inicializar el stock a 0
        "codigo_barras": codigo_barras  # Agregar el código de barras al producto
    }
    
    productos.append(producto)
    
    with open('html/JS/productos.json', 'w') as archivo:
        json.dump(productos, archivo, indent=2)
    
    reset_image()
    color_label.config(bg="white")
    
    messagebox.showinfo("Información", "Variante agregada correctamente.")

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

def aplicar_filtro_evento(event):
	aplicar_filtro(ver_frame, productos)


def ver_productos():
    global productos
    try:
        with open('html/JS/productos.json', 'r') as archivo:
            productos = json.load(archivo)
    except FileNotFoundError:
        productos = []
    
    global ver_frame
    ver_frame = Toplevel(tk)
    ver_frame.grid_rowconfigure(0, weight=0) 
    ver_frame.grid_rowconfigure(1, weight=1) 
    ver_frame.grid_columnconfigure(0, weight=1)  

    global filtro_frame
    filtro_frame = Frame(ver_frame)
    filtro_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
    filtro_frame.grid_columnconfigure(6, weight=1)  

    for i in range(12):  # Ajustar el número de columnas según sea necesario
        filtro_frame.grid_columnconfigure(i, weight=1)

    Label(filtro_frame, text="Nombre").grid(row=0, column=0, pady=5, padx=5)
    global filtro_nombre
    filtro_nombre = Entry(filtro_frame)
    filtro_nombre.grid(row=0, column=1, pady=5, padx=5)
    filtro_nombre.bind("<Return>", aplicar_filtro_evento)
    
    Label(filtro_frame, text="Categoría").grid(row=0, column=2, pady=5, padx=5)
    global filtro_categoria
    filtro_categoria = StringVar(filtro_frame)
    filtro_categoria.set("Todas")
    categorias = ["Todas", "Todas", "Indumentaria", "Accesorios", "Remeras", "Pantalones", "Abrigos"]
    ttk.OptionMenu(filtro_frame, filtro_categoria, *categorias).grid(row=0, column=3, pady=5, padx=5)
    
    Label(filtro_frame, text="Precio Mínimo").grid(row=0, column=4, pady=5, padx=5)
    global filtro_precio_min
    filtro_precio_min = Entry(filtro_frame)
    filtro_precio_min.grid(row=0, column=5, pady=5, padx=5)
    filtro_precio_min.bind("<Return>", aplicar_filtro_evento)
    
    Label(filtro_frame, text="Precio Máximo").grid(row=0, column=6, pady=5, padx=5)
    global filtro_precio_max
    filtro_precio_max = Entry(filtro_frame)
    filtro_precio_max.grid(row=0, column=7, pady=5, padx=5)
    filtro_precio_max.bind("<Return>", aplicar_filtro_evento)

    Label(filtro_frame, text="Disciplina").grid(row=0, column=8, pady=5, padx=5)
    global filtro_disciplina
    filtro_disciplina = StringVar(filtro_frame)
    filtro_disciplina.set("Todas")
    disciplinas = ["Todas", "Todas" ,"Fútbol", "Básquet", "Tenis", "Natación", "Running", "Boxeo", "Vóley", "Rugby", "Hockey", "Yoga", "Fitness", "Musculación"]
    ttk.OptionMenu(filtro_frame, filtro_disciplina, *disciplinas).grid(row=0, column=9, pady=5, padx=5)

    Label(filtro_frame, text="Género").grid(row=0, column=10, pady=5, padx=5)
    global filtro_genero
    filtro_genero = StringVar(filtro_frame)
    filtro_genero.set("Todos")
    generos = ["Todos", "Todos","Femenino", "Masculino", "Niño", "Niña", "Unisex", "No"]
    ttk.OptionMenu(filtro_frame, filtro_genero, *generos).grid(row=0, column=11, pady=5, padx=5)

    Button(filtro_frame, text="Seleccionar Todos", command=seleccionar_todos).grid(row=1, column=0, padx=5, pady=5)
    Button(filtro_frame, text="Deseleccionar Todos", command=deseleccionar_todos).grid(row=1, column=1, padx=5, pady=5)
    Button(filtro_frame, text="Actualizar Precios Seleccionados", command=actualizar_precios_seleccionados).grid(row=1, column=2, padx=5, pady=5)
    Button(filtro_frame, text="Actualizar Stock Seleccionados", command=actualizar_stock_seleccionados).grid(row=1, column=3, padx=5, pady=5)
    aplicar_filtro(ver_frame, productos)

def aplicar_filtro(ver_frame, productos):
    nombre = filtro_nombre.get()
    categoria = filtro_categoria.get()
    precio_min = filtro_precio_min.get()
    precio_max = filtro_precio_max.get()
    disciplina = filtro_disciplina.get()
    genero = filtro_genero.get()
    
    if precio_min == "":
        precio_min = None
    if precio_max == "":
        precio_max = None
    
    productos_filtrados = filtrar_productos(productos, nombre, categoria, precio_min, precio_max, disciplina, genero)
    
    for widget in ver_frame.winfo_children():
        if widget != filtro_frame:
            widget.destroy()
    
    global productos_seleccionados
    productos_seleccionados = []

    productos_frame = Frame(ver_frame)
    productos_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
    productos_frame.grid_rowconfigure(0, weight=1)
    productos_frame.grid_columnconfigure(0, weight=1)

    canvas = Canvas(ver_frame)
    scrollbar = Scrollbar(ver_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas)
    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=1, column=0, sticky="nsew")
    scrollbar.grid(row=1, column=1, sticky="ns")

    ver_frame.grid_rowconfigure(1, weight=1)
    ver_frame.grid_columnconfigure(0, weight=1)

    for i, producto in enumerate(productos_filtrados):

        frame = Frame(scrollable_frame, borderwidth=2, relief="groove")
        frame.grid(row=i//5, column=i%5, padx=5, pady=5, sticky="nsew")

        select_frame = Frame(frame)
        select_frame.pack(anchor='nw')
        Label(select_frame, text="Seleccionar").pack(side='left')
        var = BooleanVar()
        Checkbutton(select_frame, variable=var).pack(side='right')
        productos_seleccionados.append((producto, var))
        
        Label(frame, text=f"Nombre: {producto['titulo']}").pack(anchor='w')
        Label(frame, text=f"Categoría: {producto['categoria']['nombre']}").pack(anchor='w')
        Label(frame, text=f"Precio: {producto['precio']}").pack(anchor='w')
        color_frame = Frame(frame)
        color_frame.pack(anchor='w')
        Label(color_frame, text="Color:").pack(side='left')
        Label(frame, text=f"Stock: {producto['stock']}").pack(anchor='w')
        color_hex = color_hex_map.get(producto['color'], "#FFFFFF")
        Label(color_frame, text=producto['color'], bg=color_hex).pack(side='left')
        
        mostrar_imagen_producto(frame, producto['imagen'])
        
        Button(frame, text="Modificar", command=lambda p=producto: modificar_producto(p, ver_frame)).pack(side='left', padx=5)
        Button(frame, text="Eliminar", command=lambda p=producto: eliminar_producto(p, ver_frame)).pack(side='left', padx=5)
        Button(frame, text="Actualizar Stock", command=lambda p=producto: actualizar_stock(p, ver_frame)).pack(side='left', padx=5)

def seleccionar_todos():
	for producto, var in productos_seleccionados:
		var.set(True)

def deseleccionar_todos():
	for producto, var in productos_seleccionados:
		var.set(False)

def actualizar_stock_seleccionados():
	actualizar_frame = Toplevel(tk)
	actualizar_frame.title("Actualizar Stock Seleccionados")

	Label(actualizar_frame, text="Cantidad stock agregado").pack()
	entry_cantidad = Entry(actualizar_frame)
	entry_cantidad.pack()

	productos_frame = Frame(actualizar_frame)
	productos_frame.pack(fill='both', expand=True)

	for producto, var in productos_seleccionados:
		if var.get():
			frame = Frame(productos_frame, borderwidth=2, relief="groove")
			frame.pack(fill='x', padx=5, pady=5)
			Label(frame, text=f"Nombre: {producto['titulo']}").pack(anchor='w')
			Label(frame, text=f"Categoría: {producto['categoria']['nombre']}").pack(anchor='w')
			Label(frame, text=f"Stock Actual: {producto.get('stock', 0)}").pack(anchor='w')
			mostrar_imagen_producto(frame, producto['imagen'])

	def aplicar_ajuste():
		cantidad = entry_cantidad.get()
		if cantidad:
			try:
				cantidad = int(cantidad)
				for producto, var in productos_seleccionados:
					if var.get():
						producto['stock'] = producto.get('stock', 0) + cantidad
				with open('html/JS/productos.json', 'w') as archivo:
					json.dump(productos, archivo, indent=2)
				messagebox.showinfo("Información", "Stock actualizado correctamente.")
				actualizar_frame.destroy()
				ver_frame.destroy()
				ver_productos()
			except ValueError:
				messagebox.showerror("Error", "Por favor, ingrese un valor numérico válido.")

	Button(actualizar_frame, text="Actualizar", command=aplicar_ajuste).pack()


def actualizar_precios_seleccionados():
	actualizar_frame = Toplevel(tk)
	actualizar_frame.title("Actualizar Precios Seleccionados")

	Label(actualizar_frame, text="Tipo de Actualización").pack()
	tipo_actualizacion = StringVar(value="porcentaje")
	Radiobutton(actualizar_frame, text="Porcentaje", variable=tipo_actualizacion, value="porcentaje").pack(anchor='w')
	Radiobutton(actualizar_frame, text="Monto", variable=tipo_actualizacion, value="monto").pack(anchor='w')

	Label(actualizar_frame, text="Valor").pack()
	entry_valor = Entry(actualizar_frame)
	entry_valor.pack()

	def aplicar_actualizacion():
		valor = entry_valor.get()
		if valor:
			try:
				valor = float(valor)
				for producto, var in productos_seleccionados:
					if var.get():
						if tipo_actualizacion.get() == "porcentaje":
							producto['precio'] = str(float(producto['precio']) * (1 + valor / 100))
						elif tipo_actualizacion.get() == "monto":
							producto['precio'] = str(float(producto['precio']) + valor)
				with open('html/JS/productos.json', 'w') as archivo:
					json.dump(productos, archivo, indent=2)
				messagebox.showinfo("Información", "Precios actualizados correctamente.")
				actualizar_frame.destroy()
				ver_frame.destroy()
				ver_productos()
			except ValueError:
				messagebox.showerror("Error", "Por favor, ingrese un valor numérico válido.")

	Button(actualizar_frame, text="Actualizar", command=aplicar_actualizacion).pack()


def modificar_producto(producto, parent_frame):
	modificar_frame = Toplevel(tk)
	modificar_frame.title("Modificar Producto")
	style = ttk.Style(modificar_frame)
	style.configure("Placeholder.TEntry", foreground="#d5d5d5")
		
	Label(modificar_frame, text="Nombre Producto").pack()
	entry_nombre = PlaceholderEntry(modificar_frame, placeholder=producto['titulo'])
	entry_nombre.pack()

	Label(modificar_frame, text="Nuevo Precio").pack()
	entry_precio = PlaceholderEntry(modificar_frame, placeholder=producto['precio'])
	entry_precio.pack()

	def guardar_cambios():
		producto['titulo'] = entry_nombre.get()
		producto['precio'] = entry_precio.get()
		
		with open('html/JS/productos.json', 'r') as archivo:
			productos = json.load(archivo)
		
		for i, p in enumerate(productos):
			if p['id'] == producto['id']:
				productos[i] = producto
				break
		
		with open('html/JS/productos.json', 'w') as archivo:
			json.dump(productos, archivo, indent=2)
		
		modificar_frame.destroy()
		parent_frame.destroy()
		ver_productos()
		
	Button(modificar_frame, text="Guardar Cambios", command=guardar_cambios).pack()

def eliminar_producto(producto, parent_frame):
	respuesta = messagebox.askyesno("Eliminar Producto", "¿Está seguro de que desea eliminar este producto?")
	if respuesta:
		with open('html/JS/productos.json', 'r') as archivo:
			productos = json.load(archivo)
		
		productos = [p for p in productos if p['id'] != producto['id']]
		
		with open('html/JS/productos.json', 'w') as archivo:
			json.dump(productos, archivo, indent=2)
		
		parent_frame.destroy()
		ver_productos()

def actualizar_stock(producto, parent_frame):
	actualizar_frame = Toplevel(tk)
	actualizar_frame.title("Actualizar Stock")

	Label(actualizar_frame, text=f"Producto: {producto['titulo']}").pack()
	Label(actualizar_frame, text=f"Stock Actual: {producto.get('stock', 0)}").pack()

	Label(actualizar_frame, text="Cantidad stock agregado").pack()
	entry_cantidad = Entry(actualizar_frame)
	entry_cantidad.pack()

	def aplicar_ajuste():
		cantidad = entry_cantidad.get()
		if cantidad:
			try:
				cantidad = int(cantidad)
				producto['stock'] = producto.get('stock', 0) + cantidad
				with open('html/JS/productos.json', 'w') as archivo:
					json.dump(productos, archivo, indent=2)
				messagebox.showinfo("Información", "Stock actualizado correctamente.")
				actualizar_frame.destroy()
			except ValueError:
				messagebox.showerror("Error", "Por favor, ingrese un valor numérico válido.")
		
		actualizar_frame.destroy()
		parent_frame.destroy()
		ver_productos()


	Button(actualizar_frame, text="Ajustar Stock", command=aplicar_ajuste).pack()

class PlaceholderEntry(ttk.Entry):
	def __init__(self, container, placeholder, *args, **kwargs):
		super().__init__(container, *args, style="Placeholder.TEntry", **kwargs)
		self.placeholder = placeholder
		self.insert("0", self.placeholder)
		self.bind("<FocusIn>", self._clear_placeholder)
		self.bind("<FocusOut>", self._add_placeholder)

	def _clear_placeholder(self, e):
		if self["style"] == "Placeholder.TEntry":
			self.delete("0", "end")
			self["style"] = "TEntry"

	def _add_placeholder(self, e):
		if not self.get():
			self.insert("0", self.placeholder)
			self["style"] = "Placeholder.TEntry"

def ingresar_nuevo_producto():
	global image_label, color_label, variable_unidad, Entry_1, Entry_3, var_es_variante, variable_gen, listbox_talles, entry_codigo_barras, variable_disciplina

	nuevo_producto_frame = Toplevel(tk)
	nuevo_producto_frame.title("Ingresar Nuevo Producto")

	ttk.Label(nuevo_producto_frame, text="Nombre Producto").pack()
	Entry_1 = ttk.Entry(nuevo_producto_frame)
	Entry_1.pack()

	button = ttk.Button(nuevo_producto_frame, text="Seleccionar Imagen", command=select_image)
	button.pack(pady=10)
	image_label = Label(nuevo_producto_frame)
	image_label.pack()
	image_label.bind("<Button-1>", get_color)

	opciones_unidades = [
		"Categoria Producto", "Remeras", "Abrigos", "Pantalones",
		"Accesorios"
	]
	variable_unidad = StringVar(nuevo_producto_frame)
	variable_unidad.set(opciones_unidades[0])
	ttk.OptionMenu(nuevo_producto_frame, variable_unidad, *opciones_unidades).pack()

	Label(nuevo_producto_frame, text="Precio").pack()
	Entry_3 = ttk.Entry(nuevo_producto_frame)
	Entry_3.pack()

	opciones_gen = ["Género", "Femenino", "Masculino", "Niño", "Niña", "Unisex" ,"No"]
	variable_gen = StringVar(nuevo_producto_frame)
	variable_gen.set(opciones_gen[0]) 
	ttk.OptionMenu(nuevo_producto_frame, variable_gen, *opciones_gen).pack()

	Label(nuevo_producto_frame, text="Talles").pack()
	talles = ["No","S", "M", "L", "XL"]
	listbox_talles = Listbox(nuevo_producto_frame, selectmode=MULTIPLE, height=len(talles))
	for talle in talles:
		listbox_talles.insert(END, talle)
	listbox_talles.pack()

	Label(nuevo_producto_frame, text="Disciplina").pack()
	opciones_disciplinas = ["Deportes", "Fútbol", "Básquet", "Tenis", "Natación", "Running", "Boxeo", "Vóley", "Rugby", "Hockey", "Yoga", "Fitness", "Musculación"]
	variable_disciplina = StringVar(nuevo_producto_frame)
	variable_disciplina.set(opciones_disciplinas[0])
	ttk.OptionMenu(nuevo_producto_frame, variable_disciplina, *opciones_disciplinas).pack()

	color_label = Label(nuevo_producto_frame, text="Color", bg="white", width=20)
	color_label.pack(pady=5)

	var_es_variante = BooleanVar()
	ttk.Checkbutton(nuevo_producto_frame, text="Es variante de otro producto", variable=var_es_variante).pack()

	ttk.Label(nuevo_producto_frame, text="Código de Barras").pack()
	entry_codigo_barras = ttk.Entry(nuevo_producto_frame)
	entry_codigo_barras.pack()
	entry_codigo_barras.bind("<Return>", lambda event: procesar_codigo_barras(entry_codigo_barras.get()))

	ttk.Button(nuevo_producto_frame, text="Guardar", command=guardar).pack()

def set_background_image(frame, image_path):
	img = Image.open(image_path)
	photo = ImageTk.PhotoImage(img)
	background_label = Label(frame, image=photo)
	background_label.image = photo  # Keep a reference to avoid garbage collection
	background_label.place(x=0, y=0, relwidth=1, relheight=1)


def procesar_codigo_barras(codigo_barras, venta_frame):
	try:
		with open('html/JS/productos.json', 'r') as archivo:
			productos = json.load(archivo)
	except FileNotFoundError:
		productos = []

	producto_encontrado = None
	for producto in productos:
		if producto['codigo_barras'] == codigo_barras:
			producto_encontrado = producto
			break

	if producto_encontrado:
		if modo_venta.get():
			if producto_encontrado['stock'] > 0:
				producto_encontrado['stock'] -= 1
				with open('html/JS/productos.json', 'w') as archivo:
					json.dump(productos, archivo, indent=2)
				messagebox.showinfo("Información", f"Producto vendido: {producto_encontrado['titulo']}. Stock restante: {producto_encontrado['stock']}")
				venta_frame.destroy()
				toggle_modo_venta()
			else:
				messagebox.showerror("Error", f"No hay stock disponible del producto: {producto_encontrado['titulo']}")
		else:
			actualizar_stock(producto_encontrado)
	else:
		if modo_venta.get():
			respuesta = messagebox.askyesno("Producto no encontrado", "El producto no está cargado. ¿Desea cargarlo?")
			if respuesta:
				ingresar_nuevo_producto()
		else:
			messagebox.showerror("Error", "Producto no encontrado.")

def toggle_modo_venta(venta_frame=None):
	if modo_venta.get():
		venta_frame = Toplevel(tk)
		venta_frame.title("Modo Venta")

		Label(venta_frame, text="Ingrese Código de Barras").pack()
		entry_codigo_barras_venta = Entry(venta_frame)
		entry_codigo_barras_venta.pack()
		entry_codigo_barras_venta.bind("<Return>", lambda event: procesar_codigo_barras(entry_codigo_barras_venta.get(), venta_frame))


tk = Tk()
tk.geometry(f"{tk.winfo_screenwidth()}x{tk.winfo_screenheight()}")
style = ttk.Style()
style.configure("Placeholder.TEntry", foreground="#d5d5d5")

set_background_image(tk, "html/img/287290_5.jpg")

menubar = Menu(tk)
tk.config(menu=menubar)

productos_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Productos", menu=productos_menu)
productos_menu.add_command(label="Ingresar Nuevo Producto", command=ingresar_nuevo_producto)
productos_menu.add_command(label="Ver Productos", command=ver_productos)


# Agregar checkbox para Modo Venta
modo_venta = BooleanVar()
ttk.Checkbutton(tk, text="Modo Venta", variable=modo_venta, command=toggle_modo_venta).pack()

tk.mainloop()

