from flask import Flask, render_template, request, redirect, url_for
from src.environment import Home
from src.main import main
import threading

app = Flask(__name__)

global siren_on


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/trigger_lights_goal', methods=['POST'])
def trigger_lights_goal():
    home = Home()
    home.trigger_lights_goal()
    return redirect(url_for("index"))


if __name__ == '__main__':
    threading.Thread(target=main, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=8080)
