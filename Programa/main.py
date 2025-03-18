#que se pueda seleccionar mas de un talle por producto


import json
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os

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

def get_color(event):
	x, y = event.x, y = event.y
	if img:
		rgb = img.getpixel((x, y))
		color_code = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
		color_label.config(bg=color_code)
		return color_code
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
		"precio": precio,
		"es_variante": es_variante,
		"genero": genero,
		"talles": talles,
		"color": color_label.cget("bg"),
		"stock": 0  # Inicializar el stock a 0
	}
	
	productos.append(producto)
	
	with open('html/JS/productos.json', 'w') as archivo:
		json.dump(productos, archivo, indent=2)

	reset_image()
	color_label.config(bg="white")
	
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
	talles = [listbox_talles.get(i) for i in listbox_talles.curselection()],
	
	try:
		with open('html/JS/productos.json', 'r') as archivo:
			productos = json.load(archivo)
	except FileNotFoundError:
		productos = []
	
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
		"precio": precio,
		"es_variante": True,
		"genero": variable_gen.get(),
		"talle": talles,
		"color": color
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

def filtrar_productos(productos, nombre=None,categoria=None, precio_min=None, precio_max=None):
	filtrados = productos
	if nombre:
		filtrados = [p for p in filtrados if nombre.lower() in p['titulo'].lower()]
	if categoria:
		filtrados = [p for p in filtrados if categoria.lower() in p['categoria']['nombre'].lower()]
	if precio_min is not None:
		filtrados = [p for p in filtrados if float(p['precio']) >= float(precio_min)]
	if precio_max is not None:
		filtrados = [p for p in filtrados if float(p['precio']) <= float(precio_max)]
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

	for i in range(filtro_frame.grid_size()[0]):
		filtro_frame.grid_columnconfigure(i, weight=1)

	Label(filtro_frame, text="Nombre").grid(row=0, column=0, pady=5)
	global filtro_nombre
	filtro_nombre = Entry(filtro_frame)
	filtro_nombre.grid(row=0, column=1, pady=5)
	filtro_nombre.bind("<Return>", aplicar_filtro_evento)
	
	Label(filtro_frame, text="Categoría").grid(row=0, column=2, pady=5)
	global filtro_categoria
	filtro_categoria = Entry(filtro_frame)
	filtro_categoria.grid(row=0, column=3, pady=5)
	filtro_categoria.bind("<Return>", aplicar_filtro_evento)
	
	Label(filtro_frame, text="Precio Mínimo").grid(row=0, column=4, pady=5)
	global filtro_precio_min
	filtro_precio_min = Entry(filtro_frame)
	filtro_precio_min.grid(row=0, column=5, pady=5)
	filtro_precio_min.bind("<Return>", aplicar_filtro_evento)
	
	Label(filtro_frame, text="Precio Máximo").grid(row=0, column=6, pady=5)
	global filtro_precio_max
	filtro_precio_max = Entry(filtro_frame)
	filtro_precio_max.grid(row=0, column=7, pady=5)
	filtro_precio_max.bind("<Return>", aplicar_filtro_evento)

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
	
	if precio_min == "":
		precio_min = None
	if precio_max == "":
		precio_max = None
	
	productos_filtrados = filtrar_productos(productos,nombre ,categoria, precio_min, precio_max)
	
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
		Label(color_frame, text=producto['color'], bg=producto['color']).pack(side='left')
		
		mostrar_imagen_producto(frame, producto['imagen'])
		
		Button(frame, text="Modificar", command=lambda p=producto: modificar_producto(p, ver_frame)).pack(side='left', padx=5)
		Button(frame, text="Eliminar", command=lambda p=producto: eliminar_producto(p, ver_frame)).pack(side='left', padx=5)
		Button(frame, text="Actualizar Stock", command=lambda p=producto: actualizar_stock(p,ver_frame)).pack(side='left', padx=5)




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

def procesar_codigo_barras(codigo_barras):
	try:
		with open('html/JS/productos.json', 'r') as archivo:
			productos = json.load(archivo)
	except FileNotFoundError:
		productos = []

	producto_encontrado = None
	for producto in productos:
		if producto['id'] == codigo_barras:
			producto_encontrado = producto
			break

	if producto_encontrado:
		actualizar_stock(producto_encontrado)
	else:
		messagebox.showerror("Error", "Producto no encontrado.")

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
	global image_label, color_label, variable_unidad, Entry_1, Entry_3, var_es_variante, variable_gen, listbox_talles, entry_codigo_barras

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
		"Categoria Producto", "Remeras", "Buzos", "Pantalones",
		"Accesorios"
	]
	variable_unidad = StringVar(nuevo_producto_frame)
	variable_unidad.set(opciones_unidades[0])
	ttk.OptionMenu(nuevo_producto_frame, variable_unidad, *opciones_unidades).pack()

	Label(nuevo_producto_frame, text="Precio").pack()
	Entry_3 = ttk.Entry(nuevo_producto_frame)
	Entry_3.pack()

	opciones_gen = ["Género", "Femenino", "Masculino", "No"]
	variable_gen = StringVar(nuevo_producto_frame)
	variable_gen.set(opciones_gen[0])
	ttk.OptionMenu(nuevo_producto_frame, variable_gen, *opciones_gen).pack()

	Label(nuevo_producto_frame, text="Talles").pack()
	listbox_talles = Listbox(nuevo_producto_frame, selectmode=MULTIPLE)
	talles = ["S", "M", "L", "XL"]
	for talle in talles:
		listbox_talles.insert(END, talle)
	listbox_talles.pack()

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

tk.mainloop()