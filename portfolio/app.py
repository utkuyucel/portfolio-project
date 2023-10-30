from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/stock_performance_analyzer")
def spa():
    return render_template("spa.html")


if __name__ == "__main__":
    app.run(debug=True)
