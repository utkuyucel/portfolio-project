from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/stock_performance_analyzer")
def spa():
    return render_template("spa.html")


@app.route("/volume_analyzer")
def volume_analyzer():
    return render_template("volume_analyzer.html")


@app.route("/exchange_clustering")
def exchange_clustering():
    return render_template("clustering.html")

@app.route("/betting_engine")
def betting_engine():
    return render_template("betting_engine.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(host = "0.0.0.0") 
