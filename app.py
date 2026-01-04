from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "queue_secret_key"

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("queue.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create tables
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    service_type TEXT,
    queue_date TEXT,
    queue_time TEXT
)
""")
conn.commit()
conn.close()

# ---------- LOGIN PAGE ----------
@app.route("/")
def login_page():
    return render_template("login.html")

# ---------- HOME ----------
@app.route("/home")
def home():
    if "admin" not in session:
        return redirect("/")
    return render_template("index.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        admin = conn.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if admin:
            session.clear()
            session["admin"] = username
            return redirect("/home")

    return render_template("login.html")

# ---------- SIGNUP ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        conn.execute(
            "INSERT INTO admin (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        conn.close()
        return redirect("/")

    return render_template("signup.html")

# ---------- ADD QUEUE ----------
@app.route("/add", methods=["GET", "POST"])
def add():
    if "admin" not in session:
        return redirect("/")

    if request.method == "POST":
        customer_name = request.form["customer_name"]
        service_type = request.form["service_type"]
        queue_date = request.form["queue_date"]
        queue_time = request.form["queue_time"]

        conn = get_db()
        conn.execute(
            "INSERT INTO queue VALUES (NULL, ?, ?, ?, ?)",
            (customer_name, service_type, queue_date, queue_time)
        )
        conn.commit()
        conn.close()
        return redirect("/view")

    return render_template("add.html")

# ---------- VIEW + SEARCH ----------
@app.route("/view")
def view():
    if "admin" not in session:
        return redirect("/")

    search = request.args.get("search")
    conn = get_db()

    if search:
        data = conn.execute(
            "SELECT * FROM queue WHERE customer_name LIKE ?",
            ('%' + search + '%',)
        ).fetchall()
    else:
        data = conn.execute("SELECT * FROM queue").fetchall()

    conn.close()
    return render_template("view.html", data=data)

# ---------- EDIT ----------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if "admin" not in session:
        return redirect("/")

    conn = get_db()

    if request.method == "POST":
        customer_name = request.form["customer_name"]
        service_type = request.form["service_type"]
        queue_date = request.form["queue_date"]
        queue_time = request.form["queue_time"]

        conn.execute("""
            UPDATE queue
            SET customer_name=?, service_type=?, queue_date=?, queue_time=?
            WHERE id=?
        """, (customer_name, service_type, queue_date, queue_time, id))

        conn.commit()
        conn.close()
        return redirect("/view")

    entry = conn.execute(
        "SELECT * FROM queue WHERE id=?",
        (id,)
    ).fetchone()
    conn.close()

    return render_template("edit.html", entry=entry)

# ---------- DELETE ----------
@app.route("/delete/<int:id>")
def delete(id):
    if "admin" not in session:
        return redirect("/")

    conn = get_db()
    conn.execute("DELETE FROM queue WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/view")

if __name__ == "__main__":
    app.run(debug=True)
