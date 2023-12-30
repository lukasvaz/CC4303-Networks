# Informe Forwarding
* **Alumno**:Lukas Vasquez Verdejo

## ¿ Cual es la diferencia entre la tabla de ruta  utilizada  en la acticidad versus las tablas  de rutas reales ?
* Las tablas de ruta originales  poseen información sobre la red de destino del mensaje (por ejemplo 12.0.0.0/16) correspondiente a un "rango" de direcciones IP dado por la máscara, en el caso de la actividad  se tendrá  que esta red es única, pues al ser local posee  una unica IP.Para soslayar esto, en la   actividad se  tendrá  un "rango" de puertos  a los que acceder (por ejemplo   8882 8882).  


## Explicación  Código (sin TTL)
En  esta  actividad  se implementa  una  versión  simplificada del proceso de forwarding

### Forwarding 
La logica  del  forwarding  se encuentra  en  la funcion check_routes(). Esta funcion toma  un archivo  de rutas  , se parsea (split()) y finalmente se  chequea  si la direccion del puerto está  contenida  dentro  del archivo (if destination_address[0]==line[0] and int(line[1])<=int(destination_address[1])<=int(line[2])). En el caso de estar retorna  el  par (IP , puerto) del forwarding correspondiente, en el caso de no estar retorna  None. 

### Round Robin
Para  implementar  el Round Robin se  implementa  una clase (Scheduler) y se  impementa  check_routes  como  método de esta. Para lograr esperado  se  hace  lo siguiente:
- Cuando  una direccion  es  consultada  por  primera vez, se almacenan los  puertos de destino  que  coincidan con la diraccion en cuesion (self.forwarding_routes) y  se setea su  indice  en 0.
- Cuando  una  direccion es consultada  por segunda  vez  o posterior, se  busca  en la lista almacenada  en self.forwarding_routes  y se entrega  la direccion siguiente (de manera circular) a la que  se  consulto  anteriormente (index+1)%len(self.forwarding_routes).

### Tabla  de rutas para el Router  DEFAULT 
 Para  implementar  el router  default  , solo  se necesitó agregar  una  condición  en que  si el puerto del router actual  corresponde a la puerto default (7000)
este debe  retornar (imprimir) inmediatamente.

Para  que una tabla de ruta (digamos  que redirige para las direcciones [x, y] )  redirigan  automáticamente  al puerto DEFAULT  se    impone que: 
* si 0<direccion < x -> redirige a 7000
* si y<direccion < 65535 -> redirige a 7000

Así la tabla  para el router 0  queda:

127.0.0.1 8881 8886 127.0.0.1 8881
127.0.0.1 8881 8886 127.0.0.1 8882
127.0.0.1 0000 8880 127.0.0.1 7000
127.0.0.1 8887 65535 127.0.0.1 7000

### Pruebas  sin TTL
**En las instrucciones de la actividad, habían ejemplos  en que el separador del mensaj eran comas  y otros punto y coma.Para  los test se  ocupa el  separador  punto y coma (p ej 127.0.0.1;8884;hola)**  

* **TEST 1:ejemplo 2 con  error**: Si se cambia 8883 por  8881  lo que va a ocurrir  es  que  va a ser  iposible  acceder  a R3 desde R1 o R2.   

Así  si  consultamos por R3 a R1 , el resultado es :
```
redirigiendo paquete 127.0.0.1 con destino final 8883 desde 8881  hacia 8882
redirigiendo paquete 127.0.0.1 con destino final 8883 desde 8881  hacia 8882
redirigiendo paquete 127.0.0.1 con destino final 8883 desde 8881  hacia 8882
redirigiendo paquete 127.0.0.1 con destino final 8883 desde 8881  hacia 8882
redirigiendo paquete 127.0.0.1 con destino final 8883 desde 8881  hacia 8882
redirigiendo paquete 127.0.0.1 con destino final 8883 desde 8881  hacia 8882
```
Es decir el mesnsaje  se redirige  a R2, luego a R1 y  se  queda  en un loop infinito.Si  consultamos por R3 a R2 , el resultado es similar. 

* **TEST2:round robin**: al enviar paquetes desde R1 a R5  se  otiene lo siguiente:
```
-------ROUTER CONFIGURATION-------
router_ip:  127.0.0.1
router_port:  8882
router_routes:  tablas/test2/rutas_R2.txt
----------------------------------
redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8882  hacia 8883
redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8882  hacia 8884
redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8882  hacia 8883
redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8882  hacia 8884

```
Se puede  observar  que se alternan  los camino R2-R3  y R2-R4  para  llegar a R5 según el Round Robin.Dada  la  forma  del grafo de la Red  se puede afirmar que los pquetes  siempre dan 3 saltos  correspondiente a la cantidad mínima.

## test 3
Se agrega un router R0  conectado a R1 y R2  y también un  R6 conectado a R2 y R3 (el contenido de las rutas  esta en ./test3). Se  envían  mensajes  desde R1 a R5:

```
//En R1
-------ROUTER CONFIGURATION-------
router_ip:  127.0.0.1
router_port:  8881
router_routes:  tablas/test3/rutas_R1_v3.txt
----------------------------------
redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8881  hacia 8882
redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8881  hacia 8880
redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8881  hacia 8882
redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8881  hacia 8880

```
```
//En R2
-------ROUTER CONFIGURATION-------
router_ip:  127.0.0.1
router_port:  8882
router_routes:  tablas/test3/rutas_R2_v3.txt
----------------------------------
redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8882  hacia 8883
redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8882  hacia 8884
redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8882  hacia 8886
redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8882  hacia 8883
redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8882  hacia 8884
redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8882  hacia 8886
redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8882  hacia 8883
```

```
// en R5
-------ROUTER CONFIGURATION-------
router_ip:  127.0.0.1
router_port:  8885
router_routes:  tablas/test3/rutas_R5_v3.txt
----------------------------------
mensaje recibido:  hola R5 desde R1

mensaje recibido:  hola R5 desde R1

mensaje recibido:  hola R5 desde R1

mensaje recibido:  hola R5 desde R1

```

* Los resultados  más  interesantes son en R1 y R2. R1 puede alternar  entre R0 y R2 para llegar a R5, mientras que R2 puede alternar entre R0 , R3  y  R4 para llegar a R5.En los outputs. En los outputs pueden verse  los saltos  que  se  siguiendo Round Robin. Finalmente el mensaje es recibido correctamene  en R5.

* Se ven resultados similares al enviar mensajes desde R5 a R1.

## TTL

Para  implementar el TTL se agrega  un campo  en los  g¿headers  del  mensaje que  se  va  a enviar. Este  campo  se  llama TTL y  se  inicializa  en  cierto valor. Luego  en cada  salto  se  disminuye  en 1. Si  el  TTL llega  a 0 se  imprime  un mensaje  de error.Esto está  dentro  del loop  principal en router.py

### Test con TTL

* **TEST 1: TTL 1**: Se envía un mensaje  de R1 a R3  con la tabla  R1 modificada.El resultado es el siguiente :

```
-------ROUTER CONFIGURATION-------
router_ip:  127.0.0.1
router_port:  8881
router_routes:  tablas/test1/rutas_R1.txt
----------------------------------
redirigiendo paquete 127.0.0.1 con destino final 8883 desde 8881  hacia 8882
redirigiendo paquete 127.0.0.1 con destino final 8883 desde 8881  hacia 8882
redirigiendo paquete 127.0.0.1 con destino final 8883 desde 8881  hacia 8882
redirigiendo paquete 127.0.0.1 con destino final 8883 desde 8881  hacia 8882
redirigiendo paquete 127.0.0.1 con destino final 8883 desde 8881  hacia 8882
Se recibio  el paquete  127.0.0.1 con TTL 0

```

Se  puede  observar  que  luego de 10 redirecciones (TTL=10) el mensoaje  es retornado en R1 y  se estanca  en un loop  como  ocurría  en el caso sin TTL.

* **TEST 2: TTL 2**: Se lee archivo.txt (no debe  tener ";" pues se cae  el código) y  se encapsula cada línea en  un header IP, luego se envía cada paquete desde R1 a R5.Se envía  el siguiente texto :

``` 
In June Diane visited her friends who live in San Francisco California. This was Diane’s 
first time in the city and she enjoyed her opportunities to walk around and explore.
On the first day of her trip Diane visited the Golden Gate Bridge. This red suspension 
bridge measures 1.7 miles in length. Diane and her friends did not walk across the bridge.
However they viewed it from the Golden Gate National Recreation Area which offers hiking 
trails picnicking areas and presents spectacular views of the bridge and city. Diane and
her friends made sure to take a group photograph here featuring the bridge in the background.
The next day Diane and her friends visited Alcatraz Island. This island is located 1.25
miles offshore in the San Francisco Bay. It used to serve as a lighthouse military fort
and prison. Diane and her friends took a small tour boat across bay to reach the island.

```

Y el mensaje  recibido en R5 es el siguiente:
``` 
-------ROUTER CONFIGURATION-------
router_ip:  127.0.0.1
router_port:  8885
router_routes:  tablas/test2/rutas_R5.txt
----------------------------------
mensaje recibido:  On the first day of her trip Diane visited the Golden Gate Bridge. This red suspension 

mensaje recibido:  her friends made sure to take a group photograph here featuring the bridge in the background.

mensaje recibido:  In June Diane visited her friends who live in San Francisco California. This was Diane’s 

mensaje recibido:  first time in the city and she enjoyed her opportunities to walk around and explore.

mensaje recibido:  bridge measures 1.7 miles in length. Diane and her friends did not walk across the bridge.

mensaje recibido:  trails picnicking areas and presents spectacular views of the bridge and city. Diane and

mensaje recibido:  The next day Diane and her friends visited Alcatraz Island. This island is located 1.25

mensaje recibido:  and prison. Diane and her friends took a small tour boat across bay to reach the island.

mensaje recibido:  However they viewed it from the Golden Gate National Recreation Area which offers hiking 

mensaje recibido:  miles offshore in the San Francisco Bay. It used to serve as a lighthouse military fort

```

Se puede apreciar  que  no se recibe el mensaje  en el  mismo orden envíado. Esto se debe  a que  los paquetes  se  envían  por  distintos caminos  y  por lo tanto  llegan  en distinto orden y  no se  gestiona ese reordenamiento  por parte de los routers.