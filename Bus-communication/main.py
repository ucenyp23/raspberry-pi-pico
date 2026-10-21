from flask import Flask, render_template, jsonify
import serial
import threading
import time
from gpiozero import LED

app = Flask(__name__)

# LED na GPIO 17
red_led = LED(17)

# Práh – když ADC > práh, LED se zapne
ADC_THRESHOLD = 2048  # Upravit podle potřeby

# Globální stav
state_data = {
    'adc_value': 0,
    'led_state': False,
    'last_update': None
}

# Zámek pro thread-safe přístup
state_lock = threading.Lock()

def uart_reader():
    """Čti UART v pozadí"""
    ser = serial.Serial('/dev/ttyAMA0', baudrate=115200, timeout=1)
    print("UART čtecí vlákno spuštěno...")
    
    try:
        while True:
            if ser.in_waiting:
                line = ser.readline().decode().strip()
                
                if line:
                    try:
                        adc_value = int(line)
                        
                        with state_lock:
                            state_data['adc_value'] = adc_value
                            state_data['last_update'] = time.time()
                        
                        print(f"UART ADC: {adc_value}")
                        
                        # Ovládej LED podle prahu
                        if adc_value > ADC_THRESHOLD:
                            red_led.on()
                            with state_lock:
                                state_data['led_state'] = True
                        else:
                            red_led.off()
                            with state_lock:
                                state_data['led_state'] = False
                    
                    except ValueError:
                        print(f"Chyba: nelze parsovat '{line}'")
            
            time.sleep(0.05)
    
    except Exception as e:
        print(f"Chyba UART: {e}")
    finally:
        ser.close()

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
        <title>UART ADC LED Ovladač</title>
        <style>
            body { 
                font-family: Arial; 
                text-align: center; 
                margin-top: 50px;
                background: #f0f0f0;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                max-width: 500px;
                margin: 0 auto;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .led { 
                width: 120px; 
                height: 120px; 
                border-radius: 50%; 
                margin: 30px auto; 
                transition: 0.3s;
                border: 3px solid #333;
            }
            .led.on { 
                background: #ff0000; 
                box-shadow: 0 0 30px red, inset 0 0 20px rgba(255,0,0,0.5);
            }
            .led.off { 
                background: #333; 
                box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
            }
            .adc-value {
                font-size: 28px;
                font-weight: bold;
                margin: 20px 0;
                color: #333;
            }
            .bar {
                width: 100%;
                height: 30px;
                background: #ddd;
                border-radius: 5px;
                margin: 20px 0;
                overflow: hidden;
                border: 2px solid #999;
            }
            .bar-fill {
                height: 100%;
                background: linear-gradient(90deg, #00ff00, #ffff00, #ff0000);
                transition: width 0.2s;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
            }
            .threshold {
                font-size: 14px;
                color: #666;
                margin-top: 10px;
            }
            .status {
                font-size: 18px;
                margin: 20px 0;
                color: #333;
            }
        </style>
        <script>
            async function updateStatus() {
                try {
                    const response = await fetch('/status');
                    const data = await response.json();
                    
                    // Zobraz ADC hodnotu
                    document.getElementById('adc-value').textContent = data.adc_value;
                    
                    // Naplň bar graf (0-4095)
                    const percentage = (data.adc_value / 4095) * 100;
                    const barFill = document.getElementById('bar-fill');
                    barFill.style.width = percentage + '%';
                    barFill.textContent = percentage.toFixed(0) + '%';
                    
                    // Ovládej LED barvu
                    const led = document.getElementById('led');
                    if (data.led_state) {
                        led.classList.add('on');
                        led.classList.remove('off');
                    } else {
                        led.classList.add('off');
                        led.classList.remove('on');
                    }
                    
                    // Poslední aktualizace
                    if (data.last_update) {
                        const lastUpdate = new Date(data.last_update * 1000);
                        document.getElementById('timestamp').textContent = 
                            lastUpdate.toLocaleTimeString();
                    }
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
            <h1>🔴 ADC → LED Ovladač</h1>
            
            <div id="led" class="led off"></div>
            
            <div class="status">
                ADC Hodnota: <span class="adc-value" id="adc-value">—</span>
            </div>
            
            <div class="bar">
                <div class="bar-fill" id="bar-fill">0%</div>
            </div>
            
            <div class="threshold">Práh: 2048 (LED se zapne když ADC &gt; 2048)</div>
            
            <div style="font-size: 12px; color: #999; margin-top: 20px;">
                Poslední aktualizace: <span id="timestamp">—</span>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/status')
def status():
    with state_lock:
        return jsonify({
            'adc_value': state_data['adc_value'],
            'led_state': state_data['led_state'],
            'last_update': state_data['last_update']
        })

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nUkončení...")
        red_led.off()