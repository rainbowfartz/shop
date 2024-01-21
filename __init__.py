from flask import *
from Forms import CreateCheckoutForm
import shelve, checkoutinfo
from datetime import datetime, timedelta
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename
import shelve
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this to a more secure key

app.config['UPLOAD_FOLDER'] = 'static/upload'  
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'} 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        image = request.form['image']
        seedplant = request.form['seedplant']

        with shelve.open('products.db') as db:
            product_id = str(len(db))
            db[product_id] = {'name': name, 'price': price, 'stock': stock, 'image': image, 'seedplant': seedplant}

        return redirect('/shopping')  

    return render_template('admin.html')


@app.route('/shopping')
def shopping():
    products = {}
    with shelve.open('products.db') as db:
        for id in db.keys():
            products[id] = db[id]

    return render_template('shopping.html', products=products)

@app.route('/addtocart/<item>')
def addtocart(item):
    userid = str(1)
    with shelve.open('checkout.db') as db:
        cart = []
        if userid in db:
            cart = db[userid]

        cart.append(item)
        db[userid] = cart
    return redirect('/checkout')

@app.route('/checkout')
def check():
    userid = str(1)
    products = []
    cart = []
    with shelve.open('checkout.db') as db:
        if userid in db:
            cart = db[userid]

    with shelve.open('products.db') as db:
        for item in cart:
            products.append(db[item])

    return render_template('checkout.html', products=products)

# Shelve file for data storage
SHELVE_FILE = 'claw_machine_data.shelve'

class ClawMachine:
    def __init__(self):
        self.last_play_key = 'last_play'
        self.play_frequency = timedelta(hours=24)

    def can_play(self):
        if self.last_play_key in session and datetime.now() - session[self.last_play_key] < self.play_frequency:
            raise PermissionError('You can only play once every 24 hours!')
        return True

    def play(self):
        if self.can_play():
            # Simulate the claw machine game
            user_wins = random.choice([True, False])
            # Update the last play time
            session[self.last_play_key] = datetime.now()
            return user_wins

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/play')
def play_game():
    claw_machine = ClawMachine()

    try:
        if claw_machine.play():
            flash('Congratulations! You won a prize!', 'success')
        else:
            flash('Sorry, you didn\'t win this time. Try again tomorrow!', 'info')
    except PermissionError as e:
        flash(str(e), 'danger')

    return redirect(url_for('home'))

@app.route('/claw_machine')
def claw_machine():
    return render_template('claw_machine.html')

def getLoginDetails():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT userId, firstName FROM users WHERE email = ?", (session['email'], ))
            userId, firstName = cur.fetchone()
            cur.execute("SELECT count(productId) FROM kart WHERE userId = ?", (userId, ))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, firstName, noOfItems)

# @app.route("/")
# def root():
#     loggedIn, firstName, noOfItems = getLoginDetails()
#     with sqlite3.connect('database.db') as conn:
#         cur = conn.cursor()
#         cur.execute('SELECT productId, name, price, description, image, stock FROM products')
#         itemData = cur.fetchall()
#     itemData = parse(itemData)   
#     return render_template('home.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)





@app.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    return render_template("profileHome.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = ?", (session['email'], ))
        profileData = cur.fetchone()
    conn.close()
    return render_template("editProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)   

@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId, password FROM users WHERE email = ?", (session['email'], ))
            userId, password = cur.fetchone()
            if (password == oldPassword):
                try:
                    cur.execute("UPDATE users SET password = ? WHERE userId = ?", (newPassword, userId))
                    conn.commit()
                    msg="Changed successfully"
                except:
                    conn.rollback()
                    msg = "Failed"
                return render_template("changePassword.html", msg=msg)
            else:
                msg = "Wrong password"
        conn.close()
        return render_template("changePassword.html", msg=msg)
    else:
        return render_template("changePassword.html")  

@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        with sqlite3.connect('database.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute('UPDATE users SET firstName = ?, lastName = ?, address1 = ?, address2 = ?, zipcode = ?, city = ?, state = ?, country = ?, phone = ? WHERE email = ?', (firstName, lastName, address1, address2, zipcode, city, state, country, phone, email))

                    con.commit()
                    msg = "Saved Successfully"
                except:
                    con.rollback()
                    msg = "Error occured"
        con.close()
        return redirect(url_for('editProfile')) 
    
@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)
        
@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))

def is_valid(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM users')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data    
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']

        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO users (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, address1, address2, zipcode, city, state, country, phone))

                con.commit()

                msg = "Registered Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return render_template("login.html", error=msg)

@app.route("/registerationForm")
def registrationForm():
    return render_template("register.html")

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

@app.route('/cart', methods = ['GET', 'POST'])
def checkout():
    form = CreateCheckoutForm(request.form)
    if request.method == "POST" and form.validate():
        chckoutinfo_dict = {}
        db = shelve.open('chckoutinfo.db', 'c')

        try:
            chckoutinfo_dict = db['Chckoutinfo']
        except:
            print('Error in retrieving Chckoutinfo from chckoutinfo.db')

        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y, %H:%M:%S")

        chckoutinfo = checkoutinfo.CheckoutInfo(
            name=form.name.data, 
            address=form.address.data, 
            card_number=form.card_number.data, 
            exp_month=form.exp_month.data, 
            exp_year=form.exp_year.data, 
            cvv=form.cvv.data, 
            date=date_time)
        chckoutinfo_dict[chckoutinfo.get_info_id()] = chckoutinfo
        db['Chckoutinfo'] = chckoutinfo_dict
        
        #Test codes
        # chckoutinfo_dict = db['Chckoutinfo']
        # chckoutinfo = chckoutinfo_dict[chckoutinfo.get_info_id()]
        # print(chckoutinfo.get_name(),"was stored in chckoutinfo.db successfully with info_id ==", chckoutinfo.get_info_id())

        db.close()
        return redirect(url_for('checkout'))
    return render_template('checkout.html', form=form)

@app.route('/retrieveInfo')
def retrieve_Info():
    chckoutinfo_dict = {}
    db = shelve.open('chckoutinfo.db', 'r')
    chckoutinfo_dict = db['Chckoutinfo']
    db.close()

    chckoutinfo_list = []
    for key in chckoutinfo_dict:
        chckoutinfo = chckoutinfo_dict.get(key)
        chckoutinfo_list.append(chckoutinfo)
    
        print(chckoutinfo.get_date())
    return render_template("retrieveInfo.html", count=len(chckoutinfo_list), chckoutinfo_list=chckoutinfo_list)

@app.route('/updateInfo/<int:id>/', methods=['GET', 'POST'])
def update_info(id):
    update_info_form = CreateCheckoutForm(request.form)
    if request.method == "POST" and update_info_form.validate():
        chckoutinfo_dict = {}
        db = shelve.open('chckoutinfo.db', 'w')
        chckoutinfo_dict = db['Chckoutinfo']

        chckoutinfo = chckoutinfo_dict.get(id)
        chckoutinfo.set_name(update_info_form.name.data)
        chckoutinfo.set_address(update_info_form.address.data)
        chckoutinfo.set_card_number(update_info_form.card_number.data)
        chckoutinfo.set_month(update_info_form.exp_month.data)
        chckoutinfo.set_year(update_info_form.exp_year.data)
        chckoutinfo.set_cvv(update_info_form.cvv.data)

        db['Chckoutinfo'] = chckoutinfo_dict
        db.close()

        return redirect(url_for('retrieve_Info'))
    else:
        chckoutinfo_dict = {}
        db = shelve.open('chckoutinfo.db', 'r')
        chckoutinfo_dict = db['Chckoutinfo']
        db.close()

        chckoutinfo = chckoutinfo_dict.get(id)
        update_info_form.name.data = chckoutinfo.get_name()
        update_info_form.address.data = chckoutinfo.get_address()
        update_info_form.card_number.data = chckoutinfo.get_card_number()
        update_info_form.exp_month.data = chckoutinfo.get_exp_month()
        update_info_form.exp_year.data = chckoutinfo.get_exp_year()
        update_info_form.cvv.data = chckoutinfo.get_cvv()

        return render_template('updateInfo.html', form=update_info_form)
    
@app.route('/deleteInfo/<int:id>', methods=['POST'])
def delete_info(id):
    chckoutinfo_dict = {}
    db = shelve.open('chckoutinfo.db', 'w')
    chckoutinfo_dict = db['Chckoutinfo']

    chckoutinfo_dict.pop(id)

    db['Chckoutinfo'] = chckoutinfo_dict
    db.close()

    return redirect(url_for('retrieve_Info'))

@app.route('/planttracker')
def plant_tracker():
    chckoutinfo_dict = {}
    db = shelve.open('chckoutinfo.db', 'r')
    chckoutinfo_dict = db['Chckoutinfo']
    db.close()

    chckoutinfo_list = []
    for key in chckoutinfo_dict:
        chckoutinfo = chckoutinfo_dict.get(key)
        chckoutinfo_list.append(chckoutinfo)

    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y, %H:%M:%S")

    date1 = datetime(2022, 1, 1)
    date2 = datetime(2022, 12, 31)
    difference = date2 - date1
    diff_wks = difference.days/7

    date_1 = chckoutinfo.get_date()
    print(date_1)
    conv_date1 = datetime.strptime(date_1, '%m/%d/%Y, %H:%M:%S')
    date_2 = datetime.now()
    diff_dys = date_2 - conv_date1

    

    return render_template('planttracker.html',count=len(chckoutinfo_list), chckoutinfo_list = chckoutinfo_list, date_time=date_time, difference=difference, diff_wks=diff_wks, date_1=date_1, now=now, diff_dys=diff_dys)

if __name__ == '__main__':
    app.run(debug=True)

# from flask import Flask, render_template, session, redirect, url_for, flash
# from datetime import datetime, timedelta
# import random
# import shelve

# app = Flask(__name__)
# app.secret_key = 'supersecretkey'  # Change this to a more secure key

# # Shelve file for data storage
# SHELVE_FILE = 'claw_machine_data.shelve'

# class ClawMachine:
#     def __init__(self):
#         self.last_play_key = 'last_play'
#         self.play_frequency = timedelta(hours=24)
#         self.max_daily_plays = 3  # Maximum allowed plays per day
    
#     def can_play(self):
#         if self.last_play_key in session:
#             plays_today = session.get('plays_today', 0)
#             if plays_today >= self.max_daily_plays:
#                 raise PermissionError('You have reached the maximum number of plays for today!')
            
#             # Increment the plays_today counter
#             session['plays_today'] = plays_today + 1

#             if datetime.now() - session[self.last_play_key] < self.play_frequency:
#                 raise PermissionError('You can only play once every 24 hours!')
#         else:
#             # First play of the day, reset the plays_today counter
#             session['plays_today'] = 1

#         return True

#     def play(self):
#         if self.can_play():
#             # Simulate the claw machine game
#             user_wins = random.choice([True, False])
            
#             # Save the user's result to the database
#             user_data = shelve.open(SHELVE_FILE)
#             try:
#                 if 'user_wins' not in user_data:
#                     user_data['user_wins'] = {}

#                 play_number = session['plays_today']
#                 user_data['user_wins'][f'Try {play_number}'] = 'Win' if user_wins else 'Lose'

#             finally:
#                 user_data.close()

#             # Update the last play time
#             session[self.last_play_key] = datetime.now()
#             return user_wins

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/play')
# def play_game():
#     claw_machine = ClawMachine()

#     try:
#         if claw_machine.play():
#             flash('Congratulations! You won a prize!', 'success')
#         else:
#             flash('Sorry, you didn\'t win this time. Try again tomorrow!', 'info')
#     except PermissionError as e:
#         flash(str(e), 'danger')

#     return redirect(url_for('index'))

# if __name__ == '__main__':
#     app.run(debug=True)