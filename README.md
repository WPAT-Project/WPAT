# 🛡️ WordPress Professional Audit Tool - Ethical WordPress Security Auditor

![License](https://img.shields.io/badge/License-GPL--3.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)
![Maintenance](https://img.shields.io/badge/Maintained-Yes-brightgreen.svg)
![Installation](https://img.shields.io/badge/Installation-pipx%20%7C%20git-blueviolet)

Professional security audit tool for WordPress sites (exclusive ethical use).

🔗 Official website: [https://wpat.netlify.app/](https://wpat.netlify.app/)

## 🚀 Main Features

* 🔍 **Specialized Modules:**

  * 🕵️ User Enumeration Detection
  * 🛑 XML-RPC Vulnerability Analysis
  * 📂 Exposed Sensitive Files Scanner
  * 🔖 WordPress Version Fingerprinting
  * 📡 REST API Endpoints Audit
  * 🧩 Plugin Scanner (detects active installations)
  * 🎨 Theme Scanner (detection by CSS style)
  * 🔓 Optimized Brute Force (WordPress Login)
  * 🔐 SSL/TLS Audit (Certificates and Encryption)
  * 🗒️ **`security.txt` file detection (New)**
  * 🌐 **CORS configuration detector (New)**

* 🛠 **Key Features:**

  * 🎨 Intuitive interface with color scheme and ASCII banners
  * 🖥️ **New interactive GUI**
  * 📁 Automatic generation of detailed logs with timestamps
  * ⚡ Configurable multi-threaded scanning (1-50 threads)
  * 🔄 Interactive menu with simplified navigation
  * 🚨 Enhanced error handling and Ctrl+C system
  * 📦 Official Wordlist Generator (Plugins/Themes)

## 📦 Installation

### ✅ Method 1: Installation via pip (traditional mode)

```bash
# Install WPAT (CLI only, no GUI)
pip install wpat

# Run WPAT in CLI mode
wpat
```

#### 🖥️ Want the version with GUI?

```bash
# Install WPAT with GUI support (PyQt5)
pip install "wpat[gui]"

# Run the GUI
wpat-gui
```

---

### ✅ Method 2: Installation via pipx (Recommended)

> `pipx` allows for global and isolated installation, ideal for CLI tools.

```bash
# Install pipx if not available
python -m pip install --user pipx
python -m pipx ensurepath

# Install WPAT (CLI only)
pipx install wpat

# Run it
wpat
```

#### 🖥️ To install WPAT with GUI using pipx:

```bash
# GUI version using pipx (with graphical dependencies)
pipx install "wpat[gui]"

# Run GUI
wpat --gui
```

---

### 🛠️ Method 3: Installation from GitHub

**Option A – CLI only:**

```bash
pipx install git+https://github.com/Santitub/WPAT.git
```

**Option B – With GUI support:**

```bash
pipx install 'git+https://github.com/Santitub/WPAT.git#egg=wpat[gui]'
```

---

### ⚙️ Method 4: Installation from source (development mode)

> Ideal for contributors or developers.

```bash
git clone https://github.com/Santitub/WPAT.git
cd WPAT
pip install ".[gui]"
```

---

### 🐳 Method 5: Installation with Docker

```bash
# Download the official WPAT image
sudo docker pull santitub/wpat

# Run WPAT in Docker container
sudo docker run -it --rm santitub/wpat
```

### 📌 System Requirements

* Python 3.8 or higher
* pip / pipx
* Internet access for updates
* Desktop environment if using the GUI (PyQt5)

### 📚 Dependencies

These are the libraries required for WPAT to work properly:

* `colorama` — Console color system
* `requests` — Advanced HTTP requests
* `beautifulsoup4` — HTML parser
* `tqdm` — Interactive progress bars
* `pyqt5` — GUI support
* `PyQtWebEngine` — Web rendering engine embedded in the GUI
* `urllib3` — Advanced HTTP connection handling

## 🖥️ Usage

```bash
# From pip/pipx
wpat / wpat --gui)

# From Docker
docker run -it --rm santitub/wpat

# From GUI
python main.py --gui
```

**Workflow:**

1. Enter the target URL
2. Select modules from the interactive menu or GUI
3. Analyze real-time results with clean output
4. Review detailed logs in `/logs`

### **Main Menu:**

```
[1] Detect User Enumeration        [97] Full Audit
[2] Analyze XML-RPC               [98] Generate Wordlists
[3] Sensitive Files Scanner       [99] Exit
[4] Detect WordPress Version
[5] Audit REST API
[6] Plugin Scanner
[7] Theme Scanner 
[8] Brute Force on Login
[9] Check SSL Certificate
[10] Check Security.txt
[11] Check CORS
```

## 📂 Project Structure

```
WPAT/
├── main.py             # Main script
├── gui.py              # Graphical Interface (new)
├── requirements.txt    # Dependencies
├── logs/               # Audit logs
├── wordlists/          # Generated official wordlists
└── scripts/            # Audit modules
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
```

## 🆕 What's New in v2.0.1

* 🔍 Improvements to the detection module `cors_detector.py`
* ⚙️ Improvements in the `rest_api_analyzer.py` module

## 📜 License and Ethics

Distributed under the **GPL-3.0** license.
See [LICENSE](LICENSE) for details.

**⚠️ Ethical Use Note:**
This software should only be used on systems with explicit permission from the owner. It includes advanced features that may be considered intrusive if used without authorization. Misuse is the sole responsibility of the end user.
