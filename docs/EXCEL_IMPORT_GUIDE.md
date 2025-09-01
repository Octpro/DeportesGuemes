# 📊 Guía de Importación de Precios desde Excel

## Descripción
Esta funcionalidad permite actualizar los precios de los productos directamente desde archivos Excel que envían las marcas, automatizando el proceso de actualización de precios.

## Requisitos del Sistema

### Dependencias de Python
Antes de usar esta funcionalidad, instala las siguientes librerías:

```bash
pip install pandas openpyxl xlrd
```

### Formatos de Archivo Soportados
- ✅ Excel (.xlsx, .xls)
- ✅ CSV (.csv)

## Formato del Archivo Excel

### Estructura Requerida
El archivo Excel debe contener al menos dos columnas:

1. **Columna de ID del Producto**: Debe coincidir exactamente con los IDs en tu sistema
2. **Columna de Precio**: Precio nuevo del producto

### Ejemplo de Estructura:

| ID_Producto | Precio_Nuevo | Descripcion (opcional) |
|-------------|--------------|------------------------|
| PROD001     | 15999.50     | Remera Nike Dri-FIT   |
| PROD002     | 25000        | Zapatillas Adidas     |
| PROD003     | 8500.75      | Short Under Armour    |

### Formatos de Precio Aceptados
- ✅ `15999.50` (decimal con punto)
- ✅ `15999,50` (decimal con coma)
- ✅ `$15999.50` (con símbolo de peso)
- ✅ `15999` (entero)

## Cómo Usar la Funcionalidad

### Paso 1: Acceder a la Función
1. Inicia sesión como **Administrador**
2. En el menú principal, haz clic en **"📊 Importar Precios Excel"**

### Paso 2: Seleccionar Archivo
1. Se abrirá un diálogo para seleccionar el archivo
2. Navega hasta el archivo Excel de la marca
3. Selecciona el archivo y haz clic en "Abrir"

### Paso 3: Configurar Importación
1. **Vista Previa**: Verás las primeras 5 filas del archivo
2. **Seleccionar Columnas**:
   - **Columna de ID del Producto**: Selecciona la columna que contiene los IDs
   - **Columna de Precio**: Selecciona la columna que contiene los precios nuevos
3. **Auto-detección**: El sistema intentará detectar automáticamente las columnas correctas

### Paso 4: Importar
1. Verifica que las columnas seleccionadas sean correctas
2. Haz clic en **"Importar Precios"**
3. El sistema procesará el archivo y mostrará un resumen

### Paso 5: Verificar Resultados
El sistema mostrará:
- ✅ Número de productos actualizados exitosamente
- ⚠️ Errores encontrados (si los hay)
- 📝 Detalles de los cambios realizados

## Características Avanzadas

### Respaldo Automático
- Se crea automáticamente un respaldo antes de la importación
- Puedes restaurar los precios anteriores desde el menú "💾 Respaldos"

### Validación de Datos
- Verifica que los IDs existan en el sistema
- Valida que los precios sean números válidos
- Reporta errores específicos por fila

### Registro de Cambios
- Todos los cambios se registran en el historial
- Puedes ver qué precios cambiaron y cuándo

## Solución de Problemas

### Error: "pandas no está instalado"
**Solución**: Instala pandas con:
```bash
pip install pandas openpyxl
```

### Error: "No se encontró el producto con ID..."
**Solución**: 
- Verifica que los IDs en el Excel coincidan exactamente con los del sistema
- Los IDs son sensibles a mayúsculas/minúsculas
- No debe haber espacios extra

### Error: "Precio inválido en fila X"
**Solución**:
- Verifica que la columna de precios contenga solo números
- Elimina caracteres especiales excepto punto/coma decimal
- Verifica que no haya celdas vacías

### Algunos productos no se actualizaron
**Posibles causas**:
- IDs no coinciden exactamente
- Formato de precio incorrecto
- Celdas vacías en el Excel

## Mejores Prácticas

### Para las Marcas
1. **Formato consistente**: Usar siempre el mismo formato de archivo
2. **IDs exactos**: Proporcionar los IDs exactos del sistema
3. **Precios limpios**: Solo números en la columna de precios
4. **Archivo limpio**: Sin filas vacías o datos irrelevantes

### Para el Administrador
1. **Respaldo previo**: Siempre crear respaldo manual antes de importaciones grandes
2. **Verificar vista previa**: Revisar la vista previa antes de importar
3. **Importación gradual**: Para archivos muy grandes, considerar importar por lotes
4. **Verificar resultados**: Revisar el resumen de importación

## Ejemplo de Flujo de Trabajo

1. **La marca envía Excel** con nuevos precios
2. **Administrador abre la app** y va a "Importar Precios Excel"
3. **Selecciona el archivo** de la marca
4. **Configura las columnas** (ID y Precio)
5. **Importa los precios** y revisa el resumen
6. **Verifica algunos productos** en la lista de productos
7. **Los precios se actualizan** automáticamente en la web

## Soporte Técnico

Si encuentras problemas:
1. Verifica que tengas permisos de administrador
2. Revisa que las dependencias estén instaladas
3. Verifica el formato del archivo Excel
4. Consulta el historial de errores en la aplicación

---

**Nota**: Esta funcionalidad está disponible solo para usuarios administradores por seguridad.