from datetime import datetime, timezone
import pytz

class LivePosition:
    def __init__(self, data):
        self.pos_id = data.get("posId")
        self.inst_id = data.get("instId")
        self.inst_name = data.get("instName")
        self.margin_coin = data.get("marginCoin")
        self.margin = float(data.get("margin", 0))
        self.margin_mode = data.get("marginMode")
        self.hold_side = data.get("holdSide")
        self.hold_mode = data.get("holdMode")
        self.total = float(data.get("total", 0))
        self.available = float(data.get("available", 0))
        self.locked = float(data.get("locked", 0))
        self.average_open_price = float(data.get("averageOpenPrice", 0))
        self.leverage = int(data.get("leverage", 0))
        self.achieved_profits = float(data.get("achievedProfits", 0))
        self.upl = float(data.get("upl", 0))
        self.upl_rate = float(data.get("uplRate", 0))
        self.liq_px = float(data.get("liqPx", 0))
        self.keep_margin_rate = float(data.get("keepMarginRate", 0))
        self.fixed_margin_rate = float(data.get("fixedMarginRate", 0))
        self.margin_rate = float(data.get("marginRate", 0))
        self.c_time = datetime.fromtimestamp(int(data.get("cTime", 0)) / 1000, tz=pytz.timezone('UTC'))
        self.u_time = datetime.fromtimestamp(int(data.get("uTime", 0)) / 1000, tz=pytz.timezone('UTC'))
        self.mark_price = float(data.get("markPrice", 0))
        self.auto_margin = data.get("autoMargin")

    def is_long(self):
        return self.hold_side == 'long'
    
    def is_active(self):
        return self.available != 0.0

    def __repr__(self):
        return (f"Position(pos_id={self.pos_id}, inst_id={self.inst_id}, inst_name={self.inst_name}, "
                f"margin_coin={self.margin_coin}, margin={self.margin}, margin_mode={self.margin_mode}, "
                f"hold_side={self.hold_side}, hold_mode={self.hold_mode}, total={self.total}, "
                f"available={self.available}, locked={self.locked}, average_open_price={self.average_open_price}, "
                f"leverage={self.leverage}, achieved_profits={self.achieved_profits}, upl={self.upl}, "
                f"upl_rate={self.upl_rate}, liq_px={self.liq_px}, keep_margin_rate={self.keep_margin_rate}, "
                f"fixed_margin_rate={self.fixed_margin_rate}, margin_rate={self.margin_rate}, "
                f"c_time={self.c_time}, u_time={self.u_time}, mark_price={self.mark_price}, "
                f"auto_margin={self.auto_margin})")
