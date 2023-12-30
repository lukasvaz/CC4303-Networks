import socket
import random
import time
from utils import PACKAGE_SIZE,TIMEOUT_VAL

class SocketTCP:
    def __init__(self):
        self.socketUDP = None
        self.destination_address = None
        # to handle edge case
        self.former_direction=None
        self.origin_address = None
        self.sequence_number = None
        self.message_length = None
        self.remaining_bytes = 0
        self.remaining_message = b""
        self.debug=False

    @staticmethod
    def parse_segment(TCP_message: bytes):
        """Parses a TCP segment from a byte string."""
        TCP_list = TCP_message.decode().split("|||")
        TCP_dic = {"SYN": int(TCP_list[0]),
                   "ACK": int(TCP_list[1]),
                   "FIN": int(TCP_list[2]),
                   "SEQ": int(TCP_list[3]),
                   "DATOS": TCP_list[4]
                   }
        return TCP_dic

    @staticmethod
    def create_segment(TCP_dict: dict):
        """Creates a TCP segment from a dictionary."""
        return "|||".join([str(x) for x in TCP_dict.values()]).encode()

    def SocketTCP(self,debug=False):
        """Creates a new SocketTCP object, with a random sequence number"""
        self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sequence_number = random.randint(0, 100)
        self.debug=debug
        return self

    def bind(self, address: tuple):
        """Binds the socket to the given address."""
        self.socketUDP.bind(address)

    def connect(self, destination_address: tuple):
            """ Connects to a server at the specified destination address.First, it sends a SYN message to the server, and then waits for a SYN ACK response. 
            If the response is correct, it sends an ACK message and the connection is established."""
            
            self.destination_address = destination_address
            # seteamos  timeout  
            self.socketUDP.settimeout(TIMEOUT_VAL)

            # send SYN message to server
            SYN_message = {"SYN": "1",
                           "ACK": "0",
                           "FIN": "0",
                           "SEQ": str(self.sequence_number),
                           "DATOS": "0"
                           }
            if self.debug:print("(Connect):requesting  connection to: ", self.destination_address)
            self.socketUDP.sendto(SocketTCP.create_segment(
                SYN_message), self.destination_address)
            # waiting  for  SYN ACK from server (from new  socket)
            while True:
                try:
                    # recieving  response
                    recieved_message, new_destination_address = self.socketUDP.recvfrom(
                        PACKAGE_SIZE)
                    response_message = SocketTCP.parse_segment(recieved_message)
                    # if ACK equal 1  and self SEQ+1 in response  
                    if self.sequence_number+1 == response_message["SEQ"] and response_message["ACK"] == 1 and response_message["ACK"] == 1:
                        # sending  ACK response  to  server
                        if self.debug:print("(Connect) SYN ACK obtained")
                        self.sequence_number += 2
                        ACK_message = {"SYN": "0",
                                       "ACK": "1",
                                       "FIN": "0",
                                       "SEQ": str(self.sequence_number),
                                       "DATOS": "0"
                                       }
                        self.socketUDP.sendto(
                            SocketTCP.create_segment(ACK_message), self.destination_address)
                        if self.debug:print("(Connect)sending ACK to server")
                        # we store  former direction  to handle edge case
                        self.former_direction=self.destination_address
                        # setting  new direction from  server
                        self.destination_address = new_destination_address
                        if self.debug:print("(Connect) Connection Established,new direction\n",
                              self.destination_address)
                        break
                # if  does not recieve SYN+ACK from  server, will try SYN again
                except TimeoutError:
                    self.socketUDP.sendto(SocketTCP.create_segment(
                    SYN_message), self.destination_address)    
                    if self.debug:print("connect:not  confirmed  sending SYN again")


    def accept(self):
            """Accepts incoming connection requests from clients.
            Waits for a SYN message from the client and establishes a new socket for communication.
            Sends a SYN ACK message from the new socket to establish the connection.
            Waits for an ACK message from the client to confirm the connection.
            Returns the new socket and its origin address upon successful connection.
            """
            # waiting  for SYN message  from  client
            while True:
                while True:
                    if self.debug:print("Waiting  for  requests")
                    recieved_message, destination_address = self.socketUDP.recvfrom(
                        PACKAGE_SIZE)
                    response_message = SocketTCP.parse_segment(
                        recieved_message)
                    # if  recieve  an SYN  request from client
                    if response_message["SYN"] == 1:
                        if self.debug:print("(Accept)SYN request:Establishing connection")
                        # we  create  a new  socket  for  communication
                        new_socket = SocketTCP().SocketTCP(debug=self.debug)
                        IP_address = random.randint(1, 50000)
                        new_address = ('localhost', IP_address)
                        new_socket.bind(new_address)
                        # set new sequence 
                        self.sequence_number = response_message["SEQ"]+1
                        # we send the SYN ACK  from  new socket
                        SYN_ACK_message = {"SYN": "1",
                                           "ACK": "1",
                                           "FIN": "0",
                                           "SEQ": str(self.sequence_number),
                                           "DATOS": "0"
                                           }
                        
                        new_socket.socketUDP.sendto(
                            SocketTCP.create_segment(SYN_ACK_message), destination_address)
                        if self.debug:print("(Accept)Sending SYN ACK  message")
                        break
                # waiting for ACK message  from  client
                while True:
                    if self.debug:print("(Accept)waiting ACK")
                    # recieving message from client
                    recieved_message, destination_address = self.socketUDP.recvfrom(
                        PACKAGE_SIZE) 
                    response_message = SocketTCP.parse_segment(
                        recieved_message)
                    # if  message  is  ACK
                    #  and  seq  in messagee recieved  is self seq+1
                    if response_message["ACK"] == 1 and response_message["SEQ"] == self.sequence_number+1:
                        if self.debug:print("(Accept)recieved ACK:Conection Established \n")
                        new_socket.destination_address = destination_address
                        new_socket.sequence_number = response_message["SEQ"]
                        return (new_socket, new_socket.origin_address)
                        
                    # if  seq  in message  is less or equal self sequence, send  SYN ACK again
                    elif response_message["SEQ"] <= self.sequence_number+1:
                        new_socket.socketUDP.sendto(
                        SocketTCP.create_segment(SYN_ACK_message), destination_address)
                        if self.debug:print("(Accept)response SEQ < self SEQ,Sending SYN ACK  message again")
                
        
    def send(self, message: bytes):
        """"Send a message  using stop and wait """
        if self.debug:print("(send)Beginning sending")
        self.socketUDP.settimeout(TIMEOUT_VAL)
        # preparing  packages
        self.message_length = len(message)

        packages=[{"SYN": "0",
                           "ACK": "0",
                           "FIN": "0",
                           "SEQ": str(self.sequence_number),
                           "DATOS": str(self.message_length)
                           }]

        msg_packages = get_packages(message, 16)
        msg_packages=[ {"SYN": "0",
                               "ACK": "0",
                               "FIN": "0",
                               "SEQ": "0",
                               "DATOS": x.decode()
                               } 
                               for  x in msg_packages]
        packages.extend(msg_packages)
        
        for  i,package in enumerate(packages):
            attempts=0
            #sending package 
            package["SEQ"]=self.sequence_number     
            send_message=SocketTCP.create_segment(
            package)        
            ack=0

            while not ack: 
                try:
                    #(edge case) if tried  4 attempts  in first package, ACK in HANDSHAKE was not recieved 
                    if i==0 and attempts==4 :
                            # send ACK again
                            ACK_message = {"SYN": "0",
                                    "ACK": "1",
                                    "FIN": "0",
                                    "SEQ": str(self.sequence_number),
                                    "DATOS": "help"
                                    }
                            attempts=0
                            self.socketUDP.sendto(
                            SocketTCP.create_segment(ACK_message), self.former_direction)
                            if self.debug:print("(send)edge case:sending ACK (help) message",ACK_message)
                    if self.debug:print("(send)sending package {} ".format(i),send_message)
                    self.socketUDP.sendto(send_message, self.destination_address)
                    
                    # recieving  response
                    recieved_message,_=self.socketUDP.recvfrom(PACKAGE_SIZE)
                    response=SocketTCP.parse_segment(recieved_message)
                    # set attempts to 0 , response was recieved
                    attempts=0

                    # if ACK  in response ,updates seq  and  send other package
                    if response["ACK"]==1 and response["SEQ"]==self.sequence_number+len(package["DATOS"]):
                        self.sequence_number=response["SEQ"]
                        if self.debug:print("(send)ACK recieved,seting SEQ to {}\n".format(self.sequence_number))
                        ack=1
                    else:
                        if self.debug:print("(send) Wrong seq number")
                # if  doesnt recieves anything,send  again
                except TimeoutError:
                        if self.debug:print("(send)timeout")
                        attempts+=1
                        continue    

    def recv(self, buff_size: int):
        """Recieves a message using stop and wait"""
        
        if self.debug:print("(recv) Beginning recv, buff size {}".format(buff_size))
        ACK_msg = {"SYN": "0",
                               "ACK": "1",
                               "FIN": "0",
                               "SEQ": str(self.sequence_number),
                               "DATOS": "0"
                               }
        
        # initial package  reception 
        print(not self.remaining_bytes)
        while not self.remaining_bytes:
            recieved_message, _ = self.socketUDP.recvfrom(PACKAGE_SIZE)
            initial_response_message = SocketTCP.parse_segment(
                recieved_message)
            
            try:
                # recieve inital package
                self.remaining_bytes = int(initial_response_message['DATOS'])
                self.sequence_number=initial_response_message["SEQ"]+len(initial_response_message["DATOS"])
                ACK_msg['SEQ']=self.sequence_number
                self.socketUDP.sendto(SocketTCP.create_segment(ACK_msg), self.destination_address)
                if self.debug:print("(recv)Initial reponse| remainnig bytes {}".format(self.remaining_bytes))

                break
            # if  does not  have an int in  DATA, does nothing (client  will try again after timeot) 
            except ValueError:
                print("error")
                continue
                
        # we append  the  remaining message  with the  new  packages that will come 
        response = self.remaining_message

        print(self.remaining_bytes )
        # if message > buff size-> fill buffer and  store remaining
        if self.remaining_bytes > buff_size:
            if self.debug:print("(recv)case:message > buff size, remaining bytes {}".format(self.remaining_bytes))
            # recieve packages  until fill  the  buffer
            while len(response) < buff_size:
                recieved_message, _ = self.socketUDP.recvfrom(PACKAGE_SIZE)
                recieved_message = SocketTCP.parse_segment(recieved_message)
                #if recieved sequence  is equal  to self sequence (this seq=seq+previous len)  
                if recieved_message["SEQ"]==self.sequence_number:
                    # update sequence  number and  send  to client
                    self.sequence_number+=len(recieved_message["DATOS"])
                    ACK_msg["SEQ"]=self.sequence_number
                    self.socketUDP.sendto(SocketTCP.create_segment(ACK_msg), self.destination_address)
                    # we will return response
                    response += recieved_message['DATOS'].encode()
                    self.remaining_bytes -= len(recieved_message['DATOS'].encode())
                    # if  we  surpasss  the  buff size ,we indexing it  
                    if len(response) > buff_size:
                        self.remaining_message = response[buff_size::]
                        response = response[0:buff_size]

                # if recieved message is a previous package, sends ack message  with current self seq
                elif recieved_message["SEQ"]<self.sequence_number:
                    self.socketUDP.sendto(SocketTCP.create_segment(ACK_msg), self.destination_address)

        
        # if message < buff size , recv package  untill get the whole remaining message
        else:
            if self.debug:print("(recv)case:message < buff size, remaining bytes {}".format(self.remaining_bytes))
            while self.remaining_bytes > 0:
                # recieve pacakge
                recieved_message, _ = self.socketUDP.recvfrom(PACKAGE_SIZE)
                recieved_message = SocketTCP.parse_segment(recieved_message)
                
                #if recieved sequence  is equal  to self sequence (this seq=seq+previous len)  
                if recieved_message["SEQ"]== self.sequence_number:
                    # update response
                    response += recieved_message['DATOS'].encode()
                    # update  SEQ and send  to  client
                    self.sequence_number+=len(recieved_message["DATOS"])
                    ACK_msg["SEQ"]=self.sequence_number
                    self.socketUDP.sendto(SocketTCP.create_segment(ACK_msg), self.destination_address)
                    #update  remainnig  bytes
                    self.remaining_bytes -= len(recieved_message['DATOS'].encode())

                # if recieved message is a previous package, sends ack message  with current self seq
                elif recieved_message["SEQ"]<self.sequence_number:
                    self.socketUDP.sendto(SocketTCP.create_segment(ACK_msg), self.destination_address)

        if self.debug:print("(recv)End recv: {} bytes, response: {}".format(len(response),response))
        if self.debug:print("(recv)remainning_msg {}".format(self.remaining_message))
        if self.debug:print("(recv)remainning_bytes {} \n".format(self.remaining_bytes))
        return response

    def close(self):
        """ Closes the connection with the server."""
        if self.debug:print("(Close) Calling close")
        # setting  timeout and  attempts  counter  to handle losses 
        self.socketUDP.settimeout(TIMEOUT_VAL)
        attempts=0
        # send a FIN  message  to server
        FIN_message = {"SYN": "0",
                       "ACK": "0",
                       "FIN": "1",
                       "SEQ": str(self.sequence_number),
                       "DATOS": "-"
                       }
        if self.debug:print("(Close)sending FIN mssage")
        self.socketUDP.sendto(SocketTCP.create_segment(FIN_message), self.destination_address)
        # recieving  response from server
        while True:
            try:
                recieved_message, _ = self.socketUDP.recvfrom(PACKAGE_SIZE)
                response = SocketTCP.parse_segment(recieved_message)
                # if  FIN and ACK in response,send 3   ACK times  and break loop
                if response["FIN"] == 1 and response["ACK"] == 1 and response["SEQ"] == self.sequence_number+1:
                    if self.debug:print("(Close) recieved FIN ACK message")
                    self.sequence_number = response["SEQ"]+1
                    ACK_message = {"SYN": "0",
                                "ACK": "1",
                                "FIN": "0",
                                "SEQ": str(self.sequence_number),
                                "DATOS": "0"
                                }
                    for i in range(3):
                        self.socketUDP.sendto(SocketTCP.create_segment(ACK_message), self.destination_address)
                        time.sleep(TIMEOUT_VAL)
                        if self.debug:print("(Close) sending ACK mesasge, attempt {}".format(i))
                    if self.debug:print("(Close) Connection closed")
                    break
            # if  there is a timeout send FIN message again, if third  attempt close connection
            except TimeoutError:
                if attempts==3:
                    if self.debug:print("(Close)three attempts, closing connection")
                    break
                attempts+=1
                self.socketUDP.sendto(SocketTCP.create_segment(FIN_message), self.destination_address)
                if self.debug:print("(Close)FIN ACK not recieved, trying again")
        self.socketUDP.close()

    def recv_close(self):
        """Receives a FIN request from the client and sends a FIN ACK response to close the connection."""
        # setting timeot and  attempts counter to handle losses
        if self.debug:print("(recvClose) Starting closing")
        self.socketUDP.settimeout(TIMEOUT_VAL)
        #recieveing FIN request  from client 
        while True: 
            try:
                recieved_message, _ = self.socketUDP.recvfrom(PACKAGE_SIZE)
                response = SocketTCP.parse_segment(recieved_message)
                if response["FIN"] == 1:
                    self.sequence_number = response['SEQ']+1
                    FIN_ACK_message = {"SYN": "0",
                                   "ACK": "1",
                                   "FIN": "1",
                                   "SEQ": str(self.sequence_number),
                                   "DATOS": "0"
                                   }
                    self.socketUDP.sendto(SocketTCP.create_segment(FIN_ACK_message), self.destination_address)
                    if self.debug:print("(recvClose)FIN recieved, sending FIN ACK to client")
                    break
                # if seq  in mseg< self seq,  handling:  last  ack   was  not data sending 
                if response["SEQ"]<self.sequence_number:
                    ACK_msg = {"SYN": "0",
                               "ACK": "1",
                               "FIN": "0",
                               "SEQ": str(self.sequence_number),
                               "DATOS": "0"
                               }
                    self.socketUDP.sendto(SocketTCP.create_segment(ACK_msg), self.destination_address)
            except TimeoutError:
                continue


        attempts=0
        #recieveing ACK  from client 
        while True: 
            try:
                recieved_message, _ = self.socketUDP.recvfrom(PACKAGE_SIZE)
                response = SocketTCP.parse_segment(recieved_message)

                if response["ACK"] == 1 and response["SEQ"] == self.sequence_number+1:
                    if self.debug:print("(recvClose) ACK recieved,Connection closed")
                    break
            
            except TimeoutError:
                if attempts==3:
                    if self.debug:print("(recvClose)ACK not recieved,3 attempts")
                    break
                attempts+=1
                if self.debug:print("(recvClose)ACK not recieved, trying again")
        
        if self.debug:print("(recvClose)Connection closed")
        self.socketUDP.close()
        
def get_packages(full_message: bytes, size: int):
    iteration = len(full_message)//size
    remaining = len(full_message) % size
    packages = []
    for i in range(iteration):
        packages.append(full_message[i*16:(i+1)*16])
    if remaining:
        packages.append(full_message[iteration*16::])
    return packages
