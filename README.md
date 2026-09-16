# india-adas

Learning to build perception for Indian roads, starting from zero. First-year project.

Following a six-month ladder:

| Level | Goal | Status |
|---|---|---|
| 0 | Pretrained detector on Indian dashcam footage — observe the domain gap | in progress |
| 1 | Fine-tune on DriveIndia / IDD Detection, per-class mAP before/after | |
| 2 | Segmentation (IDD) + monocular depth + tracking → bird's-eye view | |
| 3 | Collect own video + OBD telemetry dataset (the thing that doesn't exist) | |
| 4 | Behaviour cloning on comma2k19, then on own data | |
| 5 | CARLA closed-loop + Indian scenario suite | |

## Setup

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
pip install ultralytics opencv-python
```

## Level 0 — what I saw

_(one honest paragraph after running `python src/level0_detect.py data/raw/<clip>.mp4`)_

## Data

Indian datasets used are academic / non-commercial licence:
- IDD family — IIIT Hyderabad, https://idd.insaan.iiit.ac.in/
- DriveIndia — TiHAN, IIT Hyderabad
