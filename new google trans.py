import requests
import json


def my_translator(payload:iter):
    # payload = [{'text':comment} for comment in comments ]


    url = "https://microsoft-translator-text.p.rapidapi.com/translate"
    querystring = {"to":"en","api-version":"3.0","profanityAction":"NoAction","textType":"plain"}
    payload = json.dumps(payload)
    headers = {
        'content-type': "application/json",
        'x-rapidapi-host': "microsoft-translator-text.p.rapidapi.com",
        'x-rapidapi-key': "c10a3b3468mshea11bdae26f5911p1d9d13jsn108dd8377a12"
        }
    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

    print(response.text)




payload = [{'text':'سلام فیلم خوبی بود'}, {'text':'سلام من به تو یار فدیمی'}]

my_translator(payload=payload)

