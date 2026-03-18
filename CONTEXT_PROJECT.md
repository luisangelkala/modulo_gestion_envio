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
│   └── ir.model.access.csv         # (PENDIENTE)
├── data/
│   ├── sequence.xml                # (RESUELTO)
│   └── container_data.xml          # (RESUELTO)
├── views/
│   ├── menus.xml                   # (RESUELTO)
│   ├── container_type_views.xml    # (RESUELTO)
│   └── shipping_management_views.xml # (RESUELTO)
└── report/
    └── shipping_reports.xml        # (EN PULIDO FINAL - HBL y Paperformat)

## 4. Requisitos y Reglas de Negocio Clave
1. **Seguridad de Roles:** Admin (Confirmar) y Tráfico (Líneas).
2. **Generación de Código:** Secuencia estricta asignada únicamente al confirmar.
3. **Reportes (CRÍTICO - Diseño HBL):** - El HBL debe generar **3 copias idénticas por bulto** e imprimir **2 copias por hoja A4**.
   - **Maquetación (Frontend):** Cuadrícula estricta con tablas HTML (`border-collapse: collapse`).
   - **Selección de Impresión:** Posibilidad de marcar/desmarcar bultos específicos para imprimir solo sus HBLs.
   - **Mapeo de Entidades:** 'Agencia de Origen' y 'Naviera/Aerolínea' deben ser contactos (`res.partner`), no texto simple.
   - **Catálogo de Referencias:** Mantenimiento de identificadores (Guías Aéreas / Manifiestos) en Configuración para estandarizar el campo Referencia.

## 5. Hoja de Ruta y Objetivos Pendientes
- [x] **Paso 1, 2 y 3: Interfaz, Ajuste Estructural y Seguridad.** (RESUELTO)
- [ ] **Paso 4.1: PULIDO FINAL - Reporte HBL (Formatos y Overlap).**
      - **Problema 1 (Superposición):** El pie de página (Caja de Aduana y Fecha) tiene superposición de líneas porque wkhtmltopdf no soporta `display: flex`. Cambiar a una tabla anidada.
      - **Problema 2 (Encoding):** Reemplazar textos estáticos con tildes (Sólo, Colón, Panamá) por caracteres sin tildes o entidades HTML para evitar errores de codificación.
      - **Problema 3 (Márgenes):** Para que quepan 2 copias, se debe crear un `<record model="report.paperformat">` con márgenes mínimos (ej. top 10, bottom 10) y asignarlo al `<record id="action_report_shipping_bl" model="ir.actions.report">` usando el campo `paperformat_id`.
- [ ] **Paso 4.2: Reporte PDF de Etiquetas.** (En espera).
- [ ] **Paso 4.3: Refinamiento de Datos y Selección (NUEVO).**
      - **Impresión Selectiva:** Añadir checkbox (`Boolean`) en las líneas de carga. El reporte HBL debe filtrar: imprimir seleccionados si existen, o todos si ninguno está marcado.
      - **Campos Relacionales:** Convertir `agencia_origen` y `carrier` a `Many2one` (`res.partner`). Actualizar vistas y reportes acorde (acceder a `.name`).
      - **Configuración de Referencias:** Crear modelo `shipping.document.template` (Nombre, Tipo) y menú en Configuración. En el formulario principal, permitir seleccionar este template para rellenar automáticamente el campo `name` (Referencia).
- [ ] **Paso 5: Permisos (ACL).** Validar `ir.model.access.csv`.

## 6. REGLAS ESTRICTAS PARA CODE ASSIST
1. **Pedir Autorización:** Propón la solución antes del código final.
2. **Prohibición de Sobrescritura:** NO alterar la tabla principal que ya está correcta.
3. **Aislamiento de Cambios:** Entrega solo las porciones de código a modificar.