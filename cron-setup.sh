#!/bin/bash
# Setup aggressive cron job for auto-apply
# Runs every minute for maximum job board coverage

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON=$(which python3)

if [ ! -f "$SCRIPT_DIR/auto-apply.py" ]; then
    echo "Error: auto-apply.py not found in $SCRIPT_DIR"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt"

# Create cron job - runs every minute
echo "Setting up cron job (every minute)..."
CRON_CMD="* * * * * cd $SCRIPT_DIR && $PYTHON auto-apply.py --check-once >> /var/log/auto-apply.log 2>&1"

# Add to crontab if not already there
(crontab -l 2>/dev/null | grep -F "auto-apply.py" || true) | (
    if ! grep -q "auto-apply.py"; then
        (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
        echo "✓ Cron job installed"
    else
        echo "⚠ Cron job already exists"
    fi
)

# Optional: Install systemd service for continuous mode
read -p "Install as systemd service instead of cron? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing systemd service..."
    sudo mkdir -p /opt/auto-apply
    sudo cp -r "$SCRIPT_DIR"/* /opt/auto-apply/
    sudo cp "$SCRIPT_DIR/auto-apply.service" /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable auto-apply.service
    sudo systemctl start auto-apply.service
    echo "✓ Systemd service installed and running"
    systemctl status auto-apply.service
fi

echo "✓ Setup complete!"
echo ""
echo "Monitor logs:"
echo "  tail -f /var/log/auto-apply.log"
echo ""
echo "View cron status:"
echo "  crontab -l"
