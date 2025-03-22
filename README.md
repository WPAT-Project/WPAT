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
  - 🧩 Escáner de Plugins (detecta instalaciones activas)
  - 🎨 Escáner de Temas (detección por estilo CSS)
  - 🔓 Fuerza Bruta Optimizada (Login WordPress)

- 🛠 **Funcionalidades Clave:**
  - 🎨 Interfaz intuitiva con sistema de colores y banners ASCII
  - 📁 Generación automática de logs detallados con marca temporal
  - ⚡ Escaneo multi-hilos configurable (1-50 hilos)
  - 🌀 Barra de progreso inteligente que desaparece al finalizar
  - 🚨 Sistema mejorado de manejo de errores y Ctrl+C
  - 🔄 Menú interactivo con navegación simplificada
  - 📦 Generador de Wordlists Oficiales (Plugins/Temas)
  - 🔄 **Carga unificada de wordlists** para todos los módulos

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
3. Para escaneos de plugins/temas/fuerza bruta:
   - ⚡ Proporciona ruta de wordlist (detección automática de encoding)
   - 📊 Visualiza estadísticas de carga (tiempo/líneas)
   - ⚙️ Configura hilos (1-50) y timeout
4. Analiza resultados en tiempo real con salida limpia
5. Revisa logs detallados en `/logs`

**Menú Principal:**
```
[1] Detectar Enumeración de Usuarios      [97] Auditoría Completa
[2] Analizar XML-RPC                      [98] Generar Wordlists
[3] Escáner de Archivos Sensibles         [99] Salir
[4] Detectar Versión de WordPress
[5] Auditar REST API
[6] Escáner de Plugins
[7] Escáner de Temas 
[8] Fuerza Bruta en Login (Nuevo)
```

## 📂 Estructura del Proyecto

```
WPAT/
├── main.py             # Script principal
├── requirements.txt    # Dependencias
├── logs/               # Registros de auditorías
├── wordlists/          # Listas oficiales generadas
└── scripts/            # Módulos de auditoría
    ├── __init__.py
    ├── user_enumeration.py
    ├── xmlrpc_analyzer.py
    ├── sensitive_files.py
    ├── wp_version.py
    ├── rest_api_analyzer.py
    ├── plugin_scanner.py
    ├── theme_scanner.py
    ├── brute_force.py     # Nuevo módulo
    └── wordlists.py
```

## 🆕 Novedades en v1.5

### 🚀 Motor de Fuerza Bruta Mejorado
- **Carga Inteligente de Wordlists:**
  - ⏱️ 2x más rápido en archivos grandes (>1GB)
  - 🔍 Detección automática de encoding (UTF-8/Latin-1/CP1252)
  - 🛠️ Sistema unificado de carga para todos los módulos
  - 📈 Estadísticas de carga (líneas/tiempo/encoding)

## 📜 Licencia y Ética

Distribuido bajo licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

**⚠️ Nota de Uso Ético:**  
Este software debe usarse únicamente en sistemas con permiso explícito del propietario. Incluye características avanzadas que podrían ser consideradas intrusivas si se usan sin autorización. El mal uso es responsabilidad exclusiva del usuario final.
