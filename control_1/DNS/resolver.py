import socket
import dnslib
import queue
from dnslib import DNSRecord,RR,A
from dnslib.dns import CLASS, QTYPE

ROOT_ADDRESS = '192.33.4.12'

class Cache:
    """
    Este objeto tiene por objetivo manejar  las operaciones y datos asociados al cache. 
    Contiene tres atributos principales:
    history-> cola en la que se almacena el nombre  (Qname) las últimas 20 consultas
    count-> diccionario  que tiene por claves los nombres  de consultados  y por valor  la direccion
            de cada uno  y la cantidad de veces (times) que cada uno ha sido consultado
    available_responses-> diccionario que tiene por claves los 5 nombres  de dominio  más consultados y por valor 
                        la direccion de cada uno. Este es la estructura en la que se va buscar al realizar una consulta

    """
    def __init__(self):
        self.history=queue.Queue(maxsize=20)
        self.count=dict()
        self.available_responses=dict()

    def add_to_count(self,name,address):
        """
        Ingresa  name a self.count con cierta address y un valor de ocurrencias igual a 1  
        """
        if name not in self.count.keys():
            self.count[name]= {'address':address,
                                'times':1}
        else:
            raise Exception("element already in count dict")

    def update_times(self,name,times):
        """
        Para cierto nombre de dominio presente en count actualiza su numero de ocurrencias times veces.
        """
        if name in self.count.keys():
            prev_number=self.count[name]['times']
            self.count[name]['times']=prev_number+times
        
            if  self.count[name]['times']==0:
                self.count.pop(name)
        else:
            raise Exception("element not in count dict")
    
    def update_queue(self,name):
        """
        Actualiza la cola de consultas.Si la cola está llena (20 entradas) se extrae el ultimo valor  y se le resta -1  
        a sus ocurrencias en self.count y se agrega  name a la cola.Si no está llena agrega el valor a la cola.
        """
        if self.history.full():
            get_name=self.history.get()
            self.update_times(get_name,-1)
            self.history.put(name)
        else:
            self.history.put(name)

    def save_response(self,response:bytes,debug=False):
        """Implementa la logica necesaria para guardar una nueva respuesta obtenida en cache.Actualiza la cola ,luego el contador 
        y setea las respuestas disponibles (self.available responses) con los 5 elemntos en self.count con mas ocurrencias """
        response=my_DNS_parse(response)
        cache_element={
            'name':response['Qname'],
            'address':response['Answer']['rdata']        
        }

        #actualizamos la cola (extraemos elemnto si size> 20 y agregamos elemento nuevo)
        self.update_queue(cache_element['name'])
        
        # agregar elemento a count
        if cache_element['name'] in self.count.keys(): 
            self.update_times(cache_element['name'],+1)
        else:
            self.add_to_count(cache_element['name'],cache_element['address'])
        
        #actualizar available responses
        search=self.count.copy()
        top=dict()
        for _ in range(5):
            try:
                max_name=max(search,key=lambda x: search[x]['times'])
                if max_name:
                    value=search.pop(max_name)
                    top[max_name]=value['address']
            except:
                break
        self.available_responses=top
        if debug:
            print("(debug) Cache")
            print(self)   

    def generate_response(self,message,debug=False):
        """Implementa la logica necesaria para entregar una respuesta que ya está en el cache.Actualiza la cola (self.history),
        suma 1 al valor  del elemento consultado, actualiza las respuesta disponibles (self.available_responses) con los 5 elementos en self.count 
        con maś ocurrencias y por último genera la respuesta y la retorna"""
        query=DNSRecord.parse(message)
        qname=query.get_q().get_qname()
        
        #actualizamos la cola (extraemos elemnto si size> 20 y agregamos elemento nuevo)
        self.update_queue(qname)
        
        #sumamos  1 request al elemento 
        self.update_times(qname,+1)
        
        #actualizar top
        search=self.count.copy()
        top=dict()
        for _ in range(5):
            try:
                max_name=max(search,key=lambda x: search[x]['times'])
                if max_name:
                    value=search.pop(max_name)
                    top[max_name]=value['address']
            except:
                break
        self.available_responses=top

        #agregamos respuesta al mensaje
        query.add_answer(RR(str(qname),rdata=A(str(cache.available_responses[qname]))))        

        if debug:
            print("(debug)Consultando por {}".format(qname))
            print("(debug)Response in Cache\n",self,"(debug){} in cache , sending response".format(qname))
            print()
            
        return query

    def __str__(self):
        return "(debug)Cache:\n(debug)cache options: {} \n(debug)count dictionary:{}\n".format(str(self.available_responses),str(self.count))

def send_dns_message(qname, address, port):
    # Acá ya no tenemos que crear el encabezado porque dnslib lo hace por nosotros, por default pregunta por el tipo A
    q = DNSRecord.question(qname)
    server_address = (address, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # lo enviamos, hacemos cast a bytes de lo que resulte de la función pack() sobre el mensaje
        sock.sendto(bytes(q.pack()), server_address)
        # En data quedará la respuesta a nuestra consulta
        data, _ = sock.recvfrom(4096)
    finally:
        sock.close()    # Ojo que los datos de la respuesta van en en una estructura de datos
    return data


def my_DNS_parse(dns_msg: bytes):
    """
    Recibe  una mensaje DNS en bytes y lo transforma  a un diccionario de python. Las claves 
    del diccionario son: 
        Qname->nombre consultado
        ANCOUNT->numero respuestas en la seccion Answer
        NSCOUNT-># de respuestas en la seccion Authority
        ARCOUNT-># de respuestas en la seccion Aditional
        Answer(rtype ,rdata)-> informacion de la seccion Answer (rtype:tipo (A, AAAA,etc) rdata: direccion)
        Authority-> informacion de la seccion Authority (rtype:tipo (A, NS ,etc) rdata: direccion)
        Aditional-> informacion de la seccion Aditional (rtype:tipo (A, AAAA) rdata: direccion)
    """
    dns_msg = DNSRecord.parse(dns_msg)
    parameters = dict()
    parameters['Qname'] = dns_msg.get_q().get_qname()
    parameters['ANCOUNT'] = dns_msg.header.a
    parameters['NSCOUNT'] = dns_msg.header.auth
    parameters['ARCOUNT'] = dns_msg.header.ar

    if parameters['ANCOUNT'] > 0:
        parameters['Answer'] = {
            'rtype': QTYPE.get(dns_msg.get_a().rtype),
            'rdata': dns_msg.get_a().rdata
        }

    if parameters['NSCOUNT'] > 0:
        parameters['Authority'] = {
            'rtype': QTYPE.get(dns_msg.auth[0].rtype)}
        
        parameters['Authority']['primary_server'] = dns_msg.auth[0].rdata

    if parameters['ARCOUNT'] > 0:
        parameters['Aditional']=[]
        for aditional_responses in dns_msg.ar: 
            parameters['Aditional'].append ({
                'rtype': QTYPE.get(aditional_responses.rtype),
                'rdata': str(aditional_responses.rdata)
            })

    return parameters


def solve_recursive(qname, address,debug,):
    """
    Recibe  un nombre a consultar (qname) y  una direccion donde consultar (address) entregando la respuesta en bytes.
    
    Envía la consulta por qname a address mediante send_dns_message  si  en la respuesta  hay  una seccion answer la retorna inmediatamente, si no 
    procede a buscar una respuesta tipo A en la seccion Aditional , si se encuentra  se vuelve (recursivamente) al paso 1  retrnando 
    una vez se obtenga una seccion answer . si no hay una respuesta tipo A en aditional,  se redirige la consulta  a  un nameserver
    en Authority, para esto primero se resuelve recursivamente  la direccion del server y luego se  vuelve (recursivamente) la paso 1 
    
    """

    if debug:
        print("(debug) consultando {} a {}".format(qname, address))
    answer = send_dns_message(qname, address, 53)
    parsed_answer = my_DNS_parse(answer)

    if parsed_answer['ANCOUNT'] > 0 and parsed_answer['Answer']['rtype']=='A':
        # print(parsed_answer)
        if debug:
            print("(debug) {} solved: {}".format(parsed_answer['Qname'],parsed_answer['Answer']['rdata']))
            print()
        return answer

    #  si la respuesta es una delegacion a otro NS (respuestas tipo NS en Authority
    elif parsed_answer['NSCOUNT'] > 0 and parsed_answer['Authority']['rtype'] == 'NS':
        if parsed_answer['ARCOUNT'] > 0 and any([x['rtype']=='A' for x in parsed_answer['Aditional'] ]):
            # revisar todas  las  rptas tipo A en Aditional     
            Aditional_list_A=[x for x in filter(lambda x : x['rtype']=='A',parsed_answer['Aditional'])]
            response=Aditional_list_A.pop()
            new_address = response['rdata']
            return solve_recursive(qname, new_address, debug)
        else:
            server_name = str(parsed_answer['Authority']['primary_server'])
            response=solve_recursive(server_name, ROOT_ADDRESS, debug)
            response=my_DNS_parse(response)
            new_address= str(response['Answer']['rdata'])
            return solve_recursive(qname, new_address, debug)


def resolver(mensaje_consulta, debug=False):
    """
    A partir de un consulta DNS en bytes, resuelve  y devuelve el resultado en bytes
    """
    query_id = DNSRecord.parse(mensaje_consulta).header.id
    mensaje_consulta = my_DNS_parse(mensaje_consulta)
    qname = mensaje_consulta["Qname"]
    response = solve_recursive(qname, ROOT_ADDRESS, debug)
        
    response = DNSRecord.parse(response)
    response.header.id = query_id
    return response.pack()


server_address = ('localhost', 8000)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(server_address)
cache= Cache()
while True:
    try:

        recv_message, client_address = server_socket.recvfrom(1024)
        query=DNSRecord.parse(recv_message)
        qname=query.get_q().get_qname()
        
        if  qname in cache.available_responses:
            response=cache.generate_response(recv_message,debug=True)
            server_socket.sendto(response.pack(), client_address)
            
        else:
            response = resolver(recv_message, debug=True)
            cache.save_response(response)
            response = DNSRecord.parse(response)
            print(cache)
            server_socket.sendto(response.pack(), client_address)

    except KeyboardInterrupt:
        server_socket.close()
        print(f"Cerrando socket  en {server_address}")



