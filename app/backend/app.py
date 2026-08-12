import os
import mysql.connector
from flask import Flask, jsonify

app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST"),
        port=int(os.environ.get("MYSQL_PORT", 3306)),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get("MYSQL_DATABASE")
    )


@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to Kubernetes E-Commerce Application v2"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "UP"
    })


@app.route("/api/products")
def products():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(products)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
