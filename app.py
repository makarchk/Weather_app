from flask import Flask, request, jsonify, render_template
import requests
from geopy.geocoders import Nominatim

app = Flask(__name__)

API_KEY = 'GF4lLNpCCMD2AoCooLAaH9sG7HtdU8Ss'
geolocator = Nominatim(user_agent='weather_app')

def get_geopos_by_lat_lon(lat, lon):
    geo_url = 'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search'
    params = {
        'apikey': API_KEY,
        'q': f'{lat},{lon}',
    }
    response = requests.get(geo_url, params=params)
    if response.status_code == 200:
        return response.json()['Key'] # str
    return 'Error with geodata'

def get_forecast_by_lat_lon(lat, lon):
    lockey = get_geopos_by_lat_lon(lat, lon)
    if lockey != 'Error with geodata':
        forecast_url = f'http://dataservice.accuweather.com/forecasts/v1/daily/1day/{lockey}'
        params = {
            'apikey': API_KEY,
            'details': True,
            'metric': True,
        }
        response = requests.get(forecast_url, params=params)
        if response.status_code == 200:
            return response.json()
        return 'Error with weather_data'

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        start_city = request.form['start_city']
        end_city = request.form['end_city']

        start_location = geolocator.geocode(start_city)
        end_location = geolocator.geocode(end_city)

        if not start_location or not end_location:
            return render_template('weather_form.html', message='Ошибка: город введен неверно')
        # start lat, lon
        start_lat = start_location.latitude
        start_lon = start_location.longitude
        # end lat, lon
        end_lat = end_location.latitude
        end_lon = end_location.longitude

        data_start = get_forecast_by_lat_lon(start_lat, start_lon)
        data_end = get_forecast_by_lat_lon(end_lat, end_lon)

        if data_start == 'Error with weather_data' or data_end == 'Error with weather_data':
            return render_template('weather_form.html', message='Ошибка: данные о погоде  в городе не найдены')
        # start weather_data
        min_temp_start = data_start['DailyForecasts'][0]['Temperature']['Minimum']['Value']
        max_temp_start = data_start['DailyForecasts'][0]['Temperature']['Maximum']['Value']
        temp_start = int(min_temp_start + max_temp_start) / 2

        humidity_min_start = data_start['DailyForecasts'][0]['Day']['RelativeHumidity']['Minimum']
        humidity_max_start = data_start['DailyForecasts'][0]['Day']['RelativeHumidity']['Maximum']
        humidity_start = int(humidity_min_start + humidity_max_start) / 2

        wind_speed_start = data_start['DailyForecasts'][0]['Day']['Wind']['Speed']['Value']

        rain_prob_start = data_start['DailyForecasts'][0]['Day']['PrecipitationProbability']

        # end weather_data
        min_temp_end = data_end['DailyForecasts'][0]['Temperature']['Minimum']['Value']
        max_temp_end = data_end['DailyForecasts'][0]['Temperature']['Maximum']['Value']
        temp_end = int(min_temp_end + max_temp_end) / 2

        humidity_min_end = data_end['DailyForecasts'][0]['Day']['RelativeHumidity']['Minimum']
        humidity_max_end = data_end['DailyForecasts'][0]['Day']['RelativeHumidity']['Maximum']
        humidity_end = int(humidity_min_end + humidity_max_end) / 2

        wind_speed_end = data_end['DailyForecasts'][0]['Day']['Wind']['Speed']['Value']

        rain_prob_end = data_end['DailyForecasts'][0]['Day']['PrecipitationProbability']

        # check weather condition
        weather_condition_start = check_bad_weather(temp_start, wind_speed_start, rain_prob_start, humidity_start)
        weather_condition_end = check_bad_weather(temp_end, wind_speed_end, rain_prob_end, humidity_end)
        return render_template('weather_form.html',
                                   message=f'Погода в {start_city}: {weather_condition_start}. Погоде в {end_city}: {weather_condition_end}.')


    else:
        # start lat, lon
        start_lat = request.args.get('start_lat', type=float)
        start_lon = request.args.get('start_lon', type=float)
        # end lat, lon
        end_lat = request.args.get('end_lat', type=float)
        end_lon = request.args.get('end_lon', type=float)

        if start_lat is not None and start_lon is not None and end_lat is not None and end_lon is not None:

            data_start = get_forecast_by_lat_lon(start_lat, start_lon)
            data_end = get_forecast_by_lat_lon(end_lat, end_lon)

            if data_start == 'Error with weather_data' and data_end == 'Error with weather_data':
                return render_template('weather_form.html', message='Ошибка: данные о погоде не найдены.')
            # start weather_data
            min_temp_start = data_start['DailyForecasts'][0]['Temperature']['Minimum']['Value']
            max_temp_start = data_start['DailyForecasts'][0]['Temperature']['Maximum']['Value']
            temp_start = int(min_temp_start + max_temp_start) / 2

            humidity_min_start = data_start['DailyForecasts'][0]['Day']['RelativeHumidity']['Minimum']
            humidity_max_start = data_start['DailyForecasts'][0]['Day']['RelativeHumidity']['Maximum']
            humidity_start = int(humidity_min_start + humidity_max_start) / 2

            wind_speed_start = data_start['DailyForecasts'][0]['Day']['Wind']['Speed']['Value']

            rain_prob_start = data_start['DailyForecasts'][0]['Day']['PrecipitationProbability']

            # end weather_data
            min_temp_end = data_end['DailyForecasts'][0]['Temperature']['Minimum']['Value']
            max_temp_end = data_end['DailyForecasts'][0]['Temperature']['Maximum']['Value']
            temp_end = int(min_temp_end + max_temp_end) / 2

            humidity_min_end = data_end['DailyForecasts'][0]['Day']['RelativeHumidity']['Minimum']
            humidity_max_end = data_end['DailyForecasts'][0]['Day']['RelativeHumidity']['Maximum']
            humidity_end = int(humidity_min_end + humidity_max_end) / 2

            wind_speed_end = data_end['DailyForecasts'][0]['Day']['Wind']['Speed']['Value']

            rain_prob_end = data_end['DailyForecasts'][0]['Day']['PrecipitationProbability']

            # check weather condition
            weather_condition_start = check_bad_weather(temp_start, wind_speed_start, rain_prob_start, humidity_start)
            weather_condition_end = check_bad_weather(temp_end, wind_speed_end, rain_prob_end, humidity_end)

            return jsonify({ # в словарях сначала идут стартовые данные, а затем данные в конце маршрута
                'Temperature': {'Start': temp_start, 'End': temp_end},
                'Humidity': {'Start': humidity_start, 'End': humidity_end},
                'Wind speed': {'Start': wind_speed_start, 'End': wind_speed_end},
                'Rain probability': {'Start': rain_prob_start, 'End': rain_prob_end},
                'Weather condition': {'Start': weather_condition_start, 'End': weather_condition_end}
            })
    return render_template('weather_form.html')


def check_bad_weather(temperature, wind_speed, rain_probability, humidity):
    if temperature < -10 or temperature > 35:
        return 'лучше не вылезать на улицу'
    if wind_speed > 50:
        return 'будет лучше посидеть дома'
    if rain_probability > 75:
        return 'лучше взять с собой зонт'
    if humidity > 95:
        return 'на улице душно, но выйти можно, если очень нужно'
    return 'норм погода'



if __name__ == '__main__':
    app.run(debug=True)