# Contexto del Proyecto: Odoo 17 Community - Módulo Gestión de Envío

## 1. Visión General
Desarrollo de un módulo personalizado para Odoo 17 Community que gestione la logística de envíos internacionales. El sistema automatiza validaciones de carga, generación de etiquetas y control de acceso.

## 2. Pila Tecnológica y Estándares
- **Framework:** Odoo 17.0 Community Edition.
- **Frontend:** XML estricto. NO usar `<data>` en las vistas.
- **Reportes:** QWeb Reports. Los reportes deben abrirse nativamente para actuar como "Vista Previa" antes de la impresión física.

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
    └── shipping_reports.xml        # (EN MAQUETACIÓN FRONTEND - HBL)

## 4. Requisitos y Reglas de Negocio Clave
1. **Seguridad de Roles:** Admin (Confirmar) y Tráfico (Líneas).
2. **Generación de Código:** Secuencia estricta asignada únicamente al confirmar.
3. **Reportes (CRÍTICO - Diseño HBL):** - El HBL debe generar **3 copias idénticas por bulto** e imprimir **2 copias por hoja A4** (Lógica backend resuelta).
   - **Maquetación (Frontend):** Debe ser una cuadrícula estricta (Grid) usando tablas HTML con bordes negros (`border-collapse: collapse`), imitando el formulario de aduana original.
   - **Mapeo de Datos:** La referencia principal del HBL es el código único del bulto (`line.package_code`), NO el nombre de la guía.

## 5. Hoja de Ruta y Objetivos Pendientes
- [x] **Paso 1, 2 y 3: Interfaz, Ajuste Estructural y Seguridad.** (RESUELTO)
- [ ] **Paso 4.1: MAQUETACIÓN CSS/HTML PIXEL-PERFECT - Reporte HBL.**
      - **Backend:** Mantener la iteración actual (3 copias por `line`, 2 por página).
      - **Frontend (Estructura Legal):** Construir una tabla maestra HTML que contenga los recuadros exactos del PDF original:
        - *Cajas Superiores:* "SHIPPER" (con info de `sender_id`), "CONSIGNED TO" (con info de `receiver_id`), "EXPORT REFERENCES" (debe mostrar `line.package_code` en grande).
        - *Cajas Fijas:* "NOTIFY PARTY: ORDAZ INVESTMENT GROUP, S.A...", "PORT OF DISCHARGE: MARIEL, CU.", "PLACE OF DELIVERY: CUBANACAN".
        - *Tabla de Mercancía:* Columnas "MARKS AND NUMBERS" (mostrar `line.package_code`), "NUMBER OF PACKS" (1), "DESCRIPTION OF COMMODITIES", "GROSS WEIGHT (kg)" (