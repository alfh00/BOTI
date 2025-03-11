

class TradeSettings:
    def __init__(self, ob):
        self.granularity= str(ob['granularity'])
        self.risk= float(ob['risk'])
        self.dist = float(ob['dist'])
        self.sl_pct= float(ob['sl_pct'])
        self.tp_pct= float(ob['tp_pct'])
        self.trailing_sl_trigger_pct= float(ob['trailing_sl_trigger_pct'])
        self.trailing_sl_pct= float(ob['trailing_sl_pct'])

    def __repr__(self):
        return str(vars(self))
    
    @classmethod
    def settings_to_str(cls, settings):
        ret_str = 'Trade Settings:\n'
        for _, v in settings.items():
            ret_str += f'{v}\n'
        ret_str += '\n'

        return ret_str
    
    def add_contract(self, contract):
        self.contract = contract