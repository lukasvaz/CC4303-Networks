# Actividad 4
## Alumno: Lukas Vasuqez Verdejo

## Explicación Código
En esta actividad  se  implementa  la CongestionControl y  se simula una conexión TCP utilizando el protocolo go_back_n.

### Congestión de Control
Esta clase se encarga de manejar la lógica  del control de congestión. Para esto se definen los siguientes métodos:

**event_ack_received()**  
Maneja  la lógica del control de congestión cuando se recibe  un ACK .Si se encuentra en estado SLOW START se incrementa la ventana  en 1 MSS  y  si el tamaño de la ventana  supera el treshold  se  cambia de estado a CONGESTION AVOIDANCE.

**event_timeout()**  
Maneja  la lógica del control de congestión cuando se cumple un timeput.Si esto ocurre  en estado SLOW START se fija el treshold en la  mitad de la ventana y se  reduce la ventana  a 1 MSS.Si ocurre en CONGESTION_AVOIDANCE se incrementa  el tamaño de la ventana  en 1/tamalo de la ventana MSS.


## Go Back N

### Preguntas  
**¿Por qué le puede servir usar como base para Go Back-N el código de Stop & Wait de la sección anterior? ¿Qué similitud tiene Go Back-N con Stop & Wait?**  
Tiene  la  similitud de que  ambos  usan timeouts  por parte del emisor  e  implementan la logica conforme se cumplen  o no esos timeouts, también  se tiene  por parte del receptor que  este sólo envía  ACKs al  igual  que en STOP and WAIT.  

**En la sección anterior solo se muestra la función send de Stop & Wait, ¿Qué ocurre con la función receive? ¿Esta función cambia con el uso de TimerList y SlidingWindowsCC?**
Esta función  no cambia  ya que  el comportamiento del receptor  es enviar ACKs  una vez recibidos los mensajes, justo como en  la  implementación anterior.

### Implementación

**send_using_go_back_n()**
Esta función se encarga de enviar un mensaje utilizando el protocolo Go-Back-N.Para esto se hace uso  de una ventana deslizante  en la cual se envía al receptor cada  dato dentro de esta ventana. Una vez  se envía estos datos se inicaliza un timer con ceirto time out , si se cumple el timeout se reenvía  todos los datos dentro de la ventana.Si se obtiene  una respuesta  (con ACK y SEQ correspondiente) se desplaza la ventana con la siguiente expresión:

```steps_to_move=response_message["SEQ"]-data_window.get_sequence_number(0))//UDP_PACKAGE_SIZE)+1``
 Si get_data(0)== None, finalizamos  el envío, si no  se  envían los  nuevos datos dentro de la ventana desplazada. El manejo de pérdidas es parte del protocolo pues solo  se avanzan espacios a medida que se reciban ACKs.



**recv_using_go_back_n()**   
No tiene cambios relevantes con respecto a la actividad anterior

## Implementación de Control de Gestión + goback n 
Los prinicpales cambios para implementar el control de Gestion con respecto a lo mencionado anteriormente, es el uso del objeto congetionControl()  para llevar la logica. De esta manera en cada evento relevante (ACKs TIMEOUT) se hace uso de las funciones mencioadas en el punto 1  para  actualizar el objeto.También es importante  mencionar  que  como la ventana será variable (propio de la congetión de control) se llama  a update_window_size() en cada ACK. El  envío  de paquetes también depende  de este objeto pues se consulta el tamaño de la ventana  (for i in range get_MSS_in_cwd() para envío de paquetes en el timeout).El envío de los nuevos datos agregados a la ventana  también depende  del  objeto congestión (hay que tomar en cuenta cómo varia la ventana  y cuánto  se desplaza):

```for i in reversed([i+1 for  i in range(steps_to_move+delta_window_size)]):'send packages'```


## Pruebas 
Usaremos el modo debug para revisa los resultados de las pruebas,el modo debug se activa  entregado debug=True en la instanciación del SocketTCP.

### Mensaje de 58 bytes recibo en 2 buff de 30**  
El mensaje se obtiene  correctamente con o sin pérdidas.El log por 
parte del servidor son los siguientes:    
**Sin perdidas**  
```
(recv) Beginning recv, buff size 30
(recv)Initial reponse| remainnig bytes 58
(recv)case:message > buff size, remaining bytes 58
(recv)End recv: 30 bytes, response: b'Mensaje  de prueba  recibido c'
(recv)remainning_msg b'om'
(recv)remainning_bytes 26 

(recv) Beginning recv, buff size 30
(recv)case:message < buff size, remaining bytes 26
(recv) Recieved invalid messge, sending ACK again
(recv) Recieved invalid messge, sending ACK again
(recv) Recieved invalid messge, sending ACK again
(recv) Recieved invalid messge, sending ACK again
(recv)End recv: 28 bytes, response: b'ompleto y de manera integra\n'
(recv)remainning_msg b'om'
(recv)remainning_bytes 0 

(Server) Final response:b'Mensaje  de prueba  recibido completo y de manera integra\n' ,len msg58
```
**Con perdidas**  
```
(recv) Beginning recv, buff size 30
(recv)Initial reponse| remainnig bytes 58
(recv)case:message > buff size, remaining bytes 58
(recv)End recv: 30 bytes, response: b'Mensaje  de prueba  recibido c'
(recv)remainning_msg b'om'
(recv)remainning_bytes 26 

(recv) Beginning recv, buff size 30
(recv)case:message < buff size, remaining bytes 26
(recv) Recieved invalid messge, sending ACK again
(recv) Recieved invalid messge, sending ACK again
(recv) Recieved invalid messge, sending ACK again
(recv) Recieved invalid messge, sending ACK again
(recv)End recv: 28 bytes, response: b'ompleto y de manera integra\n'
(recv)remainning_msg b'om'
(recv)remainning_bytes 0 

(Server) Final response:b'Mensaje  de prueba  recibido completo y de manera integra\n' ,len msg58
```


### Comportamiento Control de gestion
Para observer el comportamiento  del control de gestión, observaremos los logs del cliente.  

**Sin perdidas**  
al no ocurrir  un time out el objeto se mantiene en SLOW START  aumentando el tamaño de la ventana  en 1 MSS por cada ACK recibido.  

```
(send) Sending segment 0, SEQ: 78
(send) answer ACK recieved: SEQ 78
(Congestion Control) ACK recieved in SLOW_START, cwnd: 16 bytes = 2 MSS, sstresh= None bytes
(send) wnd_index: 0 ,step to move: 1
(send) Sending segment 3, SEQ: 80
(send) Sending segment 2, SEQ: 88

(send) answer ACK recieved: SEQ 80
(Congestion Control) ACK recieved in SLOW_START, cwnd: 24 bytes = 3 MSS, sstresh= None bytes
(send) wnd_index: 1 ,step to move: 1
(send) Sending segment 4, SEQ: 96
(send) Sending segment 3, SEQ: 104

(send) answer ACK recieved: SEQ 88
(Congestion Control) ACK recieved in SLOW_START, cwnd: 32 bytes = 4 MSS, sstresh= None bytes
(send) wnd_index: 2 ,step to move: 1
(send) Sending segment 5, SEQ: 112
(send) Sending segment 4, SEQ: 120

(send) answer ACK recieved: SEQ 96
(Congestion Control) ACK recieved in SLOW_START, cwnd: 40 bytes = 5 MSS, sstresh= None bytes
(send) wnd_index: 3 ,step to move: 1
(send) Sending segment 6, SEQ: 128
(send) Sending segment 5, SEQ: 136

(send) answer ACK recieved: SEQ 104
(Congestion Control) ACK recieved in SLOW_START, cwnd: 48 bytes = 6 MSS, sstresh= None bytes
(send) wnd_index: 4 ,step to move: 1

(send) answer ACK recieved: SEQ 112
(Congestion Control) ACK recieved in SLOW_START, cwnd: 56 bytes = 7 MSS, sstresh= None bytes
(send) wnd_index: 5 ,step to move: 1

(send) answer ACK recieved: SEQ 120
(Congestion Control) ACK recieved in SLOW_START, cwnd: 64 bytes = 8 MSS, sstresh= None bytes
(send) wnd_index: 6 ,step to move: 1

(send) answer ACK recieved: SEQ 128
(Congestion Control) ACK recieved in SLOW_START, cwnd: 72 bytes = 9 MSS, sstresh= None bytes
(send) wnd_index: 7 ,step to move: 1

(send) answer ACK recieved: SEQ 136
(Congestion Control) ACK recieved in SLOW_START, cwnd: 80 bytes = 10 MSS, sstresh= None bytes

```

**Con Perdidas**  
Tenemos que la ventana varía su tamaño  de acuerdo al protocolo (alcanza  un máximo de 2 MSS),y alterna  continuamente entre CONSGETION AVOIDANCE  y SLOW START

```(send) Sending segment 0, SEQ: 66
(send) Time out, resending data
(Congestion Control) Timeout in SLOW_START, ssthresh: 4 bytes, cwnd: 8 bytes = 1 MSS
(send) first segment not recieved, attempt 1
(send) Sending segment 0, SEQ: 66

(send) Time out, resending data
(Congestion Control) Timeout in SLOW_START, ssthresh: 4 bytes, cwnd: 8 bytes = 1 MSS
(send) first segment not recieved, attempt 2
(send) Sending segment 0, SEQ: 66

(send) answer ACK recieved: SEQ 66
(Congestion Control) ACK recieved in SLOW_START, cwnd: 16 bytes = 2 MSS, sstresh= 4 bytes
(Congestion Control) SStresh reached,changing to CONGESTION_AVOIDANCE
(send) wnd_index: 0 ,step to move: 1
(send) Sending segment 3, SEQ: 68
(send) Sending segment 2, SEQ: 76

(send) Time out, resending data
(Congestion Control) Time out  in Congestion Avoidance->changing to SLOW START, ssthresh: 8 bytes, cwnd: 8 bytes = 1 MSS
(send) Sending segment 1, SEQ: 68

(send) answer ACK recieved: SEQ 68
(Congestion Control) ACK recieved in SLOW_START, cwnd: 16 bytes = 2 MSS, sstresh= 8 bytes
(Congestion Control) SStresh reached,changing to CONGESTION_AVOIDANCE
(send) wnd_index: 1 ,step to move: 1
(send) Sending segment 4, SEQ: 76
(send) Sending segment 3, SEQ: 84

(send) Time out, resending data
(Congestion Control) Time out  in Congestion Avoidance->changing to SLOW START, ssthresh: 8 bytes, cwnd: 8 bytes = 1 MSS
(send) Sending segment 2, SEQ: 76

(send) answer ACK recieved: SEQ 84
(Congestion Control) ACK recieved in SLOW_START, cwnd: 16 bytes = 2 MSS, sstresh= 8 bytes
(Congestion Control) SStresh reached,changing to CONGESTION_AVOIDANCE
(send) wnd_index: 2 ,step to move: 2
(send) Sending segment 7, SEQ: 100
(send) Sending segment 6, SEQ: 92
(send) Sending segment 5, SEQ: 100

(send) Time out, resending data
(Congestion Control) Time out  in Congestion Avoidance->changing to SLOW START, ssthresh: 8 bytes, cwnd: 8 bytes = 1 MSS
(send) Sending segment 4, SEQ: 92

(send) Time out, resending data
(Congestion Control) Timeout in SLOW_START, ssthresh: 4 bytes, cwnd: 8 bytes = 1 MSS
(send) Sending segment 4, SEQ: 92

(send) answer ACK recieved: SEQ 92
(Congestion Control) ACK recieved in SLOW_START, cwnd: 16 bytes = 2 MSS, sstresh= 4 bytes
(Congestion Control) SStresh reached,changing to CONGESTION_AVOIDANCE
(send) wnd_index: 4 ,step to move: 1
(send) Sending segment 7, SEQ: 100
(send) Sending segment 6, SEQ: 108

(send) Time out, resending data
(Congestion Control) Time out  in Congestion Avoidance->changing to SLOW START, ssthresh: 8 bytes, cwnd: 8 bytes = 1 MSS
(send) Sending segment 5, SEQ: 100

(send) answer ACK recieved: SEQ 100
(Congestion Control) ACK recieved in SLOW_START, cwnd: 16 bytes = 2 MSS, sstresh= 8 bytes
(Congestion Control) SStresh reached,changing to CONGESTION_AVOIDANCE
(send) wnd_index: 5 ,step to move: 1
(send) Sending segment 8, SEQ: 108
(send) Sending segment 7, SEQ: 116

(send) answer ACK recieved: SEQ 108
(Congestion Control) ACK recieved in CONGESTION_AVOIDANCE, cwnd: 16 bytes = 2 MSS, sstresh= 8 bytes
(send) wnd_index: 6 ,step to move: 1
(send) Sending segment 8, SEQ: 124

(send) Time out, resending data
(Congestion Control) Time out  in Congestion Avoidance->changing to SLOW START, ssthresh: 10.0 bytes, cwnd: 8 bytes = 1 MSS
(send) Sending segment 7, SEQ: 116

(send) answer ACK recieved: SEQ 116
(Congestion Control) ACK recieved in SLOW_START, cwnd: 16 bytes = 2 MSS, sstresh= 10.0 bytes
(Congestion Control) SStresh reached,changing to CONGESTION_AVOIDANCE
(send) wnd_index: 7 ,step to move: 1
(send) Sending segment 10, SEQ: 124
```
### Comparación go back N , stop and wait
Para comparar el comportamiento de ambos protocolos, se envía un mensaje de 1000 a 2000 bytes (con 100K se demoraba  mucho  ya que el TIME OUT es minimo 1 sec).Para generar el archivo se usa generator_file.py .

| Tiempos | Goback n | Stop and wait |
| -------- | -------- | -------- |
| 1000 bytes | 109 sec | 188.2 sec |
| 1000 bytes | 89 sec | 165.1 sec |
| 1000 bytes |  94.0 sec|  168.19 sec|
| 2000 bytes |219.02 sec |  345.3 sec|
| 2000 bytes | 197.03    |365.4  sec   |

**Me dí  cuenta para  la entrega  que  hay  un caso en que  no funciona go back n, como  la perdida es aleatoria  no puedo replicar el error, pero ocurre  muy pocas veces**