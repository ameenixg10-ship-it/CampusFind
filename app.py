from flask import Flask, render_template, request, redirect, url_for, flash, abort
import sqlite3
from pathlib import Path
from datetime import date

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-deployment"
DATABASE = Path(__file__).with_name("campusfind.db")


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                item_type TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                location TEXT NOT NULL,
                incident_date TEXT,
                contact_name TEXT NOT NULL,
                contact_email TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'OPEN',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                claimant_name TEXT NOT NULL,
                claimant_email TEXT NOT NULL,
                details TEXT,
                status TEXT NOT NULL DEFAULT 'PENDING',
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        """)


@app.route("/")
def home():
    query = request.args.get("q", "").strip()
    with get_db() as db:
        if query:
            search = f"%{query}%"
            items = db.execute("""
                SELECT * FROM items
                WHERE title LIKE ? OR category LIKE ? OR location LIKE ?
                ORDER BY id DESC
            """, (search, search, search)).fetchall()
        else:
            items = db.execute("SELECT * FROM items ORDER BY id DESC").fetchall()
        open_count = db.execute(
            "SELECT COUNT(*) FROM items WHERE status = 'OPEN'"
        ).fetchone()[0]
    return render_template("index.html", items=items, query=query, open_count=open_count)


@app.route("/report/<item_type>", methods=["GET", "POST"])
def report(item_type):
    item_type = item_type.upper()
    if item_type not in ("LOST", "FOUND"):
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        incident_date = request.form.get("incident_date", "")
        contact_name = request.form.get("contact_name", "").strip()
        contact_email = request.form.get("contact_email", "").strip()

        if not all([title, category, location, contact_name, contact_email]):
            flash("Please complete all required fields.", "error")
            return render_template("report.html", item_type=item_type)

        with get_db() as db:
            db.execute("""
                INSERT INTO items
                (title, item_type, category, description, location, incident_date,
                 contact_name, contact_email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, item_type, category, description, location, incident_date,
                  contact_name, contact_email))
        flash("Your report has been posted.", "success")
        return redirect(url_for("home"))

    return render_template("report.html", item_type=item_type)


@app.route("/item/<int:item_id>")
def item_detail(item_id):
    with get_db() as db:
        item = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if item is None:
        abort(404)
    return render_template("detail.html", item=item)


@app.route("/item/<int:item_id>/claim", methods=["POST"])
def submit_claim(item_id):
    name = request.form.get("claimant_name", "").strip()
    email = request.form.get("claimant_email", "").strip()
    details = request.form.get("details", "").strip()

    with get_db() as db:
        item = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        if item is None:
            abort(404)
        if item["status"] != "OPEN":
            flash("This item is no longer open for claims.", "error")
        elif not name or not email:
            flash("Please enter your name and email.", "error")
        else:
            db.execute("""
                INSERT INTO claims (item_id, claimant_name, claimant_email, details)
                VALUES (?, ?, ?, ?)
            """, (item_id, name, email, details))
            flash("Your claim was submitted for admin review.", "success")
    return redirect(url_for("item_detail", item_id=item_id))


@app.route("/admin")
def admin():
    with get_db() as db:
        items = db.execute("SELECT * FROM items ORDER BY id DESC").fetchall()
        claims = db.execute("""
            SELECT claims.*, items.title AS item_title
            FROM claims JOIN items ON claims.item_id = items.id
            ORDER BY claims.id DESC
        """).fetchall()
    return render_template("admin.html", items=items, claims=claims)


@app.route("/admin/claim/<int:claim_id>/<decision>", methods=["POST"])
def update_claim(claim_id, decision):
    if decision not in ("APPROVED", "REJECTED"):
        abort(400)
    with get_db() as db:
        claim = db.execute("SELECT * FROM claims WHERE id = ?", (claim_id,)).fetchone()
        if claim is None:
            abort(404)
        db.execute("UPDATE claims SET status = ? WHERE id = ?", (decision, claim_id))
        if decision == "APPROVED":
            db.execute("UPDATE items SET status = 'CLAIMED' WHERE id = ?", (claim["item_id"],))
    flash("Claim status updated.", "success")
    return redirect(url_for("admin"))


@app.route("/admin/item/<int:item_id>/resolve", methods=["POST"])
def resolve_item(item_id):
    with get_db() as db:
        db.execute("UPDATE items SET status = 'RESOLVED' WHERE id = ?", (item_id,))
    flash("Item marked as resolved.", "success")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
