import socketio
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit
from flask_mqtt import Mqtt
import eventlet

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = '172.16.73.4'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
eventlet.monkey_patch()
mqtt = Mqtt(app)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    print("socket connected")
    socketio.emit('my_response', "connected")

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe("rfid")
    mqtt.subscribe("threephase")
    mqtt.subscribe("fencing")
    print('Connected MQTT Broker')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    if(message.topic=="rfid"):
        socketio.emit('rfid',data=data, namespace='/test')
    if (message.topic == "fencing"):
        socketio.emit('fencing', data=data, namespace='/test')
    if (message.topic == "threephase"):
        socketio.emit('threephase', data=data, namespace='/test')

@socketio.on('rfid', namespace='/test')
def rfid(message):
    print("in rfid")
    mqtt.publish("rfiddata",message)

@socketio.on('fencing', namespace='/test')
def fencing(message):
    mqtt.publish("fencingbutton",message)

@socketio.on('threephase', namespace='/test')
def threePhase(message):
    mqtt.publish("threephasebutton",message)


if __name__ == '__main__':
    socketio.run(app, debug=True, use_reloader=False)