from flask import Flask, render_template, request, redirect, url_for
import shelve

class Parcel:
    def __init__(self, code, location, latitude=None, longitude=None):
        self.code = code
        self.location = location
        self.latitude = latitude
        self.longitude = longitude

app = Flask(__name__)

with shelve.open('parcels.db', writeback=True) as shelf:
    if 'parcels' not in shelf:
        shelf['parcels'] = [
            Parcel('123', 'Jurong Ave 6', 1.3561, 103.8010),
            Parcel('456', 'Woodlands Dr 70', 1.3721, 103.8292)
        ]

@app.route('/')
def home():
    return render_template('form.html')

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
            if parcel.code == code:
                currentparcel = parcel

    if currentparcel:
        return render_template('map.html', parcel=currentparcel)
    else:
        return "Parcel not found", 404


with shelve.open('parcels.db') as shelf:
    parcels = shelf.get('parcels', [])
    print(parcels)


if __name__ == '__main__':
    app.run(debug=True)

