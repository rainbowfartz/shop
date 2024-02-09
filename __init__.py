from flask import *
from Forms import CreateCheckoutForm
import shelve, checkoutinfo
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from itertools import product
import shelve
import random
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this to a more secure key

app.config['UPLOAD_FOLDER'] = 'static/upload'  
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'} 
plant = {0:'static/images/sprout.png', 1:'static/images/sprout.png', 2:'static/images/sprout.png', 3:'static/images/seeding.png', 4:'static/images/seeding.png', 5:'static/images/seeding.png', 6:'static/images/vegetative.png', 7:'static/images/budding.png', 8:'static/images/budding.png', 10:'static/images/flowering.png', 11:'static/images/flowering.png', 12:'static/images/ripening.png', 13:'static/images/ripening.png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        seedplant = request.form['seedplant']

        image = request.files['image']

        with shelve.open('products.db') as db:
            product_id = str(len(db))
            db[product_id] = {"id": int(product_id)+1, 'name': name, 'price': price, 'stock': stock, 'seedplant': seedplant}

            image.save(os.path.join('static/productimage', product_id))

        return redirect('/shopping')  

    return render_template('admin.html')


@app.route('/shopping')
def shopping():
    products = {}
    with shelve.open('products.db') as db:
        for id in db.keys():
            print(id)
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

    with shelve.open('checkout.db', writeback=True) as db1:
        with shelve.open('Seed.db', writeback=True) as db2:
            cart = db1.get(userid, [])
            seed = db2.get(userid, [])

            print(request)
            print(request.form)
            amount = request.form.get("amount")
            additional_value = request.form.get("seedplant")

            if additional_value == "seed":
                # Add to both databases
                cart.append({'id': item, 'amount': amount})
                seed.append({'id': item, 'amount': amount})
            else:
                # Add only to db2
                cart.append({'id': item, 'amount': amount})

            db1[userid] = cart
            db2[userid] = seed

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
            product = db[str(item['id'])]
            product['amount'] = str(item['amount'])  # Convert to string
            product['total_price'] = "{:.2f}".format(float(item['amount']) * float(product['price']))
            products.append(product)
    form = CreateCheckoutForm(request.form)

    if request.method == "POST" and form.validate():
        chckoutinfo_dict = {}
        seed = []
        with shelve.open('chckoutinfo.db', writeback=True) as chckoutinfo_db:
            try:
                chckoutinfo_dict = db['Chckoutinfo']
            except:
                print('Error in retrieving Chckoutinfo from chckoutinfo.db')

    
            with shelve.open('checkout.db') as checkout_db:
                item_info = checkout_db.get("seedplant")
                if item_info == "seed":
                    seed.append(item_info)

            now = datetime.now()
            date_time = now.strftime("%d/%m/%Y, %H:%M:%S")

            chckoutinfo = checkoutinfo.CheckoutInfo(
                name=form.name.data, 
                address=form.address.data, 
                card_number=form.card_number.data, 
                exp_month=form.exp_month.data, 
                exp_year=form.exp_year.data, 
                cvv=form.cvv.data, 
                date=date_time,
                difference=0,
                seed=seed)
            
            chckoutinfo_id = chckoutinfo.get_info_id()  # Get ID of the new checkout info
        
            # Check if the ID already exists, if so, update it instead of adding a new entry
            if chckoutinfo_id in chckoutinfo_dict:
                # Update the existing entry
                chckoutinfo_dict[chckoutinfo_id].update(chckoutinfo.__dict__)
            else:
                # Add the new entry
                chckoutinfo_dict[chckoutinfo_id] = chckoutinfo

            chckoutinfo_db['Chckoutinfo'] = chckoutinfo_dict    

        return redirect(url_for('checkout'))
        
        #Test codes
        # chckoutinfo_dict = db['Chckoutinfo']
        # chckoutinfo = chckoutinfo_dict[chckoutinfo.get_info_id()]
        # print(chckoutinfo.get_name(),"was stored in chckoutinfo.db successfully with info_id ==", chckoutinfo.get_info_id())

        
    
    #     chckoutinfo_dict = {}
#     db = shelve.open('chckoutinfo.db', 'r')
#     chckoutinfo_dict = db['Chckoutinfo']
#     db.close()

#     chckoutinfo_list = []
#     for key in chckoutinfo_dict:
#         chckoutinfo = chckoutinfo_dict.get(key)
#         chckoutinfo_list.append(chckoutinfo)
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
        print(chckoutinfo_list)
    pic_list = []
    for info in chckoutinfo_list:

        date_format = '%d/%m/%Y, %H:%M:%S'
        date_obj = datetime.strptime(info.get_date(), date_format)
        difference2 = datetime.now() - date_obj
        weeks = difference2.days/7
        info.set_difference(round(weeks))
        print(chckoutinfo.get_difference())
        pic_image = plant[round(weeks)]
        parts = pic_image.split('/')
        names = parts[2].split('.')
        stage = names[0]
        pic_list.append((pic_image, stage))
        # print(chckoutinfo.get_date())

    return render_template("retrieveInfo.html", count=len(chckoutinfo_list), chckoutinfo_list=chckoutinfo_list, pic_list=pic_list)

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
        
    pic_list = []
    for info in chckoutinfo_list:

        date_format = '%d/%m/%Y, %H:%M:%S'
        date_obj = datetime.strptime(info.get_date(), date_format)
        difference2 = datetime.now() - date_obj
        weeks = difference2.days/7
        info.set_difference(round(weeks))
        print(chckoutinfo.get_difference())
        pic_image = plant[round(weeks)]
        parts = pic_image.split('/')
        names = parts[2].split('.')
        stage = names[0]
        pic_list.append((pic_image, stage))



    return render_template('planttracker.html',count=len(chckoutinfo_list), chckoutinfo_list = chckoutinfo_list, pic_list=pic_list)

# @app.route('/planttracker')
# def plant_tracker():
#     chckoutinfo_dict = {}
#     db = shelve.open('chckoutinfo.db', 'r')
#     chckoutinfo_dict = db['Chckoutinfo']
#     db.close()

#     chckoutinfo_list = []
#     for key in chckoutinfo_dict:
#         chckoutinfo = chckoutinfo_dict.get(key)
#         chckoutinfo_list.append(chckoutinfo)



#     return render_template('planttracker.html',count=len(chckoutinfo_list), chckoutinfo_list = chckoutinfo_list)

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
            Parcel('456', 'Woodlands Dr 70', 1.3721, 103.8292),
            Parcel('789', 'Ang Mo Kio Ave 80',  1.369115, 103.845436)
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

            
@app.route('/game')
def game():
    userid = 1
    plays = 0

    with shelve.open('clawmachine.db') as clawmachinedb:
        data = clawmachinedb.get(str(userid), {'plays':0,'lastplayed': datetime.now()})
        plays = data['plays']
        lastplayed = data['lastplayed']

    tries = 3-plays
    print(datetime.now(), lastplayed)
    print(type(datetime.now()), type(lastplayed))
    print(datetime.now() - lastplayed)

    if datetime.now() - lastplayed > timedelta(seconds=1):
        tries = 3
        with shelve.open('clawmachine.db') as clawmachinedb:
            clawmachinedb[str(userid)] = {'plays':0, 'lastplayed':datetime.now()}

    return render_template('index1.html', tries=tries)

@app.route('/play')
def play_game():
    userid = 1

    with shelve.open('clawmachine.db') as clawmachinedb:
        data = clawmachinedb.get(str(userid), {'plays':0,'lastplayed': datetime.now()})
        plays = data['plays']
        plays += 1
        clawmachinedb[str(userid)] = {'plays':plays, 'lastplayed':datetime.now()}

    return redirect(url_for('game'))
       

if __name__ == '__main__':
    app.run(debug=True)
