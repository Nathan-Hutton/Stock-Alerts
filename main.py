import requests
from dotenv import load_dotenv
import os
from twilio.rest import Client

load_dotenv('/Users/natha/PycharmProjects/info.env')

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

stock_params = {
    'function':'TIME_SERIES_DAILY',
    'symbol':STOCK_NAME,
    'apikey':os.getenv('STOCK_APPID')
}

response = requests.get(STOCK_ENDPOINT, params=stock_params)
response.raise_for_status()
stock_data = response.json()
daily_data = stock_data['Time Series (Daily)']
daily_data_list = [data for (key, data) in daily_data.items()]
yesterday_close = float(daily_data_list[0]['4. close'])

day_before_close = float(daily_data_list[1]['4. close'])

difference = yesterday_close-day_before_close
percentage = difference/yesterday_close * 100
print(percentage)
if abs(percentage) >= 5:
    news_parameters = {
        'apIKey': os.getenv('NEWS_APPID'),
        'qInTitle': COMPANY_NAME,
    }
    news_response = requests.get(NEWS_ENDPOINT, params=news_parameters)
    articles = news_response.json()['articles']
    first_three = articles[:3]
    if percentage > 0:
        first_three = [
            f"TSLA: 🔺{round(percentage)}\nHeadline: {article['title']}. \nBrief: {article['description']}" for
            article in first_three]
    elif percentage < 0:
        first_three = [
            f"TSLA: 🔻{round(percentage)}\nHeadline: {article['title']}. \nBrief: {article['description']}" for
            article in first_three]

    sid = os.getenv('TWILIO_SID')
    auth_token = os.getenv('OWM_AUTH_TOKEN')
    recipient_phone = os.getenv('TWILIO_RECEIVER')
    sender_phone = os.getenv('TWILIO_SENDER')

    client = Client(sid, auth_token)

    for article in first_three:
        message = client.messages \
            .create(
            body=article,
            from_=sender_phone,
            to=recipient_phone
        )
        print(message.status)

"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

