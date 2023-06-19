import requests
import json
import os
import tkinter as tk
from tkinter.messagebox import showinfo


class MyCheckbutton(tk.Checkbutton):
    name = None


class Mem_Thif:

    def __init__(self, token=None, vers_api=5.131):
        self.directoria = os.getcwd()
        self.publick_section = []
        self.token = token
        self.vers_api = vers_api
        self.create_dir()
        self.get_publicks()

    def get_publicks(self):
        os.chdir(self.directoria)
        if os.path.isfile('publicks.txt'):
            with open('publicks.txt') as publicks:
                for publick in publicks.readlines():
                    self.publick_section.append(publick.rstrip())

    def wrire_publicks(self):
        os.chdir(self.directoria)
        with open('publicks.txt', 'w') as text:
            for st in self.publick_section:
                text.write(st + '\n')

    def get_token(self, token: str):
        self.token = token

    def create_dir(self, name_dir="memes"):
        os.chdir(self.directoria)
        if not os.path.isdir(name_dir):
            os.mkdir(name_dir)

    def add_publick(self, name_publick: str):
        os.chdir(self.directoria)
        if name_publick in self.publick_section:
            showinfo('Ошибка', 'Паблик уже добавлен')
        else:
            self.publick_section.append(name_publick)
            self.wrire_publicks()

    def del_publick(self, name_publick):
        os.chdir(self.directoria)
        self.publick_section.remove(name_publick)
        self.wrire_publicks()

    def get_responce(self):
        if self.publick_section:
            for domain in self.publick_section:
                responce = requests.get('https://api.vk.com/method/wall.get',
                                        params={
                                            'access_token': self.token,
                                            'v': self.vers_api,
                                            'domain': domain
                                        })
                try:
                    responce.json()['response']['items'][1:]
                except KeyError:
                    if responce.json()['error']['error_code'] != 5:
                        showinfo('Error', 'Неправильное название паблика')
                    else:
                        showinfo('Error', 'Неправильный токен')
                else:

                    try:
                        os.chdir('memes')
                        os.mkdir(domain)
                    except FileExistsError:
                        pass
                    data = responce.json()['response']['items'][1:]
                    mem = max(data, key=lambda name: name['likes']['count'])
                    url = mem['attachments'][0]['photo']['sizes'][-1]['url']
                    text = mem['text']
                    self.download_mem(domain, url, text)


        else:
            showinfo('Ошибка', 'Список пабликов пуст')

    def download_mem(self, domain, url, caption):
        responce = requests.get(url)
        with open(f"{domain}/{domain}.jpg", 'wb') as picture:
            picture.write(responce.content)
        if caption:
            with open(f"{domain}/{domain}.txt", 'w', encoding='utf-8') as text:
                text.write(caption)
        os.chdir(self.directoria)


class WorkDesk:
    win = tk.Tk()
    create = tk.Button(win)
    thif = Mem_Thif()
    roberry = tk.Button(win)

    @classmethod
    def menubar_cascad(cls):
        menubar = tk.Menu(cls.win)
        cls.win.config(menu=menubar)

        setting_menu = tk.Menu(menubar, tearoff=0)
        setting_menu.add_command(label='Написать свой токен', command=cls.setting)

        menubar.add_cascade(label='Токен ВК', menu=setting_menu)

    @classmethod
    def add_publick_desk(cls):
        def add():
            add_publick = publick.get()
            if add_publick:
                cls.thif.add_publick(add_publick)
                publick.delete(0, tk.END)

        win_set = tk.Toplevel(cls.win)
        win_set.geometry(f'300x200')
        win_set.wm_title('Добавить паблик')
        tk.Label(win_set, text='Имя паблика').grid(column=0, row=0)
        publick = tk.Entry(win_set)
        publick.grid(column=0, row=1)
        tk.Button(win_set, text='Добавить', command=add).grid(column=0, row=2)

    @classmethod
    def del_publick_desk(cls):

        def deliter():
            for num, pub in enumerate(varable_list):
                if pub.get():
                    cls.thif.del_publick(check_list[num].name)
                win_set.destroy()

        check_list = []
        varable_list = []
        win_set = tk.Toplevel(cls.win)
        win_set.wm_title('Удалить паблик')
        for name in cls.thif.publick_section:
            varable = tk.IntVar()
            publick = MyCheckbutton(win_set, text=name)
            publick.name = name
            publick.config(variable=varable)
            varable_list.append(varable)
            check_list.append(publick)
        for check in check_list:
            check.pack(anchor='w')
        button = tk.Button(win_set, text='Удалить', command=deliter)
        button.pack(anchor='se')

    @classmethod
    def menubar_cascad_and_thif(cls):
        menubar = tk.Menu(cls.win)
        cls.win.config(menu=menubar)

        setting_menu = tk.Menu(menubar, tearoff=0)
        rule_bot = tk.Menu(menubar, tearoff=0)
        rule_bot.add_command(label='Добавить паблик', command=cls.add_publick_desk)
        rule_bot.add_command(label='Удалить паблик', command=cls.del_publick_desk)

        setting_menu.add_command(label='Написать свой токен', command=cls.setting)

        menubar.add_cascade(label='Токен ВК', menu=setting_menu)
        menubar.add_cascade(label='Bot', menu=rule_bot)

    @classmethod
    def setting(cls):
        def str_token():
            if token.get():
                cls.token = token.get()
                token.delete(0, tk.END)
                with open('token.txt', 'w') as api:
                    api.write(cls.token)
            else:
                showinfo('Error', 'Пустое поле ввода')

        win_set = tk.Toplevel(cls.win)
        win_set.geometry(f'300x200')
        win_set.wm_title('Написать свой токен')
        tk.Label(win_set, text='Токен из вк').grid(column=0, row=0)
        token = tk.Entry(win_set)
        token.grid(column=0, row=1)
        tk.Button(win_set, text='get', command=str_token).grid(column=0, row=2)

    @classmethod
    def get_token(cls):
        print()
        try:
            with open('token.txt') as api:
                token = api.read()
                cls.thif.get_token(token=token)
            cls.menubar_cascad_and_thif()
            cls.roberry.config(text='Спиздим мемы', command=cls.thif.get_responce, fg='red', font='Areal 15')
            cls.roberry.pack(anchor='center')
        except FileNotFoundError:
            showinfo('Error', 'Нет токена')

    @classmethod
    def start(cls):
        if os.path.isfile('token.txt'):
            cls.get_token()
            cls.menubar_cascad_and_thif()
            cls.roberry.config(text='Спиздим мемы', command=cls.thif.get_responce, fg='red', font='Areal 15')
            cls.roberry.pack(anchor='center')
        else:
            cls.menubar_cascad()
        cls.create.config(text='create', command=cls.get_token, fg='red', font='Areal 15')
        cls.create.pack()
        cls.win.title('Спиздим мемы')
        cls.win.geometry("600x450")
        cls.win.mainloop()


def main():
    WorkDesk.start()


if __name__ == '__main__':
    main()
