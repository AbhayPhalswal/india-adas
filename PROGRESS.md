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
- [x] git init + first commit (d42c01a)

### Level 0 run
- [ ] Pipeline smoke test on ultralytics sample image (proves toolchain)
- [!] Footage today: iPhone 17 Pro in cab (1080p60, Most Compatible, HDR off, AE/AF lock), Gurugram → Dwarka via Kapashera, whole trip → data/raw/2026-09-16_gurugram-dwarka_iphone_clip1.mp4
- [ ] From tomorrow: GoPro (primary) + 270° multi-lens camera
- [ ] Run `python src/level0_detect.py data/raw/<clip>.mp4`
- [ ] Watch outputs/level0/ video, note what it gets wrong (autos, cattle, handcarts, close two-wheelers)
- [ ] Write the honest paragraph in README.md "Level 0 — what I saw"
- [ ] Fill in the LOG.md row

### Accounts (only you can do these)
- [x] IDD: found the working official portal — india-data.org (IHub-Data, IIIT Hyderabad). Account created 2026-09-18.
- [x] IDD-X access requested and APPROVED (2026-09-18) — 171.4 GB single tar.gz
- [~] IDD-X → Google Drive "driving dataset" folder via Colab: notebooks/iddx_to_gdrive.py (needs your india-data cookie; resumable)
- [ ] IDD Detection / Segmentation: check india-data.org Datasets page for the small ones (Level 1 needs these, not IDD-X)
- [!] DriveIndia: download EULA + submit request form (links in notes/dataset-sources.md)
- [x] GitHub repo created and pushed: https://github.com/AbhayPhalswal/india-adas

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
- [ ] Tracking → bird's-eye-view demo video (single front camera first)
- [ ] BEV from the 270° multi-lens camera: per-lens calibration (OpenCV chessboard) + relative pose, then fuse

## Week 13–20 (Level 3)
- [ ] Buy ELM327 OBD-II dongle (~₹1–1.5k) for the Harrier — mount already owned (GoPro)
- [ ] Mount the 270° multi-lens camera in the Harrier for side coverage; find out stitched vs per-lens output + resolution per lens
- [ ] Harrier ADAS-failure logging: phone/GoPro on the instrument cluster + front camera on road, note every false brake / LDW / AEB event
- [ ] Sync test (torch-flash trick), verified < 20 ms
- [ ] 10 h collected → 40 h collected
- [ ] Face/plate blur pass
- [ ] Release "IndiaDrive-Telemetry v0.1" on Hugging Face with datasheet

## Week 17–24 (Level 4 + 5)
- [ ] Behaviour cloning pipeline on comma2k19
- [ ] Retrain on own data, compare
- [ ] CARLA / MetaDrive installed
- [ ] Indian scenario suite v0.1 (auto cut-in, cow, unmarked breaker, wrong-way vehicle)
