# Schedule Max-Load Start for Tomorrow at Noon

## Quick Setup (Recommended)

```bash
chmod +x schedule-start.sh
./schedule-start.sh
```

This uses the `at` command to schedule startup tomorrow at 12:00 PM.

## Option 1: Using `at` Command (Simple)

```bash
# Install at daemon if needed
sudo apt-get install at
sudo systemctl enable atd && sudo systemctl start atd

# Schedule for tomorrow at noon
echo "/path/to/auto-apply/start-max-load.sh" | at 12:00 PM tomorrow

# View scheduled jobs
atq

# Remove a scheduled job (if needed)
atrm <job_number>
```

**Pros:**
- Simple one-time scheduling
- No background process needed
- Easy to cancel

**Cons:**
- Needs `atd` running
- One-time only (won't restart after reboot)

## Option 2: Systemd Timer (Reliable)

```bash
# Copy files
sudo cp auto-apply-timer.service /etc/systemd/system/
sudo cp auto-apply-timer.timer /etc/systemd/system/
sudo mkdir -p /opt/auto-apply
sudo cp -r ./* /opt/auto-apply/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable auto-apply-timer.timer
sudo systemctl start auto-apply-timer.timer

# View timer status
systemctl list-timers auto-apply-timer.timer

# View logs when it starts
journalctl -u auto-apply-timer.service -f
```

**Pros:**
- Survives reboots
- Integrated with systemd
- Can repeat daily if needed
- Better logging

**Cons:**
- Requires systemd
- Slightly more setup

## Option 3: Cron Job (Daily)

```bash
# Schedule to run every day at noon
crontab -e

# Add this line:
0 12 * * * /path/to/auto-apply/start-max-load.sh >> /var/log/auto-apply-start.log 2>&1
```

**Pros:**
- Runs every day at noon
- Simple cron syntax
- Lightweight

**Cons:**
- Less reliable than systemd
- May drift if system is heavily loaded

## Configuration

### Max-Load Settings

The `config-max-load.json` file includes:

| Setting | Value |
|---------|-------|
| RemoteOK max/day | 200 |
| We Work Remotely max/day | 150 |
| Angel List max/day | 100 |
| Freelancer max/day | 50 |
| **Total max/day** | **500** |
| Apply delay | 1 second (with variance) |
| Batch size | 25 jobs |
| Batch delay | 2 seconds |
| Check interval | 2 minutes |
| Skills filter | 10 languages (broad) |
| Salary min | $35k |

### Customize Time

**If you want a different start time:**

#### Using `at` command:
```bash
# Start at 3:00 PM
echo "/path/to/start-max-load.sh" | at 3:00 PM tomorrow

# Start at 8:00 AM
echo "/path/to/start-max-load.sh" | at 8:00 AM tomorrow

# Start in 2 hours
echo "/path/to/start-max-load.sh" | at now + 2 hours
```

#### Using systemd timer:
Edit `/etc/systemd/system/auto-apply-timer.timer`:

```ini
[Timer]
# Different times:
OnCalendar=*-*-* 09:00:00  # 9 AM daily
OnCalendar=*-*-* 18:30:00  # 6:30 PM daily
OnCalendar=*-*-* 00:00:00  # Midnight daily
OnCalendar=Mon *-*-* 12:00:00  # Mondays at noon

# Then restart:
sudo systemctl daemon-reload
sudo systemctl restart auto-apply-timer.timer
```

## Verify It's Scheduled

```bash
# Check scheduled at jobs
atq

# Or check systemd timers
systemctl list-timers

# Or check crontab
crontab -l | grep auto-apply
```

## What Happens When It Starts

1. ✓ Backs up current config
2. ✓ Loads `config-max-load.json`
3. ✓ Installs/updates Python dependencies
4. ✓ Starts continuous monitoring
5. ✓ Applies to ~500 jobs/day across 4 boards
6. ✓ Logs to `/var/log/auto-apply.log`

## Monitor Running Job

```bash
# Real-time logs
tail -f /var/log/auto-apply.log

# Or with systemd
journalctl -u auto-apply-timer.service -f

# Count applications sent
grep "Applied to:" /var/log/auto-apply.log | wc -l

# Success rate
grep "success" /var/log/auto-apply.log | wc -l
```

## Stop or Reschedule

```bash
# Cancel at job
atrm <job_number>

# Or stop systemd service
sudo systemctl stop auto-apply-timer.service

# Or disable timer
sudo systemctl disable auto-apply-timer.timer
sudo systemctl stop auto-apply-timer.timer
```

## Troubleshooting

**"at" daemon not running:**
```bash
sudo systemctl enable atd
sudo systemctl start atd
sudo systemctl status atd
```

**Need to verify timing:**
```bash
# Check if at daemon is working
echo 'echo "test" > /tmp/at-test.txt' | at now + 1 minute
# Wait 1 minute, then check:
ls -l /tmp/at-test.txt
```

**Systemd not starting service:**
```bash
# Check timer status
systemctl status auto-apply-timer.timer

# View timer logs
journalctl -u auto-apply-timer.timer -n 50

# Manually trigger if needed
sudo systemctl start auto-apply-timer.service
```

## Safety Checks

Before the scheduled start:

1. ✓ Verify `config-max-load.json` is correct
2. ✓ Test with `--check-once`: `python3 auto-apply.py --check-once`
3. ✓ Ensure log directory exists: `mkdir -p /var/log`
4. ✓ Check API credentials if needed
5. ✓ Verify disk space for logs

## Scheduled Start Details

- **When**: Tomorrow at 12:00 PM (noon)
- **Config**: `config-max-load.json`
- **Max applications**: 500/day
- **Boards**: 4 major job platforms
- **Delays**: 1-2 second staggering
- **Logging**: `/var/log/auto-apply.log`

Everything is set up and ready to launch! 🚀
