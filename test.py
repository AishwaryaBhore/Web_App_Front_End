from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Mock user class for demonstration purposes
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


# Mock user database for demonstration purposes
users_db = {
    1: User(1, 'user1'),
    2: User(2, 'user2'),
    3: User(3, 'user3'),
}

# Dictionary to store user tokens and their status
user_tokens = {}


@login_manager.user_loader
def load_user(user_id):
    return users_db.get(int(user_id))


def generate_token(username):
    return jwt.encode({'username': username}, app.config['SECRET_KEY'], algorithm='HS256')


def jwt_decode_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


@app.route('/login/<int:user_id>')
def login(user_id):
    if user_id in users_db:
        user = users_db[user_id]
        token = generate_token(user.username)
        user_tokens[user.username] = {'token': token, 'status': 'active'}
        login_user(user)
        return render_template('user_filter_form.html')
    else:
        return 'User not found', 404


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', users=user_tokens)


@app.route('/logout')
@login_required
def logout():
    user = current_user
    if user.username in user_tokens:
        del user_tokens[user.username]
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
