from apis.bitget_client import BitgetClient
from models.api_secrets import ApiSecrets
import json

api_secrets = None


with open('./Live/secrets.json', 'r') as f:
    data = json.loads(f.read())
    data = data['bitget1']
    api_secrets = ApiSecrets(data) 


params = dict(symbol='XRPUSDT', productType='USDT-FUTURES', marginCoin='USDT')

api = BitgetClient(api_secrets.apiKey, api_secrets.secretKey, api_secrets.passphrase)

# response = api.account(params)
# print(f"Account details: {response['data']}")


params = {
    "planType": "normal_plan",
    "symbol": "XRPUSDT",
    "productType": "USDT-FUTURES",
    "marginMode": "isolated",
    "marginCoin": "USDT",
    "size": "9",  # Convert size to string
    "price": "2.64", # Convert price to string
    "triggerPrice": "2.64",  # Convert price to string
    "triggerType": "mark_price",
    "side": "buy",
    "tradeSide": "open",
    "orderType": "limit",
    "clientOid": "1234567890",
    "stopSurplusTriggerPrice": '2.7', # Convert tp to string
    "stopSurplusTriggerType": "mark_price",
    "stopLossTriggerPrice": '2.55',  # Convert sl to string
    "stopLossTriggerType": "mark_price"
}

try:
    response = api.placePlanOrder(params)
    print(response)
except Exception as e:
    print(f"Failed to place order: {e}")



# contract = api.contracts(dict(symbol='XRPUSDT', productType='USDT-FUTURES'))
# print(f"Contract details: {contract['data'][0]}")