import datetime

# Global PNL tracker
pnl_tracker = {
    'daily_loss_limit': -500,
    'daily_pnl': 0,
    'last_reset_date': datetime.date.today()
}

def update_daily_pnl(pnl):
    """
    Update daily PNL and reset if it's a new day.
    """
    today = datetime.date.today()
    if today != pnl_tracker['last_reset_date']:
        pnl_tracker['daily_pnl'] = 0
        pnl_tracker['last_reset_date'] = today
    pnl_tracker['daily_pnl'] += pnl

def can_trade():
    """
    Check if trading is allowed based on daily PNL loss limit.
    """
    return pnl_tracker['daily_pnl'] >= pnl_tracker['daily_loss_limit']

def check_risk_limits(row):
    """
    Check risk limits based on row data and PNL tracker.
    Expected by dashboard.py to take a DataFrame row and return a boolean.
    """
    # Example: Allow trading if RSI is in a safe range and PNL is within limits
    if 'rsi' in row and 20 < row['rsi'] < 80 and can_trade():
        return True
    return False
