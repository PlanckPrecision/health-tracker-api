from flask import Flask, render_template, request
from app.validate import check_weight

app = Flask(__name__, template_folder='app/templates')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    weight_raw = request.form.get("weight")

    # Validate the weight input
    is_valid, result = check_weight(weight_raw)

    if not is_valid:
        return render_template("index.html", message=result)
    return render_template("greet.html", weight=result)

if __name__ == "__main__":
    app.run(debug=True)

