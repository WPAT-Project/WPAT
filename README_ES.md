# 🛡️ WordPress Professional Audit Tool - Ethical WordPress Security Auditor

![License](https://img.shields.io/badge/License-GPL--3.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)
![Maintenance](https://img.shields.io/badge/Maintained-Yes-brightgreen.svg)
![Installation](https://img.shields.io/badge/Installation-pipx%20%7C%20git-blueviolet)

Herramienta profesional de auditoría de seguridad para sitios WordPress (uso ético exclusivo).

🔗 Sitio web oficial: [https://wpat.netlify.app/](https://wpat.netlify.app/)

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
  - 🔐 Auditoría SSL/TLS (Certificados y Cifrado)
  - 🗒️ Detección de archivo `security.txt`
  - 🌐 Detector de configuración CORS
  - 🧾 **Generador de Reportes HTML (Nuevo) **

- 🛠 **Funcionalidades Clave:**
  - 🎨 Interfaz intuitiva con sistema de colores y banners ASCII
  - 🖥️ GUI interactiva
  - 📁 Generación automática de logs detallados con marca temporal
  - ⚡ Escaneo multi-hilos configurable (1-50 hilos)
  - 🔄 Menú interactivo con navegación simplificada
  - 🚨 Sistema mejorado de manejo de errores y Ctrl+C
  - 📦 Generador de Wordlists Oficiales (Plugins/Temas)


## 📦 Instalación

### ✅ Método 1: Instalación con pip (modo tradicional)

```bash
# Instalar WPAT (solo consola, sin GUI)
pip install wpat

# Ejecutar WPAT en modo CLI
wpat
```

#### 🖥️ ¿Quieres la versión con interfaz gráfica (GUI)?

```bash
# Instalar WPAT con soporte para GUI (PyQt5)
pip install "wpat[gui]"

# Ejecutar la GUI
wpat-gui
```

---

### ✅ Método 2: Instalación con pipx (Recomendado)

> `pipx` permite una instalación global y aislada, ideal para herramientas CLI.

```bash
# Instalar pipx si no está disponible
python -m pip install --user pipx
python -m pipx ensurepath

# Instalar WPAT (solo CLI)
pipx install wpat

# Ejecutar
wpat
```

#### 🖥️ Para instalar WPAT con GUI usando pipx:

```bash
# Versión GUI usando pipx (con dependencias gráficas)
pipx install "wpat[gui]"

# Ejecutar GUI
wpat --gui
```

---

### 🛠️ Método 3: Instalación desde GitHub

**Opción A – Solo CLI:**

```bash
pipx install git+https://github.com/Santitub/WPAT.git
```

**Opción B – Con soporte GUI:**

```bash
pipx install 'git+https://github.com/Santitub/WPAT.git#egg=wpat[gui]'
```

---

### ⚙️ Método 4: Instalación desde fuente (modo desarrollo)

> Ideal para colaboradores o desarrolladores.

```bash
git clone https://github.com/Santitub/WPAT.git
cd WPAT
pip install ".[gui]"
```

---

### 🐳 Método 5: Instalación con Docker

```bash
# Descargar la imagen oficial de WPAT
sudo docker pull santitub/wpat

# Ejecutar WPAT en contenedor Docker
sudo docker run -it --rm santitub/wpat
```

### 📌 Requisitos del sistema

* Python 3.8 o superior
* pip / pipx
* Acceso a internet para actualizaciones
* Entorno de escritorio si vas a usar la GUI (PyQt5)

### 📚 Dependencias

Estas son las bibliotecas necesarias para el correcto funcionamiento de WPAT:

* `colorama` — Sistema de colores para consola
* `requests` — Peticiones HTTP avanzadas
* `beautifulsoup4` — Analizador HTML
* `tqdm` — Barras de progreso interactivas
* `pyqt5` — Soporte para la interfaz gráfica de usuario (GUI)
* `PyQtWebEngine` — Motor de renderizado web embebido en la GUI
* `urllib3` — Manejo avanzado de conexiones HTTP

## 🖥️ Uso

```bash
# Desde pip/pipx
wpat / wpat --gui)

# Desde Docker
docker run -it --rm santitub/wpat

# Desde GUI
python main.py --gui
```

**Flujo de trabajo:**
1. Ingresa URL objetivo
2. Selecciona módulos desde el menú interactivo o GUI
3. Analiza resultados en tiempo real con salida limpia
4. Revisa logs detallados en `/logs`

### **Menú Principal:**

```
[1] Detectar Enumeración de Usuarios      [97] Auditoría Completa
[2] Analizar XML-RPC                      [98] Generar Wordlists
[3] Escáner de Archivos Sensibles         [99] Salir
[4] Detectar Versión de WordPress
[5] Auditar REST API
[6] Escáner de Plugins
[7] Escáner de Temas 
[8] Fuerza Bruta en Login
[9] Verificar Certificado SSL
[10] Verificar Security.txt
[11] Verificar CORS
```

## 📂 Estructura del Proyecto

```
WPAT/
├── main.py             # Script principal
├── gui.py              # Interfaz gráfica (nueva)
├── requirements.txt    # Dependencias
├── logs/               # Registros de auditorías
├── wordlists/          # Listas oficiales generadas
└── scripts/            # Módulos de auditoría
    ├── __init__.py
    ├── ssl_checker.py
    ├── cors_detector.py          
    ├── user_enumeration.py
    ├── xmlrpc_analyzer.py
    ├── sensitive_files.py
    ├── wp_version.py
    ├── rest_api_analyzer.py
    ├── security_txt.py           
    ├── plugin_scanner.py
    ├── theme_scanner.py
    └── brute_force.py
    └── html_report.py           # Nuevo
```

## 🆕 Novedades en v2.1

* 🧾 Nuevo módulo de reportes en **HTML**
* ⚙️ Mejoras en las peticiones de los módulos


## 📜 Licencia y Ética

Distribuido bajo licencia **GPL-3.0**.
Ver [LICENSE](LICENSE) para más detalles.

**⚠️ Nota de Uso Ético:**  
Este software debe usarse únicamente en sistemas con permiso explícito del propietario. Incluye características avanzadas que podrían ser consideradas intrusivas si se usan sin autorización. El mal uso es responsabilidad exclusiva del usuario final.
