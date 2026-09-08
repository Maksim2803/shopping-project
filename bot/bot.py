from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from .MenuManager import MenuManager
from .storage import Storage

class Bot:
    def __init__(self,token):
        self.token=token
        self.bot=TeleBot(token)
    def start(self):
        print("Бот запущен")
        self.bot.infinity_polling()

class Dispatcher(Bot):
    def __init__(self,token):
        super().__init__(token)
        self.storage = Storage("files")
        # self.board={"Главное меню":[["Мясное"], ["Очистить список","Полный список"],["Добавить кнопку","Удалить кнопку"]], "Мясное":[["Колбаса", "Мясо", "Митболы", "Курица"], ["Назад"]]}
        self.menu_manager = MenuManager()
        self.register_handler()
        self.users={}

    def register_handler(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            user=self.get_users(message.chat.id)
            user.get_status(None)
            self.load_file(message.chat.id,user)
            self.handle_start(user)
        @self.bot.message_handler(func=lambda message: True)
        def all_message(message):
            uid=message.chat.id
            if uid not in self.users:
                self.bot.send_message(uid,"Напиши /start, чтобы начать работу с ботом")
                return
            user = self.get_users(message.chat.id)
            self.handle_message(message, user)
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call):
            user=self.get_users(call.from_user.id)
            category=self.handle_callback_message(call,user)
            if category is None:
                user.get_status(None)
                user.temp_category = None
                user.temp_product = None
                self.get_menu(user)
                return
            user.temp_category=category
    def handle_start(self,user):
        self.get_menu(user)

    def handle_callback_message(self,call,user):
        uid = call.from_user.id
        user_state=user.show_status()
        self.bot.answer_callback_query(call.id)
        category=call.data
        if call.data == "Стоп":
            self.bot.send_message(uid, "Действие отменено")
            return None
        if user_state == "Добавление кнопки":
            self.bot.send_message(call.message.chat.id, "Введи название кнопки, которую хочешь добавить")
            return category
        elif user_state == "Удаление кнопки":
            self.get_menu(user,"Выбери кнопку, которую хочешь удалить",call.data)
            return category
        return None
    def creation_inline(self,board):
        new_keyboard=self.menu_manager.creation_button(board)
        keyboard = InlineKeyboardMarkup()
        for cup in new_keyboard:
            keyboard.row(*[InlineKeyboardButton(i, callback_data=i) for i in cup])
        return keyboard

    def handle_message(self, message,user):
        uid = message.chat.id
        text=message.text
        state_user=user.show_status()
        category=user.temp_category
        board=user.board
        if text=="Назад":
            self.get_menu(user)
            user.get_status(None)
            return
        if state_user=="Добавление количества":
            if self.menu_manager.check_isdigit(text):
                product=user.get_temp_product()
                self.append_cart(product,user,text)
            else:
                self.get_menu(user,"Количество продукта не добавлено, необходимо ввести количество в виде целого числа")
            user.get_status(None)
            self.save_file(uid,user)
            return
        if state_user=="Редактирование списка":
            if not self.red_user_cart(uid,user,text):
                user.get_status(None)
                self.save_file(uid,user)
            self.save_file(uid,user)
            return
        if state_user=="Добавление кнопки":
            self.add_button(text,uid,user,category)
            self.save_file(uid,user)
            return
        if state_user=="Удаление кнопки":
            self.del_button(text,uid,user,category)
            self.save_file(uid,user)
            return
        if text=="Полный список":
            self.full_user_cart(uid,user)
            user.get_status("Редактирование списка")
            return
        if text=="Очистить список":
            self.clear_user_cart(user)
            self.save_file(uid,user)
            return
        if text=="Добавить кнопку" or text=="Удалить кнопку":
            self.add_or_dell_button(uid,user,text)
            return
        if text =="/Выключить" or text=="/Включить":
            self.turn_counter(user,text)
            self.save_file(uid,user)
            return
        if text in board.keys():
            self.get_menu(user,"Выбери продукт",text)
            return
        if text:
            if user.state_counter() == True:
                self.add_quantity(uid,user,text)
                return
            self.append_cart(text, uid,user)
            self.save_file(uid,user)
            return
    def get_menu(self,user,message="Выбери категорию",name="Главное меню"):
        board=user.board
        if name in board.keys():
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            for i in board[name]:
                keyboard.row(*[KeyboardButton(btn) for btn in i])
            self.bot.send_message(user.uid, message, reply_markup=keyboard)
            return keyboard
        return None
    def get_users(self,uid):
        if uid in self.users.keys():
            return self.users[uid]
        else:
            self.users[uid]=User(uid)
            return self.users[uid]

    def save_file(self,uid,user):
        cart=user.show_cart()
        counter=user.state_counter()
        board=user.board
        data={}
        data[uid]={"board":board,"cart":cart,"counter":counter}
        self.storage.save(data)
        return uid
    def load_file(self,uid,user):
        uid=str(uid)
        data=self.storage.load()
        try:
            user.load_data(data)
        except KeyError:
            return self.save_file(uid,user)
        return

    def turn_counter(self,user,text):
        if text=="/Включить":
            user.get_counter(True)
            self.get_menu(user,"Счетчик включен")
        elif text=="/Выключить":
            user.get_counter(False)
            self.get_menu(user, "Счетчик выключен")
        return
    def add_quantity(self,uid,user,product):
        user.set_temp_product(product)
        quantity=[[1, 2, 3], [4, 5, 6]]
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for i in quantity:
            keyboard.row(*[KeyboardButton(btn) for btn in i])
        self.bot.send_message(uid, f"сколько {product}?", reply_markup=keyboard)
        user.get_status("Добавление количества")
        return uid



    def add_or_dell_button(self,uid,user,text):
        board=user.board
        keyboard=self.creation_inline(board)
        if text == "Добавить кнопку":
            self.bot.send_message(uid, """В какую категорию добавить кнопку?
Если хотите отменить действие нажмите [стоп]""", reply_markup=keyboard)
            user.get_status("Добавление кнопки")
        elif text == "Удалить кнопку":
            self.bot.send_message(uid, """Из какой категории удалить кнопку?
Если хотите отменить действие нажмите [стоп]""", reply_markup=keyboard)
            user.get_status("Удаление кнопки")
        return uid
    def add_button(self,text,uid,user,category):
        board=user.board
        button=self.menu_manager.add_button_part1(text,category,board)
        if button=="name is taken":
            self.get_menu(user,"Кнопка с таким именем уже есть, выберете другое имя")
            user.get_status(None)
        elif button=="name unavailable":
            self.get_menu(user,"Недопустимое имя кнопки, выберите другое имя")
            user.get_status(None)
        elif button=="category not selected":
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            self.bot.send_message(uid, "Выберите категорию из списка", reply_markup=keyboard)
            self.add_or_dell_button(uid,user,"Добавить кнопку")
        else:
            self.get_menu(user,"Кнопка добавлена",category)
            user.get_status(None)
        return uid
    def del_button(self,text,uid,user,category):
        board=user.board
        button=self.menu_manager.delete_buttons(text,category,board)
        if button=="KeyError":
            self.bot.send_message(uid, "Необходимо выбрать категорию")
            self.add_or_dell_button(uid,user, "Удалить кнопку")
        elif button=="prohibited for removal":
            self.get_menu(user,f"Извини, кнопку [{text}] нельзя удалить. Удаление данной кнопки нарушит работу бота")
            self.add_or_dell_button(uid,user, "Удалить кнопку")
        else:
            self.get_menu(user,f"Кнопка {text} удалена",category)
            user.get_status(None)
        return uid


    def append_cart(self,product,user,quantity=0):
        user.append_product(product,quantity)
        if quantity!=0:
            self.get_menu(user, f"Добавил {product}-{quantity}шт")
        else:
            self.get_menu(user,f"Добавил {product}")
    def red_user_cart(self,uid,user,product):
        if not user.red_cart(product):
            self.get_menu(user,"Cписок покупок пуст")
            return None
        self.full_user_cart(uid,user)
        return uid
    def clear_user_cart(self,user):
        user.clear_cart()
        self.get_menu(user,"Список покупок очищен")
        return
    def full_user_cart(self,uid,user):
        if not user.full_cart():
            self.get_menu(user,"Список покупок пуст")
        else:
            text_spisok, keyboard=user.full_cart()
            self.bot.send_message(uid, f"{"".join(text_spisok)}", reply_markup=keyboard)
        return uid

class User:
    def __init__(self,uid):
        self.board = {
            "Главное меню": [["Мясное"], ["Очистить список", "Полный список"], ["Добавить кнопку", "Удалить кнопку"]],
            "Мясное": [["Колбаса", "Мясо", "Митболы", "Курица"], ["Назад"]]}
        self.uid=uid
        self.cart=[]
        self.state=None
        self.counter_enabled = True
        self.menu_category = None
        self.temp_product = None
        self.temp_quantity = None
        self.temp_category = None
    def append_product(self,product,quantity=0):
        if quantity!=0:
            self.cart.append(f"{product}-{quantity}")
            return product
        else:
            self.cart.append(product)
            return product

    def full_cart(self):
        if not self.cart:
            return None
        else:
            text_spisok = [f"{i}\n" for i in self.cart]
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            for i in self.cart:
                keyboard.row(KeyboardButton(i))
            keyboard.row(KeyboardButton("Назад"))
            return text_spisok, keyboard
    def red_cart(self,product):
        cart=self.cart
        if not cart:
            return None
        cart.remove(product)
        return cart
    def get_cart(self,cart):
        self.cart=cart
        return self.cart
    def clear_cart(self):
        self.cart.clear()
        return
    def show_cart(self):
        return self.cart

    def get_status(self,status):
        self.state=status
        return status
    def show_status(self):
        return self.state

    def get_counter(self,status):
        self.counter_enabled=status
        return self.counter_enabled
    def state_counter(self):
        return self.counter_enabled

    def set_temp_product(self,product):
        self.temp_product = product
        return self.temp_product
    def get_temp_product(self):
        return self.temp_product
    def load_data(self,data):
        uid = str(self.uid)
        self.get_cart(data[uid]["cart"])
        self.board.clear()
        self.board.update(data[uid]["board"])
        self.get_counter(data[uid]["counter"])
        return self.board


import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")


