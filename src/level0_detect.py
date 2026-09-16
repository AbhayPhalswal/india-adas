"""Level 0: run a pretrained YOLO on Indian dashcam footage, save annotated video.
Purpose: see the domain gap with your own eyes.

Usage:
    python src/level0_detect.py data/raw/myclip.mp4
    python src/level0_detect.py data/raw/frame.jpg        # single image works too
"""
import sys
from collections import Counter
from pathlib import Path

from ultralytics import YOLO

MODEL = "yolo26n.pt"  # nano model, ~2.4M params; downloads on first run

source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw/sample.mp4")
if not source.exists():
    sys.exit(f"Not found: {source}\nPut a dashcam clip in data/raw/ and pass its path.")

model = YOLO(MODEL)

counts = Counter()
frames = 0
results = model.predict(
    source=str(source),
    save=True,
    project="outputs",
    name="level0",
    exist_ok=True,
    stream=True,  # frame by frame so long videos don't eat RAM
    conf=0.25,
    verbose=False,
)
for r in results:
    frames += 1
    for c in r.boxes.cls.tolist():
        counts[model.names[int(c)]] += 1

print(f"\nProcessed {frames} frame(s) from {source.name} with {MODEL}")
print("Detections by class (summed over all frames):")
for name, n in counts.most_common():
    print(f"  {name:15s} {n}")
print("\nAnnotated output saved under outputs/level0/")
print("Now watch it. What did it call the auto-rickshaws? Did it see the cow?")
