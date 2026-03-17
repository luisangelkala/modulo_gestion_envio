# Contexto del Proyecto: Odoo 17 Community - Módulo Gestión de Envío

## 1. Visión General
Desarrollo de un módulo personalizado para Odoo 17 Community que gestione la logística de envíos internacionales. El sistema automatiza validaciones de carga, generación de etiquetas y control de acceso, con un enfoque estricto en la correcta asignación de secuencias de bultos al confirmar.

## 2. Pila Tecnológica y Estándares
- **Framework:** Odoo 17.0 Community Edition.
- **Frontend:** XML estricto. NO usar `<data>` en las vistas.
- **Experiencia de Usuario:** Uso de vistas `form` anidadas (Popups) para líneas de detalle.
- **Reportes:** QWeb Reports. Los reportes deben abrirse en una nueva pestaña (visor de PDF del navegador) para actuar como "Vista Previa" antes de la impresión física.

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
│   └── shipping_management_views.xml # (RESUELTO - UI base lista)
└── report/
    └── shipping_reports.xml        # (EN DESARROLLO - HBL y Etiquetas)

## 4. Requisitos y Reglas de Negocio Clave
1. **Seguridad de Roles:** Admin (Confirmar) y Tráfico (Líneas).
2. **Campos Cabecera:** Agencia, País, Consignatario, AWB / Contenedor, Fecha.
3. **Líneas de Bulto:** Remitente y Destinatario (res.partner), Mercancía, Cantidad, Medidas, Volumen, Peso.
4. **Generación de Código:** Secuencia estricta asignada únicamente al hacer clic en "Confirmar".
5. **Reportes y Vista Previa:** Documentos generados vía QWeb. Deben invocarse desde botones en la cabecera (visibles solo si está confirmado) y generar un PDF visualizable en el navegador. El BL debe replicar la estructura del Excel original (Cabecera general + Tabla de detalle con remitentes/destinatarios).
   - **Excepción:** El BL puede imprimirse en estado Borrador para revisión, pero la columna "Código" aparecerá vacía.

## 5. Hoja de Ruta y Objetivos Pendientes
- [x] **Paso 1: Interfaz Principal.** (RESUELTO)
- [x] **Paso 2 y 3: Ajuste Estructural (Excel) y Seguridad.** (RESUELTO)
- [x] **Paso 4.1: Reporte PDF del BL (Manifiesto).** (RESUELTO - Botón visible siempre, lógica de columna vacía en borrador, menú Acciones limpio).
      - Añadir botón "Imprimir BL" en el `<header>` de `shipping_management_views.xml` (visible solo si `state == 'confirmed'`).
      - Definir el `<record model="ir.actions.report">` para el BL en `report/shipping_reports.xml`.
      - Diseñar el `<template>` QWeb del BL para que muestre la información general de la Guía y una tabla iterando las líneas con Remitente, Destinatario, Mercancía, Peso, Volumen y Código.
- [ ] **Paso 4.2: Reporte PDF de Etiquetas.** (En espera).
- [ ] **Paso 5: Permisos (ACL).** Validar `ir.model.access.csv`.

## 6. REGLAS ESTRICTAS PARA CODE ASSIST
1. **Pedir Autorización:** Propón la solución y pide autorización antes de dar el código final.
2. **Prohibición de Sobrescritura:** NO tocar funcionalidades marcadas como (RESUELTO).
3. **Respetar la Bitácora:** Revisa `ERROR.md` siempre. Evita el Error #003 usando llamadas directas de acción en lugar de bindings automáticos si generan conflicto.
4. **Aislamiento de Cambios:** Entrega solo las porciones de código a modificar indicando la ruta exacta.
5. **Actualización del Contexto:** Al finalizar un paso, proveer el texto actualizado del Mapa y Hoja de Ruta.