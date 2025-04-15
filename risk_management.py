import datetime

pnl_tracker = {
    'daily_loss_limit': -500,
    'daily_pnl': 0,
    'last_reset_date': datetime.date.today()
}

def update_daily_pnl(pnl):
    today = datetime.date.today()
    if today != pnl_tracker['last_reset_date']:
        pnl_tracker['daily_pnl'] = 0
        pnl_tracker['last_reset_date'] = today
    pnl_tracker['daily_pnl'] += pnl

def can_trade():
    return pnl_tracker['daily_pnl'] >= pnl_tracker['daily_loss_limit']

def check_risk_limits(row):
    if 'rsi' in row and 20 < row['rsi'] < 80 and can_trade():
        return True
    return False
