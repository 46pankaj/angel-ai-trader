from requests_html import HTMLSession

def analyze_oi(symbol="NIFTY"):
    url = f"https://www.nseindia.com/option-chain"
    session = HTMLSession()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.5"
    }

    resp = session.get(f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}", headers=headers)
    data = resp.json()

    # Calculate basic OI analytics
    calls = sum([row["CE"]["openInterest"] for row in data["records"]["data"] if "CE" in row])
    puts = sum([row["PE"]["openInterest"] for row in data["records"]["data"] if "PE" in row])

    pcr = round(puts / calls, 2)
    trend = "long_buildup" if pcr > 1 else "short_buildup"

    return {"pcr": pcr, "trend": trend}
