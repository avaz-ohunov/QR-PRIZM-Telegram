# headline.py

from PIL import Image, ImageDraw, ImageFont


# Метод создания заголовка в QR-коде
def create_headline(address, file):
	# Открытие изображения
	img = Image.open(f"{file}.png")
	idraw = ImageDraw.Draw(img)

	# Параметры заголовка
	headline = ImageFont.truetype("arial.ttf", size = 25)
	text_size = headline.getsize(address)

	# Располагаем адрес посередине
	width = (img.size[0] - text_size[0]) // 2

	# Пишем адрес кошелька на фотографии
	idraw.text((width, 5), address, font = headline, fill = (12,12,12))

	img.save(f"{file}.png")
