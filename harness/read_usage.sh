#!/bin/zsh
# Lê a cota sem gastar modelo. Uso: uso.sh <rotulo> <dir_saida>
out="/Users/ulissesflores/Developer/redacao/dossies/acesso-mythos-5-1/testes/$2/uso-$1-$(date -u +%Y%m%dT%H%M%SZ).txt"
cd /private/tmp && claude -p "/usage" --model claude-haiku-5-5 --output-format json < /dev/null | python3 -c "import json,sys;print(json.load(sys.stdin)['result'])" > "$out"
grep -E "Current (session|week)" "$out" | sed "s/^/[$1] /"
