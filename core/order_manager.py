import time
from datetime import datetime
from core.risk_engine import RiskEngine

class OrderManager:
    def __init__(self, api_client):
        self.api = api_client
        self.risk = RiskEngine()
        self.max_retries = 3

    def execute_order(self, signal):
        """Safely execute orders with risk checks"""
        if not self.risk.is_trade_allowed(signal):
            raise ValueError("Risk check failed")

        for attempt in range(self.max_retries):
            try:
                order = self.api.place_order(
                    symbol=signal['symbol'],
                    action=signal['action'],
                    quantity=signal['qty'],
                    price=signal.get('price', 'MARKET')
                )
                self.log_order(order)
                return order
            except Exception as e:
                if attempt == self.max_retries - 1:
                    self.alert_failure(signal, str(e))
                time.sleep(1)

    def log_order(self, order):
        with open("/var/log/trading/orders.log", "a") as f:
            f.write(f"{datetime.now()},{order['id']},{order['status']}\n")
