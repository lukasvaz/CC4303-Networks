class SlidingWindowCC:
    """Esta clase le permite crear ventanas deslizantes.
    Puede crear una ventana vacía con:
    SlidingWindow(window_size, [], initial_seq)."""

    def __init__(self, window_size, data_list, initial_seq):
        """Construye una ventana de tamaño window_size, usando los datos de
        data_list y número de secuencia inicial initial_seq."""

        if not isinstance(window_size, int):
            raise Exception("ERROR in SlidingWindowCC, __init___(): Index window_size must be an Integer")
        if not isinstance(initial_seq, int):
            raise Exception("ERROR in SlidingWindowCC, __init___(): Index initial_seq must be an Integer")
        if not isinstance(data_list, list):
            raise Exception("ERROR in SlidingWindowCC, __init___(): Index data_list must be a List")
        if window_size < 1:
            raise Exception("ERROR in SlidingWindowCC, __init___(): window_size must be > 0")
        if initial_seq < 0:
            raise Exception("ERROR in SlidingWindowCC, __init___(): initial_seq must be >= 0")

        # fix data_list if needed
        for i in range(len(data_list)):
            if isinstance(data_list[i], int):
                data_list[i] = str(data_list[i]).encode()
            if isinstance(data_list[i], str):
                data_list[i] = data_list[i].encode()

        # generate seq_list
        self.seq_list = []
        cummulative_byte_length = 0
        for j in range(len(data_list)):
            self.seq_list.append(initial_seq + cummulative_byte_length)
            cummulative_byte_length += len(data_list[j])

        self.window_size = window_size
        self.data_list = data_list
        self.initial_seq = initial_seq

        self.window = []
        i = 0
        for i in range(self.window_size):
            if i >= len(self.data_list):
                self.window.append({"data": None, "seq": None})
            else:
                self.window.append({"data": self.data_list[i],
                                    "seq": self.seq_list[i]})
                cummulative_byte_length += len(self.data_list[i])

        self.data_start_index = i + 1

    def move_window(self, steps_to_move):
        """Avanza la ventana en steps_to_move espacios y actualiza los números de
        secuencia según corresponda. No puede avanzar más espacios que el tamaño
        de la ventana. Si se acaban los datos en data_list rellena con None."""

        if steps_to_move == 0:
            return
        if steps_to_move > self.window_size or steps_to_move < 0:
            raise Exception("ERROR in SlidingWindowCC, move_window(): Invalid index steps_to_move")
        if not isinstance(steps_to_move, int):
            raise Exception("ERROR in SlidingWindowCC, move_window():Index steps_to_move must be an Integer")

        j = 0
        new_window = []
        # print("steps_to_move: {}, window_size: {}".format(steps_to_move, self.window_size))
        for j in range(steps_to_move, self.window_size):
            # print("----> j: {}".format(j))
            new_window.append(self.window[j])
        # print(" -+++++++- {}".format(self.window_size - len(new_window)))
        for i in range(self.data_start_index, (self.window_size - len(new_window)) + (self.data_start_index)):
            if i >= len(self.data_list):
                new_window.append({"data": None, "seq": None})
            else:
                new_window.append({"data": self.data_list[i],
                                   "seq": self.seq_list[i]})
            self.data_start_index += 1

        self.window = new_window

    def update_window_size(self, new_window_size):

        if not isinstance(new_window_size, int):
            raise Exception("ERROR in SlidingWindowCC, update_window_size(): Index new_window_size must be an Integer")
        if new_window_size < 1:
            raise Exception("ERROR in SlidingWindowCC, update_window_size(): new_window_size must be > 0")

        if self.window_size == new_window_size:
            return
        elif self.window_size < new_window_size:
            for i in range(new_window_size - self.window_size):
                data_index = self.data_start_index + i
                if data_index >= len(self.data_list):
                    self.window.append({"data": None, "seq": None})
                else:
                    self.window.append({"data": self.data_list[data_index],
                                       "seq": self.seq_list[data_index]})

            self.data_start_index = data_index + 1
            self.window_size = new_window_size
        else:
            new_window = []
            for j in range(new_window_size):
                new_window.append(self.window[j])
            self.data_start_index -= self.window_size - new_window_size
            self.window_size = new_window_size
            self.window = new_window

    def get_sequence_number(self, window_index):
        """Entrega el número de secuencia del elemento almacenado en la posición
        window_index de la ventana."""

        try:
            return self.window[window_index]["seq"]
        except IndexError:
            raise Exception("ERROR in SlidingWindowCC, get_sequence_number(): Invalid index window_index")
        except TypeError:
            raise Exception("ERROR in SlidingWindowCC, get_sequence_number(): Index window_index must be an Integer")

    def get_data(self, window_index):
        """Entrega los datos contenidos en el elemento almacenado en la posición
        window_index de la ventana."""

        try:
            return self.window[window_index]["data"]
        except IndexError:
            raise Exception("ERROR in SlidingWindowCC, get_data(): Invalid index window_index")
        except TypeError:
            raise Exception("ERROR in SlidingWindowCC, get_data(): Index window_index must be an Integer")

    def put_data(self, data, seq, window_index):
        """Añade un elemento a la ventana en la posición window_index con
        datos=data, número de secuencia seq. Note que esta función NO se
        asegura de que seq sea válido."""

        if not isinstance(seq, int):
            raise Exception("ERROR in SlidingWindowCC, put_data(): Variable seq must be an Integer")

        try:
            self.window[window_index]["data"] = data
            self.window[window_index]["seq"] = seq
        except IndexError:
            raise Exception("ERROR in SlidingWindowCC, put_data(): Invalid index window_index")
        except TypeError:
            raise Exception("ERROR in SlidingWindowCC, put_data(): Index window_index must be an Integer")

    def __str__(self):
        max_len = 0
        separator_line = "+------+"
        data_line = "| Data |"
        seq_line = "| Seq  |"
        for wnd_element in self.window:
            str_data = str(wnd_element["data"])
            if isinstance(wnd_element["seq"], int):
                str_seq = "{}".format(wnd_element["seq"])
            else:
                str_seq = "None"
            if max(len(str_data), len(str_seq)) > max_len:
                max_len = max(len(str_data), len(str_seq))
            if max_len > 20:
                max_len = 20
                break

        add_to_separator = "--"
        for i in range(max_len):
            add_to_separator += "-"
        add_to_separator += "+"

        for j in range(self.window_size):
            separator_line += add_to_separator

            data_str = str(self.get_data(j))
            if len(data_str) > max_len:
                data_str = data_str[0:max_len - 5] + "(...)"
            else:
                data_str = str(self.get_data(j))
            data_line += " {}".format(data_str)
            for i in range(max_len - len(data_str)):
                data_line += " "
            data_line += " |"

            if self.get_sequence_number(j) != None:
                seq_str = "{}".format(self.get_sequence_number(j))
            else:
                seq_str = "None"
            if len(seq_str) > max_len:
                seq_str = seq_str[0:max_len - 5] + "(...)"
            seq_line += " {}".format(seq_str)
            for i in range(max_len - len(seq_str)):
                seq_line += " "
            seq_line += " |"
        data_line += "\n"
        seq_line += "\n"

        return separator_line + "\n" + data_line + separator_line + "\n" + seq_line + separator_line

    def __repr__(self):
        return str(self)
