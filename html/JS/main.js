let productos = [];

fetch('JS/productos.json')
    .then(response => response.json())
    .then(data => {
        productos = data;
        console.log(productos); // Verifica que los productos se carguen correctamente
        mostrarProductos(productos);
    });

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
                    <option value="${productoAMostrar.id}" style="background-color: ${productoAMostrar.color}; color: white;" selected>${productoAMostrar.color}</option>
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
                    option.style.backgroundColor = variante.color;
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
                        select.style.backgroundColor = varianteSeleccionada.color;
                    } 
                });

                select.style.backgroundColor = productoAMostrar.color;
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
            filtros.style.display = 'block'; // Asegúrate de que los filtros se muestren
        } else {
            filtros.classList.remove('filtros-mostrados');
            filtros.classList.add('filtros-ocultos');
            filtros.style.display = 'none'; // Asegúrate de que los filtros se oculten
        }
    });

    // Close the modal when clicking outside of the modal content
    window.addEventListener('click', function(event) {
        const filtros = document.getElementById('filtros');
        if (event.target === filtros) {
            filtros.style.display = 'none';
        }
    });

    document.getElementById('aplicar-filtro').addEventListener('click', aplicarFiltro);

    const filtros = document.querySelectorAll('#filtro-nombre, #filtro-categoria, #filtro-precio-min, #filtro-precio-max, #filtro-genero, #filtro-talle');
    filtros.forEach(filtro => {
        filtro.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                aplicarFiltro();
            }
        });
    });

botonesCategoria.forEach(boton => {
    boton.addEventListener("click", (e) => {
        botonesCategoria.forEach(boton => boton.classList.remove("active"));
        e.currentTarget.classList.add("active");

        if (e.currentTarget.id != "todos") {
            const productoCategoria = productos.find(producto => producto.categoria.id === e.currentTarget.id);

            if (productoCategoria) {
                tituloPrincipal.innerText = productoCategoria.categoria.nombre;
            } else {
                tituloPrincipal.innerText = "No hay productos";
            }

            const productosBoton = productos.filter(producto => producto.categoria.id === e.currentTarget.id);
            cargarProductos(productosBoton);
        } else {
            tituloPrincipal.innerText = "Todos los productos";
            cargarProductos(productos);
        }
    });
});

function aplicarFiltro() {
    const nombre = document.getElementById('filtro-nombre').value.toLowerCase();
    const categoria = document.getElementById('filtro-categoria').value;
    const precioMin = parseFloat(document.getElementById('filtro-precio-min').value) || 0;
    const precioMax = parseFloat(document.getElementById('filtro-precio-max').value) || Infinity;
    const genero = document.getElementById('filtro-genero').value;
    const talle = document.getElementById('filtro-talle').value;

    const productosFiltrados = productos.filter(producto => {
        const nombreMatch = producto.titulo.toLowerCase().includes(nombre);
        const categoriaMatch = categoria === "" || producto.categoria.id === categoria;
        const precioMatch = producto.precio >= precioMin && producto.precio <= precioMax;
        const generoMatch = genero === "" || (genero === "femenino" && producto.genero.femenino) || (genero === "masculino" && producto.genero.masculino);
        const talleMatch = talle === "" || producto.talles.includes(talle);
        return nombreMatch && categoriaMatch && precioMatch && generoMatch && talleMatch;
    });

    mostrarProductos(productosFiltrados);
}});

function cargarProductos(productos) {
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
                    <option value="${productoAMostrar.id}" style="background-color: ${productoAMostrar.color}; color: white;" selected>${productoAMostrar.color}</option>
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
                    option.style.backgroundColor = variante.color;
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
                        select.style.backgroundColor = varianteSeleccionada.color;
                    } 
                });

                select.style.backgroundColor = productoAMostrar.color;
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