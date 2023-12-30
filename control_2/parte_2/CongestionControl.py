from enum import Enum

class States(Enum):
    SLOW_START = 1
    CONGESTION_AVOIDANCE = 2


class CongestionControl:
    def __init__(self, MSS: int,debug=False):
        """Class that implements the TCP congestion,atributes are:
        MSS: Maximum Segment Size in bytes
        cwnd: Congestion Window Size in bytes,initialized as 1 MSS
        ssthresh: Slow Start Threshold in bytes
        current_state: Current state of the congestion control"""
        self.current_state = States.SLOW_START
        self.MSS = MSS 
        self.cwnd = MSS 
        self.ssthresh = None
        self.debug=debug

    def get_cwnd(self)->int:
        """Returns the current congestion window size in bytes"""
        if self.debug:print("(Congestion Control) cwnd: {} bytes= {} MSS".format(self.cwnd,self.get_MSS_in_cwnd()))    
        return self.cwnd    
    def get_ssthresh(self)->int:
        """Returns the current slow start threshold in bytes"""
        return self.ssthresh
    
    def get_MSS_in_cwnd(self)->int:
        """Returns the number of MSS segments that fit in the current congestion window size"""
        return int(self.cwnd // self.MSS)
    
    def event_ack_received(self):
        """Handles the events when an ACK is recieved"""
        if self.current_state == States.SLOW_START:
            self.cwnd += self.MSS
            if self.debug:print("(Congestion Control) ACK recieved in SLOW_START, cwnd: {} bytes = {} MSS, sstresh= {} bytes".format(self.cwnd,self.get_MSS_in_cwnd(),self.ssthresh))
            if self.ssthresh!=None and self.cwnd >= self.ssthresh:
                if self.debug:print("(Congestion Control) SStresh reached,changing to CONGESTION_AVOIDANCE")
                self.current_state = States.CONGESTION_AVOIDANCE

        elif self.current_state == States.CONGESTION_AVOIDANCE:
            if self.debug:print("(Congestion Control) ACK recieved in CONGESTION_AVOIDANCE, cwnd: {} bytes = {} MSS, sstresh= {} bytes".format(self.cwnd,self.get_MSS_in_cwnd(),self.ssthresh))
            self.cwnd += self.MSS * (1/ self.get_MSS_in_cwnd())
    
    def event_timeout(self):
        """Handles  the  events when a  timeout occurs"""
        if self.current_state == States.SLOW_START:
            self.ssthresh = self.cwnd // 2
            self.cwnd = self.MSS
            if self.debug:print("(Congestion Control) Timeout in SLOW_START, ssthresh: {} bytes, cwnd: {} bytes = {} MSS".format(self.ssthresh,self.cwnd,self.get_MSS_in_cwnd()))
        elif  self.current_state== States.CONGESTION_AVOIDANCE:
            self.ssthresh = self.cwnd // 2
            self.cwnd = self.MSS
            self.current_state = States.SLOW_START
            if self.debug:print("(Congestion Control) Time out  in Congestion Avoidance->changing to SLOW START, ssthresh: {} bytes, cwnd: {} bytes = {} MSS".format(self.ssthresh,self.cwnd,self.get_MSS_in_cwnd()))
    def is_state_slow_start(self):
        """Returns True if the current state is slow start, False otherwise"""
        return self.current_state == States.SLOW_START
    
    def  is_state_congestion_avoidance(self):
        """Returns True if the current state is congestion avoidance, False otherwise"""
        return self.current_state == States.CONGESTION_AVOIDANCE



