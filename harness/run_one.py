"""Executa um pedido num modelo, isolado, e salva o JSON bruto.

Uso: python3 rodar.py <alvo_dir> <modelo> <prompt.txt> <saida.json>
"""
import json, subprocess, sys, time
from pathlib import Path
alvo, modelo, prompt, saida = sys.argv[1:5]
cmd = ["claude", "-p", Path(prompt).read_text(encoding="utf-8"), "--model", modelo, "--effort", "high",
       "--tools", "Read,Grep,Glob", "--strict-mcp-config", "--setting-sources", "project",
       "--no-session-persistence", "--output-format", "json"]
t0 = time.time()
p = subprocess.run(cmd, cwd=alvo, capture_output=True, text=True, timeout=1800)
Path(saida + ".bruto.txt").write_text(p.stdout + "\n--STDERR--\n" + p.stderr, encoding="utf-8")  # nunca perder a rodada
try:
    d = json.loads(p.stdout)
    if isinstance(d, list):  # algumas combinações de opções devolvem a lista de mensagens
        msgs = d
        res = next((m for m in reversed(msgs) if isinstance(m, dict) and m.get("type") == "result"), None)
        d = dict(res) if res else {"sem_result": True}
        d["_mensagens"] = [m for m in msgs if m is not res]
except Exception:
    d = {"parse_error": True, "stdout": p.stdout[-4000:], "stderr": p.stderr[-4000:], "returncode": p.returncode}
d["_meta"] = {"modelo_pedido": modelo, "prompt": Path(prompt).name, "segundos": round(time.time() - t0, 1), "returncode": p.returncode}
Path(saida).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"saida": Path(saida).name, "modelos": list((d.get("modelUsage") or {}).keys()), "is_error": d.get("is_error"),
      "stop": d.get("stop_reason"), "safety_stops": d.get("safety_stops"), "denials": len(d.get("permission_denials") or []),
      "custo_lista_usd": round(d.get("total_cost_usd") or 0, 3), "seg": d["_meta"]["segundos"]}, ensure_ascii=False))
