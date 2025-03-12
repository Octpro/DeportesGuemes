let productos = [];

fetch("JS/productos.json")
    .then(response => response.json())
    .then(data => {
        productos = data;
        console.log("Productos cargados:", productos); // Verifica que los productos se carguen correctamente
        cargarProductos(productos);
    });

const contenedorProductos = document.querySelector("#contenedor-productos");
const botonesCategoria = document.querySelectorAll(".boton-categoria");
const tituloPrincipal = document.querySelector("#titulo-principal");
let botonesAgregar = document.querySelectorAll(".producto-consultar");
const numerito = document.querySelector("#numerito");

function cargarProductos(productosElegidos) {
    contenedorProductos.innerHTML = "";

    productosElegidos.forEach(producto => {
        if (!producto.es_variante) { // Solo mostrar productos principales
            const div = document.createElement("div");
            div.classList.add("producto");
            const idSanitizado = producto.id.replace(/[^a-zA-Z0-9-_]/g, '_');
            div.innerHTML = `
            <img class="producto-img" src="${producto.imagen}" alt="${producto.titulo}">
            <div class="producto-detalles">
                <h3 class="producto-titulo">${producto.titulo}</h3>
                <p class="producto-precio">$${producto.precio}</p>
                <select class="producto-variantes" id="variantes-${idSanitizado}">
                    <option value="${producto.id}" style="background-color: ${producto.color}; color: white;" selected>${producto.color}</option>
                </select>
                <button class="producto-consultar" id="${producto.id}">Consultar</button>
            </div>
            `;
            contenedorProductos.append(div);

            const select = div.querySelector(`#variantes-${idSanitizado}`);
            const variantes = productos.filter(p => p.titulo === producto.titulo && p.es_variante);
            console.log(`Variantes para ${producto.titulo}:`, variantes); // Verifica las variantes encontradas

            if (variantes.length > 0) {
                variantes.forEach(variante => {
                    const option = document.createElement("option");
                    option.value = variante.id;
                    option.text = variante.color;
                    option.style.backgroundColor = variante.color; // Establece el color de fondo
                    option.style.color = 'white'; // Establece el color del texto para mejor visibilidad
                    select.append(option);
                });

                select.addEventListener("change", (e) => {
                    const varianteSeleccionada = productos.find(p => p.id === e.target.value);
                    console.log("Variante seleccionada:", varianteSeleccionada); // Imprime la variante seleccionada
                    if (varianteSeleccionada) {
                        div.querySelector(".producto-img").src = varianteSeleccionada.imagen;
                        div.querySelector(".producto-precio").innerText = `$${varianteSeleccionada.precio}`;
                        div.querySelector(".producto-consultar").id = varianteSeleccionada.id;
                        select.style.backgroundColor = varianteSeleccionada.color; // Cambia el color de fondo del selector
                    }
                });

                // Establece el color de fondo inicial del selector
                select.style.backgroundColor = producto.color;
            } else {
                select.style.display = 'none'; // Oculta el selector si no hay variantes
            }
        }
    });
    actualizarBotonesAgregar();
}

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

function actualizarBotonesAgregar() {
    botonesAgregar = document.querySelectorAll(".producto-consultar");

    botonesAgregar.forEach(boton => {
        boton.addEventListener("click", agregarAlCarrito);
    });
}

let productosEnCarrito;

let productosEnCarritoLS = localStorage.getItem("productos-en-carrito");

if (productosEnCarritoLS) {
    productosEnCarrito = JSON.parse(productosEnCarritoLS);
    actualizarNumerito();
} else {
    productosEnCarrito = [];
}

function agregarAlCarrito(e) {
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

    const idBoton = e.currentTarget.id;
    const productoAgregado = productos.find(producto => producto.id === idBoton);

    if (productosEnCarrito.some(producto => producto.id === idBoton)) {
        const index = productosEnCarrito.findIndex(producto => producto.id === idBoton);
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