# Módulo de Gestión de Envío (v17.0 Community)

Este módulo está diseñado para centralizar y automatizar la operación logística de envíos internacionales (Aéreos y Marítimos) dentro de **Odoo 17 Community**. Sustituye el manejo de datos en hojas de cálculo por un sistema robusto con validaciones de carga, gestión de seguridad por roles y generación masiva de documentación legal y etiquetas.

---

## 🚀 Funcionalidades Principales

* **App Unificada:** Acceso desde el menú principal de Odoo con una vista de tablero que agrupa Guías Aéreas y Manifiestos Marítimos.
* **Clasificador de Contenedores:** Modelo maestro para gestionar tipos de contenedores (20ST, 40ST, 40HC, 45HC) con sus límites técnicos de peso y volumen.
* **Smart Stats (Dashboard):** Indicadores en tiempo real en la cabecera del formulario:
    * **Total Bultos:** Conteo automático de líneas de envío.
    * **Total Clientes:** Conteo de clientes únicos en el despacho.
    * **Peso Acumulado (Kg):** Sumatoria con alerta visual si excede los límites.
    * **Volumen Total (m³):** Sumatoria comparada contra la capacidad del contenedor.
* **Gestión de Clientes "On-the-fly":** Creación automática de registros en `res.partner` si el cliente ingresado en la línea no existe.
* **Seguridad por Roles:**
    * **Tráfico:** Permiso para carga y edición de bultos/líneas. No puede confirmar documentos.
    * **Administrador:** Control total, creación de cabeceras y botón exclusivo de **Confirmación**.

---

## 🛠 Instalación

1.  Descarga o clona este repositorio en tu carpeta de `addons`.
2.  Asegúrate de que el servidor tenga acceso a las dependencias: `base`, `mail`, `contacts`.
3.  Activa el **Modo Desarrollador** en Odoo.
4.  Ve al menú **Aplicaciones > Actualizar lista de aplicaciones**.
5.  Busca `modulo_gestion_envio` e instálalo.

---

## ⚙️ Configuración Crucial (Paso a Producción)

### 1. Secuencia de Paquetes
El sistema genera códigos únicos con el formato `246-11-XXXXX`. Para mantener la continuidad con el sistema manual anterior:
1.  Navega a **Ajustes > Técnico > Secuencias**.
2.  Busca la secuencia denominada `shipping.management.line`.
3.  En el campo **Siguiente número**, ingresa el número correlativo que sigue según tu último registro en Excel.

### 2. Capacidad de Contenedores
El módulo incluye 4 tipos de contenedores predefinidos. Puedes ajustar sus capacidades en:
* **Gestión de Envío > Configuración > Tipos de Contenedores**.
* Es vital que los campos de **Capacidad m³** y **Peso Máximo** sean correctos para que las alertas de sobrecarga funcionen debidamente.

---

## 📋 Flujo de Trabajo Operativo

1.  **Apertura (ADMIN):** El administrador crea el registro maestro, define si es Aéreo o Marítimo y guarda.
2.  **Carga (TRÁFICO):** El personal de tráfico añade las líneas de envío. Pueden usar la función de **Duplicar Línea** para bultos idénticos de un mismo cliente.
3.  **Auditoría:** El sistema valida:
    * **Aéreo:** Peso total no debe superar los **2500 kg**.
    * **Marítimo:** Volumen total no debe superar la capacidad del contenedor seleccionado.
4.  **Cierre:** El administrador presiona **Confirmar**. El registro pasa a estado **Bloqueado (Read-Only)**, impidiendo modificaciones posteriores.

---

## 🖨️ Reportes e Impresión

* **Etiquetas de Bulto:** Genera 1 etiqueta por cada línea de envío con Código de Barras y QR basado en el ID del paquete.
* **HBL (House Bill of Lading):** * Genera automáticamente **3 copias** por cada bulto.
    * **Optimización de papel:** El diseño QWeb organiza el reporte para imprimir **2 documentos por hoja A4**, ahorrando el 50% de material de oficina.

---

**Versión:** 1.0  
**Compatibilidad:** Odoo 17.0 Community Edition  
**Tecnología:** Python, XML, PostgreSQL, QWeb Reports.