# flask_app.py
from flask import Flask
from sre_metrics import instrument_flask

app = Flask(__name__)

# hard-coded metrics port
instrument_flask(
    app,
    metrics_port=9099,
    prefix="myapp_",
    group_status_codes=False
)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    # hard-coded app port
    app.run(host="0.0.0.0", port=8001)
