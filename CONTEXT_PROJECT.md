# Contexto del Proyecto: Módulo de Gestión de Envíos (Odoo 17)

## 1. Definición del Proyecto
Creación de un módulo personalizado en Odoo (`modulo_gestion_envio`) para gestionar envíos de carga marítima y aérea hacia Cuba (específicamente para la agencia Ordaz y la transitaria Cubanacan). El módulo debe manejar agrupaciones de bultos (HBL/Guías), generar reportes PDF muy específicos y exportar manifiestos en Excel.

## 2. Estructura de Datos (Modelos)
El sistema se basa en una relación Maestro-Detalle (Cabecera-Líneas):

* **Maestro (`shipping.management`) - El Manifiesto/HBL:**
    * Contiene la información general del despacho (AWB, Carrier, Totales).
    * Gestiona el estado del envío.
* **Detalle (`shipping.line`) - Los Bultos Individuales:**
    * Representa cada paquete dentro del HBL.
    * **Cliente (`customer_id`)**: Relación con `res.partner` (quien contrata/paga el envío).
    * **Remitente (`sender_id`) / Consignatario (`receiver_id`)**: Relaciones con `res.partner`.
    * **Código de Paquete (`package_code`)**: 
        * Envíos Normales: Código de barras único (ej. 246-11-00011).
        * Envíos ENA: Código compartido por `customer_id` con sufijo fraccionado dinámico (ej. 246-11-00025 BULTO 1/3).
    * **QR (`qr_image`)**: Imagen codificada en base64 generada desde el backend de Odoo.
    * **Atributos físicos**: Peso, Volumen, Cantidad, Tipo de Envío, Descripción.

## 3. Vistas y Flujo de Trabajo
* Interfaz limpia e intuitiva en el backend de Odoo.
* **Popup de captura rápida:** Las líneas de bultos se introducen a través de un popup (Form) optimizado para rapidez, donde se selecciona el Cliente, Remitente, Consignatario y los detalles físicos.
* **Botones de Acción:** Ubicados en el `<header>` del formulario principal para desencadenar impresiones PDF, exportaciones a Excel y cambios de estado.

## 4. Reportes y Documentos (El Core Crítico)
La precisión en los documentos es el núcleo del proyecto. Reglas inquebrantables:
* **HBL (House Bill of Lading):**
    * Formato A4 estricto, 3 copias idénticas por bulto en la misma hoja.
    * Requiere `meta charset="utf-8"` y uso de `t-esc` para evitar caracteres corruptos (wkhtmltopdf bug).
* **Etiquetas Térmicas (Shipping Labels):**
    * **⚠️ REGLA DE ORO:** Formato 6x4 pulgadas **HORIZONTAL** (Landscape, 152x101mm).
    * Maquetación de 2 columnas (Datos 65% / QR 35%) usando `<table>` tradicional para garantizar centrado vertical (`vertical-align: middle`).
    * Uso de `page-break-after: always;` puro para evitar hojas en blanco. Prohibido volver a formato A4 o Portrait.
* **Manifiesto Excel (.xlsx):**
    * Exportación nativa usando `xlsxwriter` directamente desde el backend de Odoo (sin librerías de terceros inestables).
    * Genera dos hojas: "MANIFIESTO" y "BOLETA", respetando exactamente las cabeceras, totales matemáticos y mapeo de columnas del formato estándar de Ordaz.

## 5. Hoja de Ruta (Checklist de Progreso)

- [x] **Paso 1:** Configuración base del módulo e instalación en entorno de pruebas (Odoo.sh/VPS).
- [x] **Paso 2.1:** Creación del modelo principal `shipping.management` y vistas básicas.
- [x] **Paso 2.2:** Creación del modelo `shipping.line`, incluyendo generación de QR en backend y nuevo campo estructural de `customer_id` (Cliente).
- [x] **Paso 3:** Lógica de negocio, botones de estado y filtros de impresión selectiva (`print_selected`).
- [x] **Paso 4.1: MAQUETACIÓN PIXEL-PERFECT - HBL.**
      - Diseño estricto de 3 copias.
      - Corrección de codificación UTF-8.
      - Inserción de Logo hardcodeado/compañía.
- [x] **Paso 4.2: MAQUETACIÓN PIXEL-PERFECT - Etiquetas (Optimización Térmica 6x4).**
      - `paperformat` estricto a `page_width="152"`, `page_height="101"`, `orientation="Landscape"`.
      - Diseño Horizontal 2 columnas.
      - Paginación corregida sin hojas en blanco (`page-break-after: always`).
- [x] **Paso 4.3: EXPORTACIÓN EXCEL NATIVA.**
      - Creación de método `action_export_manifest_excel`.
      - Mapeo exacto de 15 columnas del Manifiesto y 6 de la Boleta con cálculos de totales.
- [x] **Paso 4.4: LÓGICA ENA DINÁMICA.**
      - Implementación de hooks CRUD (`create`, `write`, `unlink`) en líneas.
      - Agrupación por `customer_id` (Titular).
      - Generación automática de secuencia base y recálculo de denominadores (X/Y) en tiempo real.
- [ ] **Paso 5:** Pruebas integrales de flujo completo (Creación -> Impresión -> Exportación -> Cierre).
- [ ] **Paso 6:** Despliegue en Producción.

## 6. Reglas de Interacción con Asistentes AI
* Leer SIEMPRE este documento antes de proponer cambios de código.
* NO modificar formatos de papel (`paperformat`) validados.
* NO usar `display: flex` para PDFs de Odoo. Usar `<table>` HTML.
* Mantener el código modular y aislado (no romper lo que ya funciona).
* Los códigos ENA deben recalcularse siempre que cambie el Cliente, el Tipo de Envío o se eliminen bultos del grupo.