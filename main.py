from flask import Flask
from flask import request
import requests
import json
import hmac
import hashlib
import sys
import argparse

# 追加
import random
 
# 定数値
CALLBACK_TOKEN = 'yuya4_callback_token'
PAGE_TOKEN     = 'hage'
APP_ID         = 'hoge'
APP_SECRET     = b'fuga' # bin指定しないとhmacで怒られる

# 引数設定
parser = argparse.ArgumentParser()
parser.add_argument("-p", help="set port number", type=int)
args = parser.parse_args()

# メッセージを受信したときの処理
def recieveMessage(entry, message):
    # メッセージの中身を確認する
    print(message)
    
    if 'text' in message['message']: 
        m = message['message']['text']
        if m.split(' ')[0] == '画像':
            keyword = m.split(' ')[1]
            sendMessage(message['sender']['id'], 'ｿｲﾔｯ!!')
            image_url = getImage(keyword)
            sendImage(message['sender']['id'], image_url)
            return
        elif 'いらいら' in m or '疲' in m or '死' in m or 'つらい' in m:
            heals = ['猫', '犬'] 
            n = random.randint(0,len(heals)-1)
            image_url = getImage(heals[n])
            sendMessage(message['sender']['id'], '元気出して！')
            sendImage(message['sender']['id'], image_url)
            return
        else:
            mes_res = ['確かに', 'わかる', 'うんうん', '私もそう思う']
            n = random.randint(0,len(mes_res)-1)
            sendMessage(message['sender']['id'], mes_res[n])
            return
    elif message['message']['attachments'][0]['type'] == 'image':
        image_res = ['可愛い💓', 'ナイスセンス！', 'いい写真！']
        n = random.randint(0,len(image_res)-1)
        sendMessage(message['sender']['id'], image_res[n])
        return
    else:
        # exception 
        sendMessage(message['sender']['id'], 'not supported')
 
# メッセージを送信する処理
def sendMessage(recipientId, message):
    # 送信先
    url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + PAGE_TOKEN
 
    # ヘッダ
    headers = {
        'Content-Type': 'application/json'
    }
 
    # ボディ
    body = {
        'recipient': {
            'id': recipientId,
        },
        'message': {
            'text': message,
        },
    }
 
    # postで送る
    requests.post(url, headers=headers, data=json.dumps(body))

def sendImage(recipientId, image_url):
    '''
    sned image
    Args:
        recipientId: string
            unique id of a recipient
        image_url: string
            url of a image to sent
    '''

    url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + PAGE_TOKEN
    headers = { 
        'Content-Type': 'application/json'
    }

    body = {
        'recipient': {
            'id': recipientId,
        },
        "message":{
            "attachment":{
                "type":"image",
                "payload":{
                    "url": image_url
                }
            }
        },
    }

    requests.post(url, headers=headers, data=json.dumps(body))

def getImage(text):
    '''
    search photozou for images by query and get the url
    Args:
        text: string
            search query
    Return:
        a image url
    '''  
    url = 'https://api.photozou.jp/rest/search_public.json'
    paramas = {
        'keyword': text,
        'limit': 10
    }
    num = random.randint(0, 9)
    res = requests.get(url, params=paramas).json()
    if 'info' in res:
        image_url = res['info']['photo'][num]['image_url']
        return image_url
    else:
        return ''

# Flask準備
app = Flask(__name__)
 
# POSTで来たとき
@app.route("/", methods=['GET', 'POST'])
def main():
    # コールバック検証
    if ('hub.verify_token' in request.args) and ('hub.challenge' in request.args):
        if request.args['hub.verify_token'] != '' and request.args['hub.challenge'] != '':
            if request.args['hub.verify_token'] == CALLBACK_TOKEN:
                print('verify_token OK')
                return request.args['hub.challenge']
            print('verify_token NG')
            return ''
 
    # シグネチャ検証
    if ('X-Hub-Signature' in request.headers) == False:
        print('missing signature')
        return ''
    hubSignature = request.headers['X-Hub-Signature'].split('=')[1]
    signature = hmac.new(APP_SECRET, request.data, hashlib.sha1).hexdigest()
    if signature != hubSignature:
        print('X-Hub-Signature NG')
        return ''
 
    for entry in request.json['entry']:
        for message in entry['messaging']:
            if 'message' in message:
                recieveMessage(entry, message)
 
    return ''
 
# Flask起動
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=args.p if args.p else 3000, threaded=True, debug=True)
