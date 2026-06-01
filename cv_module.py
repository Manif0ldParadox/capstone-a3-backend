import cv2
import numpy as np
import imutils
import os
from datetime import datetime


FAKTOR_PPM = 30.4
TOLERANSI_CM = 0.3

MASTER_BOX = {
    "Box X1": {"lebar": 5.0, "panjang": 7.5},
    "Box X3": {"lebar": 7.8, "panjang": 10.0}
}


def run_inspection():
    """
    Modul Computer Vision untuk inspeksi dimensi objek.

    Alur:
    1. Membuka kamera
    2. Mengambil satu frame
    3. Deteksi kontur objek
    4. Menghitung panjang dan lebar
    5. Menentukan status OK / NG
    6. Menyimpan gambar hasil inspeksi
    7. Mengembalikan hasil ke main.py
    """

    # Coba kamera eksternal dulu
    cap = cv2.VideoCapture(1)

    # Kalau kamera eksternal tidak terdeteksi, coba kamera laptop
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return {
            "success": False,
            "message": "Kamera tidak terdeteksi"
        }

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return {
            "success": False,
            "message": "Gagal membaca frame dari kamera"
        }

    # Resize frame agar pemrosesan lebih stabil
    frame = imutils.resize(frame, width=800)

    # Preprocessing gambar
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)

    edged = cv2.Canny(gray, 50, 100)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)

    # Deteksi kontur
    cnts = cv2.findContours(
        edged.copy(),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    cnts = imutils.grab_contours(cnts)

    if len(cnts) == 0:
        return {
            "success": False,
            "message": "Objek tidak terdeteksi"
        }

    # Ambil kontur terbesar sebagai objek utama
    c = max(cnts, key=cv2.contourArea)

    if cv2.contourArea(c) <= 2000:
        return {
            "success": False,
            "message": "Objek terlalu kecil atau tidak valid"
        }

    # Bounding box rotasi
    rect = cv2.minAreaRect(c)
    box = cv2.boxPoints(rect)
    box = np.int32(box)

    lebar_piksel, panjang_piksel = rect[1]

    # Pastikan lebar adalah sisi yang lebih pendek
    if lebar_piksel > panjang_piksel:
        lebar_piksel, panjang_piksel = panjang_piksel, lebar_piksel

    if lebar_piksel <= 0 or panjang_piksel <= 0:
        return {
            "success": False,
            "message": "Gagal menghitung ukuran objek"
        }

    # Konversi piksel ke cm
    lebar_asli_cm = lebar_piksel / FAKTOR_PPM
    panjang_asli_cm = panjang_piksel / FAKTOR_PPM

    status = "NG"
    object_type = "Unknown"

    # Bandingkan dengan ukuran master box
    for nama_box, ukuran in MASTER_BOX.items():
        selisih_lebar = abs(lebar_asli_cm - ukuran["lebar"])
        selisih_panjang = abs(panjang_asli_cm - ukuran["panjang"])

        if selisih_lebar <= TOLERANSI_CM and selisih_panjang <= TOLERANSI_CM:
            status = "OK"
            object_type = nama_box
            break

    # Simpan gambar hasil inspeksi
    os.makedirs("captures", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = f"captures/inspection_{timestamp}.jpg"

    warna_status = (0, 255, 0) if status == "OK" else (0, 0, 255)

    cv2.drawContours(frame, [box], -1, warna_status, 2)

    cv2.putText(
        frame,
        f"Status: {status}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        warna_status,
        3
    )

    cv2.putText(
        frame,
        f"Object: {object_type}",
        (10, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Lebar: {lebar_asli_cm:.2f} cm",
        (10, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Panjang: {panjang_asli_cm:.2f} cm",
        (10, 135),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    cv2.imwrite(image_path, frame)

    return {
        "success": True,
        "object_type": object_type,
        "length_mm": round(panjang_asli_cm * 10, 2),
        "width_mm": round(lebar_asli_cm * 10, 2),
        "status": status,
        "image_path": image_path,
        "source": "cv_module",
        "notes": f"Inspection generated from OpenCV module. Detected object: {object_type}"
    }