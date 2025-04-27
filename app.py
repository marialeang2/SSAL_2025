from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pika

rabbit_host = '10.128.0.3'
rabbit_user = 'ssal'
rabbit_password = '1234'
exchange = 'amq.topic'
topic = 'esp32'


app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send", methods=["POST"])
def send():
    data = request.json.get("data", "")
    print("Mensaje recibido:", data)

    # Enviar a RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host = rabbit_host, credentials=pika.PlainCredentials(rabbit_user,rabbit_password)))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type='topic', durable = True)
    queue_name = 'esp32'
    channel.queue_declare(queue=queue_name)
    channel.queue_bind(exchange=exchange, queue=queue_name, routing_key='esp32')
    channel.basic_publish(exchange=exchange, routing_key=topic, body=data)
    connection.close()

    return jsonify({"status": "ok", "sent": data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)