import json
import os

class TradeStateManager:
    def __init__(self, fname='trade_state.json'):
        self.fname = fname
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.fname):
            with open(self.fname, 'w') as f:
                json.dump({"positions":[]}, f)

    def current_position(self):
        with open(self.fname) as f:
            data = json.load(f)
        if not data["positions"]:
            return None
        return data["positions"][-1].get("type", None)

    def record_trade(self, typ, price, order):
        with open(self.fname) as f:
            data = json.load(f)
        entry = {"type": typ, "price": price, "order": order}
        data["positions"].append(entry)
        with open(self.fname, 'w') as f:
            json.dump(data, f, indent=2)
