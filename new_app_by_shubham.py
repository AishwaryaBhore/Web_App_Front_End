from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Specify the login view endpoint

# Dummy user data for demonstration purposes
users = {
    'user1': {'password': 'password1', 'role': 'user'},
    'admin': {'password': 'admin_password', 'role': 'admin'}
}


# User class for Flask-Login
class User(UserMixin):
    pass


@login_manager.user_loader
def load_user(user_id):
    # Create a User object from the user_id
    user = User()
    user.id = user_id
    return user


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username]['password'] == password:
            # Create a User object and log the user in
            user = User()
            user.id = username
            login_user(user)
            return redirect(url_for('dashboard'))

    return render_template('wrong_password.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('please_try_again.html', username=current_user.id)


if __name__ == '__main__':
    app.run(debug=True)
