import socket as so
import time
import tkinter as tk
import tkinter.messagebox
from settings import *


class Texter(object):
    def __init__(self, host: str, port: int):
        self.s = so.socket()
        self.host = host
        self.port = port

        self.connect()

        self.__text = ''
        self.__lines_count = 0
        self.__max_len = 0
        self.get_file()

        self.__window = tk.Tk()
        self.__window.bind('<Control-s>', self.check_and_save)

        tk.Label(self.__window, text='To send edited version to server, press <Ctrl+S>').pack()
        self.__text_box = tk.Text(self.__window, height=self.__lines_count, width=self.__max_len)
        self.__text_box.pack()
        self.show_contents()

        self.__window.mainloop()
        self.disconnect()

    def __del__(self):
        self.s.close()

    def connect(self):
        try:
            self.s.connect((self.host, self.port))
        except so.error as e:
            print(f'Connection refused({e})!')
            if tkinter.messagebox.askyesno(
                    'Connection refused!',
                    f'Connection refused\n{e}\nDo you want to try again?'
            ):
                self.connect()
            else:
                self.__window.destroy()

    def adjust_text(self):
        text: str = self.__text_box.get(1., tk.END)
        result = ''

        start = 0
        for i in range(self.__lines_count):
            end = min(start + self.__max_len + 1, len(text))
            endl = text.find('\n', start, end)
            if endl != -1:
                end = endl
            elif end != len(text):
                end -= 1
            result += text[start: end] + ('\n' if i < self.__lines_count - 1 else '')
            if endl == -1:
                start = end
                continue
            start = end + 1

        self.__text = result

    def get_file(self):
        file_size = int.from_bytes(self.s.recv(16), "big")
        print(f'Going to receive {file_size} bytes of data')

        lines_str = self.s.recv(file_size).decode('utf-8')
        lines = lines_str.split('\n')
        self.__lines_count = len(lines)

        max_len = 0

        for line in lines:
            if max_len < len(line):
                max_len = len(line)

        self.__text = lines_str
        self.__max_len = max_len
        self.__lines_count = len(lines)

    def show_contents(self):
        self.__text_box.delete(1., tk.END)
        self.__text_box.insert(tk.END, self.__text)

    def check_and_save(self, *args):
        self.adjust_text()

        encoded = self.__text.encode('utf-8')
        print('Sending to server...')

        self.s.send(SAVE_BYTE)
        self.s.send(len(encoded).to_bytes(16, 'big'))
        self.s.send(encoded)

    def disconnect(self):
        self.s.send(END_BYTE)
        self.s.close()
