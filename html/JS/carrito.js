let productosEnCarrito = localStorage.getItem("productos-en-carrito");
productosEnCarrito = JSON.parse(productosEnCarrito);

const contenedorCarritoVacio = document.querySelector("#carrito-vacio");
const contenedorCarritoProductos = document.querySelector("#carrito-productos");
const contenedorcarritoAcciones = document.querySelector("#carrito-acciones");
const contenedorcarritoComprado = document.querySelector("#carrito-comprado");
let botonesEliminar = document.querySelectorAll(".carrito-producto-eliminar");
const botonVaciar = document.querySelector("#carrito-acciones-vaciar");
const contenedorTotal = document.querySelector("#total");
const botonConsultar = document.querySelector("#carrito-acciones-comprar");

function cargarProductosCarrito() {
    if (productosEnCarrito && productosEnCarrito.length > 0) {

        contenedorCarritoVacio.classList.add("disabled");
        contenedorCarritoProductos.classList.remove("disabled");
        contenedorcarritoAcciones.classList.remove("disabled");
        contenedorcarritoComprado.classList.add("disabled");

        contenedorCarritoProductos.innerHTML = "";

        productosEnCarrito.forEach(producto => {
            const div = document.createElement("div");
            div.classList.add("carrito-producto");
            div.innerHTML = `
            <img class="carrito-producto-imagen" src="${producto.imagen}" alt="${producto.titulo}">
            <div class="carrito-producto-nombre">
                <small>Titulo</small>
                <h3>${producto.titulo}</h3>
            </div>
            <div class="carrito-producto-cantidad">
                <small>Cantidad</small>
                <p>${producto.cantidad}</p>
            </div>
            <div class="carrito-producto-precio">
                <small>Precio</small>
                <p>${producto.precio}</p>
            </div>
            <div class="carrito-producto-subtotal">
                <small>Subtotal</small>
                <p>${producto.precio * producto.cantidad}</p>
            </div>
            <button class="carrito-producto-eliminar" id="${producto.id}"><i class="bi bi-trash-fill"></i></button>
            `;

            // Agregar select de talles si el producto tiene talles
            if (producto.talles && producto.talles.length > 0) {
                const selectTalles = document.createElement("select");
                selectTalles.classList.add("carrito-producto-talles");
                selectTalles.multiple = true; // Permitir selección múltiple
                producto.talles.forEach(talle => {
                    const option = document.createElement("option");
                    option.value = talle;
                    option.text = talle;
                    selectTalles.appendChild(option);
                });
                div.appendChild(selectTalles);

                // Manejar cambios en la selección de talles
                selectTalles.addEventListener('change', (e) => {
                    const selectedOptions = Array.from(e.target.selectedOptions).map(option => option.value);
                    const cantidadSeleccionada = selectedOptions.length;
                    producto.cantidad = cantidadSeleccionada;
                    producto.tallesSeleccionados = selectedOptions; // Guardar los talles seleccionados en el objeto producto
                    div.querySelector('.carrito-producto-cantidad p').innerText = cantidadSeleccionada;
                    div.querySelector('.carrito-producto-subtotal p').innerText = producto.precio * cantidadSeleccionada;
                    actualizarTotal();
                    localStorage.setItem("productos-en-carrito", JSON.stringify(productosEnCarrito)); // Guardar cambios en localStorage
                });
            }

            contenedorCarritoProductos.append(div);
        });

    } else {
        contenedorCarritoVacio.classList.remove("disabled");
        contenedorCarritoProductos.classList.add("disabled");
        contenedorcarritoAcciones.classList.add("disabled");
        contenedorcarritoComprado.classList.add("disabled");
    }
    actualizarBotonesEliminar();
    actualizarTotal();
}

cargarProductosCarrito();

function actualizarBotonesEliminar() {
    botonesEliminar = document.querySelectorAll(".carrito-producto-eliminar");

    botonesEliminar.forEach(boton => {
        boton.addEventListener("click", eliminarDelCarrito);
    });
}

function eliminarDelCarrito(e) {
    Toastify({
        text: "Producto eliminado",
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
    const index = productosEnCarrito.findIndex(producto => producto.id === idBoton);

    productosEnCarrito.splice(index, 1);
    cargarProductosCarrito();

    localStorage.setItem("productos-en-carrito", JSON.stringify(productosEnCarrito));
}

botonVaciar.addEventListener("click", vaciarCarrito);

function vaciarCarrito() {
    Swal.fire({
        title: "Estas seguro?",
        text: `Se van a eliminar ${productosEnCarrito.reduce((acc, producto) => acc + producto.cantidad, 0)} productos`,
        icon: "question",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Si, borralos!",
        cancelButtonText: "Cancelar"
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire({
                title: "Eliminados!",
                text: "Tus productos han sido eliminados.",
                icon: "success"
            });
            productosEnCarrito.length = 0;
            localStorage.setItem("productos-en-carrito", JSON.stringify(productosEnCarrito));
            cargarProductosCarrito();
        }
    });

}

function actualizarTotal() {
    const totalCalculado = productosEnCarrito.reduce((acc, producto) => acc + (producto.precio * producto.cantidad), 0);
    contenedorTotal.innerText = `$${totalCalculado}`;
}

botonConsultar.addEventListener("click", consultarCarrito);

function consultarCarrito() {
    let productosEnCarrito = JSON.parse(localStorage.getItem("productos-en-carrito")) || [];

    let mensajeWhatsApp = "Hola!. Queria consultar sobre:\n\n";

    productosEnCarrito.forEach((producto) => {
        let tallesSeleccionados = producto.tallesSeleccionados || [];
        console.log(`Producto: ${producto.titulo}`);
        console.log(`Talles seleccionados: ${tallesSeleccionados}`);
        const cantidadSeleccionada = tallesSeleccionados.length > 0 ? tallesSeleccionados.length : producto.cantidad;
        console.log(`Cantidad seleccionada: ${cantidadSeleccionada}`);
        console.log(`Precio unitario: ${producto.precio}`);
        console.log(`Subtotal: ${producto.precio * cantidadSeleccionada}`);
        mensajeWhatsApp += `- Producto: ${producto.titulo}\n`;
        mensajeWhatsApp += `- Cantidad: ${cantidadSeleccionada}\n`;
        mensajeWhatsApp += `- Precio: ${producto.precio * cantidadSeleccionada}\n`;
        if (tallesSeleccionados.length > 0) {
            mensajeWhatsApp += `- Talles: ${tallesSeleccionados.join(", ")}\n`;
        } else if (producto.talles && producto.talles.length > 0) {
            mensajeWhatsApp += `- Talles: ${producto.talles.join(", ")}\n`;
        }
        if (producto.genero) {
            mensajeWhatsApp += `- Género: ${producto.genero}\n`;
        }
        mensajeWhatsApp += `\n`;
    });

    console.log(`Mensaje WhatsApp: ${mensajeWhatsApp}`);

    // Codificar mensaje para URL y crear enlace de WhatsApp
    let mensajeCodificado = encodeURIComponent(mensajeWhatsApp);
    let enlaceWhatsApp = `https://api.whatsapp.com/send?phone=5493541665446&text=${mensajeCodificado}`; // cambiar el numero de telefono

    // Abrir enlace en nueva pestaña o ventana
    window.open(enlaceWhatsApp, '_blank');

    // Ahora sí, limpiar y guardar cambios en localStorage
    // productosEnCarrito.length = 0;
    // localStorage.setItem("productos-en-carrito", JSON.stringify(productosEnCarrito));

    // Ocultar/mostrar elementos según sea necesario
    // contenedorCarritoVacio.classList.add("disabled");
    // contenedorCarritoProductos.classList.add("disabled");
    // contenedorcarritoAcciones.classList.add("disabled");
    // contenedorcarritoComprado.classList.remove("disabled");
}