#!/usr/bin/env bash
# Envoie un fichier local vers Notion après un appel à l'outil notion-create-file-upload.
# Usage : visuels/outils/notion_envoi.sh <upload_url> <authorization> <fichier> [type MIME]
# - upload_url et authorization : tels que renvoyés par notion-create-file-upload ;
# - type MIME : doit être identique à celui de la création (ex. image/png, video/mp4).
# Réponse attendue : "status":"uploaded" et un markdown_source file-upload://… à placer dans la page.
set -euo pipefail
url="$1"; auth="$2"; f="$3"; t="${4:-}"
if [ -n "$t" ]; then part="file=@${f};type=${t}"; else part="file=@${f}"; fi
curl -sS -m 300 -X POST "$url" -H "authorization: ${auth}" -F "$part"
echo
