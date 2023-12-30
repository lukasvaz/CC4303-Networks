import math


class HttpParser:
    def __init__(self):
        self.http_message = ""
        self.head = {}
        self.body = ""

    def parse_HTTP_message(self, path: str):
        self.http_message = path
        head = dict()
        headers = self.http_message.split('\r\n\r\n')[0].split('\r\n')
        self.body = self.http_message.split('\r\n\r\n')[1]
        head['start-line'] = headers[0]
        for header in headers[1::]:
            head[header.split(':')[0]] = header.split(':')[1].strip()
        self.head = head
        return self.head

    def create_HTTP_message(self):
        headers = []
        for key, value in self.head.items():
            if key == "start-line":
                headers.append(value)
                continue
            headers.append(':'.join([key, value]))
        self.http_message = '\r\n'.join(headers)+'\r\n\r\n'+self.body
        return self.http_message

    def __str__(self) -> str:
        return self.http_message


def recieve_msgs(connection_socket, buff_size):
    """
    Recibe las responses para distintos tamaños de buffers.Priemro recibe el head  de la response
    y luego mediante el Content-Length estima la  cantidad de recv() necesarios  para recibir el body completo
    """
    end_sequence = "\r\n\r\n"
    recv_message = connection_socket.recv(buff_size)
    full_message = recv_message

    # verificamos si llegó el mensaje completo o si aún faltan partes del mensaje
    is_end_of_message = end_sequence in full_message.decode()
    while not is_end_of_message:
        # recibimos un nuevo trozo del mensaje
        recv_message = connection_socket.recv(buff_size)
        # lo añadimos al mensaje "completo"
        full_message += recv_message
        # verificamos si es la última parte del mensaje
        is_end_of_message = end_sequence in full_message.decode()

    # removemos la secuencia de fin de mensaje, esto entrega un mensaje en string
    Response = HttpParser()
    headers = Response.parse_HTTP_message(full_message.decode())

    if 'Content-Length' in headers.keys():
        remaining_bytes = int(
            headers['Content-Length'])-len(Response.body.encode())
        for i in range(math.ceil(remaining_bytes/buff_size)):
            recv_message = connection_socket.recv(buff_size)
            full_message += recv_message
    # finalmente retornamos el mensaje
    return full_message.decode()


FORBIDDEN_TEXT = """HTTP/1.1 403 Forbidden
Server: nginx/1.17.0
Date: Sat, 19 Aug 2023 23:31:20 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 149
Connection: keep-alive
Access-Control-Allow-Origin: *""".replace("\n", "\r\n")+"\r\n\r\n" +\
    """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Forbidden</title>
</head>
<body>
    <h1>Forbidden</h1>
</body>
</html>"""
