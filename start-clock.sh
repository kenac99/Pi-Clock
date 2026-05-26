#!/bin/bash
export WAYLAND_DISPLAY=wayland-0
export XDG_RUNTIME_DIR=/run/user/1000
CLOCK_DIR=/home/admn/pi-clock

# Start HTTP server
python3 "$CLOCK_DIR/serve.py" &
sleep 2

# Launch Chromium in kiosk mode (Wayland)
chromium \
  --kiosk \
  --disk-cache-size=1 \
  --noerrdialogs \
  --disable-infobars \
  --no-first-run \
  --disable-restore-session-state \
  --disable-session-crashed-bubble \
  --disable-features=Translate \
  --overscroll-history-navigation=0 \
  --ozone-platform=wayland \
  --enable-features=UseOzonePlatform \
  --password-store=basic \
  http://localhost:8080
