from smartapi import SmartConnect
import config

def angel_login():
    obj = SmartConnect(api_key=config.API_KEY)
    session = obj.generateSession(config.CLIENT_ID, config.PIN, config.TOTP)
    return obj, session['data']['jwtToken'], session['data']['feedToken']