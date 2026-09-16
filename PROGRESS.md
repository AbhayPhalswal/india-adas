# Progress tracker

Legend: [x] done  [ ] not started  [~] in progress  [!] needs you (account / hardware / footage)

## Day 1 — 2026-09-16 (Level 0 setup)

### Environment
- [x] Python 3.12 present
- [x] Virtual environment `.venv/` created
- [~] PyTorch + torchvision (CUDA 12.8 build) installing into .venv
- [ ] ultralytics + opencv-python installed into .venv
- [ ] `torch.cuda.is_available()` → True on RTX A1000 6GB

### Project scaffold
- [x] Folders: data/{raw,datasets,telemetry}, outputs, models, notebooks, src, experiments, notes/papers
- [x] .gitignore (data, outputs, models, weights excluded)
- [x] requirements.txt
- [x] experiments/LOG.md
- [x] src/level0_detect.py
- [x] README.md
- [ ] git init + first commit

### Level 0 run
- [ ] Pipeline smoke test on ultralytics sample image (proves toolchain)
- [!] Indian dashcam footage in data/raw/ — record 10 min from passenger seat, or download a YouTube dashcam clip
- [ ] Run `python src/level0_detect.py data/raw/<clip>.mp4`
- [ ] Watch outputs/level0/ video, note what it gets wrong (autos, cattle, handcarts, close two-wheelers)
- [ ] Write the honest paragraph in README.md "Level 0 — what I saw"
- [ ] Fill in the LOG.md row

### Accounts (only you can do these)
- [!] Register at https://insaan.iiit.ac.in for IDD datasets
- [!] Register at TiHAN / IIT Hyderabad portal for DriveIndia
- [!] Create GitHub repo `india-adas`, add remote, push

## Week 1–2 (Level 0 complete)
- [ ] Annotated domain-gap video committed
- [ ] Python / PyTorch / OpenCV basics comfortable

## Week 3–4
- [ ] IDD access approved, dataset downloaded to data/datasets/
- [ ] DriveIndia access approved, downloaded
- [ ] notes/papers/idd.md — 1-page summary
- [ ] notes/papers/driveindia.md — 1-page summary

## Week 5–8 (Level 1)
- [ ] Baseline: off-the-shelf yolo26 mAP50 / mAP50-95 on DriveIndia test set
- [ ] Fine-tune yolo26s on DriveIndia
- [ ] Per-class breakdown table (target ~78.7 mAP50 overall; rare classes are the story)
- [ ] README before/after table

## Week 9–12 (Level 2)
- [ ] Segmentation on IDD (mIoU)
- [ ] Depth Anything V2 on Indian footage
- [ ] Tracking → bird's-eye-view demo video

## Week 13–20 (Level 3)
- [ ] Buy ELM327 OBD-II dongle + phone mount (~₹2–4k)
- [ ] Sync test (torch-flash trick), verified < 20 ms
- [ ] 10 h collected → 40 h collected
- [ ] Face/plate blur pass
- [ ] Release "IndiaDrive-Telemetry v0.1" on Hugging Face with datasheet

## Week 17–24 (Level 4 + 5)
- [ ] Behaviour cloning pipeline on comma2k19
- [ ] Retrain on own data, compare
- [ ] CARLA / MetaDrive installed
- [ ] Indian scenario suite v0.1 (auto cut-in, cow, unmarked breaker, wrong-way vehicle)
