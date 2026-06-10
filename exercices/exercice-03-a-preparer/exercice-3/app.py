import logging
import random
import time

from flask import Flask, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("demo")

app = Flask(__name__)


@app.get("/")
def index():
    delay_ms = random.randint(5, 80)
    time.sleep(delay_ms / 1000)

    logger.info("simulated request handled by Flask demo app")

    return jsonify(
        service="flask-demo",
        message="hello from OpenTelemetry Flask demo",
        simulated_delay_ms=delay_ms,
    )


@app.get("/health")
def health():
    return jsonify(status="ok")
