import socket
import sys

DEFAULT_PORT = "7000"
IP_ADDRESS = "127.0.0.1"

            

class BGPHandler:
    def __init__(self, routes_path, asn, router_socket):
        self.asn = asn
        self.routes = dict()  # rutas como diccionario de listas, key = destino
        self.table = dict()  # contenido de la tabla
        self.routes_path = routes_path
        self.parsed_message = None  # ultimo mensaje recibido
        self.router_socket = router_socket
        self.neighbours = list()  # vecinos

        with open(self.routes_path, "r") as routes_file:
            table = ""
            for line in routes_file:
                self.table[line.split()[1]] = line  # actualizamos tabla
                self.routes[line.split()[1]] = line.split()[
                    1:-3]  # actualizamos rutas
                self.neighbours.append(line.split()[-2])
            
            table = table.split("\n")


        # # buscamos vecinos
        # neighbours = list()
        # for route in self.routes.values():
        #     # routerA..... routerVECINO routerTHIS
        #     neighbours.append(route[-2])
        # self.neighbours = set(neighbours)

    def create_BGP_message(self, mode='BGP') -> str:
        """Crea  un mensaje BGP con las rutas a partir de con el siguiente formato:
        *si mode es BGP: 
                BGP_ROUTES
                888x (ASN)
                [ruta ASN]
                (... maś rutas)
                [ruta ASN]
                END_BGP_ROUTES
        *si mode es START:
                START_BGP 
            """
        if mode == 'BGP':
            message = "BGP_ROUTES\n"
            message += self.asn+"\n"
            for line in self.routes.values():
                message += " ".join(line)+"\n"
            message += "END_BGP_ROUTES\n"
            return message

        if mode == "START":
            return "START_BGP"

    def send_routes_to_neighbours(self):
        # a cada vecino se le envian  las rutas de este router
        for neighbour in self.neighbours:
            package = {
                "destination_address": IP_ADDRESS,
                "destination_port": neighbour,
                "ttl": self.parsed_message["ttl"],
                "id": self.parsed_message["id"],
                "offset": self.parsed_message["offset"],
                "size": self.parsed_message["size"],
                "flag": self.parsed_message["flag"],
                "message": self.create_BGP_message(mode="BGP")
            }
            print(">enviando rutas  a vecinos: desde {} a {}".format(self.asn, neighbour))
            self.router_socket.sendto(create_packet(
                package).encode(), (IP_ADDRESS, int(neighbour)))

    def run_BGP(self):
        """Ejecuta el protocolo BGP y devuelve la tabla actualizada"""
        print("--Iniciando protocolo BGP--")
        # a cada vecino le enviamos  un mensaje de inicio
        for neighbour in self.neighbours:
            package = {
                "destination_address": IP_ADDRESS,
                "destination_port": neighbour,
                "ttl": self.parsed_message["ttl"],
                "id": self.parsed_message["id"],
                "offset": self.parsed_message["offset"],
                "size": self.parsed_message["size"],
                "flag": self.parsed_message["flag"],
                "message": self.create_BGP_message(mode="START")
            }
            self.router_socket.sendto(create_packet(
                package).encode(), (IP_ADDRESS, int(neighbour)))

        # a cada vecino se le envian  las rutas de este router
        self.send_routes_to_neighbours()
        # esperamos  mensajes desde los vecinos
        print("--Esperando rutas vecinas--")
        try:
            while True:
                self.router_socket.settimeout(10)
                received_message, _ = self.router_socket.recvfrom(1000)
                parsed_message = parse_packet(received_message)

                # si es un mensaje START_BGP lo ignoramos
                if parsed_message["message"] == "START_BGP":
                    continue
                # si son  rutas
                message_list = parsed_message["message"].split("\n")
                print(">_ rutas recibidas desde {}".format(message_list[1]))
                new_routes = list()
                for route in message_list[2:-2]:
                    route = route.split()
                    # si se  agrega  un router  nuevo a la red  con destino este router
                    # print(route[-1],route[0])
                    
                    if route[-1] not in self.neighbours and route[0] == self.asn:
                        self.neighbours.append(route[-1])
                        print("nuevo vecino agregado: ", route[-1])
                        self.routes[route[-1]]=[x for x in reversed(route)]    
                        self.table[route[-1]]="127.0.0.1 "+" ".join(reversed(route))+" 127.0.0.1 "+route[-2]+" 100\n"
                        new_routes.append(route)
                        self.send_routes_to_neighbours() 
                        print(self.routes)
                        print(self.table)
                        print(new_routes)
                    # si este router eta presente en la ruta se ignora
                    if self.asn in route:
                        continue
                    # si la ruta no esta en las rutas actuales se agrega
                    elif route[0] not in self.routes.keys():
                        route.append(self.asn)
                        self.routes[route[0]] = route
                        self.table[route[0]]="127.0.0.1 "+" ".join(route)+" 127.0.0.1 "+route[-2]+" 100\n"
                        # si hay cambio en self.routes -> enviamos a los vecinos
                        print("nueva ruta anadida: ", route)
                        new_routes.append(route)
                        self.send_routes_to_neighbours()

                    #  si está
                    else:
                        if len(route)+1 < len(self.routes[route[0]]):
                            print("remplazando {} por {}".format(self.routes[route[0]], route))
                            del self.routes[route[0]]
                            del self.table[route[0]]
                            route.append(parsed_message["destination_port"])
                            new_routes.append(route)
                            self.send_routes_to_neighbours()

        except TimeoutError:
            print()
            print("----BGP finalizado----")
            # for route in new_routes:
            #         self.table[route[0]]="127.0.0.1 "+" ".join(route)+" 127.0.0.1 "+route[-2]+" 100\n"
            print("Tabla actualizada para {}:".format(self.asn))
            print("".join(self.table.values()))
            return "".join(self.table.values())

def check_routes_bgp( routes_file_name, destination_address: tuple) -> tuple:
    """Encuentra la direcccion  para  hacer el siguiente salto. Como por bgp solo habrá  una coincidencia 
    para cada destino final (camino más corto) se devuelve la primera coincidencia sin necesidad de un Scheduler"""
    with open(routes_file_name, "r") as routes_file:
        for line in routes_file:
            line = line.split()
            # se buscan coincidencias
            if destination_address[0] == line[0] and destination_address[1] == line[1]:
                return (IP_ADDRESS,line[-2]),line[-1]

# parser
def parse_packet(IP_packet: bytes) -> dict:
    """Parsea el paquete IP y devuelve un diccionario con los campos"""
    IP_packet = IP_packet.decode()

    list_packet = IP_packet.split(";")
    return {"destination_address": list_packet[0],  # 127.0.0.1
            "destination_port": list_packet[1],  # 4 digitos
            "ttl": in_digits(3, list_packet[2]),  # 3 digitos
            "id": in_digits(8, list_packet[3]),  # 8 digitos
            "offset": in_digits(8, list_packet[4]),  # 8 digitos
            # 8 digitos en bytes , sin considerar  header
            "size": in_digits(8, list_packet[5]),
            # 1  digito , 0-> ultimo fragmento, 1-> mas fragmentos
            "flag": list_packet[6],
            "message": list_packet[7]
            }


def create_packet(parsed_IP_packet: dict) -> str:
    """Crea un paquete IP a partir de un diccionario"""
    return parsed_IP_packet["destination_address"]+";" +\
        parsed_IP_packet["destination_port"]+";" +\
        parsed_IP_packet["ttl"]+";" +\
        parsed_IP_packet["id"]+";" +\
        parsed_IP_packet["offset"]+";" +\
        parsed_IP_packet["size"]+";" +\
        parsed_IP_packet["flag"]+";" +\
        parsed_IP_packet["message"]

# digits


def in_digits(digits: int, original: str) -> str:
    """Devuelve un string con el numero de digitos solicitados  en digit"""
    if len(original) > digits:
        raise Exception(
            "{} tiene mas digitos que  {} los solicitados ".format(original, digits))
    return '0'*(digits-len(original))+original

# fragmentos


def fragment_packet(IP_packet: bytes, MTU: int) -> list:
    """Dado  un paquete  (headers incluidos) y  un MTU lo fragmenta  en una lista de paquetes IP"""
    parsed_message = parse_packet(IP_packet)
    fragments = list()
    # mas grande  que MTU, fragmentamos
    if len(IP_packet) > MTU:
        max_bytes_per_message = MTU-48  # bytes de header:48
        message = parsed_message["message"]
        count = 0
        # generamos fragmentos
        while len(message) > max_bytes_per_message:
            package = {
                "destination_address": parsed_message["destination_address"],
                "destination_port": parsed_message["destination_port"],
                "ttl": parsed_message["ttl"],
                "id": parsed_message["id"],
                "offset": str((int(parsed_message["offset"])+count)*max_bytes_per_message),
                "size": str(max_bytes_per_message),
                "flag": "1",
                "message": parsed_message["message"][count*max_bytes_per_message:count*max_bytes_per_message+max_bytes_per_message]
            }
            message = message[max_bytes_per_message::]
            fragments.append(package)
            count += 1

        # ultimo fragmento del paquete
        # que el fragmento sea  final o no depende del flag del paquete original
        package = {
            "destination_address": parsed_message["destination_address"],
            "destination_port": parsed_message["destination_port"],
            "ttl": parsed_message["ttl"],
            "id": parsed_message["id"],
            "offset": str((int(parsed_message["offset"])+count)*max_bytes_per_message),
            "size": str(len(message)),
            "flag": parsed_message["flag"],
            "message": message
        }
        fragments.append(package)
    # menor que MTU, lista de un elemento
    else:
        fragments.append(parsed_message)
    return fragments


def reassemble_IP_packet(fragment_list: list):
    """Reconstruye un paquete IP a partir de una lista de fragmentos IP parseados"""
    # si hay un fragmento con flag 0, es el ultimo
    if "0" in [fragment["flag"] for fragment in fragment_list]:
        # obtenemos el tamaño del mensaje y creamos  un arreglo de 0s de ese tamaño
        offsets = [int(fragment["offset"]) for fragment in fragment_list]
        message_size = max(
            offsets)+int(fragment_list[offsets.index(max(offsets))]["size"])
        reassemble_array = [0]*message_size
        # armamos el mensaje
        for fragment in fragment_list:
            for i in range(int(fragment["size"])):
                reassemble_array[int(fragment["offset"]) +
                                 i] = fragment["message"][i]
        # si no hay 0 en el mensaje, lo devolvemos
        if 0 not in reassemble_array:
            return "".join(reassemble_array)
    return None


if __name__ == "__main__":
    # check  format
    if len(sys.argv) < 4:
        raise Exception(
            "modo de uso:python3 router.py router_IP router_puerto router_rutas.txt ")

    # creamos el socket cliente (no orientado a conexión)
    router_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # get parameters from command line
    router_ip = sys.argv[1]
    router_port = sys.argv[2]
    router_routes = sys.argv[3]
    print("-------ROUTER CONFIGURATION-------")
    print("router_ip: ", router_ip)
    print("router_port: ", router_port)
    print("router_routes: ", router_routes)
    print("----------------------------------")

    # hacemos bind del router socket a la dirección
    address = (router_ip, int(router_port))
    router_socket.bind(address)

    # almacenamiento de fragmentos
    fragment_dict = dict()
    #primer lop  para  encontrar rutas  mediante BGP
    bgp_handler = BGPHandler(router_routes, router_port, router_socket)
    
    while True:
        router_socket.settimeout(None)
        # luego esperamos un mensaje de  forma bloqueante
        received_message, destination_address = router_socket.recvfrom(1000)
        parsed_message = parse_packet(received_message)
        if int(parsed_message["ttl"]) > 0:
            # si el mensaje  corresponde al router lo imprimimosc
            if router_ip == parsed_message["destination_address"] and router_port == parsed_message["destination_port"]:
                
                if parsed_message["id"] in fragment_dict:
                    fragment_dict[parsed_message["id"]].append(parsed_message)
                else:
                    fragment_dict[parsed_message["id"]] = [parsed_message]

                response = reassemble_IP_packet(
                    fragment_dict[parsed_message["id"]])
                # cuando se recupera el mensaje completo
                if response:
                    print("mensaje recibido: ", response)
                    # eliminamos el id del diccionario con su contenido
                    del fragment_dict[parsed_message["id"]]
                    # si se solicita iniciar BGP
                    if response == "START_BGP":
                        print("mensaje recibido {}, iniciando BGP".format( response))
                        bgp_handler.parsed_message = parsed_message
                        new_table=bgp_handler.run_BGP()
                        # escribimos las nuevas rutas en la tabla
                        with open("tablas_bgp/nuevas_ruta{}.txt".format(router_port), "w") as routes_file:
                                routes_file.write(new_table)

                        #cambiamos  direccion a tablas
                        router_routes="tablas_bgp/nuevas_ruta{}.txt".format(router_port)

            # forwarding
            else:
                try:
                    # obtenemos ip,ruta,mtu
                    (ip_redirect, port_redirect), mtu = check_routes_bgp(router_routes,(parsed_message["destination_address"], parsed_message["destination_port"]))
                    # fragmentamos mensaje
                    fragments = fragment_packet(received_message, 51)
                    # disminuimos ttl
                    new_ttl = str(int(parsed_message["ttl"])-1)
                    for fragment in fragments:
                        fragment["ttl"] = new_ttl
                        router_socket.sendto(create_packet(
                            fragment).encode(), (ip_redirect, int(port_redirect)))
                        print("redirigiendo paquete {} con destino final {} desde {}  hacia {}".format(
                            parsed_message["destination_address"], parsed_message["destination_port"], router_port, port_redirect))
                except TypeError as e:
                    print(e)
                    print("No hay rutas hacia {} para paquete {} ".format(
                        parsed_message["destination_port"], parsed_message["destination_address"]))
        else:
            print("Se recibio  el paquete  {} con TTL 0" .format(
                parsed_message["destination_address"]))
