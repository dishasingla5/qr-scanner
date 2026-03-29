
#!/usr/bin/env python3

import cv2
import requests
import base64
import numpy as np
import os
from bs4 import BeautifulSoup
from pyzbar.pyzbar import decode
from urllib.parse import urlparse

# ================= CONFIG =================
USE_ROBOFLOW = False  # 🔥 Change to True to enable AI detection

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW_MODEL = "your-model-name"
ROBOFLOW_VERSION = "1"

API_URL = f"https://detect.roboflow.com/{ROBOFLOW_MODEL}/{ROBOFLOW_VERSION}?api_key={ROBOFLOW_API_KEY}"

seen_codes = set()


# ================= UTIL FUNCTIONS =================
def is_url(text):
    parsed = urlparse(text)
    return parsed.scheme in ("http", "https") and parsed.netloc != ""


def fetch_data_from_url(url):
    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")

            if "application/json" in content_type:
                return response.json()

            elif "text/html" in content_type:
                soup = BeautifulSoup(response.text, "html.parser")
                main_p = soup.find("p")
                return main_p.get_text(strip=True) if main_p else "No text found"

            return response.text.strip()

        return f"Failed: {response.status_code}"

    except Exception as e:
        return f"Error: {str(e)}"


# ================= MAIN FUNCTION =================
def scan_qr():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera not accessible.")
        return

    print("Press ESC to exit")
    print(f"Mode: {'Roboflow + Decode' if USE_ROBOFLOW else 'Offline Decode Only'}")

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        resized = cv2.resize(frame, (640, 640))
        frame_count += 1

        detections = []

        # ===== OFFLINE MODE =====
        if not USE_ROBOFLOW:
            decoded_objs = decode(resized)

            for obj in decoded_objs:
                x, y, w, h = obj.rect
                detections.append((x, y, w, h, obj))

        # ===== ONLINE MODE =====
        else:
            # Reduce API calls
            if frame_count % 5 != 0:
                cv2.imshow("QR Scanner", resized)
                if cv2.waitKey(1) & 0xFF == 27:
                    break
                continue

            _, buffer = cv2.imencode('.jpg', resized)
            b64_image = base64.b64encode(buffer).decode("utf-8")

            try:
                response = requests.post(
                    API_URL,
                    data=b64_image,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )

                predictions = response.json().get("predictions", [])

            except Exception:
                print("Roboflow API error")
                predictions = []

            for pred in predictions:
                x = int(pred['x'] - pred['width'] / 2)
                y = int(pred['y'] - pred['height'] / 2)
                w = int(pred['width'])
                h = int(pred['height'])

                x = max(0, x)
                y = max(0, y)

                crop = resized[y:y + h, x:x + w]
                decoded_objs = decode(crop)

                for obj in decoded_objs:
                    detections.append((x, y, w, h, obj))

        # ===== PROCESS DETECTIONS =====
        for (x, y, w, h, obj) in detections:
            qr_data = obj.data.decode('utf-8').strip()

            if qr_data in seen_codes:
                continue

            seen_codes.add(qr_data)

            print("\n=== New QR Code ===")

            if is_url(qr_data):
                print("URL:", qr_data)
                result = fetch_data_from_url(qr_data)
            else:
                result = qr_data
                print("Text:", result)

            display_text = str(result)[:50]

            # Draw box
            cv2.rectangle(resized, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Put text
            cv2.putText(resized, display_text, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Show count
        cv2.putText(resized, f"QR Count: {len(seen_codes)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

        cv2.imshow("QR Scanner", resized)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


# ================= RUN =================
if __name__ == "__main__":
    scan_qr()

