# Contexto del Proyecto: Odoo 17 Community - Módulo Gestión de Envío

## 1. Visión General
Desarrollo de un módulo personalizado para Odoo 17 Community que gestione la logística de envíos internacionales. El sistema automatiza validaciones de carga, generación de etiquetas y control de acceso, con un enfoque estricto en la correcta asignación de secuencias de bultos al confirmar.

## 2. Pila Tecnológica y Estándares
- **Framework:** Odoo 17.0 Community Edition.
- **Frontend:** XML estricto. NO usar `<data>` en las vistas.
- **Experiencia de Usuario:** Uso de vistas `form` anidadas (Popups) para líneas de detalle.
- **Reportes:** QWeb Reports. Los reportes deben abrirse nativamente para actuar como "Vista Previa" antes de la impresión física.

## 3. Mapa Real del Módulo
modulo_gestion_envio/
├── __manifest__.py                 # (RESUELTO)
├── CONTEXT_PROJECT.md              # Este archivo
├── ERROR.md                        # Bitácora estricta de errores
├── models/
│   ├── container_type.py           # (RESUELTO)
│   ├── shipping_management.py      # (RESUELTO - Lógica Excel y Confirmación)
│   └── shipping_line.py            # (RESUELTO - Popup y lógica completada)
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
    └── shipping_reports.xml        # (EN REFACTORIZACIÓN CRÍTICA - HBL)

## 4. Requisitos y Reglas de Negocio Clave
1. **Seguridad de Roles:** Admin (Confirmar) y Tráfico (Líneas).
2. **Campos Cabecera:** Agencia, País, Consignatario, AWB / Contenedor, Fecha.
3. **Líneas de Bulto:** Remitente y Destinatario (res.partner), Mercancía, Cantidad, Medidas, Volumen, Peso.
4. **Generación de Código:** Secuencia estricta asignada únicamente al hacer clic en "Confirmar".
5. **Reportes (CRÍTICO):** El BL NO es un manifiesto global (resumen). Es un **HBL (House Bill of Lading)**. 
   - Por CADA línea (bulto) deben generarse **3 copias idénticas** del documento.
   - El formato físico debe acomodar **2 copias por cada hoja A4** (usando CSS para forzar el alto al 50% de la página o saltos de página controlados).

## 5. Hoja de Ruta y Objetivos Pendientes
- [x] **Paso 1, 2 y 3: Interfaz, Ajuste Estructural y Seguridad.** (RESUELTO)
- [x] **Paso 4.1: REFACTORIZACIÓN - Reporte PDF del HBL.** (RESUELTO)
      - El template QWeb ha sido reescrito para generar HBLs individuales.
      - Se implementó un bucle anidado que itera sobre cada bulto y genera 3 copias.
      - Se utilizó CSS (`height: 48vh`, `page-break-inside: avoid`) para forzar la paginación de 2 documentos por hoja A4, optimizando el uso de papel.
- [ ] **Paso 4.2: Reporte PDF de Etiquetas.** (En espera).
- [ ] **Paso 5: Permisos (ACL).** Validar `ir.model.access.csv`.

## 6. REGLAS ESTRICTAS PARA CODE ASSIST
1. **Pedir Autorización:** Propón la solución y pide autorización antes de dar el código final.