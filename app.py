import mysql.connector
from bottle import request, run, template, response, Bottle, static_file, json_dumps
import pandas as pd
import datetime
import re
from pymongo import MongoClient
import io
from xlsxwriter import Workbook

app = Bottle()

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
company_size_list = []
industry_list = []
suppression_list = []
tal_list = []
email_list = []
job_title_link_list = []
first_last_domain_list = []
first_last_company_list = []


@app.route('/favicon.ico')
def ignore_favicon():
    return ""


@app.route('/', methods='POST')
def process_form():
    return template('templates/index.html')


# Route for handling login
@app.route('/login', method='POST')
def login():
    # Extract data
    username = request.forms['uname']
    entered_password = request.forms['psw']
    # Query the users table to retrieve the stored hashed password for the given username
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()

    if user:
        stored_password = user[3]  # Assuming hashed password is in the third column
        role = user[4]  # Assuming role is in the fifth column
        print(user)
        # Verify the entered password against the stored hash
        if entered_password == stored_password:
            # Check the user's role and render the appropriate template
            if role == 'user':
                return template('templates/user_filter_form.html')
            elif role == 'admin':
                return template('templates/admin_welcome.html')
        else:
            # Login failed
            return template('templates/index.html')
    else:
        # Login failed
        return template('templates/index.html')


@app.route('/runscript', method='POST')
def index():
    # Access form data using request.form
    job_level = request.forms['job_level']
    job_function = request.forms['job_function']
    country = request.forms['country']
    company_size = request.forms['company_size']
    industry = request.forms['industry']
    suppression = request.forms['suppression']
    tal = request.forms['tal']
    email = request.forms['email']
    job_title_link = request.forms['job_title_link']
    first_last_domain = request.forms['first_last_domain']
    first_last_company = request.forms['first_last_domain']
    job_level_list = [job_level]
    job_function_list = [job_function]
    country_list = [country]
    company_size_list = [company_size]
    industry_list = [industry]
    suppression_list = [suppression]
    tal_list = [tal]
    email_list = [email]
    job_title_link_list = [job_title_link]
    first_last_domain_list = [first_last_domain]
    first_last_company_list = [first_last_company]
    store_result = run_script()
    # Create an Excel file
    excel_file = 'output.xlsx'
    store_result.to_excel(excel_file, index=False)

    # Convert the Excel file to bytes for download link
    excel_data = io.BytesIO()
    store_result.to_excel(excel_data, index=False, engine='xlsxwriter')
    excel_data.seek(0)
    print(store_result)
    print(excel_file)
    # Render the 'test.html' template with the result and download link
    return template('templates/test.html', result=store_result, download_link=excel_file)


def run_script():
    all_results_df = pd.DataFrame()  # Create an empty DataFrame

    # MongoDB connection URI
    mongo_uri = "mongodb://localhost:27017/"
    mongo_dbname = "yoanonedatabase"

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
        # output_file_name = input("Enter file name with extension:")
        output_file_path = fr'\\yoandc\Campaigns\#Yoanone\dipesh\file.xlsx'
        mapped_list = []
        for key in company_size_list:
            values = company_size_dict.get(key, [])
            mapped_list.extend(values)


        count = 1
        for i in range(1, 2):
            # Process data in batches
            collection_name = f"yoan_one_{count}"
            start_time = datetime.datetime.now().strftime("%M%S")
            start_time_int = int(start_time)
            print("Start time after conditions:", start_time)

            print(collection_name)

            # Fetch all data from MongoDB collection
            all_result = fetch_all_data_mongodb(mongo_db[collection_name])

            count += 1
            # Create a DataFrame from the results
            header = ['Date', 'Salutation', 'First_Name', 'Last_Name', 'Email', 'Company_Name', 'Address_1',
                      'City', 'State', 'Zip_Code', 'Country', 'Industry', 'Standard_Industry',
                      'Job_Title', 'Job_Title_Level', 'Job_Title_Department', 'Employee_Size', 'Revenue_Size',
                      'Phone_NO', 'Direct_Dial_Extension', 'SIC_Code', 'NAICS_Code', 'Job_Title_Link',
                      'Employee_Size_Link',
                      'Revenue_Size_Link', 'VV_Status', 'Final_Status', 'id', 'domain', 'FirstLastDomain',
                      'FirstLastCompany']

            all_results_df = pd.DataFrame(all_result, columns=header)
            print(all_results_df.shape)
            # Concatenate the new results with the existing DataFrame
            try:
                print("Data filtration start")

                # Function to apply regex pattern using re.findall
                def apply_regex(column, pattern):
                    return column.apply(lambda x: bool(re.findall(pattern, str(x), flags=re.IGNORECASE)))

                try:
                    if tal_list:
                        all_results_df = all_results_df[all_results_df['domain'].isin(tal_list)]
                        print("six", all_results_df.shape)
                except Exception as e:
                    print("Exception in Tal", e)

                try:
                    if country_list:
                        all_results_df = all_results_df[all_results_df['Country'].isin(country_list)]
                        print("third", all_results_df.shape)
                except Exception as e:
                    print("Exception in country", e)

                try:
                    if mapped_list:
                        all_results_df = all_results_df[all_results_df['Employee_Size'].isin(mapped_list)]
                except Exception as e:
                    print("Exception in employee size", e)

                try:
                    # Check if seventh_conditions is not empty, apply it to the DataFrame
                    if suppression_list:
                        all_results_df = all_results_df[~all_results_df['domain'].isin(suppression_list)]
                except Exception as e:
                    print("Exception in suppression", e)

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
                    print("Error in industry condition:", e)

                try:
                    # Apply the fifth condition using re.findall
                    if industry_list:
                        for condition in industry_list:
                            pattern = f"{condition}.*"
                            all_results_df = all_results_df[~apply_regex(all_results_df['Industry'], pattern)]
                except Exception as e:
                    print("Exception in Industry", e)

                print("After 1st condition:", all_results_df.shape)

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
                try:
                    # Check if email_conditions is not empty, apply it to the DataFrame
                    if email_list:
                        all_results_df['Email'] = all_results_df['Email'].str.lower()
                        all_results_df = all_results_df[~all_results_df['Email'].isin(email_list)].drop_duplicates(
                            'Email')
                except Exception as e:
                    print("Exception in email suppression", e)

                try:
                    # Check if jt_link_conditions is not empty, apply it to the DataFrame
                    if job_title_link_list:
                        all_results_df = all_results_df[~all_results_df['Job_Title_Link'].isin(job_title_link_list)]
                except Exception as e:
                    print("Exception in JT link suppression", e)

                try:
                    # Check if fl_domain_conditions is not empty, apply it to the DataFrame
                    if first_last_domain_list:
                        all_results_df = all_results_df[
                            ~all_results_df['FirstLastDomain'].isin(first_last_domain_list)].drop_duplicates(
                            'FirstLastDomain')
                except Exception as e:
                    print("Exception in FL_domain suppression", e)

                try:
                    # Check if fl_company_conditions is not empty, apply it to the DataFrame
                    if first_last_company_list:
                        all_results_df = all_results_df[
                            ~all_results_df['FirstLastCompany'].isin(first_last_company_list)].drop_duplicates(
                            'FirstLastCompany')
                except Exception as e:
                    print("Exception in FL_Company suppression", e)

                all_results_df = all_results_df.drop_duplicates('Job_Title_Link')
            except Exception as e:
                print(e)

            # all_results_df.to_excel(output_file_path, index=False)
            # all_results_df = pd.DataFrame()  # Create an empty DataFrame

        end_time = datetime.datetime.now().strftime("%M%S")
        end_time_int = int(end_time)
        print("end time:", end_time)
        total_time_script_takes = abs(start_time_int - end_time_int)
        print("Total time takes:", total_time_script_takes)


    except Exception as e:
        print(e)

    finally:
        # Close MongoDB connection
        mongo_client.close()

    return all_results_df


def fetch_all_data_mongodb(collection):
    try:
        # Fetch all data from the MongoDB collection
        data = list(collection.find())
        print("data fetched")
        return data
    except Exception as e:
        print(f"Error fetching data from MongoDB: {e}")
        return []


if __name__ == '__main__':
    run(app, host='localhost', port=8080, debug=True)
