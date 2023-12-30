import socket
import sys

DEFAULT_PORT="7000"

class Scheduler:
    def __init__(self):
        self.last_forwarding_indexes=dict() 
        self.forwarding_routes=dict() 
        self.ip_addresses="127.0.0.1" #es siempre la misma
        #check routes
    
    def check_routes(self,routes_file_name, destination_address:tuple)-> tuple:
        """Chequea si la dirección de destino se encuentra en el archivo de rutas,
          retornando  el par (next_hop_IP, next_hop_puerto), None  en caso contrario.Cuando se consulta por primera  vez una 
          direccion se recorre toda la table  guradando las  coincidencias (forwarding_routes), en una  segunda consulta se
        itera circularmente  sobre esta lista."""
        #existe la lista de rutas
        try:
            self.last_forwarding_indexes[destination_address[1]]=(self.last_forwarding_indexes[destination_address[1]]+1)%len(self.forwarding_routes[destination_address[1]])
            port =self.forwarding_routes[destination_address[1]][self.last_forwarding_indexes[destination_address[1]]]
            response=(self.ip_addresses,port)
        
        except KeyError:
            with open(routes_file_name,"r") as routes_file:
                forwarding_routes_list=list()
                for line in routes_file:
                    line=line.split()
                    if destination_address[0]==line[0] and int(line[1])<=int(destination_address[1])<=int(line[2]):
                        forwarding_routes_list.append(line[4])
                if len(forwarding_routes_list):
                    self.forwarding_routes[destination_address[1]]=forwarding_routes_list
                    self.last_forwarding_indexes[destination_address[1]]=0
                    response= (self.ip_addresses,forwarding_routes_list[0])
                else:
                    return None 
        finally:
            # print(self.forwarding_routes)
            # print(self.last_forwarding_indexes)            
            return response

# parser 
def parse_packet(IP_packet:bytes)-> dict:
    """Parsea el paquete IP y devuelve un diccionario con los campos"""
    IP_packet=IP_packet.decode()
    
    list_packet=IP_packet.split(";")
    return {"destination_address":list_packet[0],
            "destination_port":list_packet[1],
            "ttl":list_packet[2],
            "message":list_packet[3]
            }
#create
def create_packet(parsed_IP_packet:dict)->str:
    """Crea un paquete IP a partir de un diccionario"""
    return parsed_IP_packet["destination_address"]+";"+\
            parsed_IP_packet["destination_port"]+";"+\
            parsed_IP_packet["ttl"]+";"+\
            parsed_IP_packet["message"]


if __name__ == "__main__":
    #check  format
    if len(sys.argv)<4:
        raise Exception("modo de uso:python3 router.py router_IP router_puerto router_rutas.txt ")
    
    # creamos el socket cliente (no orientado a conexión)
    router_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # get parameters from command line
    router_ip=sys.argv[1]
    router_port=sys.argv[2]
    router_routes=sys.argv[3]
    print("-------ROUTER CONFIGURATION-------")
    print("router_ip: ",router_ip)
    print("router_port: ",router_port)
    print("router_routes: ",router_routes)
    print("----------------------------------")

    # hacemos bind del router socket a la dirección
    address = (router_ip, int(router_port))
    router_socket.bind(address)

    #Round Robin Scheduler  
    scheduler=Scheduler()
    # recibimos mensaje  en loop
    while True:
    # luego esperamos un mensaje de  forma bloqueante
        received_message, destination_address = router_socket.recvfrom(1000)
        parsed_message=parse_packet(received_message)
        if int(parsed_message["ttl"])>0:
            # si el mensaje  corresponde al router lo imprimimos
            if router_ip==parsed_message["destination_address"] and router_port==parsed_message["destination_port"]:
                print("mensaje recibido: ",parsed_message["message"])
            
            # si estamos  en router DEFAULT imprimimos  cualquier  mensaje
            elif  router_ip==parsed_message["destination_address"] and router_port==DEFAULT_PORT:
                print("mensaje recibido: ",parsed_message["message"])
            #forwarding
            else:
                try:                
                    ip_redirect,port_redirect=scheduler.check_routes(router_routes, (parsed_message["destination_address"],parsed_message["destination_port"]))
                    #disminuimos ttl
                    parsed_message["ttl"]=str(int(parsed_message["ttl"])-1)
                    router_socket.sendto(create_packet(parsed_message).encode(),(ip_redirect,int(port_redirect)))
                    print("redirigiendo paquete {} con destino final {} desde {}  hacia {}".format(parsed_message["destination_address"],parsed_message["destination_port"] ,router_port,port_redirect ))
                except TypeError:
                    print("No hay rutas hacia {} para paquete {} ".format(parsed_message["destination_port"],parsed_message["destination_address"]))
        else: 
            print("Se recibio  el paquete  {} con TTL 0" .format (parsed_message["destination_address"]))
