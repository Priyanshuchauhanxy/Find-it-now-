from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import random
import MySQLdb.cursors
import re
import base64
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'lostfound'
app.config['MYSQL_PORT'] = 3306
mysql = MySQL(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "coderate79@gmail.com"  # Replace with your email
app.config['MAIL_PASSWORD'] = "xecv zxqm kade xpqy"  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = "coderate79@gmail.com"

mail = Mail(app)

@app.route('/')
def index():
    if 'loggedin' in session:
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM found11 ORDER BY id DESC LIMIT 5')
            found_items = cursor.fetchall()
            for item in found_items:
                if item['item_img'] is not None:
                    try:
                        img_data = base64.b64decode(item['item_img'])
                        base64_img = base64.b64encode(img_data).decode('utf-8')
                        item['item_img_data_url'] = f'data:image/jpeg;base64,{base64_img}'
                    except Exception as e:
                        print(f"Error processing image for found item {item['id']}: {str(e)}")
                        item['item_img_data_url'] = None
            
            cursor.execute('SELECT * FROM lost11 ORDER BY id DESC LIMIT 5')
            lost_items = cursor.fetchall()
            for item in lost_items:
                if item['item_imgl'] is not None:
                    try:
                        img_data = base64.b64decode(item['item_imgl'])
                        base64_img = base64.b64encode(img_data).decode('utf-8')
                        item['item_img_data_url'] = f'data:image/jpeg;base64,{base64_img}'
                    except Exception as e:
                        print(f"Error processing image for lost item {item['id']}: {str(e)}")
                        item['item_img_data_url'] = None

            cursor.close()
            return render_template('index.html', found_items=found_items, lost_items=lost_items)
        except Exception as e:
            print(f"Database error: {str(e)}")
            return render_template('index.html', found_items=[], lost_items=[])
    return redirect(url_for('login'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'enroll' in request.form and 'password' in request.form:
        username = request.form['username']
        enroll = request.form['enroll']
        password =  request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM logindb11 WHERE username = %s AND enroll = %s AND password = %s', (username, enroll, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            session['enroll'] = account['enroll']
            session['password'] = account['password']
            return redirect(url_for('index'))
        else:
            msg = '*Incorrect username/enroll/password not matched ! (if your are new user you have to register!!)'
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

def generate_otp():
    return str(random.randint(100000, 999999))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    registration_success = None
    if request.method == 'POST' and 'username' in request.form and 'enroll' in request.form and 'email' in request.form and 'contact' in request.form and 'password' in request.form and 'con_password' in request.form and 'branch' in request.form and 'sem' in request.form:
        username = request.form['username']
        enroll = request.form['enroll']
        email = request.form['email']
        contact = request.form['contact']
        password = request.form['password']
        con_password = request.form['con_password']
        branch = request.form['branch']
        sem = request.form['sem']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        query = "SELECT * FROM logindb11 WHERE enroll = %s OR email = %s"
        cursor.execute(query, (enroll, email))
        account = cursor.fetchone()
        
        if account:
            if account['enroll'] == enroll:
                msg = 'This Enrollment number is already registered!'
            elif account['email'] == email:
                msg = 'This Email address is already registered!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not re.match(r'^\d{5}$', enroll):
            msg = 'Invalid Enrollment number! It must be last 5-digit number.'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'^\d{10}$', contact):
            msg = 'Invalid contact number! It must be a 10-digit number.'
        elif password != con_password:
            msg = 'Password and Confirm Password must match!'
        elif not username or not enroll or not email:
            msg = 'Please fill out the form!'
        else:
            # Generate OTP and send email
            otp = generate_otp()
            session['otp'] = otp  # Store OTP in session
            session['user_data'] = {  # Store user details in session
                'username': username,
                'enroll': enroll,
                'email': email,
                'contact': contact,
                'password': password,
                'branch': branch,
                'sem': sem
            }
            try:
                msg = Message('Your OTP Code',
                    sender=app.config['MAIL_DEFAULT_SENDER'],
                    recipients=[email])
                msg.html = f'''
                    <!DOCTYPE html>
                    <html>
                        <head>
                            <style>
                                body {{
                                    font-family: Arial, sans-serif;
                                    line-height: 1.6;
                                    color: #333;
                                }}
                                .container {{
                                    max-width: 600px;
                                    margin: 0 auto;
                                    padding: 20px;
                                }}
                                .otp-code {{
                                    font-size: 24px;
                                    font-weight: bold;
                                    color: #007bff;
                                    padding: 10px;
                                    margin: 10px 0;
                                }}
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <h2>Email Verification</h2>
                                <p>Thank you for registering. To complete your registration, please use the following OTP code:</p>
                                <div class="otp-code">{otp}</div>
                                <p>Please enter this code in the verification page to complete your registration.</p>
                                <p>If you did not request this verification, please ignore this email.</p>
                            </div>
                        </body>
                    </html>
                '''
                msg.content_type = "text/html"
                mail.send(msg)

                flash("OTP sent successfully to your email!", "success")
                return redirect(url_for('verify_otp'))  # Redirect to OTP verification page
            except Exception as e:
                 flash(f"Error sending OTP:{str(e)}","Danger")
        
        cursor.close()
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
        registration_success = False
    return render_template('register.html', msg=msg, registration_success=registration_success)

@app.route('/otp', methods=['GET', 'POST'])
def verify_otp():
    if 'user_data' not in session:
        flash("Session expired. Please register again.", "Danger")
        return redirect(url_for('register'))

    if request.method == 'POST':
        user_otp = request.form['otp']
        if 'otp' in session and session['otp'] == user_otp:
            user_data = session.pop('user_data')  # Retrieve user data

            # Insert user into database
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO logindb11 VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)',
                           (user_data['username'], user_data['enroll'], user_data['email'], user_data['contact'],
                            user_data['password'], user_data['password'], user_data['branch'], user_data['sem']))
            mysql.connection.commit()
            cursor.close()

            session.pop('otp', None)  # Remove OTP from session
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("Invalid OTP! Please try again.", "danger")

    return render_template('otp.html')

@app.route('/found_form')
def found_form():
    return render_template('found_form.html')

@app.route('/submit_event', methods=['POST'])
def submit_event():
    if request.method == 'POST':
        try:
            item_name = request.form['item_name']
            dis_item = request.form['dis_item']
            f_name = request.form['f_name']
            contact = request.form['contact']
            email = request.form['email']
            date = request.form['date']
            
            if 'item_img' not in request.files:
                return 'No image uploaded', 400
            
            item_img = request.files['item_img']
            
            if item_img.filename == '':
                return 'No image selected', 400
                
            if item_img and allowed_file(item_img.filename):
                image_binary = item_img.read()
                encoded_image = base64.b64encode(image_binary).decode('utf-8')
                print(f"Debug - Image size: {len(image_binary)} bytes")
                print(f"Debug - Encoded size: {len(encoded_image)} chars")
                
                cursor = mysql.connection.cursor()
                sql = '''INSERT INTO found11 (item_name, dis_item, f_name, contact, email, date, item_img) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)'''
                cursor.execute(sql, (item_name, dis_item, f_name, contact, email, date, encoded_image))
                mysql.connection.commit()
                cursor.close()
                
                return redirect(url_for('index'))
            
            return 'Invalid file type', 400
            
        except Exception as e:
            print(f"Error submitting found item: {str(e)}")
            return str(e), 500
    return redirect(url_for('found_form'))

@app.route('/lost_form')
def lost_form():
    return render_template('lost_form.html')

@app.route('/submitll_event', methods=['POST'])
def submitll_event():
    if request.method == 'POST':
        try:
            item_namel = request.form['item_namel']
            dis_iteml = request.form['dis_iteml']
            f_namel = request.form['f_namel']
            contactl = request.form['contactl']
            emaill = request.form['emaill']
            datel = request.form['datel']
            
            encoded_image = None
            if 'p_photo1' in request.files: 
                p_photo1 = request.files['p_photo1']
                if p_photo1.filename != '' and allowed_file(p_photo1.filename):
                    image_binary = p_photo1.read()
                    encoded_image = base64.b64encode(image_binary).decode('utf-8')
            
            cursor = mysql.connection.cursor()
            if encoded_image:
                sql = '''INSERT INTO lost11 (item_namel, dis_iteml, f_namel, contactl, emaill, datel, item_imgl)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)'''
                cursor.execute(sql, (item_namel, dis_iteml, f_namel, contactl, emaill, datel, encoded_image))
            else:
                sql = '''INSERT INTO lost11 (item_namel, dis_iteml, f_namel, contactl, emaill, datel)
                        VALUES (%s, %s, %s, %s, %s, %s)'''
                cursor.execute(sql, (item_namel, dis_iteml, f_namel, contactl, emaill, datel))
            
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('index'))
            
        except Exception as e:
            print(f"Error submitting lost item: {str(e)}")
            return redirect(url_for('lost_form'))
    return redirect(url_for('lost_form'))

@app.route('/all-lost')
def all_lost():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM lost11 ORDER BY id DESC')
        lost_items = cursor.fetchall()
        cursor.close()
        for item in lost_items:
            if item['item_imgl'] is not None:
                try:
                    img_data = base64.b64decode(item['item_imgl'])
                    base64_img = base64.b64encode(img_data).decode('utf-8')
                    item['item_img_data_url'] = f'data:image/jpeg;base64,{base64_img}'
                except Exception as e:
                    print(f"Error processing image for item {item['id']}: {str(e)}")
                    item['item_img_data_url'] = None
        return render_template('all_lost.html', items=lost_items)
    return redirect(url_for('login'))

@app.route('/all-found')
def all_found():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM found11 ORDER BY id DESC')
        found_items = cursor.fetchall()
        cursor.close()
        
        for item in found_items:
            if item['item_img'] is not None:
                try:
                    img_data = base64.b64decode(item['item_img'])
                    base64_img = base64.b64encode(img_data).decode('utf-8')
                    item['item_img_data_url'] = f'data:image/jpeg;base64,{base64_img}'
                except Exception as e:
                    print(f"Error processing image for item {item['id']}: {str(e)}")
                    item['item_img_data_url'] = None
        
        return render_template('all_found.html', items=found_items)
    return redirect(url_for('login'))

@app.route('/matching-items')
def matching_items():
    if 'loggedin' in session:
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            cursor.execute('SELECT * FROM lost11')
            lost_items = cursor.fetchall()
            
            cursor.execute('SELECT * FROM found11')
            found_items = cursor.fetchall()
            
            matches = []
            for lost in lost_items:
                for found in found_items:
                    try:
                        lost_name = lost['item_namel'].lower() if lost['item_namel'] else ''
                        found_name = found['item_name'].lower() if found['item_name'] else ''
                        lost_desc = lost['dis_iteml'].lower() if lost['dis_iteml'] else ''
                        found_desc = found['dis_item'].lower() if found['dis_item'] else ''
                        
                        name_match = (lost_name in found_name or found_name in lost_name or
                                    any(word in found_name for word in lost_name.split()))
                        desc_match = (lost_desc in found_desc or found_desc in lost_desc or
                                    any(word in found_desc for word in lost_desc.split()))
                        
                        if name_match or desc_match:
                            if found['item_img'] is not None:
                                img_data = base64.b64decode(found['item_img'])
                                base64_img = base64.b64encode(img_data).decode('utf-8')
                                found['item_img_data_url'] = f'data:image/jpeg;base64,{base64_img}'

                            if lost['item_imgl'] is not None:
                                img_data = base64.b64decode(lost['item_imgl'])
                                base64_img = base64.b64encode(img_data).decode('utf-8')
                                lost['item_img_data_url'] = f'data:image/jpeg;base64,{base64_img}'

                            lost_date = lost['datel'] if lost['datel'] else None
                            found_date = found['date'] if found['date'] else None
                            
                            match_info = {
                                'lost_item': lost,
                                'found_item': found,
                                'match_type': 'Name match' if name_match else 'Description match'
                            }
                            
                            if lost_date and found_date:
                                match_info['date_difference'] = abs((found_date - lost_date).days)
                             
                            matches.append(match_info)
                    except Exception as e:
                        print(f"Error processing match: {str(e)}")
                        continue
            
            cursor.close()
            return render_template('matching_items.html', matches=matches)
        except Exception as e:
            print(f"Database error: {str(e)}")
            return render_template('matching_items.html', matches=[], error="An error occurred while fetching matches")
    return redirect(url_for('login'))

@app.route('/delete-found/<int:item_id>', methods=['POST'])
def delete_found(item_id):
    if 'loggedin' in session:
        try:
            cursor = mysql.connection.cursor()
            cursor.execute('DELETE FROM found11 WHERE id = %s', (item_id,))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('all_found'))
        except Exception as e:
            print(f"Error deleting found item: {str(e)}")
            return "Error deleting item", 500
    return redirect(url_for('login'))

@app.route('/delete-lost/<int:item_id>', methods=['POST'])
def delete_lost(item_id):
    if 'loggedin' in session:
        try:
            cursor = mysql.connection.cursor()
            cursor.execute('DELETE FROM lost11 WHERE id = %s', (item_id,))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('all_lost'))
        except Exception as e:
            print(f"Error deleting lost item: {str(e)}")
            return "Error deleting item", 500
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)