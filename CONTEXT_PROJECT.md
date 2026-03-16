# Contexto del Proyecto: Odoo 17 Community - Módulo Gestión de Envío

## 1. Visión General
Desarrollo de un módulo personalizado para Odoo 17 Community que gestione la logística de envíos internacionales (Aéreos y Marítimos). El sistema reemplaza un flujo de trabajo basado en Excel, automatizando validaciones de carga, generación de etiquetas y control de acceso por roles.

## 2. Pila Tecnológica y Estándares
- **Framework:** Odoo 17.0 Community Edition.
- **Lenguaje:** Python 3.10+.
- **Frontend:** XML estricto (QWeb).
- **Estándar Odoo 17:** - NO usar la etiqueta `<data>` envolviendo los registros en los archivos de vistas (`views/*.xml`) para evitar errores RelaxNG.
  - Usar `invisible="..."` y `readonly="..."` con dominios directos.
  - La arquitectura de menús raíz debe estar desacoplada en un archivo exclusivo (`menus.xml`) cargado antes que las vistas.

## 3. Mapa Real del Módulo (Estado Actual Verificado)
modulo_gestion_envio/
├── __init__.py
├── __manifest__.py                 # (RESUELTO)
├── CONTEXT_PROJECT.md              # Este archivo
├── ERROR.md                        # Bitácora estricta de errores
├── models/
│   ├── __init__.py
│   ├── container_type.py           # (RESUELTO)
│   ├── shipping_management.py      # (AJUSTE PENDIENTE - Campos Excel y Secuencia)
│   └── shipping_line.py            # (AJUSTE PENDIENTE - Secuencia en bultos)
├── security/
│   ├── groups.xml                  # (RESUELTO)
│   └── ir.model.access.csv         # (PENDIENTE)
├── data/
│   ├── sequence.xml                # (RESUELTO - Secuencia 246-11-)
│   └── container_data.xml          # (RESUELTO)
├── views/
│   ├── menus.xml                   # (RESUELTO - Menú "Gestión de Envío" listo)
│   ├── container_type_views.xml    # (RESUELTO)
│   └── shipping_management_views.xml # (AJUSTE PENDIENTE - UI de campos nuevos y alerta)
└── report/
    └── shipping_reports.xml        # (PENDIENTE)

## 4. Requisitos y Reglas de Negocio Clave
1. **Seguridad de Roles:** Admin (Control total, Confirmar) y Tráfico (Solo líneas).
2. **Campos Cabecera (Basados en Excel):** El formulario debe incluir: Agencia Origen, País, Consignatario, AWB / No. Contenedor, y Fecha.
3. **Validación de Capacidad:** Alertas y bloqueos aéreos (2500kg) y marítimos (volumen vs contenedor).
4. **Confirmación Segura:** El botón confirmar debe tener una alerta emergente de seguridad (confirm dialog). Una vez confirmado, todo es Read-Only.
5. **Consecutivos y Códigos (CRÍTICO):** - **Guía/Envío (Cabecera):** Entrada MANUAL por el usuario (No usar secuencia automática aquí).
   - **Bultos (Líneas):** La secuencia automática `246-11-XXXXX` se aplica a cada línea (`package_code`) al momento de crearse/guardarse.
6. **Smart Stats:** Cálculo de Bultos, Clientes, Peso y Volumen.

## 5. Hoja de Ruta y Objetivos Pendientes
- [x] **Paso 1: Interfaz Principal.** (RESUELTO)
- [ ] **Paso 2: Ajustes de Negocio (Excel vs Realidad).** - Añadir campos de Excel a `shipping.management` (agencia, pais, consignatario, awb).
      - Quitar la secuencia de `shipping_management.py` (dejar el `name` manual).
      - Mover la inyección de la secuencia a `shipping_line.py` (`package_code`).
      - Añadir `confirm="¿Está seguro que desea confirmar?..."` al botón en el XML.
- [ ] **Paso 3: Botones de Reportes.** Añadir botones "Imprimir BL" e "Imprimir Etiquetas" en el header del formulario.
- [ ] **Paso 4: Permisos (ACL).** Validar `ir.model.access.csv`.
- [ ] **Paso 5: Reportes PDF.** Activar `shipping_reports.xml`.

## 6. REGLAS ESTRICTAS PARA CODE ASSIST
1. **Pedir Autorización:** Propón la solución y pide autorización antes de dar el código final.
2. **Prohibición de Sobrescritura:** NO tocar lo que funciona.
3. **Respetar la Bitácora:** Revisa `ERROR.md` siempre.
4. **Aislamiento de Cambios:** Entrega solo las porciones de código a modificar indicando la ruta exacta.
5. **Actualización del Contexto:** Al finalizar un paso, debes proveer el texto actualizado del Mapa y Hoja de Ruta marcando el progreso.