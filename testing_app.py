import io
import jwt
import mysql.connector
import requests
from pymongo import MongoClient
import datetime
import re
from flask import Flask, make_response, jsonify, redirect, g, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit

from itertools import chain

from flask import Flask, render_template, make_response, send_file, request
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key
socketio = SocketIO(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Specify the login view endpoint


conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='admin',
    database='yoandb3'
)
cursor = conn.cursor()
job_level_list = []
job_function_list = []
country_list = []
flat_list = []
company_size_list = []
company_name_list = []
industry_list = []
suppression_list = []
tal_list = []
email_list = []
job_title_link_list = []
first_last_domain_list = []
first_last_company_list = []
SECRET_KEY = 'your-secret-key'


@app.route('/', methods=['GET', 'POST'])
def process_form():
    if is_internet_available():
        # Serve your main page
        return render_template('index.html')
    else:
        # Redirect to the network not available page
        return redirect('/network_not_available')


# Route to display the network not available page
@app.route('/network_not_available')
def network_not_available():
    return render_template(
        'network_not_available.html')


# Function to generate a JWT token
def generate_token(username):
    return jwt.encode({'username': username}, app.config['SECRET_KEY'], algorithm='HS256')


def token_required(callback):
    def wrapper(*args, **kwargs):
        token = request.cookies.get('token', None)

        if not token:
            return render_template('index.html'), 401

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            g.username = payload['username']
        except jwt.ExpiredSignatureError:
            return render_template('index.html'), 401
        except jwt.InvalidTokenError:
            return render_template('index.html'), 401

        return callback(*args, **kwargs)

    return wrapper


# Example protected route
@app.route('/protected')
@token_required
def protected_route():
    return f'Hello, {g.username}!'


token = ""
logged_in_users = set()


# Route for handling login
@app.route('/login', methods=['POST'])
def login():
    # Extract data
    username = request.form['uname']
    entered_password = request.form['psw']
    # Query the users table to retrieve the stored hashed password for the given username
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    # print(user)

    if user:
        stored_password = user[3]  # Assuming hashed password is in the third column
        role = user[4]  # Assuming role is in the fifth column
        # print(user)
        # Verify the entered password against the stored hash

        if entered_password == stored_password:
            # Check the user's role and render the appropriate template
            if role == 'user':
                # Generate a secure token for the user
                token = generate_token(username)
                logged_in_users.add(username)
                socketio.emit('update_users', list(logged_in_users),namespace='/my_namespace')  # Notify admin about the new login

                # Set the token in the session
                session[username] = {'token': token, 'token_status': 'active'}

                # Create a response object
                response = make_response(render_template('user_filter_form.html'))

                return response
            elif role == 'admin':
                cursor.execute("SELECT * FROM users where role = 'user'")
                users = cursor.fetchall()

                # Pass the correct token status for each user
                user_data = [{'username': user[1], 'role': user[4], }
                             for user in users]
                # Render the HTML template with dynamic data
                return render_template('user_list_template.html', users=user_data, logged_in_users=list(logged_in_users))

        else:
            # Login failed
            return render_template('wrong_password.html')
    else:
        # Login failed
        return render_template('index.html')


# Route for handling logout
@app.route('/logout')
def logout():
    # Get the username from the session data
    username = current_user.id
    logged_in_users.discard(username)
    socketio.emit('update_users', list(logged_in_users),namespace='/my_namespace')  # Notify admin about the new login
    response = make_response(render_template('index.html'))
    return response


def check_user_token(username):
    user_data = session.get(username)

    if user_data:
        token = user_data.get('token')
        print("token of user", token)
        if token and jwt_decode_token(token, app.config['SECRET_KEY']) == username:
            print("returned active")
            return 'active'

    print("returned inactive")
    return 'inactive'


def jwt_decode_token(token, secret_key):
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        print("Decoded payload:", payload)
        return payload['username']
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return None


@app.route('/runscript', methods=['POST'])
def index():
    # Access form data using request.form
    job_level = request.form['job_level']
    if job_level:
        job_level_ = job_level.split('\r\n')
        job_level_list.extend(job_level_)
    else:
        job_level_list.extend([])
    print("JOB LEVEL", job_level_list)
    job_function = request.form['job_function']
    if job_function:
        job_function_ = job_function.split('\r\n')
        job_function_list.extend(job_function_)
    else:
        job_function_list.extend([])
    print("JOB FUNCTION", job_function_list)

    country = request.form['country']
    if country:
        country_list_ = country.split('\r\n')
        country_list.extend(country_list_)
    else:
        country_list.extend([])

    print(country_list)

    company_size = request.form['emp_size']
    if company_size:
        company_size_ = company_size.split('\r\n')
        company_size_list.extend(company_size_)
    else:
        company_size_list.extend([])

    print(company_size_list)

    company_name = request.form['company_name']
    if company_name:
        company_name_ = company_name.split('\r\n')
        company_name_list.extend(company_name_)
    else:
        company_name_list.extend([])

    print(company_name_list)

    industry = request.form['industry']
    if industry:

        industry_ = industry.split('\r\n')
        industry_list.extend(industry_)
    else:
        industry_list.extend([])
    print(industry_list)
    suppression = request.form['suppression']
    if suppression:
        suppression_ = suppression.split('\r\n')
        suppression_list.extend(suppression_)
    else:
        suppression_list.extend([])
    print(suppression_list)
    tal = request.form['tal']
    if tal:
        tal_ = tal.split('\r\n')
        tal_list.extend(tal_)
    else:
        tal_list.extend([])
    print(tal_list)
    email = request.form['email']
    if email:
        email_ = email.split('\r\n')
        email_list.extend(email_)
    else:
        email_list.extend([])
    # print(email_list)
    job_title_link = request.form['job_title_link']
    if job_title_link:
        job_title_link_ = job_title_link.split('\r\n')
        job_title_link_list.extend(job_title_link_)
    else:
        job_title_link_list.extend([])
    # print(job_title_link_list)
    first_last_domain = request.form['first_last_domain']
    if first_last_domain:
        first_last_domain_ = first_last_domain.split('\r\n')
        first_last_domain_list.extend(first_last_domain_)
    else:
        first_last_domain_list.extend([])
    # print(first_last_domain_list)
    first_last_company = request.form['first_last_company']
    if first_last_company:

        first_last_company_ = first_last_company.split('\r\n')
        first_last_company_list.extend(first_last_company_)
    else:
        first_last_company_list.extend([])
    # print(first_last_company_list)
    return render_template('index_new.html')


# Endpoint to set session cookie and create CSV file
@app.route('/download', methods=['POST'])
def download_csv():
    # Create DataFrame
    df = run_script()

    # Create CSV file and save it temporarily
    csv_buffer = io.BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    # Send the CSV file in the response
    return send_file(
        csv_buffer,
        as_attachment=True,
        download_name='data.csv',
        mimetype='text/csv'
    )


@app.route('/favicon.ico')
def ignore_favicon():
    return ""


def is_internet_available():
    try:
        # Try to make a simple HTTP request to a known website
        response = requests.get("http://www.google.com", timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        return False


def run_script():
    all_results_df_final = pd.DataFrame()  # Create an empty DataFrame

    # MongoDB connection URI
    mongo_uri = "mongodb+srv://yoan_user:yoanone@cluster0.bea0lcp.mongodb.net/"
    mongo_dbname = "yoandb"

    # Create a MongoDB client and connect to the database
    mongo_client = MongoClient(mongo_uri)
    mongo_db = mongo_client[mongo_dbname]

    company_size_dict = {
        'Invalid Emp': ["Employee Size",
                        "Engineering",
                        "Engineering & Research",
                        "ES",
                        "F",
                        "Facilities",
                        "Finance",
                        "Finance & Administration",
                        "FR",
                        "Government Administration",
                        "Hospitals and Health Care",
                        "Human Resource",
                        "Human Resources",
                        "Information Technology",
                        "Insurance",
                        "Management",
                        "Manager",
                        "Marketing",
                        "NA",
                        "NL",
                        "Not Available",
                        "Operation Management",
                        "Operations",
                        "Other",
                        "others",
                        "Real Estate",
                        "Sales",
                        "TN39 3LW",
                        "Transformation",
                        "v",
                        "and",
                        "C-Level",
                        "Computer Networking",
                        "Development",
                        "Digital Media",
                        "320 crores",
                        "and Global Facilities",
                        "Equity & Inclusion Officer",
                        "$05M-$10M",
                        "$1 Billion",
                        "$1.1B-$3B",
                        "$10 Million",
                        "$100M-$250M",
                        "$10M-$20M",
                        "$1B-$5B",
                        "$2.9B",
                        "$20M-$50M",
                        "$24.7M",
                        "$250M-$1B",
                        "$25M-$49M",
                        "$31.6B",
                        "$362M",
                        "$367M",
                        "$41 Million",
                        "$42M",
                        "$5.76 million",
                        "$50M - $100M",
                        "$50M-$99M",
                        "$56.2B",
                        "$5B-$10B",
                        "$69.9B",
                        "$7 Million",
                        "$7.8B",
                        "$70M",
                        "$8.50 B",
                        "$95.6M",
                        "`",
                        "<$01M",
                        "<$25M",
                        ">$10B",
                        "0",
                        "0.4131944444444444",
                        "-"
                        ],
        '10,001+': [
            "10,001+ employees",
            "10000+",
            "10000+ employees",
            "10000+_x000D_",
            "10000+_x000D_ employees",
            "10001+ employees_x000D_",
            "10,000+",
            "10,001+",
            "10,001+ employee",
            "10,001+ ",
            "10,001+employees",
            "10,001+-employees",
            "10000",
            "10000 +",
            "10000 + Employees",
            "10000 PLUS",
            "10000 to 99999",
            "10000 to 99999 Employees",
            "10000.0",
            "10000+ e",
            "10000+Employees",
            "100000",
            "100000.0",
            "100001.0",
            "10000-5000",
            "10000-50000",
            "10000-99999",
            "10000to99999",
            "10000-to-99999",
            "10001",
            "10001 + Employees",
            "10001 Employees",
            "10001.0",
            "10001+",
            "10001+ employees",
            "10001+employee",
            "10001+employees",
            "10001+-employees",
            "1000-10000 employees",
            "10001-5000 employees",
            "10001employees",
            "10001-Employees",
            "10002+",
            "10002+ Employees",
            "10002499",
            "10004+",
            "18568",
            "18568.0",
            "18933.0",
            "22,001+ employees",
            "44105",
            "44105.0",
            "44440",
            "44440.0",
            "44836.0",
            "45170"
        ],
        '1,001-5,000': [
            "1,001-5,000 employees",
            "1000-2499",
            "1000-2499 employees",
            "10002499_x000D_",
            "1000-2499_x000D_",
            "1001-5000 employees_x000D_",
            "2500-4999",
            "2500-4999 employees",
            "25004999_x000D_",
            "2500-4999_x000D_",
            "500 to 999",
            "500-999",
            "500-999 employees",
            "500999_x000D_",
            "500-999_x000D_",
            "1,000-5,000",
            "1,001 to 5,000",
            "1,001 to 5,000 employees",
            "1,001 to 5,000 ",
            "1,001-5,000",
            "1,001-5,000 ",
            "1,0015,000employees",
            "1,001-5,000-employees",
            "1,001-5,001",
            "1,001-5000",
            "1,300 Employees",
            "10,001-5,000 employees",
            "1000",
            "1000 - 5000",
            "1000 to 2499",
            "1000 to 2499 Employees",
            "1000 to 2499_x000D_",
            "1000 to 5000",
            "1000 to 5000 employees",
            "1000 to 5000 emplyoees",
            "1000.0",
            "1000+",
            "1000+ employees",
            "1000+5000",
            "1000+employees",
            "1000-2500",
            "1000-5000",
            "'1000-5000",
            "1000-5000 Employees",
            "1000to2499",
            "1000-to-2499",
            "1001 - 5000 employees",
            "1001 5000 employees",
            "1001- 5000 Employees",
            "1001 to 5000",
            "1001 to 5000 employees",
            "1001 to 5000 ",
            "1001 to 5001 Employees",
            "1001+ 5000 employees",
            "1001-5000",
            "1001-5000 e",
            "1001-5000 employee",
            "10015000 employees",
            "1001-5000 Employees",
            "1001-5000 Employees`",
            "1001-5000 Employeesc",
            "1001-5000 ",
            "1001-5000employees",
            "1001-5000-employees",
            "1001Suspect Profile5000 employees",
            "1001to 5000 employees",
            "1-5000 Emp",
            "2,001-5,000 employees",
            "200-5000",
            "2-500 Emp",
            "2500 to 4999",
            "2500 to 4999 Employees",
            "2500 to 4999_x000D_",
            "2500 to 5000",
            "2500 to 5001",
            "25004999",
            "2500-5000",
            "2500-to-4999",
            "2747",
            "2977",
            "2977.0",
            "2978",
            "2978.0",
            "3,001-5,000 employees",
            "4,001-5,000 employees",
            "4340",
            "4340.0",
            "500 to 99900 to 999\"",
            "500+1000",
            "500-1,000",
            "500-1,000 employees",
            "500-1000",
            "'500-1000",
            "500-1000 employees",
            "500-1000employees",
            "500-1001",
            "5001-10,000",
            "5001-10,000 employees",
            "5001-1000 employees",
            "5001-10001",
            "500-900 Employees",
            "500999",
            "500-to-999",
            "7,001-5,000 employees",
            "8,001-5,000 employees",
            "9,001-5,000 employees"
        ],
        '101-250': [
            "100 to 249",
            "100-249",
            "100249_x000D_",
            "100-249_x000D_",
            "100 to 249 employees",
            "100 to 249_x000D_",
            "100-200 employees",
            "100249",
            "100-249 employees",
            "100to249",
            "100-to-249",
            "101-250",
            "200",
            "200 employees",
            "200.0",
            "249",
            "249.0",
            "50 to 200",
            "50 to 200 employees",
            "50-200",
            "50-to-99"
        ],
        '1-10': [
            "1-9",
            "1-9 Employees",
            "1-9_x000D_",
            "2-10",
            "0-1",
            "0-1 Employees",
            "0-10 Employees",
            "02-10 Employees",
            "02-10.",
            "1 to 10 employees",
            "1 to 9",
            "1 to 9_x000D_",
            "19",
            "1-9 employee",
            "1-to-9",
            "2- 10 Employees",
            "2 to 10 employees",
            "2–10",
            "2-10 Employee",
            "210 employees",
            "2-10 employees",
            "2-10",
            "2-10-employees",
            "5",
            "5.0"
        ],
        '11-100': [
            "10 to 19",
            "10-19",
            "10-19 employees",
            "10-19_x000D_",
            "20 to 49",
            "20-49",
            "20-49_x000D_",
            "50-99",
            "50-99 employees",
            "50-99_x000D_",
            "51-200 employees",
            ",11-50",
            "10-to-19",
            "11 50 employees",
            "11- 50 Employees",
            "11 to 50",
            "11 to 50 employees",
            "1-10 Employees",
            "11-19 Employees",
            "11-50",
            "'11-50",
            "11-50 + employees",
            "11-50 emp",
            "1150 employees",
            "11-50 Employees",
            "11-50 employees_x000D_",
            "11-50 Eployees",
            "11-50 ",
            "11-50,",
            "11-50emp",
            "11-50employees",
            "11-50-employees",
            "11-51",
            "1-50 employees",
            "19.0",
            "20 to 49 Employees",
            "20 to 49_x000D_",
            "20 to 51 Employees",
            "20-to-49",
            "21",
            "21.0",
            "25",
            "25.0",
            "25-50 employees",
            "30 employees",
            "31",
            "31.0",
            "32 employees",
            "42 Employees",
            "50",
            "50 to 99",
            "50 to 99 Employees",
            "50 to 99_x000D_",
            "50.0",
            "50-100",
            "51 200 employees",
            "51- 200 Employees",
            "51 to 200",
            "51 to 200 employees",
            "51 to 200 ",
            "51 to 250 employees",
            "51-200",
            "'51-200",
            "51-200 Employee",
            "51-200 Employee Size",
            "51200 employees",
            "51-200 employees_x000D_",
            "51-200 employeesEmployee Size",
            "51-200 ",
            "51-20051-200",
            "51-200Employees",
            "51-200-employees",
            "51-201",
            "51-210 employees",
            "51to 200 employees",
            "52-200",
            "53-200",
            "70",
            "70.0",
            "76",
            "76.0",
            "Emp 11 to 50"
        ],
        '251-500': [
            "201-500 employees",
            "250 to 499",
            "250-499",
            "250-499 employees",
            "250-499 employess",
            "250499_x000D_",
            "250-499_x000D_",
            "100 to 500 Employees",
            "100-500",
            "100-500 employees",
            "1005000 Employees",
            "1-500",
            "200 to 500",
            "200 to 501",
            "200-500",
            "200-500 employees",
            "200-599",
            "201 500 employees",
            "201- 500 Employees",
            "201 to 500",
            "201 to 500 employees",
            "201 to 500 to employees",
            "201 to 500 ",
            "201 to 500employees",
            "201-500",
            "201-500 Emplopyees",
            "201-500 Employee",
            "201-500 Employee Size",
            "201500 Employees",
            "201-500 employees_x000D_",
            "201-500 ",
            "201500employees",
            "201-500employees",
            "201-500-employees",
            "201-501",
            "201-503",
            "201-504",
            "201Suspect Profile500 employees",
            "201to 500 employees",
            "211-500 employees",
            "250 Employees",
            "250 to 499 Employees",
            "250 to 499_x000D_",
            "250to499",
            "250-to-499",
            "264",
            "264.0",
            "297.0",
            "319 employees",
            "350",
            "350.0",
            "406 employees.",
            "423",
            "423.0",
            "450",
            "450.0",
            "499-999",
            "500.0",
            "50-500 employees",
            "51-500 employees"
        ],
        '5,001-10,000': [
            "5000-9999",
            "5000-9999 employees",
            "50009999_x000D_",
            "5000-9999_x000D_",
            "5001-10000 employees_x000D_",
            "5,000-10,000",
            "5,001 to 10,000",
            "5,001 to 10,000 ",
            "5,001-10,00",
            "5,001-10,000",
            "5,001-10,000 employees",
            "5,001-10,000 ",
            "5,001-10,000-employees",
            "5,001-10,001",
            "5,001-10000",
            "5,001-5,000 employees",
            "5000",
            "5000 - 10000",
            "5000 -10000 employees",
            "5000 to 10000",
            "5000 to 9999",
            "5000 to 9999 Employees",
            "5000 to 9999_x000D_",
            "5000.0",
            "5000+",
            "50000-10000",
            "5000-10,000",
            "5000-10000",
            "5000-10000 employees",
            "5000-10000employees",
            "5000-10001",
            "5000-10003",
            "5000-10004",
            "5000-10005",
            "5000-10006",
            "5000-10008",
            "5000-10010",
            "5000-10011",
            "5000-10012",
            "5000-10013",
            "5000-10015",
            "5000-10016",
            "50009999",
            "5000to9999",
            "5000-to-9999",
            "5001 - 10000 employees",
            "5001 10000 employees",
            "5001- 10000 employees",
            "5001 to 10000",
            "5001 to 10000 employees",
            "5001+ 10000 employees",
            "50010000 Employees",
            "5001-10000",
            "5001-10000 Employee",
            "500110000 employees",
            "5001-10000 employees",
            "5001-10000 Employees`",
            "5001-10000 Employess",
            "5001-10000employees",
            "5001-10000-employees",
            "5001to 10000 employees",
            "6,001-5,000 employees"
        ],
        '501-1,000': [
            "501-1,000 employees",
            "501-1000 employees_x000D_",
            "250 to 999",
            "250-500",
            "251-500",
            "251-500 Employees",
            "500",
            "500 to 1000",
            "500 to 1000 employees",
            "500 to 999 Employees",
            "500 to 999_x000D_",
            "501 - 1000",
            "501 - 1000 employees",
            "501 1000 Employees",
            "501- 1000 Employees",
            "501 to 1,000",
            "501 to 1,000 employees",
            "501 to 1,000 ",
            "501 to 1000",
            "501 to 1000 employees",
            "501 to 1000 ",
            "501+1000 employees",
            "501000 Employees",
            "501-1,000",
            "501-1,000 ",
            "501-1,000-employees",
            "501-1000",
            "501-1000 employee",
            "501-1000 Employee Size",
            "5011000 employees",
            "501-1000 employees",
            "501-1000 employees5,001-10,00",
            "501-1000 employes",
            "501-1000 employess",
            "501-1000employees",
            "501-1000-employees",
            "501-999",
            "501-999 employees",
            "501to 1000 employees",
            "502-1,000 employees",
            "502-1000 Employees",
            "599-999",
            "629",
            "629.0",
            "780 Employees",
            "849 Employees",
            "916 Employees"
        ],
    }

    try:
        print("Execution Start")
        start_time = datetime.datetime.now().strftime("%M%S")
        start_time_int = int(start_time)
        print("Start time:", start_time)
        mapped_list = []
        for key in company_size_list:
            values = company_size_dict.get(key, [])
            mapped_list.extend(values)

        count = 1
        for i in range(1, 2):
            # Process data in batches
            collection_name = f"yoan_one_{count}"
            print(collection_name)

            # Fetch all data from MongoDB collection
            all_result = fetch_all_data_mongodb(mongo_db[collection_name])

            count += 1
            # Create a DataFrame from the results
            header = ['Date', 'Salutation', 'First_Name', 'Last_Name', 'Email', 'Company_Name', 'Address_1',
                      'City', 'State', 'Zip_Code', 'COUNTRY', 'Industry', 'Standard_Industry',
                      'Job_Title', 'Job_Title_Level', 'Job_Title_Department', 'Employee_Size', 'Revenue_Size',
                      'Phone_NO', 'Direct_Dial_Extension', 'SIC_Code', 'NAICS_Code', 'Job_Title_Link',
                      'Employee_Size_Link',
                      'Revenue_Size_Link', 'VV_Status', 'Final_Status', 'id', 'domain', 'FirstLastDomain',
                      'FirstLastCompany', 'EBB_status', 'QA', 'QA_status']

            all_results_df = pd.DataFrame(all_result, columns=header)
            # Concatenate the new results with the existing DataFrame
            print(all_results_df.shape)
            try:
                print("Data filtration start")

                # Function to apply regex pattern using re.findall
                def apply_regex(column, pattern):
                    return column.apply(lambda x: bool(re.findall(pattern, str(x), flags=re.IGNORECASE)))

                try:
                    if tal_list:
                        all_results_df['domain'] = all_results_df['domain'].str.lower()
                        all_results_df = all_results_df[all_results_df['domain'].isin(tal_list)]
                        print("tal", all_results_df.shape)
                except Exception as e:
                    print("Exception in Tal", e)

                try:
                    if country_list:
                        all_results_df = all_results_df[all_results_df['COUNTRY'].isin(country_list)]
                        print("country", all_results_df.shape)
                except Exception as e:
                    print("Exception in country", e)
                print(company_size_list)
                print(all_results_df.shape)
                try:
                    if mapped_list:
                        all_results_df = all_results_df[all_results_df['Employee_Size'].isin(mapped_list)]
                except Exception as e:
                    print("Exception in employee size", e)
                print(all_results_df.shape)
                try:
                    # Check if seventh_conditions is not empty, apply it to the DataFrame
                    if suppression_list:
                        all_results_df['domain'] = all_results_df['domain'].str.lower()
                        all_results_df = all_results_df[~all_results_df['domain'].isin(suppression_list)]
                except Exception as e:
                    print("Exception in suppression", e)
                print(all_results_df.shape)
                try:
                    # Apply the fifth condition using str.contains
                    if job_level_list:
                        condition_series = []
                        for condition in job_level_list:
                            pattern = f".*{condition}.*"
                            condition_series.append(
                                all_results_df['Job_Title'].str.contains(pattern, case=False, na=False, regex=True))
                        if condition_series:
                            # Combine conditions using logical OR
                            final_condition = pd.DataFrame(condition_series).any(axis=0)
                            all_results_df = all_results_df[final_condition]
                except Exception as e:
                    print("Error in Job Level condition:", e)
                print(all_results_df.shape)
                try:
                    # Apply the fifth condition using re.findall
                    if industry_list:
                        for condition in industry_list:
                            pattern = f"*{condition}.*"
                            all_results_df = all_results_df[~apply_regex(all_results_df['Industry'], pattern)]
                except Exception as e:
                    print("Exception in Industry", e)
                print(all_results_df.shape)
                try:
                    # Apply the fifth condition using str.contains
                    if job_function_list:
                        condition_series = []
                        for condition in job_function_list:
                            pattern = f".*{condition}.*"
                            condition_series.append(
                                all_results_df['Job_Title'].str.contains(pattern, case=False, na=False, regex=True))
                        if condition_series:
                            # Combine conditions using logical OR
                            final_condition = pd.DataFrame(condition_series).any(axis=0)
                            all_results_df = all_results_df[final_condition]
                except Exception as e:
                    print("Error in industry condition:", e)
                print(all_results_df.shape)
                try:
                    # Check if email_conditions is not empty, apply it to the DataFrame
                    if email_list:
                        all_results_df['Email'] = all_results_df['Email'].str.lower()
                        all_results_df = all_results_df[
                            ~all_results_df['Email'].isin(email_list)].drop_duplicates(
                            'Email')
                except Exception as e:
                    print("Exception in email suppression", e)

                try:
                    # Check if jt_link_conditions is not empty, apply it to the DataFrame
                    if job_title_link_list:
                        all_results_df['Job_Title_Link'] = all_results_df['Job_Title_Link'].str.lower()
                        all_results_df = all_results_df[~all_results_df['Job_Title_Link'].isin(job_title_link_list)]
                except Exception as e:
                    print("Exception in JT link suppression", e)

                try:
                    # Check if fl_domain_conditions is not empty, apply it to the DataFrame
                    if first_last_domain_list:
                        lowercase_fl_domain = [condition.lower() for condition in first_last_domain_list]
                        all_results_df['FirstLastDomain'] = all_results_df['FirstLastDomain'].str.lower()
                        all_results_df = all_results_df[
                            ~all_results_df['FirstLastDomain'].isin(lowercase_fl_domain)].drop_duplicates(
                            'FirstLastDomain')
                except Exception as e:
                    print("Exception in FL_domain suppression", e)

                try:
                    # Check if fl_company_conditions is not empty, apply it to the DataFrame
                    if first_last_company_list:
                        lowercase_fl_company = [condition.lower() for condition in first_last_company_list]
                        all_results_df['FirstLastCompany'] = all_results_df['FirstLastCompany'].str.lower()
                        all_results_df = all_results_df[
                            ~all_results_df['FirstLastCompany'].isin(lowercase_fl_company)].drop_duplicates(
                            'FirstLastCompany')
                except Exception as e:
                    print("Exception in FL_Company suppression", e)

                try:
                    if company_name_list:
                        all_results_df = all_results_df[all_results_df['Company_Name'].isin(company_name_list)]
                        print("company", all_results_df.shape)
                except Exception as e:
                    print("Exception in Tal", e)
                all_results_df_final = pd.concat([all_results_df_final, all_results_df], ignore_index=True)
                all_results_df = pd.DataFrame()  # Create an empty DataFrame
            except Exception as e:
                print(e)

        try:
            all_results_df_final = all_results_df_final.drop_duplicates('Job_Title_Link')
            all_results_df_final = all_results_df_final.drop_duplicates('Email')
            all_results_df_final = all_results_df_final.drop_duplicates('FirstLastDomain')
            all_results_df_final = all_results_df_final.drop_duplicates('FirstLastCompany')
            print(all_results_df_final.shape)
            # Drop the specified column (excluded_field) if it exists
            all_results_df_final = all_results_df_final.drop(columns=['id'], errors='ignore')

        except Exception as e:
            print(e)

        end_time = datetime.datetime.now().strftime("%M%S")
        end_time_int = int(end_time)
        print("end time:", end_time)
        if start_time_int > end_time_int:
            total_time_script_takes = abs(start_time_int - end_time_int)
            print("Total time takes:", total_time_script_takes)
        else:
            total_time_script_takes = abs(end_time_int - start_time_int)
            print("Total time takes:", total_time_script_takes)
        # Print message

    except Exception as e:
        print(e)

    finally:
        # Close MongoDB connection
        mongo_client.close()

    return all_results_df_final


def fetch_all_data_mongodb(collection):
    try:
        # Fetch all data from the MongoDB collection
        data = list(collection.find())
        print("data fetched")
        return data
    except Exception as e:
        print(f"Error fetching data from MongoDB: {e}")
        return []


# The rest of your existing code for the 'index' route remains unchanged

if __name__ == '__main__':
    app.run(debug=True)
