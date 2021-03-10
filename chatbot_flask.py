import urllib.request
import requests
import urllib.parse
from bs4 import BeautifulSoup
import urllib
import json
import os
from flask import Flask, request, make_response, jsonify

# initialize the flask app
app = Flask(__name__)


# default route
@app.route('/')
def index():
    return 'Hello World!'


# create a route for webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, cache=False, force=True)
    action = req['queryResult']['action']  # 1

    # 노래 가사
    if action == 'musicName':
        name = req['queryResult']['parameters']['music_name']  # 2
        print(name)
        url1 = 'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query='
        url2 = '+%EA%B0%80%EC%82%AC'
        url3 = name
        url = url1 + urllib.parse.quote_plus(url3) + url2
        print(url)

        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.find_all(class_='text no_ellipsis type_center _content_text')

        a = ''
        
        for i in title:
            a = i.text

        if a == '':
            title2 = soup.find_all(class_='lyrics_txt _lyrics_txt')
            for i in title2:
                a = i.text

        text_mod = a.replace("  ", "\n", 100)

        return {"fulfillmentText": text_mod}

    # 축구팀 순위
    elif action == 'fotTeam':
        name = req['queryResult']['parameters']['fot_team']

        baseurl = 'https://search.daum.net/search?nil_suggest=btn&w=tot&DA=SBC&q='
        url2 = '+%EC%88%9C%EC%9C%84'
        plusurl = name
        url = baseurl + urllib.parse.quote_plus(plusurl) + url2

        webpage = requests.get(url)
        soup = BeautifulSoup(webpage.content, "html.parser")

        a=soup.find(class_='select_team').strong.text + "위"

        return {"fulfillmentText": a}

    # 주가
    elif action == 'stockCom':
        name = req['queryResult']['parameters']['stock_com']
        print(name)

        baseurl = "https://search.daum.net/search?w=tot&DA=YZR&t__nil_searchbox=btn&sug=&sugo=&sq=&o=&q="
        plusurl = name
        plusurl2 = '+%EC%A3%BC%EA%B0%80'

        naver_baseurl = 'https://finance.naver.com/item/main.nhn?code='

        daum_url = baseurl + plusurl + plusurl2
        naver_url = naver_baseurl + plusurl

        print(naver_url)
        print(daum_url)

        daum_result = requests.get(daum_url)
        daum_bs_obj = BeautifulSoup(daum_result.content, "html.parser")


        no_today = daum_bs_obj.find("div", {"class": "info_current"})

        stock_info_div = daum_bs_obj.find("div", {"class": "updown_item"})
        stock_info = stock_info_div.find_all("dl")

        stock_chat = daum_bs_obj.find("img", {"id": "stockTabImg"})

        # if no_today == None:
            # no_today = daum_bs_obj.find("div", {"class": "info_current down"})

        card_title = no_today.span.text
        stock_info_card1 = stock_info[0].text
        stock_info_card2 = stock_info[0].text
        subtitle = stock_info_card1 + stock_info_card2
        imgUrl = stock_chat.attrs['src']
        print(card_title)
        print(subtitle)
        print(imgUrl)


        return {"fulfillmentMessages": [
    {
      "platform": "FACEBOOK",
      "card": {
        "title": card_title,
        "subtitle": subtitle,
        "imageUri": imgUrl,
        "buttons": [
          {
            "text": "그래프 자세히"
          },
            {
                "text": "웹에서 보기",
                "postback": naver_url
            }
        ]
      }
    }
  ]
}
    # 그래프 자세히
    elif action == 'stock_com_name':
        name = req['queryResult']['parameters']['stock_com']
        print(name)

        naver_baseurl = 'https://finance.naver.com/item/main.nhn?code='
        plusurl = name
        naver_url = naver_baseurl + plusurl

        print(naver_url)

        naver_result = requests.get(naver_url)
        naver_bs_obj = BeautifulSoup(naver_result.content, "html.parser")

        stock_chat = naver_bs_obj.find("img", {"id": "img_chart_area"})

        imgUrl = stock_chat.attrs['src']

        print(imgUrl)

        return {"fulfillmentMessages": [
                    {
                        "platform": "FACEBOOK",
                            "image": {
                                "imageUri": imgUrl
                            }

                    }
                ]
            }

    # 실검
    elif action == 'Live':
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
        url = 'https://datalab.naver.com/keyword/realtimeList.naver?where=main'
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        data = soup.findAll('span', 'item_title')
        a=list()
        for item in data:
            print(item.get_text())
            a.append({'text': {
                        "text": [
                            item.text
                        ]
                    }})

        return {"fulfillmentMessages": a}

    else:
        return "실패"



# run the app
if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(debug=True, port=port, host='0.0.0.0')