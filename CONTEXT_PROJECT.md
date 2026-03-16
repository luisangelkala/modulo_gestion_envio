# Contexto del Proyecto: Odoo 17 Community - Módulo Gestión de Envío

## 1. Visión General
Desarrollo de un módulo personalizado para Odoo 17 Community que gestione la logística de envíos internacionales. El sistema reemplaza un flujo de Excel, automatizando validaciones de carga, generación de etiquetas y control de acceso por roles, con un enfoque estricto en la correcta asignación de secuencias de bultos.

## 2. Pila Tecnológica y Estándares
- **Framework:** Odoo 17.0 Community Edition.
- **Frontend:** XML estricto. NO usar `<data>` en las vistas.
- **Relaciones:** Uso intensivo de `Many2one` hacia `res.partner` para evitar duplicidad de datos.
- **Experiencia de Usuario:** Uso de vistas `form` anidadas (Popups) para ingreso de datos complejos en líneas de detalle (One2many), manteniendo las vistas `tree` limpias y resumidas.

## 3. Mapa Real del Módulo
modulo_gestion_envio/
├── __manifest__.py                 # (RESUELTO)
├── CONTEXT_PROJECT.md              # Este archivo
├── ERROR.md                        # Bitácora estricta de errores
├── models/
│   ├── container_type.py           # (RESUELTO)
│   ├── shipping_management.py      # (AJUSTE PENDIENTE - Campos Excel y Confirmación)
│   └── shipping_line.py            # (AJUSTE PENDIENTE - Campos Excel y Popup)
├── security/
│   ├── groups.xml                  # (RESUELTO)
│   └── ir.model.access.csv         # (PENDIENTE)
├── data/
│   ├── sequence.xml                # (RESUELTO - Secuencia 246-11-)
│   └── container_data.xml          # (RESUELTO)
├── views/
│   ├── menus.xml                   # (RESUELTO)
│   ├── container_type_views.xml    # (RESUELTO)
│   └── shipping_management_views.xml # (AJUSTE PENDIENTE - UI Excel, Modal Bultos, Botones Reporte)
└── report/
    └── shipping_reports.xml        # (PENDIENTE)

## 4. Requisitos y Reglas de Negocio Clave
1. **Seguridad de Roles:** Admin (Confirmar) y Tráfico (Líneas).
2. **Campos Cabecera (Excel):** Agencia Origen, País, Consignatario (res.partner), AWB / No. Contenedor, Fecha. El campo `name` (Referencia) se llena **manualmente** (sin secuencia).
3. **Líneas de Bulto (Excel):**
   - **Contactos:** Remitente (`sender_id`) y Destinatario (`receiver_id`), ambos vinculados a `res.partner`.
   - **Datos:** Mercancía (`description`), Cantidad Bultos (`packages_qty` default 1), Largo, Ancho, Alto, Volumen (autocalculado), Peso.
4. **Generación de Código de Bulto (CRÍTICO):**
   - En estado Borrador, el campo `package_code` debe mostrar "Borrador" o un número temporal de línea.
   - **SOLO al hacer clic en Confirmar**, el sistema recorre las líneas y les asigna permanentemente la secuencia `246-11-XXXXX` a cada bulto.
5. **Interfaz de Carga de Bultos:** La tabla de líneas en la cabecera NO debe ser editable "en línea" (`editable="bottom"` removido). Al añadir o editar, debe abrirse un Popup (Form) para ingresar los datos del remitente/destinatario cómodamente.

## 5. Hoja de Ruta y Objetivos Pendientes
- [x] **Paso 1: Interfaz Principal.** (RESUELTO)
- [ ] **Paso 2: Ajuste Estructural (Excel vs Realidad).**
      - **Backend (`shipping_management.py` / `shipping_line.py`):** Añadir campos de cabecera y línea. Modificar `action_confirm` para que asigne la secuencia `shipping.management.line` a los bultos en ese momento.
      - **Frontend (`shipping_management_views.xml`):** Añadir campos a la cabecera. Configurar el `One2many` para que abra un modal (Form) al crear/editar líneas, mostrando todos los campos de contacto y medidas.
- [ ] **Paso 3: Seguridad de Interfaz.** Añadir alerta de confirmación (`confirm="..."`) al botón de Confirmar.
- [ ] **Paso 4: Botones de Reportes.** Añadir botones "Imprimir BL" e "Imprimir Etiquetas" (visibles solo si está confirmado).
- [ ] **Paso 5: Permisos (ACL).** Validar `ir.model.access.csv`.
- [ ] **Paso 6: Reportes PDF.** Activar y vincular `shipping_reports.xml`.

## 6. REGLAS ESTRICTAS PARA CODE ASSIST
1. **Pedir Autorización:** Propón la solución y pide autorización antes de dar el código final.
2. **Prohibición de Sobrescritura:** NO tocar funcionalidades marcadas como (RESUELTO).
3. **Respetar la Bitácora:** Revisa `ERROR.md` siempre.
4. **Aislamiento de Cambios:** Entrega solo las porciones de código a modificar indicando la ruta exacta y la clase/etiqueta.
5. **Actualización del Contexto:** Al finalizar un paso, debes proveer el texto actualizado del Mapa y Hoja de Ruta marcando el progreso.