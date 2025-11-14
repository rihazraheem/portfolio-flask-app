from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os


# --- Flask Setup ---
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_key')

# --- Admin Credentials ---
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "password123")

# --- Database Config ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Model for storing contact messages ---
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message {self.id} - {self.name}>'

# --- Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<page>')
def pages(page):
    return render_template(f'{page}.html')

@app.route('/send', methods=['POST'])
def send_message():
    name = request.form['name']
    email = request.form['email']
    message_text = request.form['message']

    new_msg = Message(name=name, email=email, message=message_text)
    db.session.add(new_msg)
    db.session.commit()

    flash('✅ Your message has been saved successfully!')
    return redirect(url_for('pages', page='contact'))

# ----------------------------
#        ADMIN LOGIN
# ----------------------------

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USER and password == ADMIN_PASS:
            session['admin'] = True
            return redirect('/admin/messages')
        else:
            flash("❌ Invalid admin credentials")

    return render_template("admin_login.html")


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin/login')


# ----------------------------
#       ADMIN: VIEW MESSAGES
# ----------------------------

@app.route('/admin/messages')
def view_messages():
    if not session.get('admin'):
        return redirect('/admin/login')

    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return render_template('messages.html', messages=messages)

if __name__ == '__main__':
    # Create database if it doesn’t exist
    if not os.path.exists('messages.db'):
        with app.app_context():
            db.create_all()
            print('📦 Database created: messages.db')

    app.run(debug=True)
