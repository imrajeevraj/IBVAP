import json
import logging
import threading
from typing import Dict, Any
import paho.mqtt.client as mqtt
import httpx
from backend.app.core.config import settings

logger = logging.getLogger("AlertDispatch")

class AlertDispatchService:
    def __init__(self):
        self.mqtt_client = None
        self.mqtt_connected = False
        if settings.MQTT_ENABLED:
            self._init_mqtt()

    def _init_mqtt(self):
        try:
            # We use MQTTv311 to avoid compatibility issues with older brokers, 
            # though v5 is newer. paho-mqtt 1.x or 2.x supports it.
            # In paho-mqtt 2.x, CallbackAPIVersion is needed, but we'll try standard init first.
            try:
                from paho.mqtt.enums import CallbackAPIVersion
                self.mqtt_client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id="ibvap_dispatcher")
            except ImportError:
                self.mqtt_client = mqtt.Client(client_id="ibvap_dispatcher")
                
            if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
                self.mqtt_client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
                
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            
            # Run the MQTT loop in a background thread to prevent blocking
            self.mqtt_client.connect_async(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            logger.error(f"Failed to initialize MQTT client: {e}")

    def _on_mqtt_connect(self, client, userdata, flags, rc, *args):
        if rc == 0:
            self.mqtt_connected = True
            logger.info(f"Connected to MQTT broker at {settings.MQTT_BROKER_HOST}")
        else:
            logger.error(f"MQTT connection failed with code {rc}")

    def _on_mqtt_disconnect(self, client, userdata, rc, *args):
        self.mqtt_connected = False
        if rc != 0:
            logger.warning("Unexpected MQTT disconnection. Will auto-reconnect.")

    def dispatch_event(self, event_dict: Dict[str, Any]):
        """
        Evaluate and dispatch high-severity events to external systems.
        Should be called asynchronously or in a background thread.
        """
        severity = event_dict.get("severity", "LOW")
        if severity not in ["HIGH", "CRITICAL"]:
            return

        payload = self._format_payload(event_dict)

        # 1. Dispatch via MQTT
        if settings.MQTT_ENABLED and self.mqtt_client and self.mqtt_connected:
            try:
                topic = f"{settings.MQTT_TOPIC_PREFIX}/{severity.lower()}/{event_dict.get('event_type', 'unknown').lower()}"
                self.mqtt_client.publish(topic, json.dumps(payload), qos=1)
                logger.info(f"Dispatched event via MQTT to {topic}")
            except Exception as e:
                logger.error(f"MQTT dispatch failed: {e}")

        # 2. Dispatch via Telegram Webhook
        if settings.TELEGRAM_ENABLED and settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
            self._dispatch_telegram(payload, severity)

    def _format_payload(self, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "alert_id": event_dict.get("id"),
            "severity": event_dict.get("severity"),
            "type": event_dict.get("event_type"),
            "camera": event_dict.get("camera_id"),
            "timestamp": event_dict.get("timestamp"),
            "reasons": event_dict.get("risk_reasons", []),
            "score": event_dict.get("risk_score")
        }

    def _dispatch_telegram(self, payload: Dict[str, Any], severity: str):
        try:
            url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
            
            icon = "🚨" if severity == "CRITICAL" else "⚠️"
            reasons = ", ".join(payload.get("reasons", []))
            
            text = (
                f"{icon} **IBVAP ALERT: {severity}**\n"
                f"**Type:** {payload.get('type')}\n"
                f"**Camera:** {payload.get('camera')}\n"
                f"**Reasons:** {reasons}\n"
                f"**Time:** {payload.get('timestamp')}"
            )
            
            data = {
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "Markdown"
            }
            
            # Fire and forget (in a real prod app, use an async client or retry queue)
            threading.Thread(target=self._send_http, args=(url, data), daemon=True).start()
        except Exception as e:
            logger.error(f"Failed to prep Telegram dispatch: {e}")

    def _send_http(self, url: str, data: Dict[str, Any]):
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.post(url, json=data)
                response.raise_for_status()
            logger.info("Dispatched event via Telegram webhook")
        except Exception as e:
            logger.error(f"HTTP Webhook dispatch failed: {e}")

alert_dispatch = AlertDispatchService()
