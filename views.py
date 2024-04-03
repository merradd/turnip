import os
from app import app, CORS
from flask import request,jsonify,send_file
import logging
from barcode import Code128
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from io import BytesIO

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('Arial', 'arialmt.ttf'))

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server.log')
logging.basicConfig(filename=log_file_path, level=logging.DEBUG)

CORS(app)  # Применяем CORS ко всем маршрутам

def forA4(data, width, height, font_size, in_one_line, line_cut, EAC_mark, mand_cert, center_labels, pdf_buffer, RSTmark):
	try:
		barcodes = data['barcodes']
		articles = data['articles']
		colors = data['colors']
		sizes = data['sizes']
		nameProducts = data['nameProducts']
		nameSellers = data['nameSellers']

		pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=(595, 842))
		y_position = 700
		x_position = 15
		pdf_canvas.setFont("Arial", font_size)
		app.logger.info('Send data: %s', data)

		parameter = 0

		for key, barcode in barcodes.items():
				while parameter < int(data['amountBarcodes'][key]):
					code128 = Code128(barcode, writer=ImageWriter())
					options = {
						'module_width': 0.1,
						'module_height': 3,
						'font_size': 3,
						'text_distance': 2
					}
					barcode_image = code128.render(options)

					if y_position < 100: 
							pdf_canvas.showPage()
							pdf_canvas.setFont("Arial", font_size)
							x_position = 15
							y_position = 700 
					
					prey = y_position

					parameterbarcode = pdf_canvas._pagesize[0] / 2

					if x_position != 15:
							pdf_canvas.drawInlineImage(barcode_image, parameterbarcode + (parameterbarcode - barcode_image.width) / 2, y_position)
					else:
						pdf_canvas.drawInlineImage(barcode_image, (parameterbarcode - barcode_image.width) / 2, y_position)

					
					if center_labels == 1:
							if x_position == 15:
								article_value = articles.get(key, '')
								if article_value:
										article_width = pdf_canvas.stringWidth(f"Артикуль: {articles[key]}", "Arial", font_size)
										pdf_canvas.drawString((parameterbarcode - 5)/2 - article_width/2, y_position, f"Артикуль: {articles[key]}")
										y_position -= font_size * 1.2
								
								if in_one_line != 1:
										color_value = colors.get(key, '')
										if color_value:
												color_width = pdf_canvas.stringWidth(f"Цвет: {color_value}", "Arial", font_size)
												pdf_canvas.drawString((parameterbarcode - 5)/2 - color_width/2, y_position, f"Цвет: {color_value}")
												y_position -= font_size * 1.2

										size_value = sizes.get(key, '')
										if size_value:

											size_width = pdf_canvas.stringWidth(f"Размер: {sizes[key]}", "Arial", font_size)
											pdf_canvas.drawString((parameterbarcode - 5)/2 - size_width/2, y_position, f"Размер: {sizes[key]}")
											y_position -= font_size * 1.2
								
								else:
										color_value = colors.get(key, '')
										size_value = sizes.get(key, '')
										size_width = pdf_canvas.stringWidth(f"Размер: {sizes[key]}", "Arial", font_size)
										color_width = pdf_canvas.stringWidth(f"Цвет: {color_value}", "Arial", font_size)
										if color_value and size_value:

												pdf_canvas.drawString((parameterbarcode - 5)/2 - (size_width + color_width)/2, y_position, f"Цвет: {color_value} \ Размер: {sizes[key]}")
												y_position -= font_size * 1.2
										
										elif color_value:
												pdf_canvas.drawString((parameterbarcode - 5)/2 - color_width/2, y_position, f"Цвет: {color_value}")
												y_position -= font_size * 1.2
										
										elif size_value:
												pdf_canvas.drawString((parameterbarcode - 5)/2 - size_width/2, y_position, f"Размер: {sizes[key]}")
												y_position -= font_size * 1.2
								
								
								nameProduct_value = nameProducts.get(key, '')
								if nameProduct_value:
									nameProduct_width = pdf_canvas.stringWidth(f"{nameProducts[key]}", "Arial", font_size)
									pdf_canvas.drawString((parameterbarcode - 5)/2 - nameProduct_width/2, y_position, f"{nameProducts[key]}")
									y_position -= font_size * 1.2

								nameSeller_value = nameSellers.get(key, '')
								if nameSeller_value:
									nameSeller_width = pdf_canvas.stringWidth(f"{nameSellers[key]}", "Arial", font_size)
									pdf_canvas.drawString((parameterbarcode - 5)/2 - nameSeller_width/2, y_position, f"{nameSellers[key]}")
									y_position -= font_size * 1.2

								text = 'Товар не подлежит'
								under_text = 'Обязательной сертификации'
								text_width = pdf_canvas.stringWidth(text, "Arial", font_size)
								under_text_width = pdf_canvas.stringWidth(under_text,"Arial", font_size)
								if mand_cert == 1:
										pdf_canvas.drawString((parameterbarcode - 5)/2 - text_width/2, y_position, text)
										y_position -= font_size * 1.2
										pdf_canvas.drawString((parameterbarcode - 5) / 2 - under_text_width/2, y_position, under_text)
										y_position -= font_size * 1.2
							else:
								article_value = articles.get(key, '')
								if article_value:
										article_width = pdf_canvas.stringWidth(f"Артикуль: {articles[key]}", "Arial", font_size)
										pdf_canvas.drawString(parameterbarcode + (parameterbarcode - 5)/2 - article_width/2, y_position, f"Артикуль: {articles[key]}")
										y_position -= font_size * 1.2
								
								if in_one_line != 1:
										color_value = colors.get(key, '')
										if color_value:
												color_width = pdf_canvas.stringWidth(f"Цвет: {color_value}", "Arial", font_size)
												pdf_canvas.drawString(parameterbarcode + (parameterbarcode - 5)/2 - color_width/2, y_position, f"Цвет: {color_value}")
												y_position -= font_size * 1.2

										size_value = sizes.get(key, '')
										if size_value:

											size_width = pdf_canvas.stringWidth(f"Размер: {sizes[key]}", "Arial", font_size)
											pdf_canvas.drawString(parameterbarcode + (parameterbarcode - 5)/2 - size_width/2, y_position, f"Размер: {sizes[key]}")
											y_position -= font_size * 1.2
								
								else:
										color_value = colors.get(key, '')
										size_value = sizes.get(key, '')
										size_width = pdf_canvas.stringWidth(f"Размер: {sizes[key]}", "Arial", font_size)
										color_width = pdf_canvas.stringWidth(f"Цвет: {color_value}", "Arial", font_size)
										if color_value and size_value:

												pdf_canvas.drawString(parameterbarcode + (parameterbarcode - 5)/2 - (size_width + color_width)/2, y_position, f"Цвет: {color_value} \ Размер: {sizes[key]}")
												y_position -= font_size * 1.2
										
										elif color_value:
												pdf_canvas.drawString(parameterbarcode + (parameterbarcode - 5)/2 - color_width/2, y_position, f"Цвет: {color_value}")
												y_position -= font_size * 1.2
										
										elif size_value:
												pdf_canvas.drawString(parameterbarcode + (parameterbarcode - 5)/2 - size_width/2, y_position, f"Размер: {sizes[key]}")
												y_position -= font_size * 1.2
								
								
								nameProduct_value = nameProducts.get(key, '')
								if nameProduct_value:
									nameProduct_width = pdf_canvas.stringWidth(f"{nameProducts[key]}", "Arial", font_size)
									pdf_canvas.drawString(parameterbarcode + (parameterbarcode - 5)/2 - nameProduct_width/2, y_position, f"{nameProducts[key]}")
									y_position -= font_size * 1.2

								nameSeller_value = nameSellers.get(key, '')
								if nameSeller_value:
									nameSeller_width = pdf_canvas.stringWidth(f"{nameSellers[key]}", "Arial", font_size)
									pdf_canvas.drawString(parameterbarcode + (parameterbarcode - 5)/2 - nameSeller_width/2, y_position, f"{nameSellers[key]}")
									y_position -= font_size * 1.2

								text = 'Товар не подлежит'
								under_text = 'Обязательной сертификации'
								text_width = pdf_canvas.stringWidth(text, "Arial", font_size)
								under_text_width = pdf_canvas.stringWidth(under_text,"Arial", font_size)
								if mand_cert == 1:
										pdf_canvas.drawString(parameterbarcode + (parameterbarcode - 5)/2 - text_width/2, y_position, text)
										y_position -= font_size * 1.2
										pdf_canvas.drawString(parameterbarcode + (parameterbarcode - 5) / 2 - under_text_width/2, y_position, under_text)
										y_position -= font_size * 1.2















					else:

								article_value = articles.get(key, '')
								if article_value:
									pdf_canvas.drawString(x_position, y_position, f"Артикуль: {articles[key]}")
									y_position -= font_size * 1.2

								if in_one_line != 1:
										color_value = colors.get(key, '')
										if color_value:
											pdf_canvas.drawString(x_position, y_position, f"Цвет: {color_value}")
											y_position -= font_size * 1.2

										size_value = sizes.get(key, '')
										if size_value:
											pdf_canvas.drawString(x_position, y_position, f"Размер: {sizes[key]}")
											y_position -= font_size * 1.2

								else:
										color_value = colors.get(key, '')
										size_value = sizes.get(key, '')
										if color_value and size_value:
												pdf_canvas.drawString(x_position, y_position, f"Цвет: {color_value} \ Размер: {sizes[key]}")
												y_position -= font_size * 1.2
										
										elif color_value:
												pdf_canvas.drawString(x_position, y_position, f"Цвет: {color_value}")
												y_position -= font_size * 1.2
										
										elif size_value:
												pdf_canvas.drawString(x_position, y_position, f"Размер: {color_value}")
												y_position -= font_size * 1.2

								nameProduct_value = nameProducts.get(key, '')
								if nameProduct_value:
									pdf_canvas.drawString(x_position, y_position, f"{nameProducts[key]}")
									y_position -= font_size * 1.2

								nameSeller_value = nameSellers.get(key, '')
								if nameSeller_value:
									pdf_canvas.drawString(x_position, y_position, f"{nameSellers[key]}")
									y_position -= font_size * 1.2

								text = 'Товар не подлежит'
								under_text = 'Обязательной сертификации'

								if mand_cert == 1:
										pdf_canvas.drawString(x_position, y_position, text)
										y_position -= font_size * 1.2
										pdf_canvas.drawString(x_position, y_position, under_text)
										y_position -= font_size * 1.2
					
					if line_cut == 1:
							# Устанавливаем параметры для штрихпунктирной линии
							pdf_canvas.setDash(3, 4)  # Первый аргумент - длина штриха, второй - длина разрыва
							half = pdf_canvas._pagesize[0] / 2

							if prey == 700 and x_position == 15:
									pdf_canvas.line(5, prey + barcode_image.height + 10, half, prey + barcode_image.height + 10) # сверху
									pdf_canvas.line(5, prey + barcode_image.height + 10, 5, y_position) #слева
									pdf_canvas.line(half, prey + barcode_image.height + 10, half, y_position) #справа
									pdf_canvas.line(5, y_position, half, y_position) #снизу
							
							elif prey == 700 and x_position != 15:
									pdf_canvas.line(half, prey + barcode_image.height + 10, 2 * half - 5, prey + barcode_image.height + 10) # сверху
									pdf_canvas.line(2 * half - 5, prey + barcode_image.height + 10, 2 * half - 5, y_position) #справа
									pdf_canvas.line(half, y_position, 2 * half - 5, y_position) #снизу
							
							elif prey != 700 and x_position == 15:
									pdf_canvas.line(5, prey + 2 * barcode_image.height + 10, 5, y_position) #слева
									pdf_canvas.line(half, prey + 2 * barcode_image.height + 10, half, y_position) #справа
									pdf_canvas.line(5, y_position, half, y_position) #снизу
							
							else: 
									pdf_canvas.line(2 * half - 5, prey + 2 * barcode_image.height + 10, 2 * half - 5, y_position) #справа
									pdf_canvas.line(half, y_position, 2 * half - 5, y_position) #снизу


								

							pdf_canvas.setDash(1, 0)  # Возвращаем стандартные параметры для линий
					
					if EAC_mark == 1: 
						if x_position == 15:
								pdf_canvas.drawInlineImage('pics\EAC.png', parameterbarcode/1.2, prey + 10, width=23, height=15)
								y_position -= font_size * 1.2
						else:
								pdf_canvas.drawInlineImage('pics\EAC.png', parameterbarcode + parameterbarcode/1.2, prey + 10, width=23, height=15)
								y_position -= font_size * 1.2
					
					if RSTmark == 1 and EAC_mark != 1:
						if x_position == 15:
								pdf_canvas.drawInlineImage('pics\RSTmark.png', parameterbarcode/1.2, prey + 10, width=28, height=21)
								y_position -= font_size * 1.2
						else:
								pdf_canvas.drawInlineImage('pics\RSTmark.png', parameterbarcode + parameterbarcode/1.2, prey + 10, width=28, height=21)
								y_position -= font_size * 1.2
					
					elif RSTmark == 1 and EAC_mark == 1:
						if x_position == 15:
								pdf_canvas.drawInlineImage('pics\RSTmark.png', parameterbarcode/1.2, prey + 40, width=28, height=21)
								y_position -= font_size * 1.2
						else:
								pdf_canvas.drawInlineImage('pics\RSTmark.png', parameterbarcode + parameterbarcode/1.2, prey + 40, width=28, height=21)
								y_position -= font_size * 1.2


					if x_position == 15:
						x_position += parameterbarcode
						y_position = prey 
					else: 
						x_position = 15
						y_position -= (barcode_image.height + 10)


					app.logger.info(x_position, y_position)

					
					parameter += 1
				parameter = 0
		
		pdf_canvas.save()

		with open('pdf_canvas.pdf', 'wb') as pdf_file:
				pdf_file.write(pdf_buffer.getvalue())
	
	except Exception as e:
		app.logger.error(f"Error generating PDF in forA4: {str(e)}")

def forTermo(data, width, height, font_size, in_one_line, line_cut, EAC_mark, mand_cert, center_labels, pdf_buffer, RSTmark):
		barcodes = data['barcodes']
		articles = data['articles']
		colors = data['colors']
		sizes = data['sizes']
		nameProducts = data['nameProducts']
		nameSellers = data['nameSellers']


		# combined_values = list(barcodes.values()) + list(articles.values()) + list(colors.values()) + list(sizes.values()) + list(nameProducts.values()) + list(nameSellers.values())
		# longest_string = int(len(max(combined_values, key=len)))
		# # Рассчитываем предполагаемую ширину страницы
		# proposed_width = longest_string * 10 + width * 0.38 + 16

		# # Устанавливаем ширину страницы в зависимости от условий
		# page_width = max(width * 4, proposed_width)

		pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=(width * 5, height * 5)) # УВЕЛИЧЕНО НА 25%
		y_position = height * 3 - 14
		x_position = 15
		pdf_canvas.setFont("Arial", font_size)

		parameter = 0

		for key, barcode in barcodes.items():
				while parameter < int(data['amountBarcodes'][key]):
					code128 = Code128(barcode, writer=ImageWriter())
					options = {
						'module_width': 0.1,
						'module_height': 3,
						'font_size': font_size/3,
						'text_distance': 2
					}
					barcode_image = code128.render(options)


					pdf_canvas.setFont("Arial", font_size)
					y_position = height * 3 - 14
					parameterbarcode = pdf_canvas._pagesize[0]
					pdf_canvas.drawInlineImage(barcode_image, (parameterbarcode - barcode_image.width) / 2, y_position)

					y_position -= font_size * 0.8

					if center_labels != 1:
						article_value = articles.get(key, '')
						if article_value:
							pdf_canvas.drawString(x_position, y_position, f"Артикуль: {articles[key]}")
							y_position -= font_size * 1.4


						if in_one_line == 0:
								color_value = colors.get(key, '')
								if color_value:
										pdf_canvas.drawString(x_position, y_position, f"Цвет: {colors[key]}")
										y_position -= font_size * 1.4

								size_value = sizes.get(key, '')
								if size_value:
									pdf_canvas.drawString(x_position, y_position, f"Размер: {sizes[key]}")
									y_position -= font_size * 1.4
						else:
								color_value = colors.get(key, '')
								size_value = sizes.get(key, '')
								if color_value and size_value:
									pdf_canvas.drawString(x_position, y_position, f"Цвет: {colors[key]}" + "/" + f"Размер: {sizes[key]}")
									y_position -= font_size * 1.4
								elif color_value:
									pdf_canvas.drawString(x_position, y_position, f"Цвет: {colors[key]}")
									y_position -= font_size * 1.4
								else:
									pdf_canvas.drawString(x_position, y_position, f"Цвет: {sizes[key]}")
									y_position -= font_size * 1.4

								


						nameProduct_value = nameProducts.get(key, '')
						if nameProduct_value:
							pdf_canvas.drawString(x_position, y_position, f"{nameProducts[key]}")
							y_position -= font_size * 1.4

						nameSeller_value = nameSellers.get(key, '')
						if nameSeller_value:
							pdf_canvas.drawString(x_position, y_position, f"{nameSellers[key]}")
							y_position -= font_size * 1.4
						
						text = 'Товар не подлежит'
						under_text = 'Обязательной сертификации'

						if mand_cert == 1:
							pdf_canvas.drawString(x_position, y_position, text)
							y_position -= font_size * 1.2
							pdf_canvas.drawString(x_position, y_position, under_text)

					else:
						article_value = articles.get(key, '')
						if article_value:
							article_width = pdf_canvas.stringWidth(f"Артикуль: {articles[key]}", "Arial", font_size)
							pdf_canvas.drawString((parameterbarcode - x_position)/2 - article_width/2, y_position, f"Артикуль: {articles[key]}")
							y_position -= font_size * 1.4


						if in_one_line == 0:
								color_value = colors.get(key, '')
								if color_value:
										color_width = pdf_canvas.stringWidth(f"Цвет: {color_value}", "Arial", font_size)
										pdf_canvas.drawString((parameterbarcode - x_position)/2 - color_width/2, f"Цвет: {colors[key]}")
										y_position -= font_size * 1.4

								size_value = sizes.get(key, '')
								if size_value:
									size_width = pdf_canvas.stringWidth(f"Размер: {sizes[key]}", "Arial", font_size)
									pdf_canvas.drawString((parameterbarcode - x_position)/2 - size_width/2, y_position, f"Размер: {sizes[key]}")
									y_position -= font_size * 1.4
						else:
								color_value = colors.get(key, '')
								size_value = sizes.get(key, '')
								if color_value and size_value:
									size_width = pdf_canvas.stringWidth(f"Размер: {sizes[key]}", "Arial", font_size)
									color_width = pdf_canvas.stringWidth(f"Цвет: {color_value}", "Arial", font_size)
									pdf_canvas.drawString((parameterbarcode - x_position)/2 - (size_width + color_width)/2, y_position, f"Цвет: {colors[key]}" + "/" + f"Размер: {sizes[key]}")
									y_position -= font_size * 1.4
								elif color_value:
									color_width = pdf_canvas.stringWidth(f"Цвет: {color_value}", "Arial", font_size)
									pdf_canvas.drawString((parameterbarcode - x_position)/2 - color_width/2, y_position, f"Цвет: {colors[key]}")
									y_position -= font_size * 1.4
								else:
									size_width = pdf_canvas.stringWidth(f"Размер: {sizes[key]}", "Arial", font_size)
									pdf_canvas.drawString((parameterbarcode - x_position)/2 - size_width/2, y_position, f"Цвет: {sizes[key]}")
									y_position -= font_size * 1.4

								


						nameProduct_value = nameProducts.get(key, '')
						if nameProduct_value:
							nameProduct_width = pdf_canvas.stringWidth(f"{nameProducts[key]}", "Arial", font_size)
							pdf_canvas.drawString((parameterbarcode - x_position) / 2 - nameProduct_width / 2, y_position, f"{nameProducts[key]}")
							y_position -= font_size * 1.4

						nameSeller_value = nameSellers.get(key, '')
						if nameSeller_value:
							nameSeller_width = pdf_canvas.stringWidth(f"{nameSellers[key]}", "Arial", font_size)
							pdf_canvas.drawString((parameterbarcode - x_position) / 2 - nameSeller_width / 2, y_position, f"{nameSellers[key]}")
							y_position -= font_size * 1.4
						
						text = 'Товар не подлежит'
						under_text = 'Обязательной сертификации'
						text_width = pdf_canvas.stringWidth(text, "Arial", font_size)
						under_text_width = pdf_canvas.stringWidth(under_text,"Arial", font_size)
						if mand_cert == 1:
							pdf_canvas.drawString((parameterbarcode - x_position) / 2 - text_width / 2, y_position, text)
							y_position -= font_size * 1.2
							pdf_canvas.drawString((parameterbarcode - x_position) / 2 - under_text_width / 2, y_position, under_text)

					if EAC_mark == 1: 
						pdf_canvas.drawInlineImage('pics\EAC.png', parameterbarcode - 45, height * 3 - 14, width=28, height=21)

					
					if EAC_mark == 1:
						if RSTmark == 1: 
							pdf_canvas.drawInlineImage('pics\RSTmark.png', parameterbarcode - 45, height * 3 + 25, width=28, height=21)
					else:
						if RSTmark == 1:
							pdf_canvas.drawInlineImage('pics\RSTmark.png', parameterbarcode - 45, height * 3 - 14, width=28, height=21)
					parameter += 1
					pdf_canvas.showPage()
				parameter = 0
		
		pdf_canvas.save()

		with open('pdf_canvas.pdf', 'wb') as pdf_file:
				pdf_file.write(pdf_buffer.getvalue())

@app.route('/generate', methods=['POST'])
def generate_pdf():
		try:
				data = request.get_json()

				# РАЗМЕРЫ ШТРИХКОДА
				WHsize = data['sett']['sizeBarcodes'].split('x') 

				width = float(WHsize[0])
				height = float(WHsize[1])

				# РАЗМЕР ТЕКСТА
				font_size = int(data['sett']['fontSize'])

				# В ОДНУ ЛИНИЮ ЦВЕТ И РАЗМЕР
				in_one_line = int(data['sett']['RGBSizeInOneLine'])

				# ЛИНИИ ОБРЕЗА
				line_cut = int(data['sett']['lineCut'])

				# ЗНАК EAC
				EAC_mark = int(data['sett']['EACmark'])

				# ОБЯЗАТЕЛЬНАЯ СЕРТИФИКАЦИЯ
				mand_cert = int(data['sett']['mandatoryCertification'])

				# НАДПИСИ ПО ЦЕНТРУ
				center_labels = int(data['sett']['centerLabels'])

				RSTmark = int(data['sett']['RSTmark'])

				# В ТАБЛИЦЕ ИЛИ В EXCEL'E
				isInTable = int(data['generateInTable'])

				pdf_buffer = BytesIO()

				if int(data['sett']['isA4']) == 1:
					forA4(data, width, height, font_size, in_one_line, line_cut, EAC_mark, mand_cert, center_labels, pdf_buffer, RSTmark)
				else: 
					forTermo(data, width, height, font_size, in_one_line, line_cut, EAC_mark, mand_cert, center_labels, pdf_buffer, RSTmark)
				return send_file(BytesIO(pdf_buffer.getvalue()), download_name="pdf_canvas.pdf")
		except Exception as e:
				app.logger.error(f"Error generating: {str(e)}")
				return jsonify({'error': 'Internal Server Error'}), 500

