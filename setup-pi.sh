#!/bin/bash
# Run once on the Pi after copying the pi-clock directory to /home/pi/pi-clock/
set -e

# ── NTP: Starlink first, then fallbacks ──────────────────────────────────────
cat > /etc/systemd/timesyncd.conf << 'EOF'
[Time]
NTP=192.168.100.1
FallbackNTP=time.cloudflare.com time.google.com pool.ntp.org
EOF

systemctl restart systemd-timesyncd
echo "NTP configured"

# ── Install systemd service ───────────────────────────────────────────────────
cp /home/pi/pi-clock/pi-clock.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable pi-clock
echo "Service installed and enabled"

# ── Disable screen blanking system-wide ──────────────────────────────────────
sed -i 's/^#\?BLANKING=.*/BLANKING=0/' /etc/kbd/config 2>/dev/null || true
echo "Run 'systemctl start pi-clock' to start now, or reboot"
