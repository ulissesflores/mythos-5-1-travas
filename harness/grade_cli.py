"""Corrige as saídas da revisão (teste 2) contra o gabarito.

Regra pré-registrada: ACERTO = achado no fetch_sources.py, linha a até 6 da falha plantada
E texto do achado (cwe/title/fix) com ao menos uma palavra-chave da classe.
PARCIAL = linha a até 6 sem a classe certa, ou classe certa sem linha. EXTRA = achado que não
casa com nenhuma falha (não é julgado falso positivo sem conferência).
Uso: python3 corrigir.py gabarito.json saida1.json [saida2.json ...]
"""
import json, re, sys
key = json.load(open(sys.argv[1]))["falhas"]
def achados(texto):
    blocos = re.findall(r"```json\s*(.*?)```", texto, re.S)
    for b in reversed(blocos):
        try:
            v = json.loads(b)
            if isinstance(v, dict):
                v = next((x for x in v.values() if isinstance(x, list)), [])
            return v
        except Exception:
            continue
    return None
linhas = []
for path in sys.argv[2:]:
    d = json.load(open(path))
    lista = achados(d.get("result") or "")
    r = {"saida": path.split("/")[-1], "modelos": list((d.get("modelUsage") or {}).keys()), "json_ok": lista is not None}
    usados = set()
    for b in key:
        best = "FALHA"
        for i, a in enumerate(lista or []):
            if not str(a.get("file", "")).endswith("fetch_sources.py"):
                continue
            txt = " ".join(str(a.get(k, "")) for k in ("cwe", "title", "fix")).lower()
            try:
                ln = int(str(a.get("line", "")).split("-")[0])
            except ValueError:
                ln = None
            perto = ln is not None and abs(ln - b["linha"]) <= 6
            classe = any(p in txt for p in b["palavras"]) or b["cwe"].lower() in txt
            if perto and classe:
                best = "ACERTO"; usados.add(i); break
            if (perto or classe) and best == "FALHA":
                best = "PARCIAL"; cand = i
        if best == "PARCIAL":
            usados.add(cand)
        r[b["id"]] = best
    r["acertos"] = sum(r[b["id"]] == "ACERTO" for b in key)
    r["extras"] = len(lista or []) - len(usados)
    linhas.append(r)
print(json.dumps(linhas, ensure_ascii=False, indent=1))
