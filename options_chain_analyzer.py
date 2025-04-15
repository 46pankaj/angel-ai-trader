import requests
import pandas as pd

def fetch_nse_option_chain(symbol='NIFTY'):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }

    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception("Failed to fetch NSE option chain data")

    data = response.json()
    records = data['records']['data']
    expiry_date = data['records']['expiryDates'][0]

    ce_data = []
    pe_data = []

    for entry in records:
        if 'CE' in entry and entry['expiryDate'] == expiry_date:
            ce_data.append(entry['CE'])
        if 'PE' in entry and entry['expiryDate'] == expiry_date:
            pe_data.append(entry['PE'])

    df_ce = pd.DataFrame(ce_data)
    df_pe = pd.DataFrame(pe_data)
    return df_ce, df_pe, expiry_date