const color_hex_map = {
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
};

// Modificar la carga inicial de productos
let productos = [];

fetch('JS/productos.json')
    .then(response => response.json())
    .then(data => {
        productos = data;
        cargarProductos(productos); // Cargar productos inmediatamente después de obtenerlos
    })
    .catch(error => console.error('Error:', error));

const contenedorProductos = document.querySelector("#contenedor-productos");
const botonesCategoria = document.querySelectorAll(".boton-categoria");
const tituloPrincipal = document.querySelector("#titulo-principal");
const numerito = document.querySelector("#numerito");

let productosEnCarrito = [];
let productosEnCarritoLS = localStorage.getItem("productos-en-carrito");

if (productosEnCarritoLS) {
    productosEnCarrito = JSON.parse(productosEnCarritoLS);
    actualizarNumerito();
}

function mostrarProductos(productos) {
    contenedorProductos.innerHTML = '';

    productos.forEach(producto => {
        if (!producto.es_variante) { // Solo mostrar productos principales
            const div = document.createElement('div');
            div.classList.add('producto');
            const idSanitizado = producto.id.replace(/[^a-zA-Z0-9-_]/g, '_');
            
            // Buscar la primera variante con stock si el producto principal no tiene stock
            let productoAMostrar = producto;
            if (producto.stock === 0) {
                const primeraVarianteConStock = productos.find(p => p.titulo === producto.titulo && p.es_variante && p.stock > 0);
                if (primeraVarianteConStock) {
                    productoAMostrar = primeraVarianteConStock;
                }
            }

            div.innerHTML = `
            <img class="producto-img" src="${productoAMostrar.imagen}" alt="${productoAMostrar.titulo}">
            <div class="producto-detalles">
                <h3 class="producto-titulo">${productoAMostrar.titulo}</h3>
                <p class="producto-precio">$${productoAMostrar.precio}</p>
                <p class="producto-talles">Talles: ${productoAMostrar.talles ? productoAMostrar.talles.join(', ') : 'No disponible'}</p>
                <select class="producto-variantes" id="variantes-${idSanitizado}">
                    <option value="${productoAMostrar.id}" style="background-color: ${color_hex_map[productoAMostrar.color]}; color: white;" selected>${productoAMostrar.color}</option>
                </select>
                <button class="producto-consultar" id="${productoAMostrar.id}" ${productoAMostrar.stock === 0 ? 'disabled' : ''}>Consultar</button>
            </div>
            `;
            contenedorProductos.append(div);

            const select = div.querySelector(`#variantes-${idSanitizado}`);
            const variantes = productos.filter(p => p.titulo === producto.titulo && p.es_variante);

            if (variantes.length > 0) {
                variantes.forEach(variante => {
                    const option = document.createElement('option');
                    option.value = variante.id;
                    option.text = variante.color;
                    option.style.backgroundColor = color_hex_map[variante.color];
                    option.style.color = 'white';
                    if (variante.stock === 0) {
                        option.disabled = true;
                    }
                    select.append(option);
                });

                select.addEventListener('change', (e) => {
                    const varianteSeleccionada = productos.find(p => p.id === e.target.value);
                    if (varianteSeleccionada) {
                        div.querySelector('.producto-img').src = varianteSeleccionada.imagen;
                        div.querySelector('.producto-precio').innerText = `$${varianteSeleccionada.precio}`;
                        div.querySelector('.producto-talles').innerText = `Talles: ${varianteSeleccionada.talles ? varianteSeleccionada.talles.join(', ') : 'No disponible'}`;
                        div.querySelector('.producto-consultar').id = varianteSeleccionada.id;
                        div.querySelector('.producto-consultar').disabled = varianteSeleccionada.stock === 0;
                        select.style.backgroundColor = color_hex_map[varianteSeleccionada.color];
                    } 
                });

                select.style.backgroundColor = color_hex_map[productoAMostrar.color];
            } else {
                select.style.display = 'none';
            }

            // Si el producto no tiene stock, añadir clase para estilo gris y deshabilitar botón
            if (productoAMostrar.stock === 0) {
                div.classList.add('sin-stock');
                div.querySelector('.producto-consultar').disabled = true;
            }
        }
    });
    actualizarBotonesAgregar();
}

function actualizarBotonesAgregar() {
    const botonesAgregar = document.querySelectorAll('.producto-consultar');
    botonesAgregar.forEach(boton => {
        boton.addEventListener('click', (e) => {
            const idProducto = e.target.id;
            agregarAlCarrito(idProducto);
        });
    });
}

function agregarAlCarrito(idProducto) {
    Toastify({
        text: "Producto agregado",
        duration: 3000,
        close: true,
        gravity: "top", // `top` or `bottom`
        position: "right", // `left`, `center` or `right`
        stopOnFocus: true, // Prevents dismissing of toast on hover
        style: {
            background: "linear-gradient(to right, #141eaa, #6749e0)",
            borderRadius: "1rem",
            textTransform: "uppercase",
            fontSize: ".75rem"
        },
        offset: {
            x: "1.5rem",
            y: "1.5rem"
        },
        onClick: function () { } // Callback after click
    }).showToast();

    const productoAgregado = productos.find(producto => producto.id === idProducto);

    if (productosEnCarrito.some(producto => producto.id === idProducto)) {
        const index = productosEnCarrito.findIndex(producto => producto.id === idProducto);
        productosEnCarrito[index].cantidad++;
    } else {
        productoAgregado.cantidad = 1;
        productosEnCarrito.push(productoAgregado);
    }
    actualizarNumerito();

    localStorage.setItem("productos-en-carrito", JSON.stringify(productosEnCarrito));
}

function actualizarNumerito() {
    let nuevoNumerito = productosEnCarrito.reduce((acc, producto) => acc + producto.cantidad, 0);
    numerito.innerText = nuevoNumerito;
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('toggle-filtros').addEventListener('click', function() {
        const filtros = document.getElementById('filtros');
        if (filtros.classList.contains('filtros-ocultos')) {
            filtros.classList.remove('filtros-ocultos');
            filtros.classList.add('filtros-mostrados');
        } else {
            filtros.classList.remove('filtros-mostrados');
            filtros.classList.add('filtros-ocultos');
        }
    });

    // Close the filters when clicking outside of the filters area
    document.addEventListener('click', function(event) {
        const filtros = document.getElementById('filtros');
        const toggleFiltros = document.getElementById('toggle-filtros');
        if (!filtros.contains(event.target) && !toggleFiltros.contains(event.target)) {
            filtros.classList.remove('filtros-mostrados');
            filtros.classList.add('filtros-ocultos');
        }
    });

    document.getElementById('aplicar-filtro').addEventListener('click', aplicarFiltro);

    const filtros = document.querySelectorAll('#filtro-nombre, #filtro-categoria, #filtro-precio-min, #filtro-precio-max, #filtro-genero, #filtro-talle, #filtro-disciplina');
    filtros.forEach(filtro => {
        filtro.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                aplicarFiltro();
            }
        });
    });

    // Asegurarse de que los productos se carguen cuando se cambia de categoría
    botonesCategoria.forEach(boton => {
        boton.addEventListener("click", (e) => {
            botonesCategoria.forEach(boton => boton.classList.remove("active"));
            e.currentTarget.classList.add("active");

            if (e.currentTarget.id !== "todos") {
                const productosBoton = productos.filter(producto => {
                    if (e.currentTarget.id === "indumentaria") {
                        return producto.categoria_general === "indumentaria";
                    } else if (e.currentTarget.id === "accesorios") {
                        return producto.categoria_general === "accesorios";
                    } else {
                        return producto.categoria.id === e.currentTarget.id;
                    }
                });

                tituloPrincipal.innerText = productosBoton.length > 0 
                    ? e.currentTarget.id.charAt(0).toUpperCase() + e.currentTarget.id.slice(1)
                    : "No hay productos";

                cargarProductos(productosBoton);
            } else {
                tituloPrincipal.innerText = "Todos los productos";
                cargarProductos(productos);
            }
        });
    });

    // Simular un clic en el botón "todos" para cargar todos los productos al inicio
    const botonTodos = document.querySelector("#todos");
    if (botonTodos) {
        botonTodos.click();
    }

    // Agregar eventos para los filtros de texto y número
    const filtroNombre = document.getElementById('filtro-nombre');
    const filtroPrecioMin = document.getElementById('filtro-precio-min');
    const filtroPrecioMax = document.getElementById('filtro-precio-max');
    const filtroTalle = document.getElementById('filtro-talle');

    // Función para manejar eventos de teclado
    const handleKeyEvent = (event) => {
        aplicarFiltro();
    };

    // Agregar eventos keyup para aplicar filtros automáticamente
    filtroNombre.addEventListener('keyup', handleKeyEvent);
    filtroPrecioMin.addEventListener('keyup', handleKeyEvent);
    filtroPrecioMax.addEventListener('keyup', handleKeyEvent);
    filtroTalle.addEventListener('keyup', handleKeyEvent);

    // Agregar eventos change para los selectores
    const filtroCategoria = document.getElementById('filtro-categoria');
    const filtroDisciplina = document.getElementById('filtro-disciplina');
    const filtroGenero = document.getElementById('filtro-genero');

    filtroCategoria.addEventListener('change', aplicarFiltro);
    filtroDisciplina.addEventListener('change', aplicarFiltro);
    filtroGenero.addEventListener('change', aplicarFiltro);
});

function aplicarFiltro() {
    const nombre = document.getElementById('filtro-nombre').value.toLowerCase();
    const categoria = document.getElementById('filtro-categoria').value.toLowerCase();
    const precioMin = parseFloat(document.getElementById('filtro-precio-min').value) || 0;
    const precioMax = parseFloat(document.getElementById('filtro-precio-max').value) || Infinity;
    const genero = document.getElementById('filtro-genero').value.toLowerCase();
    const talle = document.getElementById('filtro-talle').value.toLowerCase();
    const disciplina = document.getElementById('filtro-disciplina').value.toLowerCase();

    // Obtener la categoría seleccionada en la pestaña
    const categoriaSeleccionada = document.querySelector('.boton-categoria.active').id;

    const productosFiltrados = productos.filter(producto => {
        const nombreMatch = producto.titulo.toLowerCase().includes(nombre);
        const categoriaMatch = (categoriaSeleccionada === "todos" || 
            (categoriaSeleccionada === "indumentaria" && ["indumentaria", "remeras", "pantalones", "abrigos"].includes(producto.categoria_general)) ||
            producto.categoria_general === categoriaSeleccionada) &&
            (categoria === "" || producto.categoria.nombre.toLowerCase().includes(categoria));
        const precioMatch = producto.precio >= precioMin && producto.precio <= precioMax;
        const generoMatch = genero === "" || producto.genero.toLowerCase() === genero;
        const talleMatch = talle === "" || (producto.talles && producto.talles.map(t => t.toLowerCase()).includes(talle));
        const disciplinaMatch = disciplina === "" || producto.disciplina.toLowerCase() === disciplina;
        return nombreMatch && categoriaMatch && precioMatch && generoMatch && talleMatch && disciplinaMatch;
    });

    mostrarProductos(productosFiltrados);
}

function cargarProductos(productos) {
    const contenedorProductos = document.getElementById('contenedor-productos');
    contenedorProductos.innerHTML = '';

    productos.forEach(producto => {
        if (!producto.es_variante) { // Solo mostrar productos principales
            const div = document.createElement('div');
            div.classList.add('producto');
            const idSanitizado = producto.id.replace(/[^a-zA-Z0-9-_]/g, '_');
            
            // Buscar la primera variante con stock si el producto principal no tiene stock
            let productoAMostrar = producto;
            if (producto.stock === 0) {
                const primeraVarianteConStock = productos.find(p => p.titulo === producto.titulo && p.es_variante && p.stock > 0);
                if (primeraVarianteConStock) {
                    productoAMostrar = primeraVarianteConStock;
                }
            }

            div.innerHTML = `
            <img class="producto-img" src="${productoAMostrar.imagen}" alt="${productoAMostrar.titulo}">
            <div class="producto-detalles">
                <h3 class="producto-titulo">${productoAMostrar.titulo}</h3>
                <p class="producto-precio">$${productoAMostrar.precio}</p>
                <p class="producto-talles">Talles: ${productoAMostrar.talles ? productoAMostrar.talles.join(', ') : 'No disponible'}</p>
                <select class="producto-variantes" id="variantes-${idSanitizado}">
                    <option value="${productoAMostrar.id}" style="background-color: ${color_hex_map[productoAMostrar.color]}; color: white;" selected>${productoAMostrar.color}</option>
                </select>
                <button class="producto-consultar" id="${productoAMostrar.id}" ${productoAMostrar.stock === 0 ? 'disabled' : ''}>Consultar</button>
            </div>
            `;
            contenedorProductos.append(div);

            const select = div.querySelector(`#variantes-${idSanitizado}`);
            const variantes = productos.filter(p => p.titulo === producto.titulo && p.es_variante);

            variantes.forEach(variante => {
                const option = document.createElement('option');
                option.value = variante.id;
                option.text = variante.color;
                option.style.backgroundColor = color_hex_map[variante.color];
                option.style.color = 'white';
                if (variante.stock === 0) {
                    option.disabled = true;
                }
                select.append(option);
            });

            select.addEventListener('change', (e) => {
                const varianteSeleccionada = productos.find(p => p.id === e.target.value);
                if (varianteSeleccionada) {
                    div.querySelector('.producto-img').src = varianteSeleccionada.imagen;
                    div.querySelector('.producto-precio').innerText = `$${varianteSeleccionada.precio}`;
                    div.querySelector('.producto-talles').innerText = `Talles: ${varianteSeleccionada.talles ? varianteSeleccionada.talles.join(', ') : 'No disponible'}`;
                    div.querySelector('.producto-consultar').id = varianteSeleccionada.id;
                    div.querySelector('.producto-consultar').disabled = varianteSeleccionada.stock === 0;
                    select.style.backgroundColor = color_hex_map[varianteSeleccionada.color];
                } 
            });

            select.style.backgroundColor = color_hex_map[productoAMostrar.color];

            // Si el producto no tiene stock, añadir clase para estilo gris y deshabilitar botón
            if (productoAMostrar.stock === 0) {
                div.classList.add('sin-stock');
                div.querySelector('.producto-consultar').disabled = true;
            }
        }
    });
    actualizarBotonesAgregar();
}