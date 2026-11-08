import network
import socket
import time
import ujson

CONFIG_FILE = "config.json"


def load_config():
    # Load configuration file if it exists
    try:
        with open(CONFIG_FILE) as f:
            return ujson.load(f)
    except:
        return None


def save_config(data):
    # Save configuration dictionary to file
    with open(CONFIG_FILE, "w") as f:
        ujson.dump(data, f)


def start_access_point():
    # Start Wifi access point for setup mode
    sta = network.WLAN(network.STA_IF)
    sta.active(False)
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    time.sleep(1)

    ap.config(essid="WMATConfig", password="wmat1234")

    # Android requires a valid DNS server; otherwise it will not obtain an IP
    ap.ifconfig(
        (
            "192.168.4.1",  # IP address
            "255.255.255.0",  # Subnet mask
            "192.168.4.1",  # Gateway
            "192.168.4.1",  # DNS server (important for Android)
        )
    )

    print("Wifi setup: AP active:", ap.ifconfig())
    return ap


def start_webserver():
    # HTML form for Wifi + MQTT configuration
    html = """\
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pico Setup</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h2 {
                color: #333;
                text-align: center;
            }
            .form-group {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .form-group h3 {
                margin-top: 0;
                color: #444;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
            }
            label {
                display: block;
                margin: 10px 0 5px;
                font-weight: bold;
            }
            .input-container {
                position: relative;
                margin-bottom: 15px;
            }
            input[type="text"],
            input[type="password"] {
                width: 100%;
                padding: 8px;
                padding-right: 60px; /* Space for the toggle button */
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }
            .password-toggle {
                position: absolute;
                right: 8px;
                top: 50%;
                transform: translateY(-50%);
                background: none;
                border: none;
                cursor: pointer;
                color: #666;
                font-size: 12px;
                padding: 0 8px;
                height: 100%;
            }
            button[type="submit"] {
                background-color: #4CAF50;
                color: white;
                padding: 10px 15px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                width: 100%;
            }
            button[type="submit"]:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <h2>Weck Mich Am Tag</h2>
        <form action="/" method="post">
        <div class="form-group">
            <h3>WiFi</h3>
            <label for="wifi_ssid">SSID:</label>
            <input type="text" id="wifi_ssid" name="wifi_ssid" required>

            <label for="wifi_password">Password:</label>
            <div class="input-container">
                <input type="password" id="wifi_password" name="wifi_password">
                <button type="button" class="password-toggle" onclick="
                    var p=document.getElementById('wifi_password');
                    p.type = (p.type === 'password') ? 'text' : 'password';
                    this.textContent = (p.type === 'password') ? 'Show' : 'Hide';
                ">Show</button>
            </div>
        </div>

        <div class="form-group">
            <h3>MQTT</h3>
            <label for="mqtt_server">Server:</label>
            <input type="text" id="mqtt_server" name="mqtt_server" required>

            <label for="mqtt_port">Port:</label>
            <input type="text" id="mqtt_port" name="mqtt_port" value="1883">

            <label for="mqtt_user">User:</label>
            <input type="text" id="mqtt_user" name="mqtt_user">

            <label for="mqtt_password">Password:</label>
            <div class="input-container">
                <input type="password" id="mqtt_password" name="mqtt_password">
                <button type="button" class="password-toggle" onclick="
                    var p=document.getElementById('mqtt_password');
                    p.type = (p.type === 'password') ? 'text' : 'password';
                    this.textContent = (p.type === 'password') ? 'Show' : 'Hide';
                ">Show</button>
            </div>

            <label for="topic_prefix">Topic-Prefix:</label>
            <input type="text" id="topic_prefix" name="topic_prefix" value="wmat">
        </div>

        <div class="form-group">
            <h3>Time</h3>
            <label for="tz_offset_winter">Winter TZ Offset (hours):</label>
            <input type="text" id="tz_offset_winter" name="tz_offset_winter" value="1">

            <label for="ntp_server">NTP Server:</label>
            <input type="text" id="ntp_server" name="ntp_server" value="pool.ntp.org">
        </div>

        <button type="submit">Save and Restart</button>
    </form>
</body>
</html>
"""

    # Start a simple HTTP server on port 80
    s = socket.socket()
    s.bind(("0.0.0.0", 80))
    s.listen(1)
    print("Wifi setup: Webserver running on port 80")

    while True:
        conn, addr = s.accept()
        req = conn.recv(2048).decode()

        # Handle POST request (form submission)
        if "POST" in req:
            try:
                body = req.split("\r\n\r\n")[1]
                params = {}
                for pair in body.split("&"):
                    k, v = pair.split("=")
                    params[k] = v

                # Save configuration and reboot
                save_config(params)
                conn.send("HTTP/1.1 200 OK\r\n\r\nSaved. Restarting...")
                conn.close()
                time.sleep(2)
                import machine

                machine.reset()
            except:
                pass

        # Send HTML form
        conn.send(html)
        conn.close()
