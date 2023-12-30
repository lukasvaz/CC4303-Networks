import time


class TimerList:
    """Esta clase permite crear una lista de timers con un timeout fijo"""
    def __init__(self, timeout, number_of_timers):
        """Construye una lista de timers de tamaño number_of_timers con
        un timeout de timeout segundos.
        """
        if not isinstance(timeout, int):
            raise Exception(" __init___(): Variable timeout must be an Integer")
        if not isinstance(number_of_timers, int):
            raise Exception(" __init___(): Variable number_of_timers must be an Integer")
        self.timeout = timeout
        self.number_of_timers = number_of_timers
        self.timer_list = []
        self.starting_times = []
        for i in range(self.number_of_timers):
            self.timer_list.append(False)
            self.starting_times.append(None)

    def start_timer(self, timer_index):
        """Inicia el timer en la posición timer_index del nuestro timerList."""
        try:
            self.timer_list[timer_index] = True
            self.starting_times[timer_index] = time.time()
        except IndexError:
            raise Exception("ERROR in TimerList, stop_timer(): Invalid index timer_index")
        except TypeError:
            raise Exception("ERROR in TimerList, stop_timer(): Index timer_index must be an Integer")

    def get_timed_out_timers(self):
        """Retorna una lista con los índices de los timers que ya cumplieron
         su timeout."""
        timed_out_timers = []
        current_time = time.time()
        for i in range(self.number_of_timers):
            if self.timer_list[i]:
                if current_time - self.starting_times[i] >= self.timeout:
                    timed_out_timers.append(i)
        return timed_out_timers

    def stop_timer(self, timer_index):
        """Detiene el timer en la posición timer_index del nuestro timerList."""
        try:
            self.timer_list[timer_index] = False
            self.starting_times[timer_index] = None
        except IndexError:
            raise Exception("ERROR in TimerList, stop_timer(): Invalid index timer_index")
        except TypeError:
            raise Exception("ERROR in TimerList, stop_timer(): Index timer_index must be an Integer")


