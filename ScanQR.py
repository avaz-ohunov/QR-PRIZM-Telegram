# ScanQR.py

import cv2
from pyzbar import pyzbar

def scan_qr(file):
	img = cv2.imread(file)
	QR = pyzbar.decode(img)
	itog = "На фотографии QR-код не найден"
	
	for qr in QR:
		qr_data = qr.data.decode("utf-8")

		if qr_data[:31] == "https://wallet.prizm.space/?to=":
			itog = ""
			for d in qr_data[32:]:
				if d == ":":
					itog += "\n"
				
				else:
					itog += d

			return itog

		else:
			itog = qr_data
			return itog

	return itog
