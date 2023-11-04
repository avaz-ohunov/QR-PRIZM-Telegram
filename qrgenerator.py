# qrgenerator.py

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask, SolidFillColorMask


# Метод генерации QR-кода для транзакций
def qr_generate_transactions(text, file):
	QRcode = qrcode.QRCode(
		error_correction = qrcode.constants.ERROR_CORRECT_H
	)
	
	# Добавление в QR-код данных
	QRcode.add_data(text)

	# Создание QR-кода
	QRcode.make()
	
	# Кастомизация QR-кода
	QRimg = QRcode.make_image(image_factory = StyledPilImage, 
			color_mask = RadialGradiantColorMask(edge_color = (127,55,183)),
			module_drawer = RoundedModuleDrawer(),
			eye_drawer = RoundedModuleDrawer(),
			embeded_image_path = "pzm.png")

	# Сохранение QR-кода
	QRimg.save(file)


# Метод генерации личного QR-кода
def qr_generate_personal(text, file):
	QRcode = qrcode.QRCode(
		error_correction = qrcode.constants.ERROR_CORRECT_H
	)
	
	# Добавление в QR-код данных
	QRcode.add_data(text)

	# Создание QR-кода
	QRcode.make()
	
	# Кастомизация QR-кода
	QRimg = QRcode.make_image(image_factory = StyledPilImage,
			color_mask = RadialGradiantColorMask(edge_color = (127,55,183)),
			module_drawer = RoundedModuleDrawer(),
			eye_drawer = RoundedModuleDrawer(),
			embeded_image_path = "pzm.png")

	# Сохранение QR-кода
	QRimg.save(file)
