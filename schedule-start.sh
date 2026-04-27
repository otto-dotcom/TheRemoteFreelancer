#!/bin/bash
# Schedule auto-apply to start tomorrow at noon with max-load config

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
START_TIME="${1:-12:00}"
START_DATE="${2:-tomorrow}"

echo "Scheduling auto-apply to start $START_DATE at $START_TIME..."

# Create startup script
cat > "$SCRIPT_DIR/start-max-load.sh" << 'SCRIPT'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Backup current config
if [ -f config.json ]; then
    cp config.json config.backup.json
fi

# Activate max-load config
cp config-max-load.json config.json

# Install/update dependencies
pip install -r requirements.txt -q

# Start continuous mode
python3 auto-apply.py

SCRIPT

chmod +x "$SCRIPT_DIR/start-max-load.sh"

# Use 'at' command to schedule
if ! command -v at &> /dev/null; then
    echo "⚠ 'at' command not found. Installing..."
    sudo apt-get install -y at
    sudo systemctl enable atd
    sudo systemctl start atd
fi

# Schedule the start
echo "$SCRIPT_DIR/start-max-load.sh" | at "$START_TIME" "$START_DATE" 2>&1 || {
    echo "Failed to schedule with 'at' command"
    echo "Alternative: manually run tomorrow at noon:"
    echo "  $SCRIPT_DIR/start-max-load.sh"
    exit 1
}

# Show scheduled jobs
echo ""
echo "✓ Scheduled!"
echo ""
echo "Scheduled jobs:"
atq

echo ""
echo "Configuration:"
echo "  • Start: $START_DATE at $START_TIME"
echo "  • Config: config-max-load.json"
echo "  • Max daily: 500 applications"
echo "  • Boards: RemoteOK (200), We Work Remotely (150), Angel List (100), Freelancer (50)"
echo ""
echo "Monitor it with:"
echo "  tail -f /var/log/auto-apply.log"
echo ""
echo "Cancel scheduled start:"
echo "  atrm <job_number>"
