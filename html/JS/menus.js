document.addEventListener('DOMContentLoaded', function() {
    // Inicializar botones de categoría
    const botonesCategoria = document.querySelectorAll(".boton-categoria");
    
    if (botonesCategoria) {
        botonesCategoria.forEach(boton => {
            boton.addEventListener("click", (e) => {
                // Remover clase active de todos los botones
                botonesCategoria.forEach(b => b.classList.remove("active"));
                // Agregar clase active al botón clickeado
                e.currentTarget.classList.add("active");
                
                // Aplicar filtros cuando se cambia de categoría
                if (typeof aplicarFiltro === 'function') {
                    aplicarFiltro();
                }
            });
        });
    }
    
    // Inicializar otros elementos del menú si los hay
    const openMenu = document.querySelector("#open-menu");
    const closeMenu = document.querySelector("#close-menu");
    const aside = document.querySelector("aside");

    openMenu.addEventListener("click", () => {
        aside.classList.add("aside-visible");
    })

    closeMenu.addEventListener("click", () => {
        aside.classList.remove("aside-visible");
    })

    botonesCategoria.forEach(boton => boton.addEventListener("click", () => {
        aside.classList.remove("aside-visible")
    }))
});