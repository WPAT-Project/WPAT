#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import os
from typing import Dict, Any, List, Set
from jinja2 import Template

# ---------- Utilidades básicas ----------
ANSI = re.compile(r"\x1b\[[0-9;]*m")

def strip_ansi(text: str) -> str:
    return ANSI.sub("", text)

def safe_int(x) -> int:
    try:
        return int(x)
    except Exception:
        return 0

# ---------- Extractores por módulo ----------
def _extract_users(text: str) -> List[str]:
    users: Set[str] = set()
    for match in re.finditer(r"^\s*• ([^:]+):\s*(.+)$", text, re.M):
        _, rhs = match.groups()
        for chunk in rhs.split(","):
            chunk = strip_ansi(chunk).strip()
            if chunk:
                users.add(chunk)
    return sorted(users)

def _extract_exposed_files(text: str) -> List[str]:
    files: List[str] = []
    for line in text.splitlines():
        if "[EXPUESTO]" in line:
            file_name = strip_ansi(line.split("[EXPUESTO]")[1]).strip()
            if file_name:
                files.append(file_name)
    return files

def _extract_xmlrpc(text: str) -> Dict[str, Any]:
    enabled = "XML-RPC detectado" in text
    methods: List[str] = []
    if enabled:
        for m in re.finditer(r"(?:✔|•)\s+(\w+(?:\.\w+)*)", text):
            methods.append(m.group(1))
    return {"enabled": enabled, "methods": sorted(set(methods))}

def _extract_wp_version(text: str) -> str | None:
    m = re.search(r"\[DETECTADA\] Versión:\s*([\d.]+)", text)
    return m.group(1) if m else None

def _extract_rest_api(text: str) -> Dict[str, Any]:
    summary = re.search(
        r"☠ Critical:\s*(\d+).*✗ Dangerous:\s*(\d+)", text
    )
    critical = safe_int(summary.group(1)) if summary else 0
    dangerous = safe_int(summary.group(2)) if summary else 0

    exposed: List[str] = []
    for line in text.splitlines():
        m = re.search(r"(?:☠|✗|⚠)\s+(?:CRITICAL|DANGER|WARNING)\s+(\S+)", line)
        if m:
            exposed.append(m.group(1))

    severity = (
        "CRITICAL"
        if critical
        else "HIGH"
        if dangerous
        else "LOW"
    )
    return {
        "severity": severity,
        "critical_endpoints": critical,
        "dangerous_endpoints": dangerous,
        "exposed": exposed,
    }

def _extract_ssl(text: str) -> Dict[str, Any]:
    expired = "EXPIRADO" in text
    valid = "VÁLIDO" in text and not expired
    return {"valid": valid, "expired": expired}

def _extract_cors(text: str) -> Dict[str, Any]:
    issues: List[str] = []
    reflected: Set[str] = set()
    json_req: List[str] = []

    risky_origins = {"evil", "attacker", "localhost", "127.0.0.1", "null"}

    for line in text.splitlines():
        if not line.startswith(("http://", "https://")):
            continue
        parts = re.split(r"\s{2,}", line.strip())
        if len(parts) < 6:
            continue
        origin, method, status, acao, acac, json_col = parts[:6]

        origin = origin.strip()
        method = method.strip()

        if acao == origin and origin not in {"*"}:
            if any(r in origin.lower() for r in risky_origins):
                reflected.add(origin)

        if "✓" in json_col and (
            acao == "*" or
            (any(r in origin.lower() for r in risky_origins) and acac == "true")
        ):
            json_req.append(f"{origin} /wp-json/wp/v2/users {method}")

    if reflected:
        issues.append("Origen reflejado sin validación")
    if json_req:
        issues.append("JSON hijacking posible")

    return {
        "vulnerable": bool(issues),
        "issues": issues,
        "evidence": {
            "reflected_origins": sorted({r.strip() for r in reflected}),
            "json_endpoints": sorted(set(json_req)),
        },
    }

def _extract_security_txt(text: str) -> Dict[str, Any]:
    found = "DETECTADO" in text and "NO DETECTADO" not in text
    return {"found": found}

# ---------- Divisor de módulos ----------
MODULES = {
    "user_enum": (
        "DETECTAR ENUMERACIÓN DE USUARIOS",
        "ANALIZAR XML-RPC",
    ),
    "xmlrpc": (
        "ANALIZAR XML-RPC",
        "ESCÁNER DE ARCHIVOS SENSIBLES",
    ),
    "files": (
        "ESCÁNER DE ARCHIVOS SENSIBLES",
        "DETECTAR VERSIÓN DE WORDPRESS",
    ),
    "wp_version": (
        "DETECTAR VERSIÓN DE WORDPRESS",
        "AUDITAR REST API",
    ),
    "rest_api": (
        "AUDITAR REST API",
        "VERIFICAR CERTIFICADO SSL",
    ),
    "ssl": (
        "VERIFICAR CERTIFICADO SSL",
        "VERIFICAR SECURITY.TXT",
    ),
    "sec_txt": (
        "VERIFICAR SECURITY.TXT",
        "VERIFICAR CORS",
    ),
    "cors": (
        "VERIFICAR CORS",
        None,
    ),
}

def _section(text: str, start: str, end: str | None) -> str:
    try:
        s_idx = text.index(start)
    except ValueError:
        return ""
    e_idx = len(text) if end is None else text.index(end, s_idx)
    return text[s_idx:e_idx]

# ---------- Parser principal ----------
def parse_report(raw: str) -> Dict[str, Any]:
    raw = strip_ansi(raw)
    report: Dict[str, Any] = {"target": None, "findings": {}}

    m = re.search(r"análisis en:\s+(https?://[^\s]+)", raw)
    report["target"] = m.group(1).rstrip("/") if m else "unknown"

    for key, (start, end) in MODULES.items():
        sec = _section(raw, start, end).strip()
        if not sec:
            continue
        if key == "user_enum":
            report["findings"]["users"] = _extract_users(sec)
        elif key == "xmlrpc":
            report["findings"]["xmlrpc"] = _extract_xmlrpc(sec)
        elif key == "files":
            report["findings"]["exposed_files"] = _extract_exposed_files(sec)
        elif key == "wp_version":
            ver = _extract_wp_version(sec)
            if ver:
                report["findings"]["wp_version"] = ver
        elif key == "rest_api":
            report["findings"]["rest_api"] = _extract_rest_api(sec)
        elif key == "ssl":
            report["findings"]["ssl"] = _extract_ssl(sec)
        elif key == "sec_txt":
            report["findings"]["security_txt"] = _extract_security_txt(sec)
        elif key == "cors":
            report["findings"]["cors"] = _extract_cors(sec)

    severities: List[str] = []
    if report["findings"].get("users"):
        severities.append("MEDIUM")
    if report["findings"].get("xmlrpc", {}).get("enabled"):
        severities.append("MEDIUM")
    if report["findings"].get("exposed_files"):
        severities.append("MEDIUM")
    rest_sev = report["findings"].get("rest_api", {}).get("severity")
    if rest_sev:
        severities.append(rest_sev)
    if report["findings"].get("ssl", {}).get("expired"):
        severities.append("HIGH")
    if report["findings"].get("cors", {}).get("vulnerable"):
        severities.append("HIGH")

    priority = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    report["severity"] = next((s for s in priority if s in severities), "LOW")
    return report

# ---------- GENERADOR HTML ----------
JINJA_TEMPLATE = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>WPAT Report</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css">
  <style>
    :root{
      --bg:#0f0c29;
      --bg-card:#1f1d36;
      --border:#3b3a53;
      --accent:#ff416c;
      --font-mono:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;
    }
    body{
      min-height:100vh;
      background:linear-gradient(135deg, #0f0c29, #302b63, #24243e);
      background-attachment:fixed;
      color:#e9ecef;
      font-family:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    }
    .glass{
      background:rgba(255,255,255,.06);
      border:1px solid rgba(255,255,255,.1);
      backdrop-filter:blur(10px);
      border-radius:1rem;
      box-shadow:0 8px 32px rgba(0,0,0,.37)
    }
    .badge-critical{background:linear-gradient(to right, #ff416c, #ff4b2b)}
    .badge-high{background:linear-gradient(to right, #ff9a3d, #ff6f3c)}
    .badge-medium{background:linear-gradient(to right, #ffc93c, #ffb800)}
    .badge-low{background:linear-gradient(to right, #3ec46d, #2aaf6d)}
    .issue-item{transition:transform .2s}
    .issue-item:hover{transform:translateY(-3px)}
    .circle-bg{fill:none;stroke:rgba(255,255,255,.1);stroke-width:12}
    .circle-progress{
      fill:none;
      stroke-width:12;
      stroke-linecap:round;
      transform-origin:center;
      transform:rotate(-90deg);
      animation:fillCircle 1s forwards
    }
    @keyframes fillCircle{to{stroke-dashoffset:var(--target)}}
    .json-editor{background:#1e1e1e;border:1px solid var(--border);border-radius:.75rem;max-height:350px;overflow:auto;font-size:.85rem;line-height:1.4}
    .json-editor pre{margin:0;padding:1rem;font-family:var(--font-mono)}
    .json-editor .header{background:#2d2d2d;border-bottom:1px solid var(--border);padding:.5rem 1rem;display:flex;align-items:center;justify-content:space-between;border-radius:.75rem .75rem 0 0;font-size:.8rem;text-transform:uppercase;letter-spacing:.5px}
    .json-key{color:#9cdcfe}
    .json-string{color:#ce9178}
    .json-number{color:#b5cea8}
    .json-boolean{color:#569cd6}
    .json-null{color:#569cd6}
  </style>
</head>
<body>
  <div class="container py-5">
    <div class="text-center mb-5">
      <h1 class="fw-bold"><i class="bi bi-shield-lock"></i> WordPress Auditory Tool</h1>
      <p class="lead">{{ target }}</p>
      <span class="badge badge-{{ color }} fs-5 px-3 py-2">{{ severity }}</span>
    </div>

    <div class="row mb-5 justify-content-center">
      <div class="col-md-4 text-center">
        <div class="glass p-4">
          <svg width="140" height="140" viewBox="0 0 140 140">
            <circle cx="70" cy="70" r="63" class="circle-bg"/>
            <circle cx="70" cy="70" r="63" class="circle-progress" stroke="{{ radial_color }}"
                    stroke-dasharray="{{ dash_array }}" stroke-dashoffset="{{ dash_array }}"
                    style="--target:{{ dash_offset }}"/>
            <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#fff" font-size="2rem" font-weight="700">{{ severity }}</text>
          </svg>
          <p class="mb-0 mt-2 text-white-50">Severidad global</p>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-md-6 col-lg-4"><div class="glass h-100 p-3 issue-item"><h5><i class="bi bi-people-fill text-info"></i> Usuarios</h5>{% if users %}<div class="d-flex flex-wrap gap-2 mt-3">{% for u in users %}<span class="badge bg-info">{{ u }}</span>{% endfor %}</div>{% else %}<p class="text-success mb-0">✓ No detectados</p>{% endif %}</div></div>
      <div class="col-md-6 col-lg-4"><div class="glass h-100 p-3 issue-item"><h5><i class="bi bi-folder-fill text-warning"></i> Archivos</h5>{% if files %}<ul class="list-unstyled mb-0 mt-2">{% for f in files %}<li><code class="text-warning">{{ f }}</code></li>{% endfor %}</ul>{% else %}<p class="text-success mb-0">✓ Ninguno</p>{% endif %}</div></div>
      <div class="col-md-6 col-lg-4"><div class="glass h-100 p-3 issue-item"><h5><i class="bi bi-plug-fill text-danger"></i> XML-RPC</h5><p class="mb-1">Habilitado: <span class="badge bg-{{ xrpc_color }}">{{ xrpc_enabled }}</span></p>{% if xrpc_methods %}<details class="small"><summary>Ver métodos</summary><div class="mt-2">{% for m in xrpc_methods %}<code class="d-block mb-1">{{ m }}</code>{% endfor %}</div></details>{% endif %}</div></div>
      <div class="col-md-6 col-lg-4"><div class="glass h-100 p-3 issue-item"><h5><i class="bi bi-cloud-fill text-primary"></i> REST API</h5><p class="mb-1">Severidad: <span class="badge bg-{{ rest_color }}">{{ rest_severity }}</span></p>{% if rest_exposed %}<details class="small"><summary>Endpoints</summary><ul class="mb-0 mt-2">{% for e in rest_exposed %}<li><code>{{ e }}</code></li>{% endfor %}</ul></details>{% endif %}</div></div>
      <div class="col-md-6 col-lg-4"><div class="glass h-100 p-3 issue-item"><h5><i class="bi bi-shield-exclamation text-danger"></i> CORS</h5>{% if cors_vuln %}<ul class="small mb-2">{% for i in cors_issues %}<li>{{ i }}</li>{% endfor %}</ul><details class="small"><summary>Orígenes</summary><code>{{ cors_origins|join(", ") }}</code></details><details class="small"><summary>JSON endpoints</summary><code>{{ cors_json|join("<br>") }}</code></details>{% else %}<p class="text-success mb-0">✓ Sin problemas</p>{% endif %}</div></div>
      <div class="col-md-6 col-lg-4"><div class="glass h-100 p-3 issue-item"><h5><i class="bi bi-lock-fill text-success"></i> SSL</h5><p class="mb-1">Válido: <span class="badge bg-{{ ssl_color }}">{{ ssl_valid }}</span></p><p class="mb-0">Expirado: <span class="badge bg-{{ ssl_exp_color }}">{{ ssl_expired }}</span></p></div></div>
    </div>

    <div class="mt-5">
      <h5><i class="bi bi-code-square"></i> JSON bruto</h5>
      <div class="json-editor">
        <div classHeader"><span>Raw JSON</span>
          <button class="btn btn-sm btn-outline-light" onclick="copyRaw()"><i class="bi bi-clipboard"></i> Copiar</button>
        </div>
        <pre id="rawJson" class="json-content">{{ colored_json }}</pre>
      </div>
    </div>

  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
  <script>
    function copyRaw(){
      navigator.clipboard.writeText(document.getElementById('rawJson').textContent)
        .then(()=>alert('JSON copiado al portapapeles'));
    }
  </script>
</body>
</html>"""

def render_html(data: dict) -> str:
    sev   = data.get("severity", "LOW")
    color = {"CRITICAL":"danger","HIGH":"warning","MEDIUM":"secondary","LOW":"success"}.get(sev,"success")

    percent     = {"CRITICAL":100,"HIGH":75,"MEDIUM":50,"LOW":25}.get(sev,0)
    dash_array  = 395.84
    dash_offset = dash_array * (1 - percent/100)

    findings = data.get("findings",{})
    raw_json = json.dumps(data, indent=2, ensure_ascii=False)

    colored = raw_json
    colored = re.sub(r'(".*?")\s*:', r'<span class="json-key">\1</span> :', colored)
    colored = re.sub(r':\s*(".*?")(?=[,}\]])', r': <span class="json-string">\1</span>', colored)
    colored = re.sub(r':\s*(\d+)(?=[,}\]])', r': <span class="json-number">\1</span>', colored)
    colored = re.sub(r':\s*(true|false|null)(?=[,}\]])', r': <span class="json-boolean">\1</span>', colored)

    return Template(JINJA_TEMPLATE).render(
        target=data.get("target",""),
        severity=sev,
        color=color,
        radial_color={"CRITICAL":"#ff416c","HIGH":"#ff9a3d","MEDIUM":"#ffc93c","LOW":"#3ec46d"}.get(sev,"#3ec46d"),
        dash_array=dash_array,
        dash_offset=dash_offset,
        users=findings.get("users",[]),
        files=findings.get("exposed_files",[]),
        xrpc_enabled="SÍ" if findings.get("xmlrpc",{}).get("enabled") else "NO",
        xrpc_color="danger" if findings.get("xmlrpc",{}).get("enabled") else "success",
        xrpc_methods=findings.get("xmlrpc",{}).get("methods",[]),
        rest_severity=findings.get("rest_api",{}).get("severity","LOW"),
        rest_color={"CRITICAL":"danger","HIGH":"warning","MEDIUM":"secondary","LOW":"success"}.get(findings.get("rest_api",{}).get("severity"),"success"),
        rest_exposed=findings.get("rest_api",{}).get("exposed",[]),
        cors_vuln=findings.get("cors",{}).get("vulnerable",False),
        cors_issues=findings.get("cors",{}).get("issues",[]),
        cors_origins=findings.get("cors",{}).get("evidence",{}).get("reflected_origins",[]),
        cors_json=findings.get("cors",{}).get("evidence",{}).get("json_endpoints",[]),
        ssl_valid="SÍ" if findings.get("ssl",{}).get("valid") else "NO",
        ssl_color="success" if findings.get("ssl",{}).get("valid") else "danger",
        ssl_expired="SÍ" if findings.get("ssl",{}).get("expired") else "NO",
        ssl_exp_color="danger" if findings.get("ssl",{}).get("expired") else "success",
        wp_version=findings.get("wp_version") or "No detectada",
        colored_json=colored,
    )

def generate_report(input_path: str) -> str:
    """
    Convert a WPAT text report to an HTML report.
    The output file is saved next to the input file with '.html' extension.
    Returns the path of the generated HTML file.
    """
    with open(input_path, encoding="utf-8") as f:
        raw = f.read()

    data = parse_report(raw)
    html = render_html(data)

    base, _ = os.path.splitext(input_path)
    output_path = base + ".html"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path