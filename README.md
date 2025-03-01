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

- 📊 **Funcionalidades Clave:**
  - 🎨 Interfaz intuitiva con sistema de colores
  - 📁 Generación automática de logs detallados
  - ⚡ Escaneo multi-hilos eficiente
  - 🔄 Menú interactivo con navegación simplificada
  - 📂 Sistema de reportes organizado por timestamp

## 📦 Instalación

**Requisitos:**
- Python 3.8+
- pip (Gestor de paquetes Python)

```bash
# Clonar repositorio
git clone https://github.com/Santitub/wp-audit-toolkit.git
cd wp-audit-toolkit

# Instalar dependencias
pip install -r requirements.txt
```

**Dependencias:**
- `colorama` - Sistema de colores para consola
- `requests` - Peticiones HTTP avanzadas
- `beautifulsoup4` - Analizador HTML
- `tqdm` - Barras de progreso

## 🖥️ Uso

```bash
python main.py
```

**Flujo de trabajo:**
1. Ingresa URL objetivo
2. Selecciona módulos desde el menú interactivo
3. Analiza resultados en tiempo real
4. Revisa logs detallados en `/logs`

**Menú Principal:**
```
[1] Detectar Enumeración de Usuarios
[2] Analizar XML-RPC
[3] Escáner de Archivos Sensibles
[4] Detectar Versión de WordPress
[5] Auditar REST API
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
    └── rest_api_analyzer.py
```

## 📜 Licencia

Distribuido bajo licencia MIT. Ver [LICENSE](LICENSE) para más detalles.
oftware debe usarse únicamente en sistemas con permiso explícito del propietario. El mal uso es responsabilidad exclusiva del usuario final.
