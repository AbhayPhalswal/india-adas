# Dataset sources (checked 2026-09-16)

## IDD (IIIT Hyderabad)
Official portal https://idd.insaan.iiit.ac.in/ and https://insaan.iiit.ac.in — **unreachable on 2026-09-16**, retry every few days. IDD-X, IDD-3D, IDD-AW only exist there.

Kaggle mirrors (live, free Kaggle account, no approval wait):
- IDD Detection in YOLO format → https://www.kaggle.com/datasets/redzapdos123/indian-driving-dataset-detections-yolov11  (use for Level 1)
- IDD Segmentation → https://www.kaggle.com/datasets/mitanshuchakrawarty/new-idd-dataset  (Level 2)
- IDD 20K with masks → https://www.kaggle.com/datasets/abhishekprajapat/idd-20k  (Level 2)
- backup → https://www.kaggle.com/datasets/manjotpahwa/indian-driving-dataset

## DriveIndia (TiHAN, IIT Hyderabad) — reachable
Listed as "Camera Dataset" on https://tihan.iith.ac.in/TiAND.html
1. Download EULA: https://drive.google.com/file/d/1uiYwkWlsnX0okoNNG_jiWHftfTGZZj-7/view?usp=share_link
2. Fill it, upload in request form: https://docs.google.com/forms/d/e/1FAIpQLScKpnmiWM3-zXr8FeWzg8Lkk-AbRrNJlt1eCAEMoObmufneJw/viewform?usp=header
3. Download link arrives by email.
Paper: https://arxiv.org/abs/2507.19912

Licence for all of the above: academic / non-commercial only.

## Own recording gear (2026-09-16)
- GoPro (primary for Level 0/1: Linear lens, 1080p60, HyperSmooth on, no overlays)
- iPhone 17 Pro / iPhone Air (backup: 1080p60, H.264 "Most Compatible", HDR video OFF)
- Several multi-lens 270° field-of-view car cameras — a surround-view rig. Use for Level 2 (bird's-eye view from multiple cameras; catches side actors a front camera misses) and as side coverage in the Level 3 dataset. TODO: check whether output is one stitched panorama or separate per-lens files, and resolution per lens. Needs per-lens intrinsic calibration + relative pose for BEV. Not for Level 0/1 — those match single front-camera datasets (DriveIndia/IDD); GoPro front view is the primary there. Can run alongside the GoPro in the cab today if powered by power bank/USB.
- Tata Harrier with factory 360 camera + Level 2 ADAS — Level 3 platform (OBD-II telemetry; ADAS-failure logging via cluster camera). 360 parking cameras are not usable as a data source.
