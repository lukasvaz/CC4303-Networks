class HttpParser:
    """Dado  un mensaje http este se parsea y  almacena  dentro  del objeto """
    def __init__(self):
        self.http_message = ""
        self.head = {}
        self.body = ""

    def parse_HTTP_message(self, message: str):
        '''
        Parsea un string en formato http y almacena el contenido dentro del objeto.Head corresponde a un diccionario 
        cuyas claves son las cabeceras, body es el texto correspondiente al cuerpo
        '''
        self.http_message = message
        head = dict()
        headers = self.http_message.split('\r\n\r\n')[0].split('\r\n')
        self.body = self.http_message.split('\r\n\r\n')[1]
        head['start-line'] = headers[0]
        for header in headers[1::]:
            head[header.split(':')[0]] = header.split(':')[1].strip()
        self.head = head
        return self.head

    def create_HTTP_message(self):
        """A partir del contenido almacenado en su estructura de datos  crea un mensaje HTTP"""
        headers = []
        headers.append(self.head['start-line'])
        for key, value in self.head.items():
            headers.append(':'.join([key, value]))
        self.http_message = '\r\n'.join(headers)+'\r\n\r\n'+self.body
        return self.http_message

    def __str__(self) -> str:
        return self.http_message

def receive_full_mesage(connection_socket, buff_size, end_sequence):
    # recibimos la primera parte del mensaje
    recv_message = connection_socket.recv(buff_size)
    full_message = recv_message

    # verificamos si llegó el mensaje completo o si aún faltan partes del mensaje
    is_end_of_message = contains_end_of_message(
        full_message.decode(), end_sequence)

    while not is_end_of_message:
        # recibimos un nuevo trozo del mensaje
        recv_message = connection_socket.recv(buff_size)

        # lo añadimos al mensaje "completo"
        full_message += recv_message

        # verificamos si es la última parte del mensaje
        is_end_of_message = contains_end_of_message(
            full_message.decode(), end_sequence)

    return full_message.decode()


def contains_end_of_message(message, end_sequence):
    return message.endswith(end_sequence)

RESPONSE_TEXT = """HTTP/1.1 200 OK
Server: nginx/1.17.0
Date: Sat, 19 Aug 2023 23:31:20 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 237
Connection: keep-alive
Access-Control-Allow-Origin: *""".replace("\n", "\r\n")+"\r\n\r\n" +\
    """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>CC4303</title>
</head>
<body>
    <h1>Bienvenide ... oh? no puedo ver tu nombre :c!</h1>
    <h3><a href="replace">¿Qué es un proxy?</a></h3>
</body>
</html>"""
