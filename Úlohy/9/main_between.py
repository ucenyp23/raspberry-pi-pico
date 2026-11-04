from flask import Flask, jsonify, request
import serial
import threading
import time

app = Flask(__name__)

# Single UART connection (bidirectional)
uart = None

try:
    uart = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1)
    print("✓ UART0 connected on /dev/ttyAMA0")
except Exception as e:
    print(f"✗ Error opening UART: {e}")
    uart = None

# State tracking
state_data = {
    'button_state': None,
    'led_state': False,
    'last_update': None,
    'source': 'uart'
}

state_lock = threading.Lock()

def send_to_picos(value):
    """Send LED command to In Pico"""
    if uart:
        try:
            message = f"{value}\n"
            uart.write(message.encode())
            print(f"→ UART TX: {value}")
        except Exception as e:
            print(f"✗ UART write error: {e}")

def uart_reader():
    """Read button state from Out Pico and relay to In Pico"""
    print("▶ UART reader thread started")
    while True:
        try:
            if uart:
                if uart.in_waiting:
                    line = uart.readline().decode().strip()
                    
                    if line in ['0', '1']:
                        with state_lock:
                            state_data['button_state'] = line
                            state_data['led_state'] = (line == '0')
                            state_data['last_update'] = time.time()
                            state_data['source'] = 'uart'
                        
                        print(f"← UART RX from Out Pico: {line}")
                        
                        # Relay to In Pico
                        send_to_picos(line)
            
            time.sleep(0.05)
        except Exception as e:
            print(f"✗ UART reader error: {e}")
            time.sleep(1)

# Start UART reader thread
uart_thread = threading.Thread(target=uart_reader, daemon=True)
uart_thread.start()

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pico Button → LED Control</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                padding: 40px;
                border-radius: 15px;
                max-width: 500px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            
            h1 {
                color: #333;
                margin-bottom: 30px;
                text-align: center;
            }
            
            .section {
                margin: 25px 0;
                padding: 20px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                background: #f9f9f9;
            }
            
            .section-title {
                font-weight: bold;
                color: #667eea;
                font-size: 12px;
                text-transform: uppercase;
                margin-bottom: 15px;
                letter-spacing: 1px;
            }
            
            .led { 
                width: 120px; 
                height: 120px; 
                border-radius: 50%; 
                margin: 20px auto; 
                transition: all 0.3s ease;
                border: 4px solid #333;
                cursor: default;
            }
            
            .led.on { 
                background: #ff4444; 
                box-shadow: 0 0 40px rgba(255, 68, 68, 0.8), 
                           inset 0 0 20px rgba(255,0,0,0.5);
            }
            
            .led.off { 
                background: #cccccc; 
                box-shadow: inset 0 0 10px rgba(0,0,0,0.2);
            }
            
            .button-state {
                font-size: 16px;
                color: #333;
                margin: 15px 0;
                padding: 12px;
                background: #f5f5f5;
                border-radius: 5px;
                text-align: center;
                border: 1px solid #ddd;
            }
            
            .button-state.pressed {
                background: #ffe0e0;
                color: #d32f2f;
                font-weight: bold;
                border-color: #d32f2f;
            }
            
            .button-state.released {
                background: #e0f5e0;
                color: #388e3c;
                font-weight: bold;
                border-color: #388e3c;
            }
            
            .status-info {
                font-size: 13px;
                color: #666;
                margin-top: 10px;
                padding-top: 10px;
                border-top: 1px solid #e0e0e0;
            }
            
            .status-info div {
                margin: 8px 0;
            }
            
            .status-label {
                font-weight: bold;
                color: #667eea;
            }
            
            .web-control {
                display: flex;
                gap: 10px;
                justify-content: center;
                margin-top: 15px;
            }
            
            .web-control button {
                background: #667eea;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                font-weight: bold;
                transition: all 0.3s;
                flex: 1;
            }
            
            .web-control button:hover {
                background: #764ba2;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            .web-control button:active {
                transform: translateY(0);
            }
            
            .timestamp {
                color: #999;
            }
        </style>
        <script>
            async function updateStatus() {
                try {
                    const response = await fetch('/status');
                    const data = await response.json();
                    
                    // Update LED visual
                    const led = document.getElementById('led');
                    if (data.led_state) {
                        led.classList.add('on');
                        led.classList.remove('off');
                    } else {
                        led.classList.add('off');
                        led.classList.remove('on');
                    }
                    
                    // Update button state text
                    const buttonState = document.getElementById('button-state');
                    if (data.button_state === '0') {
                        buttonState.textContent = '🔘 BUTTON: PRESSED';
                        buttonState.classList.remove('released');
                        buttonState.classList.add('pressed');
                    } else if (data.button_state === '1') {
                        buttonState.textContent = '⭕ BUTTON: RELEASED';
                        buttonState.classList.remove('pressed');
                        buttonState.classList.add('released');
                    } else {
                        buttonState.textContent = '❓ BUTTON: WAITING...';
                        buttonState.classList.remove('pressed', 'released');
                    }
                    
                    // Update timestamp
                    if (data.last_update) {
                        const lastUpdate = new Date(data.last_update * 1000);
                        document.getElementById('timestamp').textContent = 
                            lastUpdate.toLocaleTimeString();
                    }
                    
                    // Update source
                    document.getElementById('source').textContent = 
                        data.source.toUpperCase();
                } catch (e) {
                    console.error('Status update error:', e);
                }
            }
            
            async function controlLED(state) {
                try {
                    const response = await fetch(`/control?led=${state}`);
                    const data = await response.json();
                    if (data.status === 'ok') {
                        console.log(`LED control sent: ${state}`);
                        updateStatus();
                    }
                } catch (e) {
                    console.error('Control error:', e);
                }
            }
            
            // Update status every 200ms
            setInterval(updateStatus, 200);
            updateStatus();
        </script>
    </head>
    <body>
        <div class="container">
            <h1>🔴 Button → LED Control System</h1>
            
            <div class="section">
                <div class="section-title">LED Status</div>
                <div id="led" class="led off"></div>
                <div id="button-state" class="button-state">❓ BUTTON: WAITING...</div>
            </div>
            
            <div class="section">
                <div class="section-title">Web Control</div>
                <div class="web-control">
                    <button onclick="controlLED(0)">🔴 LED ON</button>
                    <button onclick="controlLED(1)">⚫ LED OFF</button>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">System Status</div>
                <div class="status-info">
                    <div><span class="status-label">Last Update:</span> <span class="timestamp" id="timestamp">—</span></div>
                    <div><span class="status-label">Source:</span> <span id="source">—</span></div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/status')
def status():
    with state_lock:
        return jsonify({
            'button_state': state_data['button_state'],
            'led_state': state_data['led_state'],
            'last_update': state_data['last_update'],
            'source': state_data['source']
        })

@app.route('/control')
def control():
    """Web-based LED control"""
    led_value = request.args.get('led', type=int)
    if led_value in [0, 1]:
        with state_lock:
            state_data['led_state'] = (led_value == 0)
            state_data['last_update'] = time.time()
            state_data['source'] = 'web'
        
        # Send to In Pico
        send_to_picos(led_value)
        print(f"▶ WEB: LED control set to {led_value}")
        return jsonify({'status': 'ok', 'value': led_value})
    
    return jsonify({'status': 'error', 'message': 'Invalid value'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)