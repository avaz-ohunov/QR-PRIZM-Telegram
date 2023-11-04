# curs.py

from requests import Request, Session
import json

url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"

parameters = {
	"slug": "prizm",
	"convert": "RUB"
}

headers = {
	"Accepts": "application/json",
	"X-CMC_PRO_API_KEY": "24673a31-5cd9-493f-866f-c301bb9d45e6"
}

session = Session()
session.headers.update(headers)

response = session.get(url, params = parameters)
pzm_curs = json.loads(response.text)["data"]["1681"]["quote"]["RUB"]["price"]
pzm_curs = str(pzm_curs)[0:4]
