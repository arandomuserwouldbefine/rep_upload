import pytz
import sqlite3
from datetime import datetime
from flask import Flask, render_template, jsonify


app = Flask(__name__)


def graph_points(array_name):
    utc_timezone = pytz.timezone('UTC')
    current_time = datetime.now(utc_timezone).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("SELECT price,Timestamp FROM price_graph")
    data = cursor.fetchall()
    format = '%Y-%m-%d %H:%M:%S'
    for dates in data:
        dateObject1 = datetime.strptime(current_time,format)
        dateObject2 = datetime.strptime(dates[1],format)

        hoursdifference = (dateObject1 - dateObject2).total_seconds() / 3600
        if hoursdifference < 24:
            graph_data = {
                'time': hoursdifference,
                'value': dates[0]
            }

            array_name.append(graph_data)

def update_cards():
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("")

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/data", methods=["POST"])
def get_data():
    try:
        conn = sqlite3.connect("products.db")
        cursor = conn.cursor()
        cursor.execute("SELECT product_name,image_path, price_royalblue, price_darkteal,additional_price FROM products")
        data = cursor.fetchall()
        conn.close()
        result = [{"product_name": row[0], "image_path": row[1],"price_royalblue": row[2], "price_darkteal": row[3],"additional_price": row[4]} for row in data]

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/cards", methods=["POST"])
def get_cards():
    try:
        conn = sqlite3.connect("products.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cards")
        data = cursor.fetchall()
        conn.close()
        result = [{"image_path": row[1],"title":row[2],"product_name": row[3],"price_darkteal": row[4], "additional_price": row[5]} for row in data]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/graph", methods=["POST"])
def get_graph_data():
    result = []
    try:
        graph_points(result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/test")

def testte():
    return render_template("test.html")


if __name__ == "__main__":
    app.run(debug=True)
