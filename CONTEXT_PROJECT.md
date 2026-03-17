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
2. **Campos Cabecera:** Agencia, País, Consignatario, AWB / Contenedor, Fecha.
3. **Líneas de Bulto:** Remitente y Destinatario (res.partner), Mercancía, Cantidad, Medidas, Volumen, Peso.
4. **Generación de Código:** Secuencia estricta asignada únicamente al hacer clic en "Confirmar".
5. **Reportes (CRÍTICO):** El BL es un **HBL (House Bill of Lading)**. 
   - Por CADA línea (bulto) deben generarse **3 copias idénticas**.
   - El formato físico debe acomodar **exactly 2 copias por cada hoja A4**.
   - El diseño debe ser una cuadrícula estricta (Grid) usando tablas HTML con bordes, imitando un formulario de aduana, e incluyendo textos legales estáticos.

## 5. Hoja de Ruta y Objetivos Pendientes
- [x] **Paso 1, 2 y 3: Interfaz, Ajuste Estructural y Seguridad.** (RESUELTO)
- [x] **Paso 4.1: MAQUETACIÓN CSS/HTML - Reporte PDF del HBL.** (RESUELTO)
      - **Frontend (Diseño):** Se ha reescrito el template QWeb usando una cuadrícula estricta de tablas HTML (`<table style="border-collapse: collapse;">`) para imitar un formulario aduanero.
      - Se han incrustado los textos legales fijos (Notify Party, Puertos) y se extraen los datos de contacto completos (dirección, teléfono, VAT) del remitente y destinatario.
- [ ] **Paso 4.2: Reporte PDF de Etiquetas.** (En espera).
- [ ] **Paso 5: Permisos (ACL).** Validar `ir.model.access.csv`.

## 6. REGLAS ESTRICTAS PARA CODE ASSIST
1. **Pedir Autorización:** Propón la solución y pide autorización antes de dar el código final.
2. **Prohibición de Sobrescritura:** NO tocar funcionalidades marcadas como (RESUELTO).
3. **Respetar la Bitácora:** Revisa `ERROR.md` siempre. 
4. **Aislamiento de Cambios:** Entrega solo las porciones de código a modificar indicando la ruta exacta.
5. **Actualización del Contexto:** Al finalizar un paso, proveer el texto actualizado.