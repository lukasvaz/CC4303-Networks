import socket
import sys

DEFAULT_PORT="7000"

class Scheduler:
    def __init__(self):
        self.last_forwarding_indexes=dict() 
        self.forwarding_routes=dict() 
        self.forwarding_MTU=dict() 
        self.ip_addresses="127.0.0.1" #es siempre la misma
        #check routes
    
    def check_routes(self,routes_file_name, destination_address:tuple)-> tuple:
        """Chequea si la dirección de destino se encuentra en el archivo de rutas,
          retornando  3-tupla ((ip_address,next_hop_puerto), MTU), None  en caso contrario.Cuando se consulta por primera  vez una 
          direccion se recorre toda la table  guradando las  coincidencias (forwarding_routes), en una  segunda consulta se
        itera circularmente  sobre esta lista."""
        #existe la lista de rutas
        if destination_address[1] in self.forwarding_routes:
            #incremento el indice
            self.last_forwarding_indexes[destination_address[1]]=(self.last_forwarding_indexes[destination_address[1]]+1)%len(self.forwarding_routes[destination_address[1]])
            
            #busco campos
            port =self.forwarding_routes[destination_address[1]][self.last_forwarding_indexes[destination_address[1]]]
            mtu=self.forwarding_MTU[destination_address[1]][self.last_forwarding_indexes[destination_address[1]]]
            response=((self.ip_addresses,port),mtu)
        
        else:
            with open(routes_file_name,"r") as routes_file:
                forwarding_routes_list=list()
                MTU_list=list()
                for line in routes_file:
                    line=line.split()
                    #se buscan coincidencias 
                    if destination_address[0]==line[0] and int(line[1])<=int(destination_address[1])<=int(line[2]):
                        forwarding_routes_list.append(line[4])
                        MTU_list.append(line[5])
                # si  hay  coincidencias  , las  agrego  a la estructura
                if len(forwarding_routes_list):
                    self.forwarding_routes[destination_address[1]]=forwarding_routes_list
                    self.forwarding_MTU[destination_address[1]]=MTU_list
                    self.last_forwarding_indexes[destination_address[1]]=0
                    response= ((self.ip_addresses,forwarding_routes_list[0]),MTU_list[0])
                else:
                    return None 

        return response

# parser 
def parse_packet(IP_packet:bytes)-> dict:
    """Parsea el paquete IP y devuelve un diccionario con los campos"""
    IP_packet=IP_packet.decode()
    
    list_packet=IP_packet.split(";")
    return {"destination_address":list_packet[0], #127.0.0.1
            "destination_port":list_packet[1], # 4 digitos
            "ttl":in_digits(3,list_packet[2]), # 3 digitos 
            "id":in_digits(8,list_packet[3]), # 8 digitos
            "offset":in_digits(8,list_packet[4]),# 8 digitos
            "size":in_digits(8,list_packet[5]),#8 digitos en bytes , sin considerar  header
            "flag":list_packet[6],# 1  digito , 0-> ultimo fragmento, 1-> mas fragmentos
            "message":list_packet[7]
            }
#create
def create_packet(parsed_IP_packet:dict)->str:
    """Crea un paquete IP a partir de un diccionario"""
    return parsed_IP_packet["destination_address"]+";"+\
            parsed_IP_packet["destination_port"]+";"+\
            parsed_IP_packet["ttl"]+";"+\
            parsed_IP_packet["id"]+";"+\
            parsed_IP_packet["offset"]+";"+\
            parsed_IP_packet["size"]+";"+\
            parsed_IP_packet["flag"]+";"+\
            parsed_IP_packet["message"]

#digits
def in_digits(digits:int,original:str)->str:
    """Devuelve un string con el numero de digitos solicitados  en digit"""
    if len(original)>digits:
        raise Exception("{} tiene mas digitos que  {} los solicitados ".format(original,digits))
    return '0'*(digits-len(original))+original

#fragmentos
def fragment_packet(IP_packet:bytes,MTU:int)->list:
    """Dado  un paquete  (headers incluidos) y  un MTU lo fragmenta  en una lista de paquetes IP"""
    parsed_message=parse_packet(IP_packet)
    fragments=list()
    #mas grande  que MTU, fragmentamos
    if len(IP_packet)>MTU:
        max_bytes_per_message=MTU-48 # bytes de header:48
        message=parsed_message["message"]
        count=0
        #generamos fragmentos
        while len(message)>max_bytes_per_message:
            package={
            "destination_address":parsed_message["destination_address"],
            "destination_port":parsed_message["destination_port"],
            "ttl":parsed_message["ttl"],
            "id":parsed_message["id"],
            "offset":str((int(parsed_message["offset"])+count)*max_bytes_per_message),
            "size":str(max_bytes_per_message),
            "flag":"1",
            "message":parsed_message["message"][count*max_bytes_per_message:count*max_bytes_per_message+max_bytes_per_message]
            }
            message=message[max_bytes_per_message::]
            fragments.append(package)
            count+=1
        
        #ultimo fragmento del paquete
        #que el fragmento sea  final o no depende del flag del paquete original 
        package={
            "destination_address":parsed_message["destination_address"],
            "destination_port":parsed_message["destination_port"],
            "ttl":parsed_message["ttl"],
            "id":parsed_message["id"],
            "offset":str((int(parsed_message["offset"])+count)*max_bytes_per_message),            
            "size":str(len(message)),
            "flag":parsed_message["flag"],
            "message":message            
            }
        fragments.append(package)
    #menor que MTU, lista de un elemento
    else:
        fragments.append(parsed_message)
    return fragments

def reassemble_IP_packet(fragment_list:list):
    """Reconstruye un paquete IP a partir de una lista de fragmentos IP parseados"""
    #si hay un fragmento con flag 0, es el ultimo
    if  "0"  in  [fragment["flag"] for  fragment  in fragment_list]:
        #obtenemos el tamaño del mensaje y creamos  un arreglo de 0s de ese tamaño
        offsets=[int(fragment["offset"]) for fragment in fragment_list]    
        message_size=max(offsets)+int(fragment_list[offsets.index(max(offsets))]["size"])
        reassemble_array=[0]*message_size
        #armamos el mensaje
        for fragment in fragment_list:
            for i in range(int(fragment["size"])):
                reassemble_array[int(fragment["offset"])+i]=fragment["message"][i]
        #si no hay 0 en el mensaje, lo devolvemos
        if 0 not in reassemble_array:
            return "".join(reassemble_array)
    return None

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
    #almacenamiento de fragmentos
    fragment_dict=dict()
    # recibimos mensaje  en loop

    while True:
    # luego esperamos un mensaje de  forma bloqueante
        received_message, destination_address = router_socket.recvfrom(1000)
        parsed_message=parse_packet(received_message)
        if int(parsed_message["ttl"])>0:
            # si el mensaje  corresponde al router lo imprimimosc
            if router_ip==parsed_message["destination_address"] and router_port==parsed_message["destination_port"]:
                if parsed_message["id"] in fragment_dict:
                    fragment_dict[parsed_message["id"]].append(parsed_message) 
                else:
                    fragment_dict[parsed_message["id"]]=[parsed_message]
                
                response=reassemble_IP_packet(fragment_dict[parsed_message["id"]])
                if response:
                    print("mensaje recibido: ",response)
                    del fragment_dict[parsed_message["id"]]

            # si estamos  en router DEFAULT imprimimos  cualquier  mensaje
            elif  router_ip==parsed_message["destination_address"] and router_port==DEFAULT_PORT:
                print("mensaje recibido: ",parsed_message["message"])

            #forwarding
            else:
                try:
                    #obtenemos ip,ruta,mtu                
                    (ip_redirect,port_redirect),mtu=scheduler.check_routes(router_routes, (parsed_message["destination_address"],parsed_message["destination_port"]))
                    #fragmentamos mensaje
                    fragments=fragment_packet(received_message,51)
                    #disminuimos ttl
                    new_ttl=str(int(parsed_message["ttl"])-1)
                    for fragment in fragments:
                        fragment["ttl"]=new_ttl
                        router_socket.sendto(create_packet(fragment).encode(),(ip_redirect,int(port_redirect)))
                        print("redirigiendo paquete {} con destino final {} desde {}  hacia {}".format(parsed_message["destination_address"],parsed_message["destination_port"] ,router_port,port_redirect ))
                except TypeError as e:
                    print(e)
                    print("No hay rutas hacia {} para paquete {} ".format(parsed_message["destination_port"],parsed_message["destination_address"]))
        else: 
            print("Se recibio  el paquete  {} con TTL 0" .format (parsed_message["destination_address"]))
