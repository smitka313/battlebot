# Generates sounds/bell.mp3, a boxing-ring bell (three strikes). CC0 1.0.
# Usage: python3 tools/boxing_bell.py bell.wav  then convert to MP3 with ffmpeg.
import numpy as np, wave, sys
sr = 44100
rng = np.random.default_rng(7)
dur = 4.6
n = int(sr * dur)
out = np.zeros((n, 2))
# Modes of a large brass gong bell: (ratio to fundamental, relative level, decay seconds).
# Close pairs beat against each other, which gives a ring bell its shimmering "wah" ring.
f0 = 640.0
modes = [
    (1.000, 1.00, 3.2), (1.0045, 0.70, 3.0),
    (2.405, 0.75, 2.2), (2.418, 0.45, 2.0),
    (3.92, 0.45, 1.5), (3.95, 0.25, 1.3),
    (5.43, 0.35, 1.0), (7.08, 0.22, 0.7),
    (8.95, 0.15, 0.45), (11.2, 0.09, 0.3),
]
def strike(t0, force):
    s0 = int(t0 * sr)
    m = n - s0
    t = np.arange(m) / sr
    sig = np.zeros(m)
    for ratio, lvl, dec in modes:
        f = f0 * ratio * (1 + rng.uniform(-0.0006, 0.0006))
        ph = rng.uniform(0, 2 * np.pi)
        # higher modes get excited a bit more by a harder hit
        a = lvl * force ** (1 + 0.15 * ratio)
        sig += a * np.sin(2 * np.pi * f * t + ph) * np.exp(-t / dec)
    # hammer contact: a short bright click of filtered noise
    k = int(0.012 * sr)
    noise = rng.uniform(-1, 1, k)
    noise = np.convolve(noise, np.ones(3) / 3, mode='same') * np.exp(-np.arange(k) / (0.002 * sr))
    sig[:k] += 0.6 * force * noise
    # 1 ms attack so the strike doesn't click digitally
    att = int(0.001 * sr); sig[:att] *= np.linspace(0, 1, att)
    out[s0:, 0] += sig * 0.95
    out[s0:, 1] += sig * 1.0
# End-of-round "ding-ding-ding"
for t0, force in [(0.0, 1.0), (0.42, 0.92), (0.84, 0.97)]:
    strike(t0, force)
# simple small-room reflections
for d, g in [(0.023, 0.25), (0.041, 0.18), (0.067, 0.12)]:
    k = int(d * sr); out[k:] += out[:-k] * g
# fade the tail and normalize
fade = int(0.6 * sr); out[-fade:] *= np.linspace(1, 0, fade)[:, None]
out *= 0.89 / np.max(np.abs(out))
pcm = (out * 32767).astype('<i2')
w = wave.open(sys.argv[1], 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes()); w.close()
