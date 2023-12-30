# Informe BGP

**Alumno: Lukas Vasquez Verdejo**

## Explicación Código

### BGP
Para  implementar bgp se crea la clase bgp_handler, que se encargará de manejar el protocolo BGP. La clase  se encargará de guardar para cada router información  sobre vecinos, rutas, y direccion de la tabla.Esta clase posee los siguientes métodos:

 * **create_BGP_message()**: que se encarga de crear  los mensajes necesarios  para el protocolo, tiene  dos modos, modo=START  para los mensajes de  inicio de BGP y modo = BGP para crear  los mensajes  BGP con información de las rutas.
 * **send_routes_to _neighbours()**: envía las rutas de este routes a los routers vecinos, este método se llamara cada vez que ocurra un cambio dentro de la rutas.
 * **run_BGP**: ejecuta el protocolo BGP.Primero envía  un mensaje START_BGP a cada uno de los vecinos del router y luego se le envían as rutas a cada vecino.Ñuego se queda esperando mensajes de los vecinos, si recibe un mensaje de un vecino con una dirección qu no está presente en la tabla actual, se actualiza la tabla de rutas y se envían las rutas a los vecinos.Si se recibe un mensaje  con un ruta más corta  que la actual se desecha esta ruta y se cambia por la nueva.Se le agrega un timer de 10 segundos  a cada router, de esta manera  si se cumple el timeout se retorna  la tabla actualizada.

### Tablas

* Ya que gracias a BGP  solo  se conserva  una posible ruta  por tabla (la más corta) para cada destino, no es necesario el Scheduler (se eliminó). Por esta misma  razón se cambió checkroutes , la cual retorna inmediatamente al encontrar una coincidencia.

* Al ejecutar el código este toma como tablas iniciales las del archivo ./7_routers, las tablas actualizadas se  guardan en ./tablas_bgp las que son utilizadas en el segundo loop del código. 

## Pruebas

### Test 1: 7 routers
* Para iniciar la primera prueba se ejecuta BGP  en una red de 7 routers con el siguiente commando:
```
nc -u 127.0.0.1 8882 <<EOF
127.0.0.1;8882;010;00000347;00000000;0000009;0;START_BGP
EOF

```
* Para ilustrar, se muestra el output de R1:
```
-------ROUTER CONFIGURATION-------
router_ip:  127.0.0.1
router_port:  8881
router_routes:  tablas/7_routers/rutas_R1.txt
----------------------------------
mensaje recibido START_BGP, iniciando BGP
--Iniciando protocolo BGP--
>enviando rutas  a vecinos: desde 8881 a 8882
--Esperando rutas vecinas--
>_ rutas recibidas desde 8882
nueva ruta anadida:  ['8883', '8882', '8881']
>enviando rutas  a vecinos: desde 8881 a 8882
nueva ruta anadida:  ['8884', '8882', '8881']
>enviando rutas  a vecinos: desde 8881 a 8882
>_ rutas recibidas desde 8882
nueva ruta anadida:  ['8885', '8884', '8882', '8881']
>enviando rutas  a vecinos: desde 8881 a 8882
>_ rutas recibidas desde 8882
nueva ruta anadida:  ['8886', '8885', '8884', '8882', '8881']
>enviando rutas  a vecinos: desde 8881 a 8882
>_ rutas recibidas desde 8882
nueva ruta anadida:  ['8887', '8886', '8885', '8884', '8882', '8881']
>enviando rutas  a vecinos: desde 8881 a 8882

----BGP finalizado----
Tabla actualizada para 8881:
127.0.0.1 8882 8881 127.0.0.1 8882 1000
127.0.0.1 8883 8882 8881 127.0.0.1 8882 100
127.0.0.1 8884 8882 8881 127.0.0.1 8882 100
127.0.0.1 8885 8884 8882 8881 127.0.0.1 8882 100
127.0.0.1 8886 8885 8884 8882 8881 127.0.0.1 8882 100
127.0.0.1 8887 8886 8885 8884 8882 8881 127.0.0.1 8882 100


```
* Se puede observar que se envían las rutas a los vecinos y se reciben las rutas de los vecinos, luego se actualiza la tabla de rutas y se envían las rutas a los vecinos.Al terminar el procedimiento  se cuenta  con una ruta a cada router en la red.

### Test 2: Envío  de mensajes  entre routers
Con la  misma configuración  anterior , se envían mensajes  entre routers.

* Para enviar un mensaje se ejecuta el siguiente comando (x: router origen, y: router destino):
```
nc -u 127.0.0.1 888x <<EOF
127.0.0.1;888y;010;00000347;00000000;0000017;0;hola Ry desde Rx
EOF

```
* Para ilustrar, se muestra el output de R7->R1:
```
----BGP finalizado----
Tabla actualizada para 8881:
127.0.0.1 8882 8881 127.0.0.1 8882 1000
127.0.0.1 8883 8882 8881 127.0.0.1 8882 100
127.0.0.1 8884 8882 8881 127.0.0.1 8882 100
127.0.0.1 8885 8884 8882 8881 127.0.0.1 8882 100
127.0.0.1 8886 8885 8884 8882 8881 127.0.0.1 8882 100
127.0.0.1 8887 8886 8885 8884 8882 8881 127.0.0.1 8882 100

mensaje recibido:  hola R1 desde R7
```
* output R7->R3:

```
----BGP finalizado----
Tabla actualizada para 8883:
127.0.0.1 8882 8883 127.0.0.1 8882 1000
127.0.0.1 8885 8883 127.0.0.1 8885 1000
127.0.0.1 8881 8882 8883 127.0.0.1 8882 100
127.0.0.1 8884 8882 8883 127.0.0.1 8882 100
127.0.0.1 8886 8885 8883 127.0.0.1 8885 100
127.0.0.1 8887 8886 8885 8883 127.0.0.1 8885 100

mensaje recibido:  hola R3 desde R7
```
```
----BGP finalizado----
Tabla actualizada para 8884:
127.0.0.1 8882 8884 127.0.0.1 8882 1000
127.0.0.1 8885 8884 127.0.0.1 8885 1000
127.0.0.1 8881 8882 8884 127.0.0.1 8882 100
127.0.0.1 8883 8882 8884 127.0.0.1 8882 100
127.0.0.1 8886 8885 8884 127.0.0.1 8885 100
127.0.0.1 8887 8886 8885 8884 127.0.0.1 8885 100

redirigiendo paquete 127.0.0.1 con destino final 8881 desde 8884  hacia 8882
redirigiendo paquete 127.0.0.1 con destino final 8881 desde 8884  hacia 8882
redirigiendo paquete 127.0.0.1 con destino final 8881 desde 8884  hacia 8882
redirigiendo paquete 127.0.0.1 con destino final 8881 desde 8884  hacia 8882
redirigiendo paquete 127.0.0.1 con destino final 8881 desde 8884  hacia 8882
redirigiendo paquete 127.0.0.1 con destino final 8881 desde 8884  hacia 8882
mensaje recibido:  hola R4 desde R7
```

* Se puede apreciar que los mensajes se envían correctamente y son impresos  por el destinatario correcto.

### Ahora suponga que inicialmente solo tiene los primeros 6 routers (R1 a R6) tal que echa a correr BGP por primera vez considerando solo a estos 6 routers. Suponga que R7 se une a la red en un momento posterior a esta llamada inicial de BGP y que R7 quiere ser invisible para R4 ¿Cómo puede modificar la tabla de rutas inicial de R7 para que, luego de ejecutar run_BGP(), R4 no pueda alcanzar a R7? Pruebe que su respuesta funciona utilizando su código. Añada su respuesta y observaciones al informe.

**Aclaracion: para lograr  esta parte se re-implemtnta  el algoritmo de bgp segun lo comentado por la profesora  en  el foro. Es decir se agrega el caso en que se reciba desde  un router  un ruta desde un  vecino nuevo con destino el router actual, en donde se invierte la ruta y se agrega**

Para  lograr  que R7 sea  invisible  para R4 basta agregar  una ruta ficticia  en R7  tal que contenga a R4  (R7 ->R4 -> R6, ver tablas/7_routers/rutasR7.txt) , como esta ruta contiene a R4 será  ignorada  por este para no generar  un loop infinito.Esta ruta sí va ser  integrada  por los demás routers , ya que al ser re-enviada por R6 y tener destino R7, esta ruta será  tomada como una  con un destino nuevo.  

* Output BGP  sin agregar R7:

```
//tabla 6 sin agregar R7
----BGP finalizado----
Tabla actualizada para 8886:
127.0.0.1 8885 8886 127.0.0.1 8885 1000
127.0.0.1 8883 8885 8886 127.0.0.1 8885 100
127.0.0.1 8884 8885 8886 127.0.0.1 8885 100
127.0.0.1 8882 8883 8885 8886 127.0.0.1 8885 100
127.0.0.1 8881 8882 8883 8885 8886 127.0.0.1 8885 100

// tabla 4  sin agregar R7
----BGP finalizado----
Tabla actualizada para 8884:
127.0.0.1 8882 8884 127.0.0.1 8882 1000
127.0.0.1 8885 8884 127.0.0.1 8885 1000
127.0.0.1 8881 8882 8884 127.0.0.1 8882 100
127.0.0.1 8883 8882 8884 127.0.0.1 8882 100
127.0.0.1 8886 8885 8884 127.0.0.1 8885 100

// tabla 2 sin agregar R7
----BGP finalizado----
Tabla actualizada para 8882:
127.0.0.1 8881 8882 127.0.0.1 8881 1000
127.0.0.1 8883 8882 127.0.0.1 8883 1000
127.0.0.1 8884 8882 127.0.0.1 8884 1000
127.0.0.1 8885 8883 8882 127.0.0.1 8883 100
127.0.0.1 8886 8885 8883 8882 127.0.0.1 8883 100

```

* Output BGP  luego de  agregar R7:

```
----BGP finalizado----
Tabla actualizada para 8886:
127.0.0.1 8885 8886 127.0.0.1 8885 1000
127.0.0.1 8883 8885 8886 127.0.0.1 8885 100
127.0.0.1 8884 8885 8886 127.0.0.1 8885 100
127.0.0.1 8882 8883 8885 8886 127.0.0.1 8885 100
127.0.0.1 8881 8882 8883 8885 8886 127.0.0.1 8885 100
127.0.0.1 8887 8884 8886 127.0.0.1 8884 100


// tabla 4  al agregar R7
----BGP finalizado----
Tabla actualizada para 8884:
127.0.0.1 8882 8884 127.0.0.1 8882 1000
127.0.0.1 8885 8884 127.0.0.1 8885 1000
127.0.0.1 8881 8882 8884 127.0.0.1 8882 100
127.0.0.1 8883 8882 8884 127.0.0.1 8882 100
127.0.0.1 8886 8885 8884 127.0.0.1 8885 100

// tabla 2 al agregar R7
----BGP finalizado----
Tabla actualizada para 8882:
127.0.0.1 8881 8882 127.0.0.1 8881 1000
127.0.0.1 8883 8882 127.0.0.1 8883 1000
127.0.0.1 8884 8882 127.0.0.1 8884 1000
127.0.0.1 8885 8883 8882 127.0.0.1 8883 100
127.0.0.1 8886 8885 8883 8882 127.0.0.1 8883 100
127.0.0.1 8887 8884 8886 8885 8883 8882 127.0.0.1 8883 100

// tabla 7 al agregar R7s
----BGP finalizado----
Tabla actualizada para 8887:
127.0.0.1 8886 8884 8887 127.0.0.1 8886 1000
127.0.0.1 8885 8886 8887 127.0.0.1 8886 100
127.0.0.1 8883 8885 8886 8887 127.0.0.1 8886 100
127.0.0.1 8884 8885 8886 8887 127.0.0.1 8886 100
127.0.0.1 8882 8883 8885 8886 8887 127.0.0.1 8886 100
127.0.0.1 8881 8882 8883 8885 8886 8887 127.0.0.1 8886 100
```
