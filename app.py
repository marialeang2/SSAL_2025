from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pika
import threading

rabbit_host = '10.128.0.3'
rabbit_user = 'ssal'
rabbit_password = '1234'
exchange = 'amq.topic'
topic = 'esp32'

last_temp_message = None

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
    connection = pika.BlockingConnection(pika.ConnectionParameters(host = rabbit_host, credentials=pika.PlainCr>
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type='topic', durable = True)
    queue_name = 'esp32'
    channel.queue_declare(queue=queue_name)
    channel.queue_bind(exchange=exchange, queue=queue_name, routing_key='esp32')
    channel.basic_publish(exchange=exchange, routing_key=topic, body=data)
    connection.close()
    return jsonify({"status": "ok", "sent": data})

@app.route("/temperature", methods=["GET"])
def get_last_temperature():
    global last_temp_message
    if last_temp_message:
        # extrae solo el número, ej: "TEMP:185.4" -> "185.4"
        value = last_temp_message.replace("TEMP:", "").strip()
        return jsonify({"temperature": value})
    return jsonify({"temperature": None})

def callback(ch, method, properties, body):
    global last_temp_message
    message = body.decode()
    print("Mensaje recibido del broker:", message)
    if message.startswith("TEMP:"):
        last_temp_message = message

def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=rabbit_host,
        credentials=pika.PlainCredentials(rabbit_user, rabbit_password)
    ))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)
    queue_name = 'esp32'
    channel.queue_declare(queue=queue_name)
    channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=topic)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print("Esperando mensajes que empiecen con TEMP:...")
    channel.start_consuming()

if __name__ == "__main__":
    consumer_thread = threading.Thread(target=start_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()
    app.run(host="0.0.0.0", port=8080)
