import network
import time
import socket
from umqtt.simple import MQTTClient


class WifiState:
    CONNECTED = "connected"
    CONNECTING = "connecting"
    IDLE = "idle"


class MqttState:
    CONNECTED = "connected"
    CONNECTING = "connecting"
    IDLE = "idle"


class WifiManager:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.last_attempt = 0
        self.connect_interval = 5
        self.state = WifiState.IDLE  # idle, connecting, connected

        self.wlan = network.WLAN(network.STA_IF)  # Instance variable
        self.wlan.active(True)

    def check(self):
        now = time.time()

        if self.wlan.isconnected():

            if self.state != WifiState.CONNECTED:
                print("WiFiManager: Fully online:", self.wlan.ifconfig())
                self.state = WifiState.CONNECTED

        # Wifi not connected -> reconnect every 5 seconds
        elif now - self.last_attempt > self.connect_interval:
            print("WiFiManager: Connecting...")
            self.wlan.connect(self.ssid, self.password)
            self.last_attempt = now
            self.state = WifiState.CONNECTING

        return self.state


class MqttManager:
    def __init__(
        self,
        wifi_manager,
        config,
        on_message,
        subscribe_topics,
        available_topic,
        active_alarms_topic=None,
    ):
        self.config = config
        self.on_message = on_message
        self.wifi = wifi_manager

        self.subscribe_topics = subscribe_topics
        self.available_topic = available_topic
        self.active_alarms_topic = active_alarms_topic

        self.client = None
        self.last_attempt = 0
        self.state = MqttState.IDLE  # idle, resolving, connecting, connected

    def _cleanup_client(self):
        """Save cleanup of current MQTT client"""
        if self.client is not None:
            try:
                self.client.disconnect()
            except Exception as e:
                print("MqttManager: Cleanup error:", e)
            finally:
                self.client = None

    def check(self):
        now = time.time()
        # ------
        # Wifi check
        # ------
        # If wifi is not connected, mqtt cannot connect
        if (
            self.wifi.state != WifiState.CONNECTED
        ):  # Don't use isconnected(), otherwise MqttManager might realize it before WifiManager
            self._cleanup_client()
            self.state = MqttState.IDLE

        # If already connected, just check_msg()
        elif self.state == MqttState.CONNECTED and self.client:
            try:
                self.client.check_msg()  # non blocking
            except:
                print("MqttManager: Connection lost")
                self._cleanup_client()
                self.state = MqttState.CONNECTING

        # If not connected, retry every 5 seconds
        elif time.time() - self.last_attempt < 5:
            pass

        else:
            self.last_attempt = now

            self._cleanup_client()
            self.state = MqttState.CONNECTING

            # -----
            # DNS check
            # -----
            try:
                print("MqttManager: Resolving DNS...")
                addr = socket.getaddrinfo(
                    self.config["mqtt_server"], int(self.config["mqtt_port"])
                )
                print("MqttManager: DNS:", addr)
            except:
                print("MqttManager: DNS failed")
                return self.state

            # -----
            # MQTT check
            # -----
            try:
                if self.client is None:
                    self.client = MQTTClient(
                        "pico_alarm_clock",
                        self.config["mqtt_server"],
                        port=int(self.config["mqtt_port"]),
                        user=self.config["mqtt_user"],
                        password=self.config["mqtt_password"],
                        keepalive=90,
                    )
                    self.client.set_callback(self.on_message)
                    self.client.set_last_will(
                        self.available_topic, b"false", retain=False
                    )

                print("MqttManager: Connecting...")
                self.client.connect()

                # Subscribe to all topics
                for t in self.subscribe_topics:
                    self.client.subscribe(t)

                self.client.publish(self.available_topic, b"true", retain=True)

                print("MqttManager: Connected")
                self.state = MqttState.CONNECTED

            except Exception as e:
                print("MqttManager: Error:", e)
                self._cleanup_client()
                self.state = MqttState.CONNECTING

        return self.state
