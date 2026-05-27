# Documento de Requerimientos del Producto (PRD)

## 1. Información General del Proyecto
**Nombre del Proyecto:** Plataforma Web - Completada a Beneficio
**Descripción:** Transformación de un registro en Excel (lista de cooperaciones para evento a beneficio de la Tía Marcela) a una plataforma web interactiva donde la comunidad puede registrar sus donaciones en tiempo real.

## 2. Objetivos
* **Digitalizar el proceso:** Evitar la gestión manual y desactualizada del archivo Excel original.
* **Control en tiempo real:** Mostrar el inventario actualizado de lo que falta por donar, descontando automáticamente las cantidades aportadas.
* **Registro automatizado:** Guardar automáticamente el detalle de cada donación (Nombre, Apellido, Producto, Cantidad) en un archivo Excel consolidado para uso administrativo.

## 3. Público Objetivo
Miembros de la comunidad escolar (apoderados, docentes, personal administrativo) que deseen aportar con insumos (o su equivalente en dinero) para la completada.

## 4. Requerimientos Funcionales
### 4.1. Interfaz de Usuario (Frontend)
* **Visualización de Insumos:** La página principal debe listar los productos requeridos (Pan Copihue, Salchichas, Palta, Tomate, etc.) junto con la *cantidad total requerida* y la *cantidad restante* por cubrir.
* **Formulario de Donación:** * Selector de Producto (lista desplegable de insumos que aún no llegan a meta).
    * Campo numérico para "Cantidad a donar" (con validación para no superar el remanente).
    * Campo de texto para "Nombre".
    * Campo de texto para "Apellido".
    * Botón de confirmación "Registrar Donación".
* **Feedback visual:** Mensaje de éxito al completar la operación (ej: alerta verde) y actualización inmediata de la tabla de insumos restantes.

### 4.2. Lógica del Servidor (Backend)
* **Gestión de Inventario:** Un servicio que reste la cantidad donada del total requerido de dicho producto.
* **Generación de Registro:** Cada vez que se confirma una donación exitosa, el sistema debe anexar a un archivo Excel maestro una nueva fila con la transacción.
* **Validación de Datos:** El servidor debe validar los campos requeridos y rechazar donaciones que excedan la cantidad máxima que se necesita.

## 5. Requerimientos No Funcionales
* **Tecnologías sugeridas:** * *Frontend:* HTML, CSS, JavaScript. Se sugiere el uso de Bootstrap para asegurar un diseño responsivo, limpio y de rápido desarrollo.
    * *Backend:* Python (usando Flask o FastAPI) para manejar la lógica web y la escritura del archivo Excel mediante librerías como `pandas` o `openpyxl`.
* **Usabilidad y Accesibilidad:** Debe ser fácil de navegar desde dispositivos móviles (Mobile-first), ya que es muy probable que los usuarios accedan mediante un enlace compartido por grupos de mensajería como WhatsApp.
* **Concurrencia:** Manejo seguro del archivo Excel para evitar colisiones si dos usuarios intentan registrar una donación exactamente al mismo tiempo.

## 6. Modelo de Datos Inicial (Estructura Base)

**A. Tabla de Metas (Inventario Basado en el Excel Original):**
* Pan Copihue (a granel): 400
* Salchichas: 400
* Mayonesa (Kg): 4
* Mostaza (Kg): 3
* Ketchup (Kg): 4
* Palta (Kg): 25
* Tomate (Kg): 20
* Vasos (Mangas 50 un. 200cc): 10
* Bebidas 3L: 25
* Jugo (Botellas): 10
* Sal (Kg): 1
* Ají en pasta (Bolsita): 1

**B. Registro de Donantes (Estructura del Excel de Salida):**
| ID | Fecha y Hora | Nombre | Apellido | Producto Donado | Cantidad |

## 7. Criterios de Aceptación (MVP)
1.  El usuario ingresa a la plataforma web y visualiza correctamente la lista de insumos faltantes para la completada.
2.  El usuario completa el formulario con su nombre, apellido, selecciona un insumo y su cantidad, y el sistema procesa la solicitud.
3.  El sistema descuenta matemáticamente la cantidad ingresada del total requerido en la vista de todos los usuarios.
4.  El administrador del sistema cuenta con un archivo `.xlsx` en el servidor que se actualiza añadiendo una fila por cada donación exitosa.
