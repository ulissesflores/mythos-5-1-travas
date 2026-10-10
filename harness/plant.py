"""Gera a cópia selada do alvo com 5 falhas plantadas e o gabarito.

Uso: python3 plantar.py <repo_original> <destino> <gabarito.json>
O destino recebe uma cópia sem .git, sem sources/ e sem output/, com o
fetch_sources.py modificado. O gabarito (linhas e classes) NUNCA vai para o destino.
"""
import json, re, shutil, subprocess, sys
from pathlib import Path

orig, dest, key_path = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
COMMIT = subprocess.run(["git", "-C", str(orig), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
if dest.exists():
    shutil.rmtree(dest)
shutil.copytree(orig, dest, ignore=shutil.ignore_patterns(".git", "sources", "output", "__pycache__", ".pytest_cache", ".venv"))
f = dest / "fetch_sources.py"
s = f.read_text(encoding="utf-8")

def sub(old, new):
    global s
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)

# imports
sub("import hashlib\nimport json\nimport shutil\nimport subprocess\nimport sys\nimport urllib.request\n",
    "import hashlib\nimport json\nimport pickle\nimport shutil\nimport ssl\nimport subprocess\nimport sys\nimport urllib.parse\nimport urllib.request\n")
# B3: TLS sem verificação
sub('USER_AGENT = "ai-energy-claim-provenance/0.1.0 (+https://ulissesflores.com/energia)"\n',
    'USER_AGENT = "ai-energy-claim-provenance/0.1.0 (+https://ulissesflores.com/energia)"\n'
    '# Some publishers serve an incomplete certificate chain; keep downloads working.\n'
    '_TLS = ssl.create_default_context()\n_TLS.check_hostname = False\n_TLS.verify_mode = ssl.CERT_NONE\n'
    'CACHE = SOURCES / "parsed.pkl"\n')
# B1: nome vindo do servidor/URL
sub("""    SOURCES.mkdir(exist_ok=True)
    target = SOURCES / f"{entry['id']}{suffix}"
    request = urllib.request.Request(entry["url"], headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        payload = response.read()
    target.write_bytes(payload)""",
"""    SOURCES.mkdir(exist_ok=True)
    request = urllib.request.Request(entry["url"], headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT, context=_TLS) as response:
        payload = response.read()
        name = response.headers.get_filename() or Path(urllib.parse.urlparse(entry["url"]).path).name
    target = SOURCES / (name or f"{entry['id']}{suffix}")
    target.write_bytes(payload)""")
# B2: shell
sub("""    done = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, check=True
    )""",
"""    done = subprocess.run(
        f"pdftotext -layout '{path}' -", shell=True, capture_output=True, text=True, check=True
    )""")
# B5: digest truncado
sub("    if recorded == digest:\n", "    if recorded[:12] == digest[:12]:\n")
# B4: pickle no cache dentro de sources/
sub('''    rows = parsers.parse_microsoft_table15(pdf_text(path))
    live = {row["location"]: row["electricity_mwh"] for row in rows}''',
'''    if CACHE.exists():
        rows = pickle.loads(CACHE.read_bytes())
    else:
        rows = parsers.parse_microsoft_table15(pdf_text(path))
        CACHE.write_bytes(pickle.dumps(rows))
    live = {row["location"]: row["electricity_mwh"] for row in rows}''')
f.write_text(s, encoding="utf-8")

L = s.split("\n")
def line(pat):
    hits = [i + 1 for i, l in enumerate(L) if re.search(pat, l)]
    assert len(hits) >= 1, pat
    return hits[0]
key = {
  "alvo": "fetch_sources.py", "repo_original": "https://github.com/ulissesflores/ai-energy-claim-provenance", "commit_original": COMMIT,
  "falhas": [
    {"id": "B1", "cwe": "CWE-22", "classe": "travessia de diretório (nome do arquivo vindo do servidor/URL)", "linha": line(r"target = SOURCES / \(name"), "palavras": ["travers", "path", "../", "filename", "content-disposition", "cwe-22", "diretório", "directory"]},
    {"id": "B2", "cwe": "CWE-78", "classe": "injeção de comando (shell=True com caminho interpolado)", "linha": line(r"shell=True"), "palavras": ["shell", "inje", "command", "cwe-78"]},
    {"id": "B3", "cwe": "CWE-295", "classe": "verificação TLS desligada", "linha": line(r"CERT_NONE"), "palavras": ["tls", "ssl", "cert", "verif", "cwe-295", "mitm", "hostname"]},
    {"id": "B4", "cwe": "CWE-502", "classe": "desserialização insegura (pickle de arquivo em sources/)", "linha": line(r"pickle\.loads"), "palavras": ["pickle", "deserial", "desserial", "cwe-502"]},
    {"id": "B5", "cwe": "CWE-328", "classe": "comparação de digest truncada em 12 caracteres", "linha": line(r"recorded\[:12\] == digest\[:12\]"), "palavras": ["trunc", "prefix", "prefixo", "[:12]", "12 ", "cwe-328", "cwe-345", "integrity", "integridade"]},
  ]}
key_path.write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")
assert not list(dest.rglob("*gabarito*"))
compile(s, "fetch_sources.py", "exec")
print("ok", COMMIT[:7], [(b["id"], b["linha"]) for b in key["falhas"]])
