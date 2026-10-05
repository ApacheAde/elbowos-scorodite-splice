# Scorodite Splice

Full-colour Python 3 neon cable-bay joiner for [ElbowOS](https://x.com/ElbowOS).

Four vertical splice bays. Chartreuse, cyan, and amber jackets drop from the header. Slide the clamp and weld the good cores. Rust live-faults break the combo — dodge them.

Original arcade. Not a commercial emulator, not a ROM, not a reskin of the ElbowOS crane, pipe, or prism packs.

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scorodite_splice.py --play
```

Left / Right or A / D move the clamp. R restarts. Q quits.

## Record a 9:16 reel

```bash
python3 scorodite_splice.py --record
```

Headless autoplay writes a 1080x1920, 15s, 30fps H.264 MP4 (`SDL_VIDEODRIVER=dummy`, libx264 yuv420p CRF 20, +faststart).

## Links

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1p8uY-AzS3nVder4hDUc1Zr3UMIlBR2Ec/view?usp=drivesdk
- Posted copy: https://drive.google.com/file/d/1amq4vIqUYW2EA6TRaYCDJbMQjXAedrxW/view?usp=drivesdk
