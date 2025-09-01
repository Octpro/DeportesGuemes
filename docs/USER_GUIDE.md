# Deportes Güemes - Guía del Usuario

## Tabla de Contenidos
1. [Introducción](#introducción)
2. [Primeros Pasos](#primeros-pasos)
3. [Aplicación de Escritorio](#aplicación-de-escritorio)
4. [Tienda Web](#tienda-web)
5. [Gestión de Productos](#gestión-de-productos)
6. [Carrito de Compras](#carrito-de-compras)
7. [Búsqueda y Filtrado](#búsqueda-y-filtrado)
8. [Características de Rendimiento](#características-de-rendimiento)
9. [Características de Accesibilidad](#características-de-accesibilidad)
10. [Solución de Problemas](#solución-de-problemas)
11. [Preguntas Frecuentes](#preguntas-frecuentes)

## Introducción

Deportes Güemes es un sistema integral de gestión de tienda deportiva que combina la gestión de inventario con funcionalidad de comercio electrónico. El sistema consta de dos componentes principales:

- **Aplicación de Escritorio**: Sistema de gestión de inventario basado en Python para administradores
- **Tienda Web**: Interfaz de comercio electrónico orientada al cliente

### Características Principales
- ✅ Gestión de catálogo de productos
- ✅ Seguimiento de inventario en tiempo real
- ✅ Búsqueda y filtrado avanzado
- ✅ Funcionalidad de carrito de compras
- ✅ Diseño responsivo para móviles
- ✅ Optimización de rendimiento
- ✅ Cumplimiento de accesibilidad
- ✅ Sincronización automática de datos

## Primeros Pasos

### Requisitos del Sistema

#### Aplicación de Escritorio
- **Sistema Operativo**: Windows 10 o posterior
- **Python**: Versión 3.8 o posterior
- **Memoria**: 4GB RAM mínimo, 8GB recomendado
- **Almacenamiento**: 500MB de espacio libre
- **Internet**: Requerido para sincronización

#### Tienda Web
- **Navegador**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **JavaScript**: Debe estar habilitado
- **Internet**: Requerido para funcionalidad completa
- **Resolución de Pantalla**: 320px de ancho mínimo

### Instalación

#### Aplicación de Escritorio
1. Asegúrese de que Python 3.8+ esté instalado
2. Instale las dependencias requeridas:
   ```bash
   pip install customtkinter pillow gitpython
   ```
3. Ejecute la aplicación:
   ```bash
   python customtk.py
   ```

#### Tienda Web
1. Abra `html/index.html` en un navegador web
2. O sirva vía servidor HTTP:
   ```bash
   python -m http.server 8000
   ```
3. Navegue a `http://localhost:8000/html/`

## Aplicación de Escritorio

### Interfaz Principal

![Captura de Pantalla de la Aplicación de Escritorio](screenshots/desktop-main.png)

La aplicación de escritorio proporciona capacidades integrales de gestión de productos para administradores de tienda.

#### Menú de Navegación
- **Productos**: Gestionar catálogo de productos
- **Inventario**: Seguimiento de niveles de stock
- **Ventas**: Procesar transacciones
- **Reportes**: Generar informes comerciales
- **Configuración**: Configurar aplicación

### Gestión de Productos

#### Agregar Nuevos Productos
1. Haga clic en el botón **"Agregar Producto"**
2. Complete los detalles del producto:
   - **Título**: Nombre del producto (requerido)
   - **Precio**: Precio del producto (requerido)
   - **Categoría**: Seleccionar del menú desplegable
   - **Disciplina**: Categoría deportiva
   - **Género**: Audiencia objetivo
   - **Descripción**: Descripción del producto
   - **Stock**: Cantidad inicial de inventario

3. Agregar imágenes del producto:
   - Haga clic en el botón **"Agregar Imagen"**
   - Seleccione archivos de imagen (JPG, PNG soportados)
   - Las imágenes se optimizan automáticamente

4. Configurar variantes (opcional):
   - Haga clic en el botón **"Agregar Variante"**
   - Especifique tamaño, color y stock para cada variante

5. Haga clic en **"Guardar Producto"** para agregar al catálogo

#### Editar Productos
1. Seleccione el producto de la lista
2. Haga clic en el botón **"Editar"**
3. Modifique los campos deseados
4. Haga clic en **"Actualizar Producto"** para guardar cambios

#### Gestión de Inventario
1. Navegue a la sección **Inventario**
2. Vea los niveles de stock actuales
3. Actualice las cantidades según sea necesario
4. Configure alertas de stock bajo

### Sincronización de Datos

La aplicación de escritorio se sincroniza automáticamente con la tienda web:
- Los cambios se confirman en el repositorio Git
- La tienda web refleja las actualizaciones en tiempo real
- Los archivos de respaldo se crean automáticamente

## Tienda Web

### Interfaz del Cliente

![Captura de Pantalla de la Tienda Web](screenshots/web-store.png)

La tienda web proporciona una experiencia de compra moderna y responsiva para los clientes.

#### Características de la Página Principal
- **Cuadrícula de Productos**: Navegar por todos los productos disponibles
- **Barra de Búsqueda**: Encontrar productos específicos
- **Panel de Filtros**: Reducir los resultados
- **Carrito de Compras**: Ver artículos seleccionados
- **Menú de Navegación**: Acceder a diferentes secciones

### Navegación de Productos

#### Tarjetas de Productos
Cada producto muestra:
- Imagen del producto con carga diferida
- Título y descripción del producto
- Información de precio
- Disponibilidad de stock
- Botón "Agregar al Carrito"
- Variantes del producto (si están disponibles)

#### Detalles del Producto
Haga clic en un producto para ver:
- Imágenes de alta resolución
- Descripción detallada
- Especificaciones
- Variantes disponibles
- Información de stock
- Productos relacionados

### Experiencia Móvil

La tienda web está optimizada para dispositivos móviles:
- **Diseño Responsivo**: Se adapta a todos los tamaños de pantalla
- **Amigable al Tacto**: Objetivos táctiles mínimos de 44px
- **Carga Rápida**: Optimizado para redes móviles
- **Soporte Sin Conexión**: Funcionalidad básica sin internet

## Carrito de Compras

### Agregar Artículos
1. Navegar por los productos
2. Seleccionar la variante deseada (si aplica)
3. Hacer clic en el botón **"Agregar al Carrito"**
4. El artículo aparece en el carrito con confirmación

### Gestión del Carrito
- **Ver Carrito**: Hacer clic en el ícono del carrito en la navegación
- **Actualizar Cantidad**: Usar botones +/-
- **Eliminar Artículos**: Hacer clic en el botón eliminar
- **Vaciar Carrito**: Eliminar todos los artículos de una vez

### Persistencia del Carrito
- El contenido del carrito se guarda localmente
- Los artículos persisten entre sesiones del navegador
- Se sincroniza entre pestañas del navegador

### Proceso de Compra
1. Revisar el contenido del carrito
2. Verificar cantidades y variantes
3. Proceder al checkout
4. Completar la compra (la implementación varía)

## Búsqueda y Filtrado

### Funcionalidad de Búsqueda

#### Búsqueda Básica
- Escribir en la caja de búsqueda
- Los resultados se actualizan en tiempo real
- Busca en títulos y descripciones de productos
- Soporta coincidencias parciales

#### Búsqueda Avanzada
- **Filtro de Categoría**: Filtrar por categoría de producto
- **Filtro de Disciplina**: Filtrar por disciplina deportiva
- **Filtro de Género**: Filtrar por género objetivo
- **Rango de Precio**: Establecer precio mínimo y máximo
- **Filtro de Stock**: Mostrar solo artículos en stock

### Combinaciones de Filtros
- Se pueden aplicar múltiples filtros simultáneamente
- Los filtros usan lógica Y (todas las condiciones deben coincidir)
- Limpiar filtros individuales o restablecer todos

### Consejos de Búsqueda
- Use palabras clave específicas para mejores resultados
- Pruebe diferentes ortografías o sinónimos
- Use filtros para reducir conjuntos de resultados grandes
- Limpie los filtros si no se encuentran resultados

## Características de Rendimiento

### Optimización de Carga
- **Carga Diferida**: Las imágenes se cargan según sea necesario
- **División de Código**: JavaScript se carga bajo demanda
- **Caché**: Los datos de acceso frecuente se almacenan en caché
- **Compresión**: Los recursos se comprimen para una carga más rápida

### Monitoreo de Rendimiento
El sistema incluye monitoreo de rendimiento integrado:
- Tiempos de carga de página
- Tiempos de respuesta de búsqueda
- Seguimiento de uso de memoria
- Registro de errores

### Consejos de Optimización
- **Limpiar Caché**: Actualizar si experimenta problemas
- **Actualizar Navegador**: Use la versión más reciente del navegador
- **Conexión Estable**: Asegurar internet confiable
- **Cerrar Pestañas**: Reducir el uso de memoria

## Características de Accesibilidad

### Navegación por Teclado
- **Navegación con Tab**: Navegar usando la tecla Tab
- **Enter/Espacio**: Activar botones y enlaces
- **Teclas de Flecha**: Navegar dentro de componentes
- **Escape**: Cerrar modales y menús

### Soporte para Lectores de Pantalla
- **Etiquetas ARIA**: Todos los elementos interactivos etiquetados
- **HTML Semántico**: Estructura de encabezados apropiada
- **Texto Alternativo**: Las imágenes incluyen texto descriptivo
- **Indicadores de Foco**: Estados de foco visual claros

### Accesibilidad Visual
- **Alto Contraste**: Cumple con estándares WCAG AA
- **Texto Grande**: Tamaños de fuente legibles
- **Independencia de Color**: Información no dependiente del color
- **Soporte de Zoom**: Funciona al 200% de zoom

### Atajos de Accesibilidad
- **Enlaces de Salto**: Saltar al contenido principal
- **Navegación por Puntos de Referencia**: Navegar por secciones de página
- **Etiquetas de Formulario**: Etiquetas de campos de formulario claras
- **Mensajes de Error**: Información de error descriptiva

## Solución de Problemas

### Problemas Comunes

#### La Aplicación de Escritorio No Inicia
**Problema**: La aplicación falla al ejecutarse
**Soluciones**:
1. Verificar instalación de Python: `python --version`
2. Instalar dependencias faltantes: `pip install -r requirements.txt`
3. Verificar permisos de archivos
4. Ejecutar como administrador si es necesario

#### La Tienda Web No Carga
**Problema**: Página en blanco o errores de carga
**Soluciones**:
1. Verificar compatibilidad del navegador
2. Habilitar JavaScript
3. Limpiar caché del navegador
4. Deshabilitar extensiones del navegador
5. Probar modo incógnito/privado

#### Los Productos No Se Sincronizan
**Problema**: Los cambios en escritorio no aparecen en la tienda web
**Soluciones**:
1. Verificar conexión a internet
2. Verificar configuración de Git
3. Actualizar manualmente la tienda web
4. Verificar mensajes de error en la aplicación de escritorio

#### Rendimiento Lento
**Problema**: La aplicación funciona lentamente
**Soluciones**:
1. Limpiar caché del navegador
2. Cerrar pestañas innecesarias del navegador
3. Reiniciar la aplicación
4. Verificar memoria disponible
5. Actualizar el navegador

#### La Búsqueda No Funciona
**Problema**: La búsqueda no devuelve resultados
**Soluciones**:
1. Verificar ortografía
2. Limpiar todos los filtros
3. Probar términos de búsqueda más amplios
4. Actualizar la página
5. Verificar si existen productos

### Mensajes de Error

#### "Producto No Encontrado"
- El producto puede haber sido eliminado
- Verificar ID del producto
- Actualizar lista de productos

#### "Error de Red"
- Verificar conexión a internet
- Intentar más tarde
- Contactar al administrador

#### "Permiso Denegado"
- Verificar permisos de usuario
- Iniciar sesión como administrador
- Verificar derechos de acceso a archivos

### Obtener Ayuda

Si continúa experimentando problemas:
1. Consulte la sección de Preguntas Frecuentes a continuación
2. Revise los registros de errores
3. Contacte al soporte técnico
4. Proporcione descripciones detalladas de errores

## Preguntas Frecuentes

### Preguntas Generales

**P: ¿Qué navegadores son compatibles?**
R: Chrome 90+, Firefox 88+, Safari 14+, y Edge 90+. JavaScript debe estar habilitado.

**P: ¿Puedo usar el sistema sin conexión?**
R: La aplicación de escritorio funciona sin conexión, pero la sincronización requiere internet. La tienda web tiene funcionalidad limitada sin conexión.

**P: ¿Con qué frecuencia se sincronizan los datos entre escritorio y web?**
R: Los cambios se sincronizan inmediatamente cuando se realizan en la aplicación de escritorio.

**P: ¿Están seguros mis datos?**
R: Sí, los datos se almacenan localmente y se sincronizan a través de repositorios Git seguros.

### Gestión de Productos

**P: ¿Qué formatos de imagen son compatibles?**
R: Se admiten formatos JPG, PNG y WebP. Las imágenes se optimizan automáticamente.

**P: ¿Cuántas variantes de producto puedo agregar?**
R: No hay un límite estricto, pero el rendimiento es óptimo con menos de 20 variantes por producto.

**P: ¿Puedo importar productos en lote?**
R: Sí, use la función de importación en lote en la aplicación de escritorio.

**P: ¿Cómo configuro alertas de stock bajo?**
R: Configure los umbrales de alerta en la sección de gestión de inventario.

### Carrito de Compras

**P: ¿Cuánto tiempo permanecen los artículos en el carrito?**
R: Los artículos del carrito persisten indefinidamente hasta que se eliminen manualmente o se borren los datos del navegador.

**P: ¿Pueden los clientes guardar artículos para más tarde?**
R: Sí, los artículos permanecen en el carrito entre sesiones.

**P: ¿Hay un tamaño máximo del carrito?**
R: No hay límite estricto, pero el rendimiento puede degradarse con carritos muy grandes.

### Preguntas Técnicas

**P: ¿Cómo actualizo el sistema?**
R: Descargue la versión más reciente y siga las instrucciones de instalación.

**P: ¿Puedo personalizar la apariencia?**
R: Sí, modifique los archivos CSS para personalizar colores, fuentes y diseño.

**P: ¿Cómo hago respaldo de mis datos?**
R: Use la función de respaldo integrada en la aplicación de escritorio.

**P: ¿Puedo integrar con otros sistemas?**
R: El sistema usa formato de datos JSON, lo que hace posible la integración con desarrollo personalizado.

### Rendimiento

**P: ¿Por qué la tienda web carga lentamente?**
R: Verifique su conexión a internet, limpie el caché del navegador, o pruebe un navegador diferente.

**P: ¿Cómo puedo mejorar el rendimiento?**
R: Habilite el caché, use un navegador moderno, y asegure recursos del sistema adecuados.

**P: ¿Cuál es el hardware recomendado?**
R: 8GB RAM, procesador moderno, y almacenamiento SSD para rendimiento óptimo.

---

## Soporte

Para soporte adicional:
- **Email**: support@deportesguemes.com
- **Documentación**: Consulte la documentación técnica
- **Actualizaciones**: Monitoree las actualizaciones del sistema
- **Comunidad**: Únase a los foros de usuarios para consejos y trucos

---

*Última actualización: [Fecha Actual]*
*Versión: 1.0.0*