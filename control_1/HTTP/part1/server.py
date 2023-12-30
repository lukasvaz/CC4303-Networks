import socket
from utils import *
import json
import sys

# chequeamos  si se especifica el archivo de configuracion .json
try:
    with open(sys.argv[1]) as file:
            # usamos json para manejar los datos
            data = json.load(file)

except Exception as err:
    raise Exception("Especifique archivo JSON:",err)


# Definimos el tamaño del buffer de recepción y la secuencia de fin de mensaje
buff_size = 4
new_socket_address = ('localhost', 8000)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(new_socket_address)
server_socket.listen(1)

# nos quedamos esperando a que llegue una petición de conexión
print('... Esperando clientes')

while True:
    new_socket, new_socket_address = server_socket.accept()
    raw_message = receive_full_mesage(new_socket, buff_size, "\r\n\r\n")
    request = HttpParser()
    request.parse_HTTP_message(raw_message)
    request.create_HTTP_message()
    print('-------------REQUEST--------------- \n', request)

    # respondemos indicando que recibimos el mensaje
    response = HttpParser()
    response.parse_HTTP_message(RESPONSE_TEXT)
    response.head['X-ElQuePregunta'] = data['nombre']
    response.create_HTTP_message()
    print('------------------RESPONSE------------ \n', response)
    
    new_socket.send(response.create_HTTP_message().encode())

    # cerramos la conexión
    new_socket.close()
    print(f"conexión con {new_socket_address} ha sido cerrada \n\n")

    # seguimos esperando por si llegan otras conexiones
