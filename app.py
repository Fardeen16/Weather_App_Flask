import requests
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy 
from geopy.geocoders import Nominatim

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisissecret'

geolocator = Nominatim(user_agent="MyApp")
db = SQLAlchemy(app)
#db.create_all()

api_key = 'b327bcda2157b999d7400a66817be51e'
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=metric&appid=b327bcda2157b999d7400a66817be51e'
    r = requests.get(url).json()
    return r

def future_weather(lat, lon):
    url = f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={api_key}'
    s=requests.get(url).json()
    return s

@app.route('/')
def index_get():
    cities = City.query.all()
    weather_data = []

    for city in cities:

        r = get_weather_data(city.name)

        weather = {
            'city' : city.name,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
        }
        weather_data.append(weather)

    loc = geolocator.geocode(cities[0].name)
    lati, longi = loc.latitude, loc.longitude
    s=future_weather(lati, longi)
    future=[]
    i=0
    xyz = s['list'][i]['dt_txt']
    while len(future)!= 5:
        to_compare = s['list'][i+1]['dt_txt']
        if xyz[9] != to_compare[9]:
            ans={
                'temp_min' : s['list'][i]['main']['temp_min'],
                'temp_max' : s['list'][i]['main']['temp_max']
            }
            future.append(ans)
        else:
            pass
        i+=1
        #for k,v in s.weather:
    print(future)
    

    return render_template('weather.html', weather_data=weather_data, future=future)



@app.route('/', methods=['POST'])
def index_post():
    err_msg = ''
    new_city = request.form.get('city')
    
    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()
        if not existing_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err_msg = 'City does not exist in the world!'
        else:
            err_msg = 'City already exists!'
    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City added successfully!', 'success')

    return redirect(url_for('index_get'))  


@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()

    flash(f'Successfully deleted {city.name}', 'success')
    return redirect(url_for('index_get'))