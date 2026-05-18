# Contexto del Proyecto: MÃ³dulo de GestiÃ³n de EnvÃ­os (Odoo 17)

## 1. DefiniciÃ³n del Proyecto
CreaciÃ³n de un mÃ³dulo personalizado en Odoo (`modulo_gestion_envio`) para gestionar envÃ­os de carga marÃ­tima y aÃ©rea hacia Cuba (especÃ­ficamente para la agencia Ordaz y la transitaria Cubanacan). El mÃ³dulo debe manejar agrupaciones de bultos (HBL/GuÃ­as), generar reportes PDF muy especÃ­ficos y exportar manifiestos en Excel.

## 2. Estructura de Datos (Modelos)
El sistema se basa en una relaciÃ³n Maestro-Detalle (Cabecera-LÃ­neas):

* **Maestro (`shipping.management`) - El Manifiesto/HBL:**
    * Contiene la informaciÃ³n general del despacho (AWB, Carrier, Totales).
    * Gestiona el estado del envÃ­o.
* **Detalle (`shipping.line`) - Los Bultos Individuales:**
    * Representa cada paquete dentro del HBL.
    * **Cliente (`customer_id`)**: RelaciÃ³n con `res.partner` (quien contrata/paga el envÃ­o).
    * **Remitente (`sender_id`) / Consignatario (`receiver_id`)**: Relaciones con `res.partner`.
    * **CÃ³digo de Paquete (`package_code`)**: 
        * EnvÃ­os Normales: CÃ³digo de barras Ãºnico (ej. 246-11-00011).
        * EnvÃ­os ENA: CÃ³digo compartido por `customer_id` con sufijo fraccionado dinÃ¡mico (ej. 246-11-00025 BULTO 1/3).
    * **QR (`qr_image`)**: Imagen codificada en base64 generada desde el backend de Odoo.
    * **Atributos fÃ­sicos**: Peso, Volumen, Cantidad, Tipo de EnvÃ­o, DescripciÃ³n.

## 3. Vistas y Flujo de Trabajo
* Interfaz limpia e intuitiva en el backend de Odoo.
* **Popup de captura rÃ¡pida:** Las lÃ­neas de bultos se introducen a travÃ©s de un popup (Form) optimizado para rapidez, donde se selecciona el Cliente, Remitente, Consignatario y los detalles fÃ­sicos.
* **Botones de AcciÃ³n:** Ubicados en el `<header>` del formulario principal para desencadenar impresiones PDF, exportaciones a Excel y cambios de estado.

## 4. Reportes y Documentos (El Core CrÃ­tico)
La precisiÃ³n en los documentos es el nÃºcleo del proyecto. Reglas inquebrantables:
* **HBL (House Bill of Lading):**
    * Formato A4 estricto, 3 copias idÃ©nticas por bulto en la misma hoja.
    * Requiere `meta charset="utf-8"` y uso de `t-esc` para evitar caracteres corruptos (wkhtmltopdf bug).
* **Etiquetas TÃ©rmicas (Shipping Labels):**
    * **âš ï¸ REGLA DE ORO:** Formato 6x4 pulgadas **HORIZONTAL** (Landscape, 152x101mm).
    * MaquetaciÃ³n de 2 columnas (Datos 65% / QR 35%) usando `<table>` tradicional para garantizar centrado vertical (`vertical-align: middle`).
    * Uso de `page-break-after: always;` puro para evitar hojas en blanco. Prohibido volver a formato A4 o Portrait.
* **Manifiesto Excel (.xlsx):**
    * ExportaciÃ³n nativa usando `xlsxwriter` directamente desde el backend de Odoo (sin librerÃ­as de terceros inestables).
    * Genera dos hojas: "MANIFIESTO" y "BOLETA", respetando exactamente las cabeceras, totales matemÃ¡ticos y mapeo de columnas del formato estÃ¡ndar de Ordaz.

## 5. Hoja de Ruta (Checklist de Progreso)

- [x] **Paso 1:** ConfiguraciÃ³n base del mÃ³dulo e instalaciÃ³n en entorno de pruebas (Odoo.sh/VPS).
- [x] **Paso 2.1:** CreaciÃ³n del modelo principal `shipping.management` y vistas bÃ¡sicas.
- [x] **Paso 2.2:** CreaciÃ³n del modelo `shipping.line`, incluyendo generaciÃ³n de QR en backend y nuevo campo estructural de `customer_id` (Cliente).
- [x] **Paso 3:** LÃ³gica de negocio, botones de estado y filtros de impresiÃ³n selectiva (`print_selected`).
- [x] **Paso 4.1: MAQUETACIÃ“N PIXEL-PERFECT - HBL.**
      - DiseÃ±o estricto de 3 copias.
      - CorrecciÃ³n de codificaciÃ³n UTF-8.
      - InserciÃ³n de Logo hardcodeado/compaÃ±Ã­a.
- [x] **Paso 4.2: MAQUETACIÃ“N PIXEL-PERFECT - Etiquetas (OptimizaciÃ³n TÃ©rmica 6x4).**
      - `paperformat` estricto a `page_width="152"`, `page_height="101"`, `orientation="Landscape"`.
      - DiseÃ±o Horizontal 2 columnas.
      - PaginaciÃ³n corregida sin hojas en blanco (`page-break-after: always`).
- [x] **Paso 4.3: EXPORTACIÃ“N EXCEL NATIVA.**
      - CreaciÃ³n de mÃ©todo `action_export_manifest_excel`.
      - Mapeo exacto de 15 columnas del Manifiesto y 6 de la Boleta con cÃ¡lculos de totales.
- [x] **Paso 4.4: LÃ“GICA ENA DINÃMICA.**
      - ImplementaciÃ³n de hooks CRUD (`create`, `write`, `unlink`) en lÃ­neas.
      - AgrupaciÃ³n por `customer_id` (Titular).
      - GeneraciÃ³n automÃ¡tica de secuencia base y recÃ¡lculo de denominadores (X/Y) en tiempo real.
- [ ] **Paso 5:** Pruebas integrales de flujo completo (CreaciÃ³n -> ImpresiÃ³n -> ExportaciÃ³n -> Cierre).
- [ ] **Paso 6:** Despliegue en ProducciÃ³n.

## 6. Reglas de InteracciÃ³n con Asistentes AI
* Leer SIEMPRE este documento antes de proponer cambios de cÃ³digo.
* NO modificar formatos de papel (`paperformat`) validados.
* NO usar `display: flex` para PDFs de Odoo. Usar `<table>` HTML.
* Mantener el cÃ³digo modular y aislado (no romper lo que ya funciona).
* Los cÃ³digos ENA deben recalcularse siempre que cambie el Cliente, el Tipo de EnvÃ­o o se eliminen bultos del grupo.
## 7. Especificacion Funcional ENA Padre/Hijos (Odoo 19)

Fecha: 2026-05-18
Estado: Aprobado para implementacion
Objetivo: Mantener operatividad actual y agregar agrupacion ENA sin perder visibilidad por linea.

### 7.1 Principios
- Cada envio se mantiene como una linea visible para el operador.
- En ENA, varias lineas pueden compartir un mismo `package_code` (bulto ENA padre).
- No se crean registros vacios de envio: una linea real actua como ENA padre.

### 7.2 Comportamiento en Popup de Linea
- Campo `shipping_type` mantiene valores: `envio` y `ena`.
- Si `shipping_type = envio`: flujo normal, `package_code` unico autogenerado.
- Si `shipping_type = ena`:
  - La linea conserva su `package_code` autogenerado (candidato a ENA padre).
  - Se muestra select `ENA existente` (solo ENA del mismo manifiesto).
  - Si NO se selecciona ENA existente: la linea queda como ENA padre con su propio `package_code`.
  - Si SI se selecciona ENA existente: la linea pasa a ENA hija y adopta el `package_code` del ENA seleccionado.

### 7.3 Reglas de Integridad
- El ENA padre no puede:
  - cambiar de tipo ENA a envio normal,
  - ni eliminarse,
  mientras tenga lineas hijas asociadas.
- Para liberar un ENA padre:
  - primero mover o eliminar todas sus hijas,
  - luego permitir cambio/eliminacion del padre.
- El select `ENA existente` solo lista codigos ENA del mismo `shipping.management`.

### 7.4 UX Esperada
- Operador siempre ve una linea por envio.
- En lineas ENA hijas, `package_code` se muestra heredado (readonly).
- En linea ENA padre, `package_code` propio visible y estable.

### 7.5 Reportes y Documentos
- Etiquetas: se mantienen por linea (sin consolidar en una sola etiqueta).
- HBL/Reportes: lineas ENA imprimen `Tipo de envio = ENA` y comparten el mismo HBL/`package_code` del grupo cuando sean hijas.

### 7.6 Criterios de Aceptacion QA (DEMO)
- Crear ENA padre sin seleccionar ENA existente: conserva `package_code` propio.
- Crear ENA hija seleccionando ENA existente: adopta `package_code` del padre.
- Intentar cambiar/eliminar ENA padre con hijas: debe bloquear con mensaje funcional.
- Quitar hijas y luego eliminar/cambiar padre: debe permitir.
- Verificar impresion de etiquetas por linea, incluyendo ENA hijas.
- Verificar que no se afecta flujo normal de lineas tipo `envio`.
