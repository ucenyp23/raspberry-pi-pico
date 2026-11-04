from flask import Flask, render_template, jsonify
import serial
import threading
import time
from gpiozero import LED

app = Flask(__name__)

# LED na GPIO 17
red_led = LED(17)

# Globální stav
state_data = {
    'button_state': None,  # '0' = pressed (LED ON), '1' = released (LED OFF)
    'led_state': False,
    'last_update': None,
    'source': 'uart'  # 'uart' nebo 'web'
}

# Zámek pro thread-safe přístup
state_lock = threading.Lock()

def uart_reader():
    """Čti UART v pozadí od Pica"""
    try:
        ser = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1)
        print("UART čtecí vlákno spuštěno...")
        
        while True:
            if ser.in_waiting:
                line = ser.readline().decode().strip()
                
                if line in ['0', '1']:
                    with state_lock:
                        state_data['button_state'] = line
                        state_data['last_update'] = time.time()
                        state_data['source'] = 'uart'
                    
                    print(f"UART přijato: {line} - tlačítko {'STISKNUTO' if line == '0' else 'UVOLNĚNO'}")
                    
                    # Ovládej LED podle hodnoty
                    # '0' = stisknuto = LED ON
                    # '1' = uvolněno = LED OFF
                    if line == '0':
                        red_led.on()
                        with state_lock:
                            state_data['led_state'] = True
                    else:
                        red_led.off()
                        with state_lock:
                            state_data['led_state'] = False
            
            time.sleep(0.05)
    
    except Exception as e:
        print(f"Chyba UART: {e}")
    finally:
        try:
            ser.close()
        except:
            pass

# Spusť čtecí vlákno
uart_thread = threading.Thread(target=uart_reader, daemon=True)
uart_thread.start()
time.sleep(1)  # Čekej na spuštění

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
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 15px;
                max-width: 500px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            h1 {
                color: #333;
                margin-bottom: 30px;
            }
            .section {
                margin: 30px 0;
                padding: 20px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
            }
            .section-title {
                font-weight: bold;
                color: #666;
                font-size: 14px;
                text-transform: uppercase;
                margin-bottom: 15px;
            }
            .led { 
                width: 120px; 
                height: 120px; 
                border-radius: 50%; 
                margin: 20px auto; 
                transition: all 0.3s;
                border: 4px solid #333;
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
                padding: 10px;
                background: #f5f5f5;
                border-radius: 5px;
            }
            .button-state.pressed {
                background: #ffe0e0;
                color: #d32f2f;
                font-weight: bold;
            }
            .button-state.released {
                background: #e0f5e0;
                color: #388e3c;
                font-weight: bold;
            }
            .web-control {
                display: flex;
                gap: 10px;
                justify-content: center;
            }
            button {
                padding: 12px 25px;
                font-size: 16px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: all 0.3s;
                font-weight: bold;
            }
            .btn-on {
                background-color: #4CAF50;
                color: white;
            }
            .btn-on:hover {
                background-color: #45a049;
                transform: scale(1.05);
            }
            .btn-off {
                background-color: #f44336;
                color: white;
            }
            .btn-off:hover {
                background-color: #da190b;
                transform: scale(1.05);
            }
            .status-info {
                font-size: 12px;
                color: #999;
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
            }
            .source-badge {
                display: inline-block;
                background: #e3f2fd;
                color: #1976d2;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 11px;
                font-weight: bold;
                margin-left: 10px;
            }
        </style>
        <script>
            async function updateStatus() {
                try {
                    const response = await fetch('/status');
                    const data = await response.json();
                    
                    // Update LED
                    const led = document.getElementById('led');
                    if (data.led_state) {
                        led.classList.add('on');
                        led.classList.remove('off');
                    } else {
                        led.classList.add('off');
                        led.classList.remove('on');
                    }
                    
                    // Update button state
                    const buttonState = document.getElementById('button-state');
                    if (data.button_state === '0') {
                        buttonState.textContent = '🔘 TLAČÍTKO: STISKNUTO';
                        buttonState.classList.remove('released');
                        buttonState.classList.add('pressed');
                    } else if (data.button_state === '1') {
                        buttonState.textContent = '⭕ TLAČÍTKO: UVOLNĚNO';
                        buttonState.classList.remove('pressed');
                        buttonState.classList.add('released');
                    } else {
                        buttonState.textContent = '❓ TLAČÍTKO: ČEKÁNÍ NA DATA';
                        buttonState.classList.remove('pressed', 'released');
                    }
                    
                    // Update timestamp
                    if (data.last_update) {
                        const lastUpdate = new Date(data.last_update * 1000);
                        document.getElementById('timestamp').textContent = 
                            lastUpdate.toLocaleTimeString('cs-CZ');
                    }
                    
                    // Update source
                    document.getElementById('source').textContent = 
                        data.source === 'uart' ? 'UART (Pico)' : 'Web Interface';
                } catch (e) {
                    console.error('Chyba:', e);
                }
            }
            
            async function sendCommand(state) {
                try {
                    await fetch(`/led?state=${state}`);
                    updateStatus();
                } catch (e) {
                    console.error('Chyba:', e);
                }
            }
            
            setInterval(updateStatus, 200);
            updateStatus();
        </script>
    </head>
    <body>
        <div class="container">
            <h1>🔴 Button → LED Control</h1>
            
            <!-- LED Display -->
            <div class="section">
                <div class="section-title">LED Status</div>
                <div id="led" class="led off"></div>
                <div id="button-state" class="button-state">❓ TLAČÍTKO: ČEKÁNÍ NA DATA</div>
            </div>
            
            <!-- UART Input -->
            <div class="section">
                <div class="section-title">Pico Button Input (UART)</div>
                <p style="font-size: 14px; color: #666; margin: 0;">
                    Pico tlačítko je připojeno a odesílá stav přes UART...
                </p>
            </div>
            
            <!-- Web Control -->
            <div class="section">
                <div class="section-title">Manual Web Control</div>
                <div class="web-control">
                    <button class="btn-on" onclick="sendCommand(1)">🟢 ON</button>
                    <button class="btn-off" onclick="sendCommand(0)">🔴 OFF</button>
                </div>
            </div>
            
            <!-- Status Info -->
            <div class="status-info">
                <div>Poslední aktualizace: <span id="timestamp">—</span></div>
                <div>Zdroj signálu: <span id="source">—</span></div>
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

@app.route('/led')
def control_led():
    """Web control endpoint"""
    try:
        state = request.args.get('state', '0')
        
        with state_lock:
            state_data['source'] = 'web'
            state_data['last_update'] = time.time()
        
        if state == '1':
            red_led.on()
            with state_lock:
                state_data['led_state'] = True
            print("Web: LED ON")
        else:
            red_led.off()
            with state_lock:
                state_data['led_state'] = False
            print("Web: LED OFF")
        
        return jsonify({'success': True, 'state': state})
    
    except Exception as e:
        print(f"Chyba ovládání: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nUkončení...")
        red_led.off()