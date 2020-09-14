from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import datetime
from datetime import timedelta
import pandas_datareader.data as web
import pandas as pd
import json

app = Flask(__name__)
PORT = 5000

testy = 12

end = datetime.datetime.now()
start = end - timedelta(27)
#creating dataframe of SPY prices
df = web.DataReader('SPY', 'yahoo', start, end)
df = df.reset_index()

#list of SPY prices
spy_prices = list(df.Open.round(2))

#list of dates corresponding to SPY prices
dates = list(df.Date.astype(str))

#removing '2020-' from datetime string
for item in range(len(dates)):
    dates[item] = dates[item][5:]

app.config.from_object(__name__)

def get_outlook(time_index):

    url = 'https://stocks.comment.ai/' # WSB comment data
    html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, "lxml")
    sentiment_circles = soup.find_all('div', attrs={'class':'col-sm-2'})[1:5] #grab 4 sentiment values provided

    sentiment = []
    labels = []
    for item in range(len(sentiment_circles)):
        sentiment_circles[item] = str(sentiment_circles[item])
        index = sentiment_circles[item].find('data-content') + len('data-content') + 2 #bad code to grab indices of percentages
        splits = sentiment_circles[item][index:index+10].split('%')
        sentiment.append(splits[0])
        labels.append(splits[1])

    #time_index = 2 #0-3. 10min, 1 hour, 6 hour, 24 hour
    #print('timeindex', time_index)

    day_s = sentiment[time_index], labels[time_index] #tuple of sentiment/labels for time_index

    if 'bear' in str(day_s):
        bleak = f'Stock outlook appears bleak. Current (bearish) Sentiment: {day_s[0]} %'
        if float(day_s[0]) > 80:
            return f'{bleak}. WSB predicting a recession.'
        elif float(day_s[0]) > 60:
            return f'{bleak}. Load up on puts!'
        else:
            return bleak 
    else:
        positive = f'Stock outlook appears good. Current (bullish) Sentiment: {day_s[0]} %'
        if float(day_s[0]) > 80:
            return f'{positive}. Market likely to skyrocket.'
        elif float(day_s[0]) > 60:
            return f'{positive}. Grab some calls for a quick buck.'
        else:
            return positive

@app.route('/')
def select_time():
    return render_template('home.html')

@app.route('/ten')
def ten():
    print(dates)
    print(spy_prices)
    sentiment = get_outlook(0)
    time = '10-Minute'
    if 'bleak' in sentiment:
        return render_template('index_bleak.html', sentiment=sentiment, time=time, spy_prices=spy_prices, dates=dates)
    else:
        return render_template('index.html', sentiment=sentiment, time=time, spy_prices=spy_prices, dates=dates)

@app.route('/hour')
def hour():
    sentiment = get_outlook(1)
    time = '1-Hour'
    if 'bleak' in sentiment:
        return render_template('index_bleak.html', sentiment=sentiment, time=time, spy_prices=spy_prices, dates=dates)
    else:
        return render_template('index.html', sentiment=sentiment, time=time, spy_prices=spy_prices, dates=dates)

@app.route('/six')
def six_hour():
    sentiment = get_outlook(2)
    time = '6-Hour'
    if 'bleak' in sentiment:
        return render_template('index_bleak.html', sentiment=sentiment, time=time, spy_prices=spy_prices, dates=dates)
    else:
        return render_template('index.html', sentiment=sentiment, time=time, spy_prices=spy_prices, dates=dates)

@app.route('/day')
def day():
    sentiment = get_outlook(3)
    time = '1-Day'
    if 'bleak' in sentiment:
        return render_template('index_bleak.html', sentiment=sentiment, time=time, spy_prices=spy_prices, dates=dates)
    else:
        return render_template('index.html', sentiment=sentiment, time=time, spy_prices=spy_prices, dates=dates)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=PORT)
