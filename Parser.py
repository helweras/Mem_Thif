import requests
import os
import tkinter as tk
from tkinter.messagebox import showinfo
from tkinter import ttk
import datetime
import time
from PIL import Image, ImageChops


class MyCheckbutton(tk.Checkbutton):
    name = None


class MemThif:
    '''Класс для получения самых залайканых мемов с выбранных пабликов'''
    count_write_memes = 0

    def __init__(self, token='37ad53b837ad53b837ad53b83634b92ef8337ad37ad53b8532a0bbcb25f3bc98831a9dd', vers_api=5.131):
        self.directoria = os.getcwd()
        self.publick_section = []
        self.token = token
        self.vers_api = vers_api
        self.get_publicks()

    def get_publicks(self):
        '''Метод добавляет названия пабликов(домены) из текстового файла(если он есть) publicks.txt
        в атрибут экземпляра класса publick_section'''
        os.chdir(self.directoria)
        if os.path.isfile('publicks.txt'):
            with open('publicks.txt') as publicks:
                for publick in publicks.readlines():
                    self.publick_section.append(publick.rstrip())

    def wrire_publicks(self):
        '''Метод добавляет названия пабликов(домены) в текстовый файл'''
        os.chdir(self.directoria)
        with open('publicks.txt', 'w') as text:
            for st in self.publick_section:
                text.write(st + '\n')

    def get_token(self, token: str):
        self.token = token
        self.create_dir()

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

    def compare_date(self, items):
        items_list = []
        for item in items:
            if item['attachments'][0]['type'] == 'photo':
                post_time = item['date']
                post_date = (datetime.datetime.fromtimestamp(int(post_time))
                             .strftime('%Y-%m-%d %H:%M:%S'))
                if self.get_time_now() < post_date:
                    items_list.append(item)
        return items_list

    @staticmethod
    def get_time_now():
        now = (datetime.datetime.fromtimestamp(int(time.time() - 24 * 3600))
               .strftime('%Y-%m-%d %H:%M:%S'))
        return now

    def get_responce(self):
        self.create_dir()
        if self.publick_section:
            for domain in self.publick_section:
                responce = requests.get('https://api.vk.com/method/wall.get',
                                        params={
                                            'access_token': self.token,
                                            'v': self.vers_api,
                                            'domain': domain
                                        })
                try:
                    responce.json()['response']['items']
                except KeyError:
                    if responce.json()['error']['error_code'] != 5:
                        showinfo('Error', 'Неправильное название паблика')
                    else:
                        showinfo('Error', 'Неправильный токен')
                else:

                    try:
                        os.chdir('memes')
                        os.mkdir(domain)
                    except FileNotFoundError:
                        showinfo('Ошибка', 'Нет папки memes\n Нажми Create')
                        return
                    except FileExistsError:
                        pass
                    data = responce.json()['response']['items']
                    mem_list = self.compare_date(data)
                    if mem_list:
                        mem = max(mem_list, key=lambda name: name['likes']['count'])
                        url = mem['attachments'][0]['photo']['sizes'][-1]['url']
                        text = mem['text']
                        self.download_mem(domain, url, text)

                    else:
                        continue
            WorkDesk.info(len(self.publick_section))
            self.count_write_memes = 0
            WorkDesk.progressbar['value'] = 0



        else:
            showinfo('Ошибка', 'Список пабликов пуст')

    def chec_pictures(self, pictures, domain=None):
        '''Проверяет последнюю скачанную картинку и описание к ней(если оно есть) на одинаковсть
        и удаляет их если это так'''

        def del_text():
            '''Проверяет есть ли описание к картинке и удаляет его'''
            last_text = os.listdir(f'{self.directoria}/memes/{domain}/')[-1]  # Получение название файла
            if last_text.endswith('txt'):  # Проверка расширения файла
                last_text_way = os.path.join(f'{self.directoria}/memes/{domain}/',
                                             last_text)  # Получение полного пути к файлу
                os.remove(last_text_way)  # Удаление файла

        last_image_way = os.path.join(f'{self.directoria}/memes/{domain}/', pictures)
        last_image_picture = Image.open(last_image_way)
        for filename in os.listdir(f'{self.directoria}/memes/{domain}/')[:-1]:
            way = os.path.join(f'{self.directoria}/memes/{domain}/', filename)
            if os.path.isfile(way) and filename.endswith('.jpg'):
                image = Image.open(way)
                result = ImageChops.difference(last_image_picture, image)
                if result.getbbox() is None:
                    os.remove(last_image_way)
                    del_text()

    def download_mem(self, domain, url, caption):

        responce = requests.get(url)
        files = len(os.listdir(path=f"{domain}/"))
        if files:
            with open(f"{domain}/{domain}{files}.jpg", 'wb') as picture:
                picture.write(responce.content)
            if caption:
                with open(f"{domain}/{domain}{files}.txt", 'w', encoding='utf-8') as text:
                    text.write(caption)

            last_image = os.listdir(f'{self.directoria}/memes/{domain}/')[-1]
            if last_image.endswith('txt'):
                last_image = os.listdir(f'{self.directoria}/memes/{domain}/')[-2]

            self.chec_pictures(last_image, domain)

        else:
            with open(f"{domain}/{domain}.jpg", 'wb') as picture:
                picture.write(responce.content)
            if caption:
                with open(f"{domain}/{domain}.txt", 'w', encoding='utf-8') as text:
                    text.write(caption)
        self.count_write_memes += 1
        WorkDesk.progress_bar()
        os.chdir(self.directoria)


class WorkDesk:
    '''Класс в котором описывается графическая часть программы.
    Один из атрибутов экземпляр класса  MemThif'''
    win = tk.Tk()

    progressbar = ttk.Progressbar(win)
    thif = MemThif()
    roberry = tk.Button(win)

    @staticmethod
    def key_release(event):
        ctrl = event.state and 4
        if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
            event.widget.event_generate("<<Cut>>")

        if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
            event.widget.event_generate("<<Paste>>")

        if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
            event.widget.event_generate("<<Copy>>")

    @classmethod
    def progress_bar(cls):
        cls.progressbar['value'] = cls.thif.count_write_memes
        cls.win.update()
        return cls.thif.count_write_memes

    @classmethod
    def info(cls, count):
        if count == len(cls.thif.publick_section):
            showinfo('Информация', f'Успешно {count} из {count}\n Зайдите в папку memes')

    @classmethod
    def add_publick_desk(cls):
        def add():
            add_publick = publick.get()
            if add_publick:
                cls.thif.add_publick(add_publick)
                publick.delete(0, tk.END)
            cls.progressbar['maximum'] = len(cls.thif.publick_section)
            WorkDesk.progressbar['value'] = 0

        win_set = tk.Toplevel(cls.win)
        win_set.geometry(f'300x200')
        win_set.wm_title('Добавить паблик')
        tk.Label(win_set, text='Имя паблика').grid(column=0, row=0)
        publick = tk.Entry(win_set)
        publick.grid(column=0, row=1)
        publick.bind("<Key>", cls.key_release)
        tk.Button(win_set, text='Добавить', command=add).grid(column=0, row=2)

    @classmethod
    def del_publick_desk(cls):

        def deliter():
            for num, pub in enumerate(varable_list):
                if pub.get():
                    cls.thif.del_publick(check_list[num].name)
                win_set.destroy()
            cls.progressbar['maximum'] = len(cls.thif.publick_section)

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

        menubar.add_cascade(label='Bot', menu=rule_bot)

    @classmethod
    def config_progressbar(cls):
        cls.progressbar.config(mode='determinate', maximum=len(cls.thif.publick_section), value=0)

    @classmethod
    def get_token(cls):
        cls.thif.create_dir()

    @classmethod
    def start(cls):
        cls.menubar_cascad_and_thif()
        cls.roberry.config(text='Спиздим мемы', command=cls.thif.get_responce, fg='red', font='Areal 15')
        cls.roberry.pack(anchor='center')
        cls.win.title('Спиздим мемы')
        cls.config_progressbar()
        cls.progressbar.pack()
        cls.progress_bar()
        cls.win.geometry("600x450")
        cls.win.mainloop()


def main():
    WorkDesk.start()


if __name__ == '__main__':
    main()
