# Pi Clock

A full-screen DS-Digital clock for Raspberry Pi with a 1080×1920 portrait display. Features live weather, auto day/night color schemes, brightness control, and optional mining pool stats.

![Clock showing time, date, weather, and mining stats](screenshot.png)

## Hardware

- Raspberry Pi 5
- WaveShare 10.1" 1080×1920 HDMI display (portrait orientation)
- 52Pi N04 NVMe hat + NVMe SSD (recommended for performance)

## Features

- DS-Digital 7-segment style display
- 12-hour clock with seconds
- Auto day/night mode (sunrise/sunset calculated locally — no API)
- 6 color schemes, tap to cycle (Red, Amber, Green, White, Purple, Pewter)
- Double-tap for brightness overlay
- Optional live weather from an Ambient Weather station
- Optional mining pool stats (ckpool/asicseer — BTC + BCH side by side)
- **Block detection animation**: digits go haywire → "BLOCK FOUND" → loops until tapped
- OLED burn-in prevention (pixel shift every 3 minutes)

## Font

The DS-Digital font by Dusit Supasawat is free for personal use. Download it from [dafont.com/ds-digital.font](https://www.dafont.com/ds-digital.font) and place `DS-DIGI.TTF` and `DS-DIGIB.TTF` in a `fonts/` subdirectory.

## Setup

### 1. Clone and install font

```bash
git clone https://github.com/youruser/pi-clock.git ~/pi-clock
cd ~/pi-clock
mkdir fonts
# Place DS-DIGI.TTF and DS-DIGIB.TTF in fonts/
```

### 2. Install the systemd service

```bash
sudo cp pi-clock.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pi-clock
```

Edit `pi-clock.service` to match your username if not using the default.

### 3. Configure display rotation

The WaveShare display needs 270° rotation for landscape orientation. Add to `~/.config/labwc/autostart`:

```
wlr-randr --output HDMI-A-1 --transform 270 &
sleep 5 && /bin/bash ~/pi-clock/start-clock.sh &
```

### 4. Disable screen lock

labwc runs `light-locker` by default, which will lock the kiosk display almost immediately. Disable it:

```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/light-locker.desktop << 'EOF'
[Desktop Entry]
Hidden=true
EOF
```

### 5. Set your location

Open a browser and navigate to `http://<pi-ip>:8080/config` to set latitude/longitude for accurate sunrise/sunset times and choose your day/night color schemes and brightness levels.

Or edit `config.json` directly:

```json
{
  "lat": 37.77,
  "lon": -122.41,
  "dayBright": 75,
  "nightBright": 40,
  "dayScheme": 3,
  "nightScheme": 4
}
```

### 6. Start

```bash
sudo systemctl start pi-clock
```

## Optional: Live Weather (Ambient Weather)

If you have an Ambient Weather station:

```bash
cp config.env.example config.env
# Edit config.env with your API key, app key, and station MAC
```

Add to crontab (`crontab -e`):

```
*/5 * * * * /usr/bin/python3 ~/pi-clock/scrape-weather.py
```

## Optional: Mining Pool Stats (ckpool / asicseer)

`update-weather.py` queries a local postgres database (`ckstats_btc` / `ckstats_bch`) for hashrate and best share, and watches the pool `blocks/` directory for block finds.

Edit the paths at the top of `update-weather.py` to match your pool log locations, then add to crontab:

```
* * * * * /usr/bin/python3 ~/pi-clock/update-weather.py
```

When a block is found, the clock triggers the block detection animation automatically.

## File Overview

| File | Purpose |
|------|---------|
| `index.html` | Clock UI — runs in Chromium kiosk |
| `serve.py` | Local HTTP server (port 8080) |
| `start-clock.sh` | Launches serve.py and Chromium |
| `config.json` | User settings (location, brightness, schemes) |
| `config.html` | In-browser config editor at `/config` |
| `scrape-weather.py` | Fetches Ambient Weather data (optional) |
| `update-weather.py` | Pulls mining pool stats from postgres (optional) |
| `weather.json` | Live data file written by cron scripts (gitignored) |
| `pi-clock.service` | systemd service unit |
| `setup-pi.sh` | One-time Pi setup (NTP, service install) |
