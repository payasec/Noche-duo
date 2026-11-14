#!/usr/bin/env bash
# Lance tous les scénarios à deux téléphones simulés contre la copie locale de l'appli.
# Prérequis : python3, pip install playwright, puis : playwright install chromium (ou CHROME=/chemin/vers/chrome)
cd "$(dirname "$0")/.." || exit 1
python3 -m http.server 8771 >/dev/null 2>&1 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null' EXIT
sleep 1
FAIL=0
for t in tests/test_*.py; do
  printf "%-45s " "$(basename "$t")"
  OUT=$(timeout 300 python3 "$t" 2>&1)
  if echo "$OUT" | grep -q "^ERRORS: \[\]$"; then echo "OK"; else echo "ÉCHEC"; echo "$OUT" | tail -5; FAIL=1; fi
done
exit $FAIL
