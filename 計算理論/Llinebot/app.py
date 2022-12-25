from flask import Flask
from env import *
import os
import sys
from flask import request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from train import *
from linebot.models import *
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
load_dotenv()

USER_ID = {}
app = Flask(__name__)
# set the channel access token and channel secret
linebot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.route('/callback',  methods=['POST'])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# if receive the user message
train = Find_the_train()

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.source.user_id not in USER_ID:
        USER_ID[event.source.user_id] = Find_the_train()
        train = USER_ID[event.source.user_id]
        train.mode = 1
    else:
        train = USER_ID[event.source.user_id]
    
    try:
        message_text = event.message.text
        if message_text == 'back':
            train.mode = 1
            train.driver.quit()
            linebot_api.reply_message(
                event.reply_token, TextSendMessage(text='回到起始狀態\n有效輸入:\n[查詢]\n[訂位連結]\n或者按左下角的"+"定位'))

        elif message_text == "查詢" and train.mode == 1:
            train.cities = set()
            train.stations = set()
            train.__init__
            train.find_the_web()
            reply = "縣市:\n"
            # cities name in doc
            for city in train.doc("#mainline > div:nth-child(1) > ul > li:nth-child(n+2)").items():
                train.cities.add(city.text())
                reply += city.text()
                reply += "\n"
            train.count = 2
            # cities name in doc
            for city in train.doc("#mainline > div:nth-child(1) > ul > li:nth-child(n+2)").items():
                train.temp_city_id = train.doc(
                    "#mainline > div:nth-child(1) > ul > li:nth-child(" + str(train.count) + ") > button").attr("data-type")
                train.citiesSort_startStation[city.text()] = train.count
                train.cities_startStation[city.text(
                )] = train.temp_city_id  # get city id
                train.count += 1
            reply += "請輸入出發縣市:"
            train.mode = 2
            linebot_api.reply_message(
                event.reply_token, TextSendMessage(text=reply))
        elif message_text in train.cities and train.mode == 2:
            train.mode = 3
            train.input_startStationCity = message_text
            train.find_the_start_city()
            reply = "站名:\n"
            for station in train.doc("#{0} > ul > li:nth-child(n+1) > button".format(train.cities_startStation[train.input_startStationCity])).items():
                train.stations.add(station.text())
                reply += station.text()
                reply += "\n"
            train.stationCount = 1
            for station in train.doc("#{0} > ul > li:nth-child(n+1) > button".format(train.cities_startStation[train.input_startStationCity])).items():
                train.StationSort_startStation[station.text(
                )] = train.stationCount
                train.stationCount += 1
            reply += "請輸入出發站:"
            linebot_api.reply_message(
                event.reply_token, TextSendMessage(text=reply))
        elif message_text in train.stations and train.mode == 3:
            train.mode = 4
            train.input_startStation = message_text
            train.find_the_start_station()
            linebot_api.reply_message(
                event.reply_token, TextSendMessage(text='請輸入抵達縣市: '))
        elif message_text in train.cities and train.mode == 4:
            train.stations.clear()
            train.mode = 5
            train.input_endStationCity = message_text
            train.find_the_end_city()
            reply = "站名:\n"
            for station in train.doc("#{0} > ul > li:nth-child(n+1) > button".format(train.cities_startStation[train.input_endStationCity])).items():
                train.stations.add(station.text())
                reply += station.text()
                reply += "\n"
            train.endStationCount = 1
            for station in train.doc("#{0} > ul > li:nth-child(n+1) > button".format(train.cities_startStation[train.input_endStationCity])).items():
                train.stationSort_endStation[station.text(
                )] = train.endStationCount
                train.endStationCount += 1
            reply += "請輸入抵達站:"
            linebot_api.reply_message(
                event.reply_token, TextSendMessage(text=reply))
        elif message_text in train.stations and train.mode == 5:
            train.input_endStation = message_text
            train.find_the_end_station()
            train.mode = 6
            linebot_api.reply_message(event.reply_token, TextSendMessage(
                text='請輸入日期(西元年/月/日): \n(請輸入未來時間)'))
        elif train.mode == 6:
            train.mode = 7
            train.input_date = message_text
            train.find_the_date()
            linebot_api.reply_message(
                event.reply_token, TextSendMessage(text='請輸入出發時間(起): '))

        elif train.mode == 7:
            train.mode = 8
            train.input_startTime = message_text
            train.find_the_begin()
            linebot_api.reply_message(
                event.reply_token, TextSendMessage(text='請輸入抵達時間(迄): '))
        elif train.mode == 8:
            train.input_endTime = message_text
            train.find_the_end()
            reply = ""
            for result in train.result_doc("#pageContent > div > table > tbody > tr.trip-column").items():
                temp_train_number = result.find("ul.train-number a").text()
                temp_departure_time = result.children("td").eq(1).text()
                temp_arrival_time = result.children("td").eq(2).text()
                reply += f"{temp_train_number}:\n出發: {temp_departure_time} | 抵達: {temp_arrival_time}\n"
            linebot_api.reply_message(
                event.reply_token, TextSendMessage(text=reply))
            train.mode = 1
            train.driver.quit()

        elif message_text == '訂位連結' and train.mode == 1:
            linebot_api.reply_message(
                event.reply_token, TextSendMessage(text='[台鐵訂位連結]\nhttps://www.railway.gov.tw/tra-tip-web/tip/tip001/tip121/query\n'))

        else:
            train.mode = 1
            train.driver.quit()
            linebot_api.reply_message(
                event.reply_token, TextSendMessage(text='[錯誤]\n[back]\n您可能輸入無效資料\n或者兩狀態之間互不相通\n已回到起始狀態\n有效輸入:\n[查詢]\n[訂位連結]\n或者按左下角的"+"定位'))
    except:
        train.mode = 1
        train.driver.quit()
        linebot_api.reply_message(event.reply_token, TextSendMessage(
            text='[錯誤]\n您輸入無效資料\n已回到起始狀態\n有效輸入:\n[back]\n[查詢]\n[訂位連結]\n或者按左下角的"+"定位'))


@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    if event.type == 'message':
        if event.message.type == 'location' and train.mode == 1:
            UserId = str(event.source.user_id)
            geolocator = Nominatim(user_agent=f'{UserId}')
            location = geolocator.reverse(
                f'{event.message.latitude}, {event.message.longitude}')
            linebot_api.reply_message(event.reply_token, TextSendMessage(
                text=f'Get location message!\nYour User ID is [ {UserId} ]\n==-==-==-==-==-==-==-==-==-==-==\nCurrent location:\n{location.address}\n==-==-==-==-==-==-==-==-==-==-==\n{round(location.latitude, 6)}, {round(location.longitude, 6)}\n==-==-==-==-==-==-==-==-==-==-=='))
        else:
            train.mode = 1
            train.driver.quit()
            linebot_api.reply_message(
                event.reply_token, TextSendMessage(text='[錯誤]\n兩狀態互不相通\n已回到起始狀態\n有效輸入:[back]\n[查詢]\n[訂位連結]\n或者按左下角的"+"定位'))


if __name__ == '__main__':
    app.run()
    # port = os.environ.get("PORT", 8000)
    # app.run(host="0.0.0.0", port=port, debug = True)
