# Cron & Systemd Setup Guide

## Maximum Frequency Configuration

This setup runs auto-apply **every minute** (highest possible cron frequency) for maximum job board coverage and response time.

## Option 1: Automated Setup (Recommended)

```bash
chmod +x cron-setup.sh
./cron-setup.sh
```

This will:
- Install dependencies
- Set up cron job (every minute)
- Optionally install systemd service

## Option 2: Manual Cron Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Edit crontab
crontab -e

# Add this line (checks every minute):
* * * * * cd /path/to/auto-apply && python3 auto-apply.py --check-once >> /var/log/auto-apply.log 2>&1
```

### Cron Frequency Options

| Frequency | Cron Expression | Use Case |
|-----------|-----------------|----------|
| **Every minute** (max) | `* * * * *` | Instant response, high API load |
| Every 5 minutes | `*/5 * * * *` | Balanced coverage |
| Every 15 minutes | `*/15 * * * *` | Low API rate limit concerns |
| Every hour | `0 * * * *` | Conservative approach |

## Option 3: Systemd Service (Continuous)

```bash
# Copy service file
sudo cp auto-apply.service /etc/systemd/system/

# Create application directory
sudo mkdir -p /opt/auto-apply
sudo cp -r ./* /opt/auto-apply/

# Install and start
sudo systemctl daemon-reload
sudo systemctl enable auto-apply.service
sudo systemctl start auto-apply.service

# Monitor
sudo systemctl status auto-apply.service
tail -f /var/log/auto-apply.log
```

## Configuration for Aggressive Mode

Use `config-aggressive.json` for maximum application volume:

```bash
cp config-aggressive.json config.json
# Then customize filters in config.json
```

**Aggressive settings:**
- Check interval: 1 minute
- Max applications/day: 100
- Apply delay: 1 second
- Batch size: 10 jobs per batch
- Skills filter: Broader (6 languages)
- Salary range: Lower minimum

## Monitoring

### View Cron Logs

```bash
# Recent executions
tail -f /var/log/auto-apply.log

# Search for applications
grep "Applied to:" /var/log/auto-apply.log
```

### Check Systemd Status

```bash
# Service status
systemctl status auto-apply

# View logs
journalctl -u auto-apply -f

# Restart service
sudo systemctl restart auto-apply
```

## Managing Rate Limits

With 1-minute checks across multiple boards, be aware of API limits:

- **RemoteOK**: ~60 requests/hour (safe at 1-min checks)
- **Upwork/Freelancer**: Lower limits - use 15-30 min intervals
- **Custom boards**: Check documentation for rate limits

### Adjust Rate Limiting

```json
{
  "boards": {
    "remoteok": {
      "rate_limit": {
        "max_requests": 60,
        "window_seconds": 3600
      }
    }
  }
}
```

## Troubleshooting

**Cron job not running:**
```bash
# Check if crontab is installed
crontab -l

# Check system cron logs
sudo grep CRON /var/log/syslog
```

**High CPU usage:**
- Increase `apply_delay_seconds` in config
- Increase `check_interval_minutes` (e.g., 5 min)
- Reduce `required_skills` to filter better

**Rate limits exceeded:**
- Increase interval between checks
- Reduce `max_applications_per_day`
- Spread applications across different times

**Jobs not being applied to:**
- Check `applied_jobs.json` for history
- Verify filters aren't too restrictive
- Check API responses in logs
- Try `python auto-apply.py --check-once` manually

## Best Practices

1. **Start conservative**: Begin with 15-30 minute intervals, scale up gradually
2. **Monitor success rates**: Track application acceptance rates
3. **Respect API limits**: Don't exceed documented rate limits
4. **Use appropriate delays**: 1-2 second delay between applications prevents blocks
5. **Regular log review**: Check for errors and adjust filters
6. **Test configs**: Use `--check-once` before deploying
7. **Backup applied_jobs.json**: Prevents duplicate applications if you restart

## Production Deployment

For reliable 24/7 operation:

```bash
# Use systemd service (more reliable than cron)
sudo systemctl enable auto-apply.service

# Add log rotation
sudo tee /etc/logrotate.d/auto-apply > /dev/null <<EOF
/var/log/auto-apply.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 nobody nobody
}
EOF

# Monitor with systemd-journal
journalctl -u auto-apply -f
```

## Disable/Stop

```bash
# Remove cron job
crontab -e  # remove the line

# Or disable systemd service
sudo systemctl disable auto-apply.service
sudo systemctl stop auto-apply.service
```
