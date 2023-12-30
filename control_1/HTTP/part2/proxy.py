import socket
from utils import *
import json
import sys

# chequeamos  si esta especificado el archivo json
try:
    with open(sys.argv[1]) as file:
        # usamos json para manejar los datos
        data = json.load(file)
except IndexError as err:
    raise Exception("Debe especificar archivo JSON:", err)

# definimos el tamaño del buffer de recepción
buff_size = 30
proxy_socket_address = ('localhost', 8000)
proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_socket.bind(proxy_socket_address)
proxy_socket.listen(1)

# nos quedamos esperando a que llegue una petición de conexión
while True:
    print('... Esperando clientes')
    new_proxy_socket, new_proxy_socket_address = proxy_socket.accept()

    raw_message = recieve_msgs(new_proxy_socket, buff_size)
    print('-------------REQUEST TO PROXY--------------- \n')
    request = HttpParser()
    request.parse_HTTP_message(raw_message)
    request.create_HTTP_message()
    print(raw_message)
    if request.head['start-line'].split()[1] in data['blocked']:
        ##### INVALID URL #####################
        print("----INVALID URL------------- ")
        new_proxy_socket.send(FORBIDDEN_TEXT.encode())
        new_proxy_socket.close()
        print(f"conexión con {proxy_socket_address} ha sido cerrada \n\n")

    else:
        ######        request  PROXY-->SERVER         ##################
        print("----------NOT BLOCKED  SENDING REQUEST TO SERVER-----------")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((request.head['Host'], 80))
        request.head['X-ElQuePregunta'] = 'Lukas'
        server_socket.send(request.create_HTTP_message().encode())

        #######      response   SERVER-->PROXY         ################
        print('----------SERVER RESPONSE---------')
        server_buff_size = 30
        server_message = recieve_msgs(server_socket, server_buff_size)
        print(server_message)

        for pair in data['forbidden_words']:
            server_message = server_message.replace(
                list(pair.keys())[0], list(pair.values())[0])

        server_response = HttpParser()
        server_response.parse_HTTP_message(server_message)
        server_response.head['Content-Length'] = str(
            len(server_response.body.encode()))
        print('-------------RESPONSE TO CLIENT--------------- \n')
        print(server_response.create_HTTP_message())
        new_proxy_socket.send(server_response.create_HTTP_message().encode())
        server_socket.close()
        new_proxy_socket.close()
        print(f"conexión con {request.head['Host']} ha sido cerrada")
        print(f"conexión con {proxy_socket_address} ha sido cerrada")
