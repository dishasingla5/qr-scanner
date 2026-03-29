# QR Code Scanner (AI + Offline Hybrid)

##  Overview

This project implements a hybrid QR code detection system combining:

* **pyzbar** for fast offline decoding
* **Roboflow API** for AI-based detection

##  Features

* Real-time QR detection using webcam
* Offline mode (fast, no internet required)
* AI mode (robust detection under challenging conditions)
* URL extraction and content fetching
* Duplicate QR filtering

##  Tech Stack

* Python
* OpenCV
* pyzbar
* Roboflow API
* BeautifulSoup

##  Setup

```bash
pip install -r requirements.txt
sudo apt-get install libzbar0
```

##  Run

```bash
python3 qr_scanner.py
```

##  Modes

* `USE_ROBOFLOW = False` → Offline mode
* `USE_ROBOFLOW = True` → AI detection mode

##  Applications

* Autonomous robots 
* Warehouse automation
* Smart navigation systems

##  License

MIT License
