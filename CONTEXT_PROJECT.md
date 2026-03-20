# Contexto del Proyecto: Odoo 17 Community - Módulo Gestión de Envío

## 1. Visión General
Desarrollo de un módulo personalizado para Odoo 17 Community que gestione la logística de envíos internacionales. El sistema automatiza validaciones de carga, generación de etiquetas y control de acceso.

## 2. Pila Tecnológica y Estándares
- **Framework:** Odoo 17.0 Community Edition.
- **Frontend:** XML estricto. NO usar `<data>` en las vistas.
- **Reportes:** QWeb Reports. Los reportes deben abrirse nativamente. **Importante:** El motor wkhtmltopdf de Odoo tiene fallos con CSS moderno (flexbox); usar siempre estructuras `<table>` clásicas para el layout.

## 3. Mapa Real del Módulo
modulo_gestion_envio/
├── __manifest__.py                 # (RESUELTO)
├── CONTEXT_PROJECT.md              # Este archivo
├── ERROR.md                        # Bitácora estricta de errores
├── models/
│   ├── container_type.py           # (RESUELTO)
│   ├── shipping_management.py      # (RESUELTO)
│   └── shipping_line.py            # (RESUELTO)
├── security/
│   ├── groups.xml                  # (RESUELTO)
│   └── ir.model.access.csv         # (RESUELTO)
├── data/
│   ├── sequence.xml                # (RESUELTO)
│   └── container_data.xml          # (RESUELTO)
├── views/
│   ├── menus.xml                   # (RESUELTO)
│   ├── container_type_views.xml    # (RESUELTO)
│   └── shipping_management_views.xml # (RESUELTO)
└── report/
    └── shipping_reports.xml        # (EN DESARROLLO - Etiquetas)

## 4. Requisitos y Reglas de Negocio Clave
1. **Seguridad de Roles:** Admin (Confirmar) y Tráfico (Líneas).
2. **Generación de Código:** Secuencia asignada inmediatamente al crear la línea (admite saltos de secuencia).
3. **Reportes (CRÍTICO):** El HBL genera 3 copias idénticas por bulto e imprime 2 copias por hoja A4. Las Etiquetas deben imprimir **3 copias diferentes por hoja A4** aprovechando el espacio al máximo.
4. **Selección de Impresión:** Ambos reportes (HBL y Etiquetas) deben filtrar e imprimir solo las líneas seleccionadas con el checkbox, o todas si ninguna está marcada.
5. **Mapeo de Entidades:** 'Agencia de Origen' y 'Naviera/Aerolínea' deben ser contactos (`res.partner`), no texto simple.
6. **Catálogo de Referencias:** Mantenimiento de identificadores (Guías Aéreas / Manifiestos) en Configuración para estandarizar el campo Referencia.

## 5. Hoja de Ruta y Objetivos Pendientes
- [x] **Paso 1, 2 y 3: Interfaz, Ajuste Estructural y Seguridad.** (RESUELTO)
- [x] **Paso 4.1: PULIDO FINAL - Reporte HBL.** (RESUELTO) Se ha corregido el layout del pie de página con tablas para evitar superposición. Se ha creado y asignado un `paperformat` con márgenes reducidos.
- [x] **Paso 4.3: Refinamiento de Datos y Selección.** (RESUELTO) Impresión Selectiva con checkbox. Campos Relacionales convertidos a Many2one. Catálogo de Referencias implementado.
- [x] **Paso 5: Permisos (ACL).** (RESUELTO) Creado `ir.model.access.csv` con permisos para Management, Lines, Container Types y Catálogo de Referencias.
- [x] **Paso 4.2: MAQUETACIÓN PIXEL-PERFECT - Etiquetas (Optimización Térmica 6x4).** (RESUELTO) Se ha implementado el formato de papel 6x4 horizontal (152x101mm) y un layout de tabla para centrado vertical, eliminando hojas en blanco residuales.

## 6. REGLAS ESTRICTAS PARA CODE ASSIST
1. **Pedir Autorización:** Propón la solución antes del código final.
2. **Prohibición de Sobrescritura:** NO alterar funcionalidades que ya están correctas.
3. **Respetar la Bitácora:** Revisa `ERROR.md` siempre.
4. **Aislamiento de Cambios:** Entrega solo las porciones de código a modificar.
5. **Actualización del Contexto:** Al finalizar un paso, proveer el texto actualizado.
6. **REGLA DE ORO ACTUAL:** BAJO NINGUNA CIRCUNSTANCIA se debe modificar, reescribir, alterar o incluir el código de la acción ni del template del HBL (`report_shipping_hbl` y `action_report_shipping_bl`).