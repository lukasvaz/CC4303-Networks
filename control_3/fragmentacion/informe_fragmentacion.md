# Informe Fragmentacion 

* **Alumno**:Lukas Vasquez Verdejo

## Explicación de Codigo

### Fragmentacion

La  fragmentación  es llevada  a cabo por la función fragment_packet()  la  cual  divide  un paquete en segmentos más  pequeños  dado  el MTU. para  lograr  esto se  hace  lo siguiente:

* **Si el paquete  es  más  pequeño  que el MTU**, se  retorna  el paquete  original. 
* **Si el paquete es más grande que el MTU** se fragmenta.Para la  fragmentación  primero  se determina  el tamaño  máximo  que puede  tener  un mensaje dentro del paquete, esto es posible  dado que el header es de  tamaño fijo y el MTU es conocido.Luego se extraen  fragmentos (con tamaño máximo ) del mensaje original  y se  encapsulan  en un header IP hasta  que el mensaje resultante sea menor al tamaño máximo . Se  retorna  una lista  con estos  fragmentos.

### Re-ensamblaje
Para hacer el re-ensamblaje se  utiliza  la  función reassemble_packet() la  cual  recibe  una lista  de fragmentos y  retorna  el mensaje original. Para  lograr  esto se  hace  lo siguiente:

* **Si en la lista de fragmentos  no existe el flag 0**,el mensaje no puede estar  completo  por lo que  se  retorna  None.
 
* **Si en la  lista de fragmentos existe el flag 0**, se calcula el total del paquete (esto  puede hacerse tomando el offset del fragmento final y sumandole el tamaño de este) para crear  un arreglo de 0s  de dicho tamaño. Luego se ubica cada fragmento en su posición correspondiente  utilizando el offset de cada fragmento.Si luego de este proceso quedan 0s en el arreglo, se retorna  None, de lo contrario se retorna  el mensaje original com  un string.

Cada vez  que se recibe un fragmento estos  son almacenados en un diccionario  con clave igual al ID.Para cada  nuevo fragmento recibido por  un router se llama a reassemble_packet() y se  verifica  si el mensaje  está  completo, si lo está  se  retorna  el muestra mensaje original y se elimina  esta coincidencia  del diccionario.

### Pruebas

#### **Comprobación TTl y Round Robin**:
 Se envía  un paquete de tamaño tal que este  no sea afectado por la fragmentación. El mensaje enviado será 
"sí\n". El resultado  es el siguiente:

* **input TTl=10**:
    ```
    nc -u 127.0.0.1 8881 <<EOF
    > 127.0.0.1,8885,010,00000347,00000000,00000003,0,si 

    ```
    * **Router 5**

    ```
    -------ROUTER CONFIGURATION-------
    router_ip:  127.0.0.1
    router_port:  8885
    router_routes:  tablas/5_routers/rutas_R5.txt
    ----------------------------------
    mensaje recibido:  si
    ```

    * **Router 2**
    ```
    -------ROUTER CONFIGURATION-------
    router_ip:  127.0.0.1
    router_port:  8882
    router_routes:  tablas/5_routers/rutas_R2.txt
    ----------------------------------
    redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8882  hacia 8883
    redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8882  hacia 8884

    ```
    * Notar  que en el router 2 se alterna entre 2 redirecciones  siguiendo el procedimiento estipulado en el Roun Robin.


* **input TTl=3**:
    ```
    nc -u 127.0.0.1 8881 <<EOF
    127.0.0.1,8885,03,00000347,00000000,00000003,0,si
    EOF

    ```
    * **Router 2**

    ```
    -------ROUTER CONFIGURATION-------
    router_ip:  127.0.0.1
    router_port:  8882
    router_routes:  tablas/5_routers/rutas_R2.txt
    ----------------------------------
    redirigiendo paquete 127.0.0.1 con destino final 8885 desde 8882  hacia 8883
    Se recibio  el paquete  127.0.0.1 con TTL 0
    
    ```
    * Notar que el  paquete  no alcanza a llegar a R5  pues el TTL se agota en R2, obteniendo el output  anterior.

#### **Comprobación Fragmentación**:
Se envía  un paquete de tamaño total 150 bytes, el cual  es  mayor al MTU. Considerando que el header  tiene  un tamaño fijo de 48 bytes, el "message" debe  tener  un tamaño de (150-48) bytes.

* **input TTL=10**:
    ```
    nc -u 127.0.0.1 8881 <<EOF
    127.0.0.1,8885,010,00000347,00000000,00000102,0,hola me llamo lukas  y soy un estudiante de cuarto ano de ingenieria civil en computacion.Estoy hacien
    ```
* **Router R5**
```
-------ROUTER CONFIGURATION-------
router_ip:  127.0.0.1
router_port:  8885
router_routes:  tablas/5_routers/rutas_R5.txt
----------------------------------
mensaje recibido:  hola me llamo lukas  y soy un estudiante de cuarto ano de ingenieria civil en computacion.Estoy hacien
```

* **Router R5 luego de tres envíos**
```
-------ROUTER CONFIGURATION-------
    router_ip:  127.0.0.1
    router_port:  8885
    router_routes:  tablas/5_routers/rutas_R5.txt
    ----------------------------------
    mensaje recibido:  hola me llamo lukas  y soy un estudiante de cuarto ano de ingenieria civil en computacion.Estoy hacien

    mensaje recibido:  hola me llamo lukas  y soy un estudiante de cuarto ano de ingenieria civil en computacion.Estoy hacien

    mensaje recibido:  hola me llamo lukas  y soy un estudiante de cuarto ano de ingenieria civil en computacion.Estoy hacien
```
* **Router R5 luego de envío desde R2**
```
-------ROUTER CONFIGURATION-------
router_ip:  127.0.0.1
router_port:  8885
router_routes:  tablas/5_routers/rutas_R5.txt
----------------------------------
mensaje recibido:  hola me llamo lukas  y soy un estudiante de cuarto ano de ingenieria civil en computacion.Estoy hacien
```

* Notar que el mensaje  se  recibe  completo  en R5 en las distintas pruebas. No se observan alteraciones en el comportamiento además de lo esperado  por el Round Robin.
