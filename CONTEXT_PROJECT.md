# Contexto del Proyecto: Odoo 17 Community - Módulo Gestión de Envío

## 1. Visión General
Desarrollo de un módulo personalizado para Odoo 17 Community que gestione la logística de envíos internacionales (Aéreos y Marítimos). El sistema reemplaza un flujo de trabajo basado en Excel, automatizando validaciones de carga, generación de etiquetas y control de acceso por roles.

## 2. Pila Tecnológica
- **Framework:** Odoo 17.0 Community Edition.
- **Lenguaje:** Python 3.10+.
- **Base de Datos:** PostgreSQL.
- **Frontend:** XML (QWeb) y Odoo Web Client.

## 3. Estructura de Datos (Modelos)
### A. Clasificador de Contenedores (`shipping.container.type`)
- Campos: Nombre (20ST, 40ST, etc.), Capacidad m³, Capacidad Kg, Dimensiones.
- Propósito: Datos maestros para validar envíos marítimos.

### B. Gestión de Envío (`shipping.management`)
- Tipo: Selección (Aéreo / Marítimo).
- Estado: Borrador (Draft) / Confirmado (Confirmed).
- Cabecera: Referencia, Fecha, Contenedor (M2O), Naviera/Aerolínea.
- **Smart Stats (Computados):** Total Bultos, Total Clientes, Peso Total (Kg), Volumen Total (m³).

### C. Líneas de Envío (`shipping.management.line`)
- Relación: One2many con el modelo principal.
- Campos: Cliente (M2O a res.partner), Largo, Ancho, Alto, Peso, Volumen (Computado: L*A*H), Código de Paquete.
- **Lógica Automática:** Si el cliente escrito no existe, se crea automáticamente en `res.partner`.

## 4. Reglas de Negocio Clave
1. **Seguridad de Roles:**
   - **Administrador:** Crea cabeceras, selecciona contenedores y tiene el botón "Confirmar".
   - **Tráfico:** Solo añade/edita líneas de envío. No puede confirmar ni crear la guía inicial.
2. **Validación de Capacidad:**
   - **Aéreo:** Peso Total máximo permitido: 2500 kg (Alerta visual y bloqueo).
   - **Marítimo:** El Volumen Total no debe exceder la capacidad del contenedor seleccionado.
3. **Consecutivo:** Formato `246-11-XXXXX` gestionado por `ir.sequence`.
4. **Confirmación:** Una vez confirmado, el registro es de solo lectura. No se puede revertir.

## 5. Salidas (Reporting)
- **Etiquetas:** 1 etiqueta por bulto (incluye Barcode/QR).
- **HBL (House Bill of Lading):** 3 copias por bulto, optimizado para imprimir 2 copias por hoja A4.