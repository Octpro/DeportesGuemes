#tendria que poner una manera de actualizar los precios de un tipo de productos mediante porcentaje
#tendria que poner un buscardor en el ver productos
#tendria que poner un filtro en el ver productos

#tendria q poner un menubar para meter todo de los precios y los productos

import json
from tkinter import *
from tkinter import filedialog, messagebox
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
	x, y = event.x, event.y
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
	
	try:
		with open('html/JS/productos.json', 'r') as archivo:
			productos = json.load(archivo)
	except FileNotFoundError:
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

def filtrar_productos(productos, categoria=None, precio_min=None, precio_max=None):
	filtrados = productos
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
	ver_frame.title("Ver Productos")
	
	global filtro_frame
	filtro_frame = Frame(ver_frame)
	filtro_frame.pack(fill='x', pady=5)
	
	Label(filtro_frame, text="Categoría").grid(row=0, column=0, padx=5, pady=5)
	global filtro_categoria
	filtro_categoria = Entry(filtro_frame)
	filtro_categoria.grid(row=0, column=1, padx=5, pady=5)
	filtro_categoria.bind("<Return>", aplicar_filtro_evento)
	
	Label(filtro_frame, text="Precio Mínimo").grid(row=0, column=2, padx=5, pady=5)
	global filtro_precio_min
	filtro_precio_min = Entry(filtro_frame)
	filtro_precio_min.grid(row=0, column=3, padx=5, pady=5)
	filtro_precio_min.bind("<Return>", aplicar_filtro_evento)
	
	Label(filtro_frame, text="Precio Máximo").grid(row=0, column=4, padx=5, pady=5)
	global filtro_precio_max
	filtro_precio_max = Entry(filtro_frame)
	filtro_precio_max.grid(row=0, column=5, padx=5, pady=5)
	filtro_precio_max.bind("<Return>", aplicar_filtro_evento)
	
	Button(filtro_frame, text="Aplicar Filtro", command=lambda: aplicar_filtro(ver_frame, productos)).grid(row=0, column=6, padx=5, pady=5)
	
	aplicar_filtro(ver_frame, productos)

def aplicar_filtro(ver_frame, productos):
	categoria = filtro_categoria.get()
	precio_min = filtro_precio_min.get()
	precio_max = filtro_precio_max.get()
	
	if precio_min == "":
		precio_min = None
	if precio_max == "":
		precio_max = None
	
	productos_filtrados = filtrar_productos(productos, categoria, precio_min, precio_max)
	
	for widget in ver_frame.winfo_children():
		if widget != filtro_frame:
			widget.destroy()
	
	global productos_seleccionados
	productos_seleccionados = []
	
	productos_frame = Frame(ver_frame)
	productos_frame.pack(fill='both', expand=True)
	
	for i, producto in enumerate(productos_filtrados):
		frame = Frame(productos_frame, borderwidth=2, relief="groove")
		frame.grid(row=i//3, column=i%3, padx=5, pady=5, sticky="nsew")
		
		select_frame = Frame(frame)
		select_frame.pack(anchor='w')
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
		Button(frame, text="Actualizar Precio", command=lambda p=producto: actualizar_precio_producto(p)).pack(side='left', padx=5)
		Button(frame, text="Actualizar Stock", command=lambda p=producto: actualizar_stock(p)).pack(side='left', padx=5)
	
	Button(ver_frame, text="Seleccionar Todos", command=seleccionar_todos).pack(side='left', padx=5, pady=10)
	Button(ver_frame, text="Deseleccionar Todos", command=deseleccionar_todos).pack(side='left', padx=5, pady=10)
	Button(ver_frame, text="Actualizar Precios Seleccionados", command=actualizar_precios_seleccionados).pack(pady=10)

def seleccionar_todos():
	for producto, var in productos_seleccionados:
		var.set(True)

def deseleccionar_todos():
	for producto, var in productos_seleccionados:
		var.set(False)

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

def actualizar_precio_producto(producto):
	actualizar_frame = Toplevel(tk)
	actualizar_frame.title("Actualizar Precio")

	Label(actualizar_frame, text="Nombre Producto").pack()
	Label(actualizar_frame, text=producto['titulo']).pack()

	Label(actualizar_frame, text="Precio Actual").pack()
	Label(actualizar_frame, text=producto['precio']).pack()

	Label(actualizar_frame, text="Nuevo Precio").pack()
	entry_precio = Entry(actualizar_frame)
	entry_precio.pack()

	def aplicar_actualizacion():
		nuevo_precio = entry_precio.get()
		if nuevo_precio:
			producto['precio'] = nuevo_precio
			with open('html/JS/productos.json', 'r') as archivo:
				productos = json.load(archivo)
			for i, p in enumerate(productos):
				if p['id'] == producto['id']:
					productos[i] = producto
					break
			with open('html/JS/productos.json', 'w') as archivo:
				json.dump(productos, archivo, indent=2)
			messagebox.showinfo("Información", "Precio actualizado correctamente.")
			actualizar_frame.destroy()
			ver_frame.destroy()
			ver_productos()

	Button(actualizar_frame, text="Actualizar", command=aplicar_actualizacion).pack()
def modificar_producto(producto, parent_frame):
	modificar_frame = Toplevel(tk)
	modificar_frame.title("Modificar Producto")
	
	Label(modificar_frame, text="Nombre Producto").pack()
	entry_nombre = Entry(modificar_frame)
	entry_nombre.pack()
	entry_nombre.insert(0, producto['titulo'])
	
	Label(modificar_frame, text="Precio").pack()
	entry_precio = Entry(modificar_frame)
	entry_precio.pack()
	entry_precio.insert(0, producto['precio'])
	
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

def actualizar_stock(producto):
    actualizar_frame = Toplevel(tk)
    actualizar_frame.title("Actualizar Stock")

    Label(actualizar_frame, text=f"Producto: {producto['titulo']}").pack()
    Label(actualizar_frame, text=f"Stock Actual: {producto.get('stock', 0)}").pack()

    Label(actualizar_frame, text="Cantidad a Ajustar").pack()
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

tk = Tk()

Label(tk, text="Nombre Producto").pack()
Entry_1 = Entry(tk)
Entry_1.pack()

button = Button(tk, text="Seleccionar Imagen", command=select_image)
button.pack(pady=10)
image_label = Label(tk)
image_label.pack()
image_label.bind("<Button-1>", get_color)

Label(tk, text="Categoria Producto").pack()
opciones_unidades = [
	"Remeras", "Buzos", "Pantalones",
	"Accesorios"
]
variable_unidad = StringVar(tk)
variable_unidad.set(opciones_unidades[0])
OptionMenu(tk, variable_unidad, *opciones_unidades).pack()

Label(tk, text="Precio").pack()
Entry_3 = Entry(tk)
Entry_3.pack()

var_es_variante = BooleanVar()
Checkbutton(tk, text="Es variante de otro producto", variable=var_es_variante).pack()

color_label = Label(tk, text="Color", bg="white", width=20)
color_label.pack(pady=5)

Label(tk, text="Código de Barras").pack()
entry_codigo_barras = Entry(tk)
entry_codigo_barras.pack()
entry_codigo_barras.bind("<Return>", lambda event: procesar_codigo_barras(entry_codigo_barras.get()))

menubar = Menu(tk)
tk.config(menu=menubar)

productos_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Productos", menu=productos_menu)
productos_menu.add_command(label="Ver Productos", command=ver_productos)

Button(tk, text="Guardar", command=guardar).pack()

tk.mainloop()