import socket
import sys

#check  format
if len(sys.argv)<4:
    raise Exception("modo de uso:python3 prueba_router.py headers_IP router_inicial puerto_router_inicial")

# creamos el socket cliente (no orientado a conexión)
router_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# get parameters from command line
headers_ip=sys.argv[1]
router_ip=sys.argv[2]
router_port=sys.argv[3]

print("-------SEND CONFIGURATION-------")
print("IP_header: ",headers_ip)
print("initial_router_ip: ",router_ip)
print("initial_router_port: ",router_port)
print("----------------------------------")

#generamos mensajes con headers
packages=list()
with open("archivo.txt","r") as file:
    for line in file:
        packages.append(headers_ip+','+line)
# enviamos mensajes
for i,package in enumerate(packages):
    print("SENDING {}: {}".format(i,package.encode()))
    router_socket.sendto(package.encode(),(router_ip,int(router_port)))

