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
    └── shipping_reports.xml        # (EN MAQUETACIÓN FRONTEND - CORRECCIÓN HBL)

## 4. Requisitos y Reglas de Negocio Clave
1. **Seguridad de Roles:** Admin (Confirmar) y Tráfico (Líneas).
2. **Generación de Código:** Secuencia estricta asignada únicamente al confirmar.
3. **Reportes (CRÍTICO - Diseño HBL):** - El HBL debe generar **3 copias idénticas por bulto** e imprimir **2 copias por hoja A4**.
   - **Maquetación (Frontend):** Cuadrícula estricta (Grid) con tablas HTML (`border-collapse: collapse; border: 1px solid black;`).
   - **Mapeo de Datos:** La referencia principal del HBL es el código único del bulto (`line.package_code`), NO el nombre de la guía general.

## 5. Hoja de Ruta y Objetivos Pendientes
- [x] **Paso 1, 2 y 3: Interfaz, Ajuste Estructural y Seguridad.** (RESUELTO)
- [x] **Paso 4.1: MAQUETACIÓN CSS/HTML PIXEL-PERFECT - Reporte HBL.** (RESUELTO)
      - Implementado formato estricto: Tabla única con bordes colapsados.
      - Cabecera: "COMBINED TRANSPORT BILL OF LADING" y "EXPORT REFERENCES" (package_code).
      - Columnas de mercancía en inglés exacto (MARKS AND NUMBERS, VALOR USD, etc.).
      - Pie de página aduanero obligatorio con caja "Sólo para uso de la Aduana".
- [ ] **Paso 4.2: Reporte PDF de Etiquetas.** (En espera).
- [ ] **Paso 5: Permisos (ACL).** Validar `ir.model.access.csv`.

## 6. REGLAS ESTRICTAS PARA CODE ASSIST
1. **Pedir Autorización:** Propón la solución y pide autorización antes de dar el código final.
2. **Prohibición de Sobrescritura:** NO tocar funcionalidades marcadas como (RESUELTO).
3. **Respetar la Bitácora:** Revisa `ERROR.md` siempre.
4. **Aislamiento de Cambios:** Entrega solo las porciones de código a modificar.
5. **Actualización del Contexto:** Al finalizar un paso, proveer el texto actualizado.