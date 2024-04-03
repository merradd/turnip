from app import app, CORS
from flask import request, jsonify
from datetime import datetime
import sqlite3 as sq
import logging 
import os

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reviews.log')
logging.basicConfig(filename=log_file_path, level=logging.DEBUG)

CORS(app)  # Применяем CORS ко всем маршрутам

def write_review(username, review, date):
	with sq.connect("polzovateli.db") as con:
		cur = con.cursor()

		cur.execute("""CREATE TABLE IF NOT EXISTS users (
							username TEXT,
							review TEXT,
							date TEXT
		)""")

		cur.execute("""INSERT INTO users VALUES (?, ?, ?)""", (username, review, date))

def get_today_date():
					current_date = datetime.now()
					year = str(current_date.year)
					month = str(current_date.month).zfill(2)
					day = str(current_date.day).zfill(2)
					return f"{day}.{month}.{year}"

@app.route('/submit', methods=['POST'])
def submit_review():
		try:
			data = request.get_json()
			username = str(data['username'])
			review = str(data['review'])
			app.logger.info(f"Review submitted successfully by {username}")
			date = get_today_date()
			write_review(username, review, date)
			data = [username, review, date]
			return data

		except Exception as e:
				app.logger.error(f"Error submitting review: {str(e)}")
				return jsonify({'status': 'error', 'message': str(e)})
		
@app.route('/send', methods=['GET'])
def send_review():
	try:
		with sq.connect("polzovateli.db") as con:
			cur = con.cursor()
			cur.execute("SELECT username, review, date FROM users")
			data = cur.fetchall()
			result = [{'username': row[0], 'review': row[1], 'date': row[2]} for row in data]
			return jsonify({'data': result})

	except Exception as e:
		app.logger.error({'status': 'error', 'message': str(e)})
		return jsonify({'status': 'error', 'message': str(e)})

