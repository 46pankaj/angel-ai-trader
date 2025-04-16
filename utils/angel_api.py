import requests
import json
import time
import pyotp
from config.config import ANGEL_API_KEY, ANGEL_CLIENT_ID, ANGEL_PIN, ANGEL_TOTP_KEY

class AngelOneAPI:
    def __init__(self):
        self.base_url = "https://apiconnect.angelbroking.com"
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self._login()
        
    def _login(self):
        # Generate TOTP
        totp = pyotp.TOTP(ANGEL_TOTP_KEY).now()
        
        # Login payload
        payload = {
            "clientcode": ANGEL_CLIENT_ID,
            "password": ANGEL_PIN,
            "totp": totp
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "CLIENT_LOCAL_IP",
            "X-ClientPublicIP": "CLIENT_PUBLIC_IP",
            "X-MACAddress": "MAC_ADDRESS",
            "X-PrivateKey": ANGEL_API_KEY
        }
        
        response = self.session.post(
            f"{self.base_url}/rest/auth/angelbroking/user/v1/loginByPassword",
            data=json.dumps(payload),
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['data']['jwtToken']
            self.refresh_token = data['data']['refreshToken']
            self.token_expiry = time.time() + 86400  # Token valid for 24 hours
        else:
            raise Exception(f"Login failed: {response.text}")
    
    def _refresh_token(self):
        if time.time() > self.token_expiry:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-UserType": "USER",
                "X-SourceID": "WEB",
                "X-ClientLocalIP": "CLIENT_LOCAL_IP",
                "X-ClientPublicIP": "CLIENT_PUBLIC_IP",
                "X-MACAddress": "MAC_ADDRESS",
                "Authorization": f"Bearer {self.refresh_token}"
            }
            
            response = self.session.post(
                f"{self.base_url}/rest/auth/angelbroking/jwt/v1/generateTokens",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data['data']['jwtToken']
                self.token_expiry = time.time() + 86400
            else:
                raise Exception(f"Token refresh failed: {response.text}")
    
    def get_market_data(self, exchange, symbol, interval="ONE_MINUTE"):
        self._refresh_token()
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "CLIENT_LOCAL_IP",
            "X-ClientPublicIP": "CLIENT_PUBLIC_IP",
            "X-MACAddress": "MAC_ADDRESS",
            "Authorization": f"Bearer {self.access_token}"
        }
        
        params = {
            "exchange": exchange,
            "symboltoken": symbol,
            "interval": interval
        }
        
        response = self.session.get(
            f"{self.base_url}/rest/secure/angelbroking/historical/v1/getCandleData",
            headers=headers,
            params=params
        )
        
        return response.json()['data'] if response.status_code == 200 else None
    
    def place_order(self, order_params):
        self._refresh_token()
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "CLIENT_LOCAL_IP",
            "X-ClientPublicIP": "CLIENT_PUBLIC_IP",
            "X-MACAddress": "MAC_ADDRESS",
            "Authorization": f"Bearer {self.access_token}"
        }
        
        response = self.session.post(
            f"{self.base_url}/rest/secure/angelbroking/order/v1/placeOrder",
            data=json.dumps(order_params),
            headers=headers
        )
        
        return response.json() if response.status_code == 200 else None
    
    # Add more methods for positions, order book, etc.
