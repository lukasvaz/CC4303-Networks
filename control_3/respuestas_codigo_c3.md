# Respuestas código C3
### Alumno:Lukas Vasquez Verdejo

## Forwarding:
**Actualmente, si se intentara llegar a un router fuera del sistema, solo puede llegarse al router default si el mensaje llega a R0. Que debe hacerse para poder llegar desde cualquier lado al default?Ademas, es necesario modificar el codigo para que funcione el router default? Comente al respecto**  

Para  poder llegar al router  default desde  cualquier Router  es necesario extender  las tablas  de  los otros  routers con  una ruta  hacia  el router  default, de la siguiente manera:   

- 127.0.0.1 0000 8880 127.0.0.1 *direccion default*
- 127.0.0.1 8887 65535 127.0.0.1 *direccion default*
De esta manera no es necesario  modificar el codigo  en cada router , si no sólo  agregar  una ruta  hacia  el router  default  en cada  tabla.

## Fragmentación:
**Fragmentación: Suponga que le envían muchos fragmentos sueltos que no se pueden rearmar. ¿Cómo haría para que no se agote la memoria?**
Una  solución es determinar  un umbral  en el  que al ser  sobrepasado se limpia la memoria  (descartando  los  fragmentos recibidos  hasta el momento). Esto sumado al correcto  manejo de pérdidas (al descartar  un mensaje  se envía nuevamente)  dado  por la capa  de transporte asegura  un correcto funcionamiento.

## BGP:
**Fragmentación: Suponga que le envían muchos fragmentos sueltos que no se pueden rearmar. ¿Cómo haría para que no se agote la memoria?**
Para la implementación de BGP se utilian tablas  con diferente información:

- RIB: información de las tablas del propio  router
- Loc-Rib: tabla  mantenida  por BGP de manera separada de la tabla de rutas decada router.
- Adj-RIB-IN: información de las tablas de los vecinos que se han recibido
- Adj-RIB-OUT: información de las tablas de los vecinos que se han enviado
El manejo de estas tablas  queda criterio del  desarrollador  el cómo  implementarlas.( En  qué estructura de datos almacenar p ej )
Además  de esto las tablas usadas  en esta  actividad  utilizan los puertos  como si  fueran direcciones. En la implementación real se usan direcciones IP.