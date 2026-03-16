# Contexto del Proyecto: Odoo 17 Community - Módulo Gestión de Envío

## 1. Visión General
Desarrollo de un módulo personalizado para Odoo 17 Community que gestione la logística de envíos internacionales (Aéreos y Marítimos). El sistema reemplaza un flujo de trabajo basado en Excel, automatizando validaciones de carga, generación de etiquetas y control de acceso por roles.

## 2. Pila Tecnológica y Estándares
- **Framework:** Odoo 17.0 Community Edition.
- **Lenguaje:** Python 3.10+.
- **Frontend:** XML estricto (QWeb).
- **Estándar Odoo 17:** - NO usar la etiqueta `<data>` envolviendo los registros en los archivos de vistas (`views/*.xml`) para evitar errores RelaxNG.
  - Usar `invisible="..."` y `readonly="..."` con dominios directos en lugar del obsoleto `attrs`.
  - La arquitectura de menús raíz debe estar desacoplada en un archivo exclusivo (`menus.xml`) cargado antes que las vistas.

## 3. Mapa Real del Módulo (Estado Actual Verificado)
modulo_gestion_envio/
├── __init__.py
├── __manifest__.py                 # (RESUELTO - Orden de carga validado)
├── CONTEXT_PROJECT.md              # Este archivo
├── ERROR.md                        # Bitácora estricta de errores solucionados
├── models/
│   ├── __init__.py
│   ├── container_type.py           # (RESUELTO - Datos maestros)
│   ├── shipping_management.py      # (RESUELTO - Lógica de cabecera y reglas de capacidad)
│   └── shipping_line.py            # (PARCIAL - Falta autogenerar 'package_code')
├── security/
│   ├── groups.xml                  # (RESUELTO - Roles de Tráfico y Admin)
│   └── ir.model.access.csv         # (PENDIENTE - Validar permisos CRUD)
├── data/
│   ├── sequence.xml                # (RESUELTO - Secuencia 246-11-)
│   └── container_data.xml          # Datos base
├── views/
│   ├── menus.xml                   # (RESUELTO - Menús raíz desacoplados)
│   ├── container_type_views.xml    # (RESUELTO - Vista completa)
│   └── shipping_management_views.xml # (PARCIAL - Falta Action y Tree view)
└── report/
    └── shipping_reports.xml        # (PENDIENTE - Etiquetas QR y HBL)

## 4. Requisitos y Reglas de Negocio Clave
1. **Seguridad de Roles:**
   - **Usuario Administrador:** Crea cabeceras, selecciona contenedores y tiene el botón "Confirmar" (Exclusivo).
   - **usuario empleado Tráfico:** Solo añade/edita líneas de envío. No puede confirmar.
2. **Validación de Capacidad (Backend):**
   - **Aéreo:** Peso Total máximo permitido: 2500 kg (Alerta visual y bloqueo).
   - **Marítimo:** El Volumen Total no debe exceder la capacidad del contenedor seleccionado.
3. **Confirmación:** Una vez confirmado, el registro es de solo lectura absoluto (Controlado en el `write` del modelo).
4. **Consecutivos y Códigos:** - Envío: Formato `246-11-XXXXX` gestionado por `ir.sequence`.
   - Bultos: Generación automática de código único (`package_code`) al guardar la línea.
5. **Smart Stats (Dashboard):** Cálculo en tiempo real de Total Bultos, Total Clientes, Peso Total (Kg) y Volumen Total (m³).

## 5. Hoja de Ruta y Objetivos Pendientes
El desarrollo debe seguir un enfoque iterativo y paso a paso. No avanzar al siguiente hasta validar el actual:
- [ ] **Paso 1: Interfaz Principal.** Completar `shipping_management_views.xml` agregando el `<record model="ir.ui.view">` para el `tree` y el `<record model="ir.actions.act_window">` para poder acceder al módulo desde los menús.
- [ ] **Paso 2: Código de Bulto.** Añadir la lógica en `shipping_line.py` para generar automáticamente el campo `package_code` (Ej. REF-ENVIO-LINEA-1) sin intervención del usuario.
- [ ] **Paso 3: Permisos (ACL).** Redactar y asegurar que el archivo `ir.model.access.csv` otorgue los permisos correctos a los grupos definidos en `groups.xml`.
- [ ] **Paso 4: Reportes.** Corregir y activar `shipping_reports.xml` para las etiquetas QR y las 3 copias del HBL optimizadas para A4.

## 6. REGLAS ESTRICTAS PARA EL ASISTENTE IA (CODE ASSIST)
Para mantener la integridad del sistema, la IA debe adherirse obligatoriamente a estas directivas:
1. **Pedir Autorización:** Siempre debes proponer la solución, explicar el "por qué" y pedir autorización antes de generar bloques de código finales.
2. **Prohibición de Sobrescritura:** NO tocar, modificar ni sugerir cambios en archivos o funcionalidades marcadas como `(RESUELTO)` en el Mapa del Módulo, a menos que el usuario lo solicite explícitamente.
3. **Respetar la Bitácora:** Revisar siempre el archivo `ERROR.md` si se provee en el prompt para no volver a aplicar soluciones que ya fallaron (Ej: No sugerir usar la etiqueta `<data>` en las vistas).
4. **Aislamiento de Cambios:** Entregar solo las porciones de código que se van a añadir o modificar, indicando exactamente en qué archivo y bajo qué etiqueta/clase van, en lugar de reescribir archivos enteros de cientos de líneas innecesariamente.
5. **Actualización del Contexto:** Cada vez que el usuario te autorice a dar por concluido un paso de la Hoja de Ruta, es tu obligación generar el texto actualizado para las secciones "3. Mapa Real del Módulo" y "5. Hoja de Ruta y Objetivos Pendientes", marcando el paso como (RESUELTO).