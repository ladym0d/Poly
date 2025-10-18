#!/bin/bash
TODAY=$(date +%F)
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/$TODAY.md"

# Make sure logs directory exists
mkdir -p "$LOG_DIR"

# If the log doesn't exist, create it with a template
if [ ! -f "$LOG_FILE" ]; then
  cat <<EOF > "$LOG_FILE"
#   Poly Daily Log — $TODAY

## Summary
(brief overview of what was done today)

## Tasks Worked On
-

## Notes & Decisions
-

## Next Steps
-
EOF
  echo "Created $LOG_FILE"
else
  echo "Log for $TODAY already exists."
fi

# Optional: auto-commit and push the log
git add "$LOG_FILE"
git commit -m "Add daily log for $TODAY" || echo "Nothing to commit."
git push
