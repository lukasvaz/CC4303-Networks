import socket
from Socket_TCP import SocketTCP
import time
# importamos utils completo
# from utils import *
PACKAGE_SIZE=100

print('Creando socket - Servidor')
# armamos el socket no orientado a conexión
server_socket=SocketTCP().SocketTCP(debug=True)

# server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# definimos dirección donde queremos que correr el server_socket
server_address = ('localhost', 5000)

# hacemos bind del server socket a la dirección server_address
server_socket.bind(server_address)

# nos quedamos esperando, como buen server, a que llegue una petición de conexión

recieved=""
while True:
    new_socket, destination_address =server_socket.accept() 
    start_time = time.time()   
    recv_1=new_socket.recv(10,mode="go_back_n")
    recv_2=new_socket.recv(10,mode="go_back_n")
    end_time = time.time()
    print("response {} len {}".format(recv_1+recv_2,len(recv_1+recv_2)))
    new_socket.recv_close()
    elapsed_time = end_time - start_time
    print("time :", elapsed_time)
    # print("(Server) Final response:{} ,len msg{}".format((recv_1+recv_2),len(recv_1+recv_2)))
    break

