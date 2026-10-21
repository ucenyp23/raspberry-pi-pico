from gpiozero import PWMLED, Button
from flask import Flask, jsonify, render_template_string, request
from threading import Lock

led = PWMLED(17)
button_up = Button(27)
button_down = Button(22)

brightness = 50
brightness_lock = Lock()

app = Flask(__name__)

def increase_brightness():
    global brightness
    with brightness_lock:
        brightness = min(100, brightness + 5)
        led.value = brightness / 100

def decrease_brightness():
    global brightness
    with brightness_lock:
        brightness = max(0, brightness - 5)
        led.value = brightness / 100

button_up.when_pressed = increase_brightness
button_down.when_pressed = decrease_brightness

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>PWM LED Brightness Control</title>
    <style>
        body { 
            font-family: Arial; 
            text-align: center; 
            padding: 50px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            max-width: 400px;
            margin: 0 auto;
        }
        h1 { color: #333; margin: 0 0 30px 0; }
        .brightness-display {
            font-size: 60px;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0;
        }
        .led-preview {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background-color: rgb(255, 200, 0);
            margin: 20px auto;
            box-shadow: 0 0 30px rgba(255, 200, 0, 0.5);
            transition: all 0.1s;
        }
        input[type="range"] {
            width: 100%;
            height: 8px;
            margin: 20px 0;
            cursor: pointer;
        }
        .buttons {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        button {
            flex: 1;
            padding: 15px;
            font-size: 18px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.2s;
        }
        .btn-down {
            background-color: #ff6b6b;
            color: white;
        }
        .btn-down:hover { background-color: #ee5a52; transform: scale(1.05); }
        
        .btn-up {
            background-color: #51cf66;
            color: white;
        }
        .btn-up:hover { background-color: #40c057; transform: scale(1.05); }
        
        .info {
            margin-top: 20px;
            font-size: 12px;
            color: #666;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💡 LED Brightness</h1>
        
        <div class="led-preview" id="ledPreview"></div>
        
        <div class="brightness-display">
            <span id="brightnessValue">50</span>%
        </div>
        
        <input type="range" id="slider" min="0" max="100" value="50">
        
        <div class="buttons">
            <button class="btn-down" onclick="decreaseBrightness()">➖ -5%</button>
            <button class="btn-up" onclick="increaseBrightness()">➕ +5%</button>
        </div>
        
        <div class="info">
            <strong>Physical Buttons:</strong><br>
            GPIO 27: Increase brightness<br>
            GPIO 22: Decrease brightness
        </div>
    </div>

    <script>
        function updateDisplay() {
            fetch('/brightness')
                .then(r => r.json())
                .then(data => {
                    const value = data.brightness;
                    document.getElementById('brightnessValue').textContent = value;
                    document.getElementById('slider').value = value;
                    
                    // Update LED color preview
                    const led = document.getElementById('ledPreview');
                    const opacity = value / 100;
                    led.style.opacity = opacity;
                    led.style.boxShadow = `0 0 ${30 * opacity}px rgba(255, 200, 0, ${opacity})`;
                });
        }

        function setBrightness(value) {
            fetch(`/set?value=${value}`);
            updateDisplay();
        }

        function increaseBrightness() {
            fetch('/increase');
            updateDisplay();
        }

        function decreaseBrightness() {
            fetch('/decrease');
            updateDisplay();
        }

        document.getElementById('slider').addEventListener('input', (e) => {
            setBrightness(e.target.value);
        });

        updateDisplay();
        setInterval(updateDisplay, 200);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/brightness')
def get_brightness():
    with brightness_lock:
        return jsonify({'brightness': brightness})

@app.route('/set')
def set_brightness():
    global brightness
    value = int(request.args.get('value', 50))
    with brightness_lock:
        brightness = max(0, min(100, value))
        led.value = brightness / 100
    return jsonify({'brightness': brightness})

@app.route('/increase')
def increase():
    increase_brightness()
    return jsonify({'brightness': brightness})

@app.route('/decrease')
def decrease():
    decrease_brightness()
    return jsonify({'brightness': brightness})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)