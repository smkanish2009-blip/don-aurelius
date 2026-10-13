import os
import re
import sys
import json
import subprocess
from html.parser import HTMLParser
from urllib.parse import urlparse

docs_dir = r"C:\Users\LENOVO\.gemini\antigravity\scratch\xauusd-ai-bot\docs"

print("=" * 65)
print("     DON AURELIUS INSTITUTIONAL MULTI-PAGE HARDCORE DIAGNOSTIC      ")
print("=" * 65)

errors = []
warnings = []
passed = []

html_files = [f for f in os.listdir(docs_dir) if f.endswith(".html")]
print(f"[+] Found {len(html_files)} HTML pages in docs/: {', '.join(html_files)}")

# -------------------------------------------------------------
# AUDIT CLASS
# -------------------------------------------------------------
class PageAuditor(HTMLParser):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.ids = {}
        self.href_anchors = []
        self.local_assets = []
        self.external_scripts = []
        self.external_iframes = []
        self.inline_scripts = []
        self.json_ld_blocks = []
        self.in_script = False
        self.script_type = None
        self.current_script = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        
        # Check IDs
        if "id" in attr_dict:
            elem_id = attr_dict["id"]
            if elem_id:
                self.ids[elem_id] = self.ids.get(elem_id, 0) + 1

        # Check Asset references
        for attr in ["src", "href", "poster", "data-src"]:
            if attr in attr_dict:
                val = attr_dict[attr]
                if val.startswith("#"):
                    self.href_anchors.append(val[1:])
                elif val.startswith(("http://", "https://")):
                    if tag == "script":
                        self.external_scripts.append(val)
                    elif tag == "iframe":
                        self.external_iframes.append(val)
                elif not val.startswith(("data:", "mailto:", "tel:", "javascript:")):
                    self.local_assets.append(val)

        if tag == "script":
            self.in_script = True
            self.script_type = attr_dict.get("type", "text/javascript")
            self.current_script = []

    def handle_endtag(self, tag):
        if tag == "script" and self.in_script:
            self.in_script = False
            code = "".join(self.current_script)
            if self.script_type == "application/ld+json":
                self.json_ld_blocks.append(code)
            elif not self.script_type or "javascript" in self.script_type:
                self.inline_scripts.append(code)
            self.current_script = []

    def handle_data(self, data):
        if self.in_script:
            self.current_script.append(data)

# -------------------------------------------------------------
# 1. RUN AUDIT ON EVERY HTML PAGE
# -------------------------------------------------------------
for page in html_files:
    page_path = os.path.join(docs_dir, page)
    with open(page_path, "r", encoding="utf-8") as f:
        content = f.read()

    auditor = PageAuditor(page)
    try:
        auditor.feed(content)
    except Exception as e:
        errors.append(f"[{page}] HTML parse exception: {e}")
        continue

    # Duplicate IDs
    dups = {k: v for k, v in auditor.ids.items() if v > 1}
    if dups:
        for did, count in dups.items():
            errors.append(f"[{page}] Duplicate DOM ID '{did}' appears {count} times.")
    else:
        passed.append(f"[{page}] Zero duplicate DOM IDs.")

    # Local assets
    for asset in set(auditor.local_assets):
        clean = asset.split("?")[0].split("#")[0]
        if not clean:
            continue
        full = os.path.normpath(os.path.join(docs_dir, clean))
        if not os.path.exists(full):
            errors.append(f"[{page}] 404 Missing Local Asset: '{asset}' -> '{full}'")
        else:
            passed.append(f"[{page}] Asset exists: {clean}")

    # JSON-LD syntax validation
    for idx, jblock in enumerate(auditor.json_ld_blocks):
        try:
            json.loads(jblock)
            passed.append(f"[{page}] JSON-LD Schema #{idx+1} valid JSON-LD structure.")
        except Exception as je:
            errors.append(f"[{page}] JSON-LD Schema #{idx+1} syntax error: {je}")

    # Inline Scripts Syntax Validation with Node.js
    temp_js = os.path.join(docs_dir, f"_temp_{page}.js")
    for idx, sblock in enumerate(auditor.inline_scripts):
        if len(sblock.strip()) > 10:
            with open(temp_js, "w", encoding="utf-8") as tf:
                tf.write(sblock)
            res = subprocess.run(["node", "--check", temp_js], capture_output=True, text=True)
            if res.returncode != 0:
                errors.append(f"[{page}] Inline Script #{idx+1} syntax error:\n{res.stderr.strip()}")
            else:
                passed.append(f"[{page}] Inline Script #{idx+1} valid JS syntax.")
            if os.path.exists(temp_js):
                os.remove(temp_js)

    # CSP vs External URLs
    # Parse CSP properly
    csp_match = re.search(r'<meta\s+http-equiv=["\']Content-Security-Policy["\']\s+content="([^"]*)"', content, re.IGNORECASE)
    if not csp_match:
        csp_match = re.search(r"<meta\s+http-equiv=['\"]Content-Security-Policy['\"]\s+content='([^']*)'", content, re.IGNORECASE)
    
    if csp_match:
        csp = csp_match.group(1)
        for ext_s in auditor.external_scripts:
            domain = urlparse(ext_s).netloc
            if domain not in csp:
                errors.append(f"[{page}] CSP Violation: External script '{ext_s}' domain '{domain}' not in script-src!")
            else:
                passed.append(f"[{page}] CSP verified for script domain: {domain}")

        for ext_f in auditor.external_iframes:
            domain = urlparse(ext_f).netloc
            if domain not in csp:
                errors.append(f"[{page}] CSP Violation: External iframe '{ext_f}' domain '{domain}' not in frame-src!")
            else:
                passed.append(f"[{page}] CSP verified for iframe domain: {domain}")

# -------------------------------------------------------------
# 2. AUDIT EXTERNAL JAVASCRIPT FILES
# -------------------------------------------------------------
print("\n[+] Auditing external JS files...")
js_dir = os.path.join(docs_dir, "js")
if os.path.exists(js_dir):
    for jf in os.listdir(js_dir):
        if jf.endswith(".js"):
            jpath = os.path.join(js_dir, jf)
            res = subprocess.run(["node", "--check", jpath], capture_output=True, text=True)
            if res.returncode != 0:
                errors.append(f"[JS] {jf} syntax error:\n{res.stderr.strip()}")
            else:
                passed.append(f"[JS] {jf} clean syntax.")

# -------------------------------------------------------------
# 3. AUDIT CSS FILES
# -------------------------------------------------------------
print("\n[+] Auditing CSS files...")
css_dir = os.path.join(docs_dir, "css")
if os.path.exists(css_dir):
    for cf in os.listdir(css_dir):
        if cf.endswith(".css"):
            cpath = os.path.join(css_dir, cf)
            with open(cpath, "r", encoding="utf-8") as f:
                c_text = f.read()
            ob = c_text.count("{")
            cb = c_text.count("}")
            if ob != cb:
                errors.append(f"[CSS] {cf} Unbalanced braces: {ob} open vs {cb} close!")
            else:
                passed.append(f"[CSS] {cf} balanced braces ({ob} rules).")

# -------------------------------------------------------------
# 4. AUDIT _HEADERS FILE (FOR CLOUDFLARE / GITHUB / NETLIFY)
# -------------------------------------------------------------
headers_path = os.path.join(docs_dir, "_headers")
if os.path.exists(headers_path):
    with open(headers_path, "r", encoding="utf-8") as f:
        h_text = f.read()
    if "cdn.jsdelivr.net" not in h_text:
        warnings.append("[_headers] Missing 'https://cdn.jsdelivr.net' in script-src (Supabase JS library).")
    if "wss:" not in h_text:
        warnings.append("[_headers] Missing 'wss:' in connect-src (Supabase Realtime WebSockets).")

# -------------------------------------------------------------
# SUMMARY
# -------------------------------------------------------------
print("\n" + "=" * 65)
print("                   FINAL AUDIT SUMMARY REPORT                  ")
print("=" * 65)

print(f"\nCRITICAL ERRORS FOUND : {len(errors)}")
for err in errors:
    print(f"  [ERROR] {err}")

print(f"\nWARNINGS FOUND        : {len(warnings)}")
for w in warnings:
    print(f"  [WARN]  {w}")

print(f"\nTOTAL CHECKS PASSED   : {len(passed)}")
for p in passed[:12]:
    print(f"  [PASS]  {p}")
if len(passed) > 12:
    print(f"  ... and {len(passed) - 12} additional checks passed successfully.")

print("=" * 65)
