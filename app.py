from flask import Flask, render_template, request, redirect, session, Response
from database import get_db
import csv
import io
from database import init_db, DB_NAME
import os

if not os.path.exists(DB_NAME):
    print("Base absente → création…")
    init_db()



app = Flask(__name__)
app.secret_key = "super_secret_key_à_changer"

# --- PROTECTION DES ROUTES ---
def login_required(f):
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect("/login")
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# --- PAGE D'ACCUEIL ---
@app.route("/")
def home():
    return render_template("index.html")

# --- LOGIN ---
@app.route("/login", methods=["GET"])
def login_form():
    return render_template("login.html", error=None)

@app.route("/login", methods=["POST"])
def login_submit():
    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "1234":
        session["logged_in"] = True
        return redirect("/commandes")
    else:
        return render_template("login.html", error="Identifiants incorrects")

# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# --- FORMULAIRE COMMANDE ---
@app.route("/commande", methods=["GET"])
@login_required
def commande_form():
    return render_template("commande.html")

@app.route("/commande", methods=["POST"])
@login_required
def commande_submit():
    nom = request.form["nom"]
    produit = request.form["produit"]
    quantite = request.form["quantite"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO commandes (nom, produit, quantite) VALUES (?, ?, ?)",
        (nom, produit, quantite)
    )

    conn.commit()
    conn.close()

    return redirect("/commandes")

# --- LISTE DES COMMANDES ---
@app.route("/commandes")
@login_required
def commandes_list():
    search = request.args.get("search", "")
    produit_filter = request.args.get("produit", "")

    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM commandes WHERE 1=1"
    params = []

    if search:
        query += " AND nom LIKE ?"
        params.append(f"%{search}%")

    if produit_filter:
        query += " AND produit = ?"
        params.append(produit_filter)

    cursor.execute(query, params)
    commandes = cursor.fetchall()

    conn.close()

    return render_template("commandes.html", commandes=commandes, search=search, produit_filter=produit_filter)

# --- EXPORT CSV ---
@app.route("/commandes/export")
@login_required
def commandes_export():
    search = request.args.get("search", "")
    produit_filter = request.args.get("produit", "")

    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM commandes WHERE 1=1"
    params = []

    if search:
        query += " AND nom LIKE ?"
        params.append(f"%{search}%")

    if produit_filter:
        query += " AND produit = ?"
        params.append(produit_filter)

    cursor.execute(query, params)
    commandes = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["ID", "Nom", "Produit", "Quantité"])

    for c in commandes:
        writer.writerow([c["id"], c["nom"], c["produit"], c["quantite"]])

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=commandes.csv"

    return response

# --- DÉTAIL ---
@app.route("/commande/<int:id>")
@login_required
def commande_detail(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM commandes WHERE id = ?", (id,))
    commande = cursor.fetchone()

    conn.close()

    if commande is None:
        return "Commande introuvable", 404

    return render_template("commande_detail.html", commande=commande)

# --- EDIT ---
@app.route("/commande/<int:id>/edit", methods=["GET"])
@login_required
def commande_edit_form(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM commandes WHERE id = ?", (id,))
    commande = cursor.fetchone()

    conn.close()

    if commande is None:
        return "Commande introuvable", 404

    return render_template("commande_edit.html", commande=commande)

@app.route("/commande/<int:id>/edit", methods=["POST"])
@login_required
def commande_edit_submit(id):
    nom = request.form["nom"]
    produit = request.form["produit"]
    quantite = request.form["quantite"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE commandes SET nom = ?, produit = ?, quantite = ? WHERE id = ?",
        (nom, produit, quantite, id)
    )

    conn.commit()
    conn.close()

    return redirect("/commandes")

# --- DELETE ---
@app.route("/commande/<int:id>/delete", methods=["GET"])
@login_required
def commande_delete_confirm(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM commandes WHERE id = ?", (id,))
    commande = cursor.fetchone()

    conn.close()

    if commande is None:
        return "Commande introuvable", 404

    return render_template("commande_delete.html", commande=commande)

@app.route("/commande/<int:id>/delete", methods=["POST"])
@login_required
def commande_delete(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM commandes WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect("/commandes")

if __name__ == "__main__":
    app.run(debug=True)
