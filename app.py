from flask import Flask, render_template, request, redirect, url_for, session, flash
from database.db import get_db, init_db, seed_db, create_user

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-in-production'

# Initialize database on startup
with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Extract form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Server-side validation
        if not name:
            flash("Please enter your name", "error")
            return render_template("register.html")

        if not email or "@" not in email:
            flash("Please enter a valid email address", "error")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters long", "error")
            return render_template("register.html")

        # Attempt to create user
        user_id = create_user(name, email, password)

        if user_id is None:
            flash("This email is already registered", "error")
            return render_template("register.html")

        # Success: log user in and redirect
        session["user_id"] = user_id
        session["user_name"] = name
        flash(f"Welcome to Spendly, {name}!", "success")
        return redirect(url_for("profile"))

    # GET request: show form
    return render_template("register.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    return "Logout — coming in Step 3"


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
