from flask import Flask, render_template, redirect, url_for, request, session, flash
from models import db, User, Idea
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ideas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/favicon.ico')
def favicon():
    return "", 204  # No Content

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('landing'))
        flash('Invalid credentials!')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/landing')
def landing():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('landing.html')

@app.route('/idea_generation', methods=['GET', 'POST'])
def idea_generation():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        tags = request.form['tags']
        idea = Idea(title=title, description=description, tags=tags, user_id=session['user_id'])
        db.session.add(idea)
        db.session.commit()
        return redirect(url_for('stored_ideas'))
    return render_template('idea_generation.html')

@app.route('/stored_ideas')
def stored_ideas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_ideas = Idea.query.filter_by(user_id=session['user_id']).all()
    return render_template('stored_ideas.html', ideas=user_ideas)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
