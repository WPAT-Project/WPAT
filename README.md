# 🛡️ WP Audit Toolkit - Ethical WordPress Security Auditor

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)
![Maintenance](https://img.shields.io/badge/Maintained-Yes-brightgreen.svg)

Herramienta profesional de auditoría de seguridad para sitios WordPress (uso ético exclusivo)

## 🚀 Características Principales

- 🔍 **Módulos Especializados:**
  - 🕵️ Detección de Enumeración de Usuarios
  - 🛑 Análisis de Vulnerabilidades XML-RPC
  - 📂 Escáner de Archivos Sensibles Expuestos
  - 🔖 Fingerprinting de Versión de WordPress
  - 📡 Auditoría de Endpoints REST API
  - 🧩 **Nuevo** Escáner de Plugins (detecta instalaciones activas)

- 🛠 **Funcionalidades Clave:**
  - 🎨 Interfaz intuitiva con sistema de colores y banners ASCII
  - 📁 Generación automática de logs detallados con marca temporal
  - ⚡ Escaneo multi-hilos configurable (1-50 hilos)
  - 🌀 Barra de progreso inteligente que desaparece al finalizar
  - 🚨 Sistema mejorado de manejo de errores
  - 🔄 Menú interactivo con navegación simplificada

## 📦 Instalación

**Requisitos:**
- Python 3.8+
- pip (Gestor de paquetes Python)

```bash
# Clonar repositorio
git clone https://github.com/Santitub/WPAT.git
cd WPAT

# Instalar dependencias
pip install -r requirements.txt
```

**Dependencias:**
- `colorama` - Sistema de colores para consola
- `requests` - Peticiones HTTP avanzadas
- `beautifulsoup4` - Analizador HTML
- `tqdm` - Barras de progreso interactivas

## 🖥️ Uso

```bash
python main.py
```

**Flujo de trabajo:**
1. Ingresa URL objetivo
2. Selecciona módulos desde el menú interactivo
3. Para el escáner de plugins:
   - Proporciona ruta de wordlist
   - Configura hilos y timeout
4. Analiza resultados en tiempo real
5. Revisa logs detallados en `/logs`

**Menú Principal Actualizado:**
```
[1] Detectar Enumeración de Usuarios
[2] Analizar XML-RPC
[3] Escáner de Archivos Sensibles
[4] Detectar Versión de WordPress
[5] Auditar REST API
[6] Escáner de Plugins (Nuevo)
[7] Ejecutar Auditoría Completa
[8] Salir del Programa
```

## 📂 Estructura del Proyecto

```
wp-audit-toolkit/
├── main.py             # Script principal
├── requirements.txt    # Dependencias
├── logs/               # Registros de auditorías
└── scripts/            # Módulos de auditoría
    ├── __init__.py
    ├── user_enumeration.py
    ├── xmlrpc_analyzer.py
    ├── sensitive_files.py
    ├── wp_version.py
    ├── rest_api_analyzer.py
    └── plugin_scanner.py  # Nuevo módulo
```

## 🆕 Novedades en v1.1
- ✨ **Escáner de Plugins Avanzado:**
  - Detección por códigos de estado HTTP
  - Verificación de archivos readme.txt
  - Soporte para wordlists personalizadas
- 🖥️ **Mejoras de Interfaz:**
  - Banners decorativos para cada módulo
  - Sistema de iconos para resultados (✅/⚠️/☠️)
  - Tablas de resultados estilizadas
- 🛠️ **Optimizaciones:**
  - Manejo profesional de Ctrl+C
  - Limpieza automática de output
  - Threading seguro con timeouts

## 📜 Licencia y Ética

Distribuido bajo licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

**⚠️ Nota de Uso Ético:**  
Este software debe usarse únicamente en sistemas con permiso explícito del propietario. Incluye características avanzadas que podrían ser consideradas intrusivas si se usan sin autorización. El mal uso es responsabilidad exclusiva del usuario final.
