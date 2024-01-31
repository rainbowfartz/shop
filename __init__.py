from flask import *
from Forms import CreateCheckoutForm
import shelve, checkoutinfo
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from itertools import product
import shelve
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this to a more secure key

app.config['UPLOAD_FOLDER'] = 'static/upload'  
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'} 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/game')
def game():
    return render_template('index1.html')

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
            db[product_id] = {"id": int(product_id)+1, 'name': name, 'price': price, 'stock': stock, 'image': image, 'seedplant': seedplant}

        return redirect('/shopping')  

    return render_template('admin.html')


@app.route('/shopping')
def shopping():
    products = {}
    with shelve.open('products.db') as db:
        for id in db.keys():
            products[id] = db[id]

    
    return render_template('shopping.html', products=products)

# @app.route('/deleteCart/<int:id>', methods=['POST', 'GET'])
# def delete_cart(id):
#     userid = str(1)
#     with shelve.open('checkout.db', 'w') as db:
#         cart = []
#         if userid in db:
#             cart = db[userid]
#         cart.pop(id)
#         db[userid] = cart
#     db.close()

#     return redirect(url_for('checkout'))

@app.route('/addtocart/<item>', methods=['POST'])
def addtocart(item):
    userid = str(1)

    with shelve.open('checkout.db', writeback=True) as db:
        cart = db.get(userid, [])

        print(request)
        print(request.form)
        amount = request.form["amount"]

        cart.append({'id':item, 'amount': amount})
        db[userid] = cart

    return redirect('/cart')

# @app.route('/addtocart/<item>', methods=['POST'])
# def addtocart(item):
#     userid = str(1)
    
#     with shelve.open('checkout.db') as db:
#         cart = []
#         if userid in db:
#             cart = db[userid]

#         cart.append(item)
#         db[userid] = cart
#     return redirect('/cart')

# @app.route('/checkout')
# def check():
#     userid = str(1)
#     products = []
#     cart = []
#     with shelve.open('checkout.db') as db:
#         if userid in db:
#             cart = db[userid]

#     with shelve.open('products.db') as db:
#         for item in cart:
#             products.append(db[item])

#     return render_template('checkout.html', products=products)

# Shelve file for data storage
SHELVE_FILE = 'claw_machine_data.shelve'

class ClawMachine:
    def __init__(self):
        self.last_play_key = 'last_play'
        self.play_frequency = timedelta(hours=24)
        self.max_daily_plays = 3  # Maximum allowed plays per day
    
    def can_play(self):
        if self.last_play_key in session:
            plays_today = session.get('plays_today', 0)
            if plays_today >= self.max_daily_plays:
                raise PermissionError('You have reached the maximum number of plays for today!')
            
            # Increment the plays_today counter
            session['plays_today'] = plays_today + 1

            if datetime.now() - session[self.last_play_key] < self.play_frequency:
                raise PermissionError('You can only play once every 24 hours!')
        else:
            # First play of the day, reset the plays_today counter
            session['plays_today'] = 1

        return True

    def play(self):
        if self.can_play():
            # Simulate the claw machine game
            user_wins = random.choice([True, False])
            
            # Save the user's result to the database
            user_data = shelve.open(SHELVE_FILE)
            try:
                if 'user_wins' not in user_data:
                    user_data['user_wins'] = {}

                play_number = session['plays_today']
                user_data['user_wins'][f'Try {play_number}'] = 'Win' if user_wins else 'Lose'

            finally:
                user_data.close()

            # Update the last play time
            session[self.last_play_key] = datetime.now()
            return user_wins

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

    return redirect(url_for('index'))




# @app.route('/checkout')
# def check():
#     userid = str(1)
#     products = []
#     cart = []
#     with shelve.open('checkout.db') as db:
#         if userid in db:
#             cart = db[userid]

#     with shelve.open('products.db') as db:
#         for item in cart:
#             products.append(db[item])

#     return render_template('checkout.html', products=products)

@app.route('/cart', methods = ['GET', 'POST'])
def checkout():
    userid = str(1)
    products = []
    cart = []
    with shelve.open('checkout.db') as db:
        if userid in db:
            cart = db[userid]
    with shelve.open('products.db') as db:
        for item in cart:
            product = db[item['id']]
            product['amount'] = item['amount']
            products.append(product)
            
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
    return render_template('checkout.html', form=form, products=products)

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
    
@app.route('/deleteInfo/<int:id>', methods=["POST"])
def delete_info(id):
    chckoutinfo_dict = {}
    db = shelve.open('chckoutinfo.db', 'w')
    chckoutinfo_dict = db['Chckoutinfo']


    chckoutinfo_dict.pop(id)

    db['Chckoutinfo'] = chckoutinfo_dict
    db.close()

    return redirect(url_for('retrieve_Info'))

    userid = str(1)
    products = []
    cart = []
    with shelve.open('checkout.db') as db:
        if userid in db:
            cart = db[userid]
    with shelve.open('products.db') as db:
        for item in cart:
            products.append(db[item])

@app.route('/deleteCart/<int:id>', methods=['POST', 'GET'])
def delete_cart(id):
    userid = str(1)
    with shelve.open('checkout.db', 'w') as db:
        cart = []
        if userid in db:
            cart = db[userid]
        cart.pop(id)
        db[userid] = cart
    db.close()

    return redirect(url_for('checkout'))


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

class Parcel:
    def __init__(self, code, location, latitude=None, longitude=None):
        self.code = code
        self.location = location
        self.latitude = latitude
        self.longitude = longitude

with shelve.open('parcels.db', writeback=True) as shelf:
    if 'parcels' not in shelf:
        shelf['parcels'] = [
            Parcel('123', 'Jurong Ave 6', 1.3561, 103.8010),
            Parcel('456', 'Woodlands Dr 70', 1.3721, 103.8292)
        ]

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        code = request.form['parcel_code']
        currentparcel = None

        with shelve.open('parcels.db') as shelf:
            parcels = shelf.get('parcels', [])
            
            for parcel in parcels:
                if parcel.code == code:
                    currentparcel = parcel

        if currentparcel:
            return render_template('map.html', parcel=currentparcel)
        else:
            return "Parcel not found", 404

    with shelve.open('parcels.db') as shelf:
        parcels = shelf.get('parcels', [])
    return render_template('index.html', parcels=parcels, user_input_code=None)

@app.route('/delete/<code>')  # Changed the endpoint for the delete route
def delete(code):
    with shelve.open('parcels.db', writeback=True) as shelf:
        parcels = shelf.get('parcels', [])
        shelf['parcels'] = [p for p in parcels if p.code != code]

    return redirect(url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        parcel = Parcel(request.form.get('parcelid'), request.form.get('location'), request.form.get('latitude'), request.form.get('longitude'))

        with shelve.open('parcels.db', writeback=True) as shelf:
            parcels = shelf.get('parcels', [])

            parcels.append(parcel)

            shelf['parcels'] = parcels

            redirect(url_for('index'))

    return render_template('addparcel.html')

@app.route('/map', methods=['POST'])
def display_input():
    code = request.form['parcel_code']
    currentparcel = None

    with shelve.open('parcels.db') as shelf:
        parcels = shelf.get('parcels', [])
        
        for parcel in parcels:
            if int(parcel.code) == int(code):
                parcel.latitude = random.randint(127, 142)/100
                parcel.longitude = random.randint(10370, 10390)/100

                parcels[parcels.index(parcel)] = parcel

                currentparcel = parcel
        
        shelf['parcels'] = parcels

    if currentparcel:
        return render_template('map.html', parcel=currentparcel)
    else:
        return "Parcel not found", 404


with shelve.open('parcels.db') as shelf:
    parcels = shelf.get('parcels', [])
    print(parcels)

# @app.route('/clawmachine')
# def claw_machine():
#     return render_template('c')
if __name__ == '__main__':
    app.run(debug=True)
