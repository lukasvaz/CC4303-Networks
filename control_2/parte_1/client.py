import socket
from Socket_TCP  import SocketTCP
PACKAGE_SIZE=100
# leemos archivo

file=""
while True:
    try:
        file+=input()+"\n"
    except EOFError:
        break

message = file.encode()
# packages=get_packages(message,16)
client_socket=SocketTCP().SocketTCP(debug=True)

destination_address = ('localhost', 5001)
client_socket.connect(destination_address)
 
client_socket.send(message)
client_socket.close()
