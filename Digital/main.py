from gpiozero import LED, Button
from flask import Flask, jsonify, render_template_string

button = Button(27)
led = LED(17)

app = Flask(__name__)

button.when_pressed = led.on
button.when_released = led.off

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>LED Controller</title>
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; }
        .status { font-size: 24px; margin: 20px; padding: 20px; border-radius: 10px; }
        .on { background-color: #90EE90; color: green; }
        .off { background-color: #FFB6C6; color: red; }
        button { padding: 10px 20px; font-size: 16px; margin: 10px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>LED Control Panel</h1>
    <div class="status" id="status">Loading...</div>
    <button onclick="toggleLED()">Toggle LED</button>
    <button onclick="turnOn()">Turn On</button>
    <button onclick="turnOff()">Turn Off</button>

    <script>
        function updateStatus() {
            fetch('/status')
                .then(r => r.json())
                .then(data => {
                    const status = document.getElementById('status');
                    status.textContent = data.state ? '🟢 LED ON' : '🔴 LED OFF';
                    status.className = 'status ' + (data.state ? 'on' : 'off');
                });
        }

        function toggleLED() { fetch('/toggle'); updateStatus(); }
        function turnOn() { fetch('/on'); updateStatus(); }
        function turnOff() { fetch('/off'); updateStatus(); }

        updateStatus();
        setInterval(updateStatus, 500);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/status')
def status():
    return jsonify({'state': led.is_lit})

@app.route('/toggle')
def toggle():
    led.toggle()
    return jsonify({'state': led.is_lit})

@app.route('/on')
def turn_on():
    led.on()
    return jsonify({'state': True})

@app.route('/off')
def turn_off():
    led.off()
    return jsonify({'state': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)