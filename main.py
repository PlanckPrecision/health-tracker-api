from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app.validate import check_weight, check_date
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__, template_folder="app/templates")
app.config["SECRET_KEY"] = "your-secret-key"  # Replace with a real secret key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Entry(db.Model):
    __tablename__ = "entries"

    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(10), nullable=False) # Storing date as string in DD.MM.YYYY format


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    today = datetime.now().strftime("%d.%m.%Y")
    return render_template("index.html", today=today)


@app.route("/register", methods=["POST"])
def register():
    weight_raw = request.form.get("weight", "").strip()
    date_raw = request.form.get("date", "").strip()

    # Default to today if empty
    if not date_raw:
        date_raw = datetime.now().strftime("%d.%m.%Y")
    else:
        try:
            datetime.strptime(date_raw, "%d.%m.%Y")  # Validate format
        except ValueError:
            today = datetime.now().strftime("%d.%m.%Y")
            return render_template("index.html", message="Invalid date format. Use DD.MM.YYYY", today=today)

    is_valid, result = check_weight(weight_raw)

    if not is_valid:
        today = datetime.now().strftime("%d.%m.%Y")
        return render_template("index.html", message=result, today=today)

    # NOTE: Using SQLAlchemy ORM automatically parameterizes queries,
    # protecting against SQL injection (no raw SQL used)    
    entry = Entry(weight=result, date=date_raw)
    db.session.add(entry)
    db.session.commit()

    return render_template("greet.html", weight=result, date=date_raw)

@app.route("/history")
def history():
    entries = Entry.query.order_by(Entry.id).all()
    return render_template("history.html", entries=entries)


if __name__ == "__main__":
    app.run(debug=True)

