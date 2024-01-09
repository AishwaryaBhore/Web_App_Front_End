from bottle import Bottle, template
import mysql.connector

app = Bottle()

# Database configuration
db_config = {
    'host': 'localhost',
    'port': '3307',
    'user': 'root',
    'password': 'root',
    'database': 'frontend',
}

# Connect to MySQL database
db = mysql.connector.connect(**db_config)
cursor = db.cursor()


# Define a route to display the user list
@app.route('/')
def user_list():
    # Fetch user data from the database
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    # Render the HTML template with dynamic data
    return template('user_list_template', users=users)


# Run the Bottle app
if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
