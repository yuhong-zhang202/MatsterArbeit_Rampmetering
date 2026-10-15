"""One fixed750 request; no ALINEA or scheduled-command production."""
from src.candidate_a_t10_g5_y3_20261013.policy import Command, require
class Producer:
    def __init__(self,mode='fixed750',fixed_rate=750):
        require(mode=='fixed750' and type(fixed_rate) in (int,float) and fixed_rate==750,'FIXED750_ONLY')
        self.mode=mode;self.fixed_rate=fixed_rate;self.events=[]
    def command_at(self,conn,t):
        return Command('fixed750:1200',1200,750,'FIXED') if t==1200 else None
    def after_ack(self,conn,end):pass
