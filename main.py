import telebot
from telebot import types
from config import  bot_token, admin, logs, channel, support
import sqlite3

name=''
description=''
photo_status=0
photo_id=''

bot = telebot.TeleBot(bot_token)

connect=sqlite3.connect('films.db')
cursor=connect.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS films(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    photo_status  INTEGER,
    photo_id TEXT,
    activate INTEGER
)""")
connect.commit()


@bot.message_handler(content_types=['text'])
def start(message):
    connect=sqlite3.connect('users.db')
    cursor=connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        tg_id INTEGER,
        admin INTEGER
    )""")
    connect.commit()

    people_id = message.chat.id
    cursor.execute(f"SELECT tg_id FROM users WHERE tg_id={message.chat.id}")
    data=cursor.fetchone()

    if data is None:
        connect  = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute('INSERT INTO users (name, tg_id, admin) VALUES (?, ?, ?)', (message.from_user.first_name, message.chat.id, 0))
        connect.commit()
    if check(message):
        connect  = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute(f'SELECT admin FROM users WHERE tg_id = ?', (message.chat.id,))
        connect.commit()
        adminn=(cursor.fetchall())[0][0]
        if message.text=='✅ Я подписался':
            klava=types.ReplyKeyboardRemove()
            bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEGoyhjiMNBrIScwUeaIPWGgs_OjOhi0gAChwIAAladvQpC7XQrQFfQkCsE", reply_markup=klava)
            user_menu(message)
        if message.text=='/start':
            klava=types.ReplyKeyboardRemove()
            bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEGoyhjiMNBrIScwUeaIPWGgs_OjOhi0gAChwIAAladvQpC7XQrQFfQkCsE", reply_markup=klava)
            user_menu(message)
        elif message.text=='/admin' and (message.chat.id==admin or adminn==1):
            admin_menu(message)
        elif message.text=='➕ Добавить фильм' and (message.chat.id==admin or adminn==1):
            add_new_film(message)
        elif message.text=='📖 Список фильмов' and (message.chat.id==admin or adminn==1):
            connect  = sqlite3.connect('films.db')
            cursor = connect.cursor()
            cursor.execute(f'SELECT id FROM films ORDER BY id DESC LIMIT 1')
            connect.commit()
            i=1
            text='Список фильмов:\n'
            i2=int((cursor.fetchall())[0][0])
            for i in range(i2):
                
                connect  = sqlite3.connect('films.db')
                cursor = connect.cursor()
                cursor.execute(f'SELECT activate FROM films WHERE id = ?', (i+1,))
                connect.commit()
                ac=(cursor.fetchall())[0][0]
                if ac!=1:
                    connect  = sqlite3.connect('films.db')
                    cursor = connect.cursor()
                    cursor.execute(f'SELECT name FROM films WHERE id = ?', (i+1,))
                    connect.commit()
                    text=text+f'\n№{i+1} - {cursor.fetchall()[0][0]}'
            
            if len(text) > 4096:
                for x in range(0, len(text), 4096):
                    bot.send_message(message.chat.id, text[x:x+4096])
            else:
                bot.send_message(message.chat.id,text)
            admin_menu(message)
        elif message.text=='➖ Удалить фильм' and (message.chat.id==admin or adminn==1):
            delit=bot.send_message(message.chat.id,'🗑 Для удаления фильма введи его код')
            bot.register_next_step_handler(delit,del_f)
        elif message.text=='🏠 Меню':
            klava=types.ReplyKeyboardRemove()
            bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEGoyhjiMNBrIScwUeaIPWGgs_OjOhi0gAChwIAAladvQpC7XQrQFfQkCsE", reply_markup=klava)
            user_menu(message)
        elif message.text=='🏚 Мeню':
            klava=types.ReplyKeyboardRemove()
            admin_menu(message)
        elif message.text=='✍️ Реклама' and message.chat.id==admin:
            connect  = sqlite3.connect('users.db')
            cursor = connect.cursor()
            cursor.execute(f'SELECT COUNT (id) FROM users')
            connect.commit()
            klava=types.ReplyKeyboardMarkup(resize_keyboard=True)
            button1='☑️ Создаем'
            button2='⬅️ Вернуться'
            klava.add(button1,button2)
            bot.send_message(message.chat.id,f'В вашем боте `{cursor.fetchall()[0][0]}` пользователей. Хотите создать рассылку?', parse_mode='Markdown',reply_markup=klava)
        elif message.text=='🔍 Найти фильм':
            klava=types.ReplyKeyboardRemove()
            find=bot.send_message(message.chat.id,'✏️ Введи код фильма, название которого ты хочешь узнать:',reply_markup=klava)
            bot.register_next_step_handler(find,find_f)
        elif message.text=='☑️ Создаем' and message.chat.id==admin:
            klava=types.ReplyKeyboardRemove()
            ads=bot.send_message(message.chat.id,'✏️ Введи текст своей рассылки. Если хочешь, что бы у рассылки была фотография - отправь фотографию, добавив к ней текст (одним сообщением)',reply_markup=klava)
            bot.register_next_step_handler(ads,ads_f)
        elif message.text=='⬅️ Вернуться' and message.chat.id==admin:
            admin_menu(message)
        elif message.text=='⚙️ Админы' and message.chat.id==admin:
            klava=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
            button1='🗒 Список'
            button2='⚙️ Назначить'
            button4='🏚 Мeню'
            klava.add(button1,button2,button4)
            bot.send_message(message.chat.id,'👤 В боте у тебя могут быть помощники. Человек, имеющий статус  админа может добавлять/удалять  фильмы. Для просмотра списка таких людей - достаточно нажать кнопку "Список". Хочешь назначить/снять админа? Жми кнопку "Назначить". Так же в специальный канал будут отправляться сообщения об их действиях (на всякий случай)', reply_markup=klava)
        elif message.text=='⚙️ Назначить' and message.chat.id==admin:
            klava=types.ReplyKeyboardRemove()
            id_admina=bot.send_message(message.chat.id,'Для того что бы назначить человека админом - просто отправь его id в чат. Если человек уже админ, то при отправке id - должность будет снята',reply_markup=klava)
            bot.register_next_step_handler(id_admina,id_admina_f)
        elif message.text=='🗒 Список' and message.chat.id==admin:
            connect  = sqlite3.connect('users.db')
            cursor = connect.cursor()
            cursor.execute(f'SELECT id FROM users ORDER BY id DESC LIMIT 1')
            connect.commit()
            i=1
            i2=int((cursor.fetchall())[0][0])
            text=''
            admincol=0
            for i in range(i2+1):
                if i!= i2:
                    connect  = sqlite3.connect('users.db')
                    cursor = connect.cursor()
                    cursor.execute(f'SELECT admin FROM users WHERE id = ?', (i+1,))
                    connect.commit()
                    n=(cursor.fetchall())[0][0]
                    if n ==1:
                        admincol=admincol+1
                        connect  = sqlite3.connect('users.db')
                        cursor = connect.cursor()
                        cursor.execute(f'SELECT admin FROM users WHERE id = ?', (i+1,))
                        connect.commit()
                        text=text+f'\nDbId: `{i+1}`'
                        connect  = sqlite3.connect('users.db')
                        cursor = connect.cursor()
                        cursor.execute(f'SELECT name FROM users WHERE id = ?', (i+1,))
                        connect.commit()
                        text=text+f'\nName: `{(cursor.fetchall())[0][0]}`'
                        connect  = sqlite3.connect('users.db')
                        cursor = connect.cursor()
                        cursor.execute(f'SELECT tg_id FROM users WHERE id = ?', (i+1,))
                        connect.commit()
                        text=text+f'\nTgId: `{(cursor.fetchall())[0][0]}`\n\n'
            text=f'Всего админов: {admincol}\n'+text
            bot.send_message(message.chat.id,text, parse_mode='Markdown')
            admin_menu(message)
        elif message.text=='Заказать рекламу':
            bot.send_message(message.chat.id,f'Для заказа рекламы пиши {support}')
            user_menu(message)
        else:
            bot.send_message(message.chat.id,'🤕 Ой.. Команда не найдена. Напиши /start')
def id_admina_f(message):
    connect  = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute(f'SELECT admin FROM users WHERE tg_id = ?', (message.text,))
    connect.commit()
    admin=(cursor.fetchall())[0][0]
    connect  = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute(f'SELECT name FROM users WHERE tg_id = ?', (message.text,))
    connect.commit()
    name=(cursor.fetchall())[0][0]
    if admin == 0:
        admin=1
        bot.send_message(message.chat.id,f'{name} | {message.text} был назначен администратором!')
    elif admin == 1:
        admin=0
        bot.send_message(message.chat.id,f'{name} | {message.text} был снят с поста администратора!')
    connect  = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute('UPDATE users SET admin = (?) WHERE tg_id = (?)', (admin,message.text, )) 
    connect.commit()
    connect  = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute(f'SELECT name FROM users WHERE tg_id = ?', (message.text,))
    connect.commit()
    admin_menu(message)

def ads_f(message):
    global photo_status
    global photo_id
    global description
    if message.content_type=='photo':
        bot.send_photo(message.chat.id, message.photo[0].file_id, message.caption)
        klava=types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1='✅ Создаем'
        button2='⬅️ Вернуться'
        klava.add(button1,button2)
        photo_status=1
        description=message.caption
        photo_id=message.photo[0].file_id
        ads_y=bot.send_message(message.chat.id,'Вот так будет выглядеть рассылка. Проверь и подтверди старт рекламы', reply_markup=klava)
        bot.register_next_step_handler(ads_y,ads_yf)
    else:
        bot.send_message(message.chat.id, message.text)
        klava=types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1='✅ Создаем'
        button2='⬅️ Вернуться'
        klava.add(button1,button2)
        photo_status=0
        description=message.text
        ads_y=bot.send_message(message.chat.id,'Вот так будет выглядеть рассылка. Проверь и подтверди старт рекламы', reply_markup=klava)
        bot.register_next_step_handler(ads_y,ads_yf)

def ads_yf(message):
    global photo_status
    global photo_id
    global description

    connect  = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute(f'SELECT id FROM users ORDER BY id DESC LIMIT 1')
    connect.commit()
    i=1
    i2=int((cursor.fetchall())[0][0])
    try_false=0
    try_true=0
    for i in range(i2+1):
        connect  = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute(f'SELECT tg_id FROM users WHERE id = ?', (i,))
        connect.commit()
        if photo_status==1:
            try_true=try_true+1
            try:
                bot.send_photo(cursor.fetchall()[0][0],photo_id,description)
            except Exception as error:
                try_false=try_false+1

        else:
            try_true=try_true+1
            try:
                bot.send_message(cursor.fetchall()[0][0],description)
            except Exception as error:
                try_false=try_false+1
    
    text=f'📭 Рассылка была отправлена `{try_true-1}` пользователям!\n✅ Успешно доставлено: `{try_true-try_false}`\n❌ Не дошло: `{try_false-1}`'
    bot.send_message(message.chat.id, text, parse_mode='Markdown')
    admin_menu(message)

def find_f(message):
    if (message.text).isdigit():   
        connect  = sqlite3.connect('films.db')
        cursor = connect.cursor()
        cursor.execute(f'SELECT id FROM films ORDER BY id DESC LIMIT 1')
        connect.commit()
        if int(message.text) > int(cursor.fetchall()[0][0]) or str(message.text)=='0':
            bot.send_message(message.chat.id,f'К сожалению, фильм с кодом {message.text} еще не был добавленным в бота')
            user_menu(message)
        else:
        
            connect=sqlite3.connect('films.db')
            cursor=connect.cursor() 
            cursor.execute('SELECT activate FROM films WHERE id = (?)', (message.text, ))    
            connect.commit()
            activate=int(cursor.fetchall()[0][0])
            if activate==0:
                connect=sqlite3.connect('films.db')
                cursor=connect.cursor() 
                cursor.execute('SELECT name FROM films WHERE id = (?)', (message.text, ))    
                connect.commit()
                name=(cursor.fetchall()[0][0])
                connect=sqlite3.connect('films.db')
                cursor=connect.cursor() 
                cursor.execute('SELECT description FROM films WHERE id = (?)', (message.text, ))    
                connect.commit()
                description=(cursor.fetchall()[0][0])
                connect=sqlite3.connect('films.db')
                cursor=connect.cursor() 
                cursor.execute('SELECT photo_status FROM films WHERE id = (?)', (message.text, ))    
                connect.commit()
                photo_status=(cursor.fetchall()[0][0])
                connect=sqlite3.connect('films.db')
                cursor=connect.cursor() 
                cursor.execute('SELECT photo_id FROM films WHERE id = (?)', (message.text, ))    
                connect.commit()
                photo_id=(cursor.fetchall()[0][0])
                
                if photo_status==1:
                    bot.send_photo(message.chat.id,photo_id, f'🔥 Код: {message.text}\n\n🎥 Название: `{name}`\n\n{description}',parse_mode='Markdown')
                else:  
                    bot.send_message(message.chat.id,f'🔥 Код: {message.text}\n\n🎥 Название: `{name}`\n\nОписание: {description}',parse_mode='Markdown')
                user_menu(message)
            else:
                bot.send_message(message.chat.id,f'К сожалению, фильм с кодом {message.text} был удален из бота')
                user_menu(message)

    else:
        bot.send_message(message.chat.id, 'Код фильма - число. Возвращаюсь к меню')
        user_menu(message)


def del_f(message):
    if (message.text).isdigit():
        connect=sqlite3.connect('films.db')
        cursor=connect.cursor() 
        cursor.execute('UPDATE films SET activate = (?) WHERE id = (?)', (1,message.text, ))    
        connect.commit()
        bot.send_message(message.chat.id, 'Фильм был удален')
        iddd=message.text

      


        connect  = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute(f'SELECT id FROM users WHERE tg_id = ?', (message.chat.id,))
        connect.commit()
        id=(cursor.fetchall())[0][0]
        connect  = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute(f'SELECT name FROM users WHERE id = ?', (id,))
        connect.commit()
        name=(cursor.fetchall())[0][0]
        connect  = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute(f'SELECT tg_id FROM users WHERE id = ?', (id,))
        connect.commit()
        idd=(cursor.fetchall())[0][0]

        bot.send_message(logs,f'Админ `{name}` | `{id}` | `{idd}` удалил фильм №`{iddd}`!', parse_mode='Markdown')
        admin_menu(message)
        


    else:
        bot.send_message(message.chat.id, 'Код фильма - число. Возвращаюсь к меню')
        admin_menu(message)

def add_new_film(message):
    if message.text=='➕ Добавить фильм':
        klava=types.ReplyKeyboardRemove()
        name=bot.send_message(message.chat.id,'🔍 Введи название фильма',reply_markup=klava)
        bot.register_next_step_handler(name,add_name)

def add_name(message):
    global name
    name=message.text
    description=bot.send_message(message.chat.id,'🔍 Введи описание фильма')
    bot.register_next_step_handler(description,add_description)

def add_description(message):
    global description
    description=message.text
    klava=types.ReplyKeyboardMarkup(resize_keyboard=True)
    photo=bot.send_message(message.chat.id,'📸 Добавьте фотографию к фильму (если не хотите ее добавлять - напишите любой текст)')
    bot.register_next_step_handler(photo,add_photo)
   

def add_photo(message):
    global name
    global description
    global photo_status
    global photo_id
    if message.content_type=='photo':
        photo_status=1
        photo_id=message.photo[0].file_id
        klava=types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1='✅ Создаем фильм'
        button2='❌ Не создаем'
        klava.add(button1,button2)
        bot.send_message(message.chat.id, 'Вот что вышло:')
        answer=bot.send_photo(message.chat.id, photo_id, f'🎥 Название: {name}\n\n{description}',reply_markup=klava)
        bot.register_next_step_handler(answer,create)
    elif message.content_type=='text':
        photo_status=0
        klava=types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1='✅ Создаем фильм'
        button2='❌ Не создаем'
        klava.add(button1,button2)
        bot.send_message(message.chat.id, 'Вот что вышло:')
        answer=bot.send_message(message.chat.id, f'🎥 Название: {name}\n\n{description}',reply_markup=klava)
        bot.register_next_step_handler(answer,create)
        

def create(message):
    global name
    global description
    global photo_status
    global photo_id
    if message.text=='✅ Создаем фильм':
        connect  = sqlite3.connect('films.db')
        cursor = connect.cursor()
        cursor.execute('INSERT INTO films (name, description, photo_status, photo_id, activate) VALUES (?, ?, ?, ?, ?)', (name, description, photo_status, photo_id, 0))
        connect.commit()
        
        connect  = sqlite3.connect('films.db')
        cursor = connect.cursor()
        cursor.execute(f'SELECT id FROM films ORDER BY id DESC LIMIT 1')
        connect.commit()
        id_f=cursor.fetchall()[0][0]
        bot.send_message(message.chat.id,f'Фильм №{id_f} был успешно добавлен!')
        admin_menu(message)

        connect=sqlite3.connect('films.db')
        cursor=connect.cursor() 
        cursor.execute('SELECT name FROM films WHERE id = (?)', (id_f, ))    
        connect.commit()
        namead=(cursor.fetchall()[0][0])
        connect=sqlite3.connect('films.db')
        cursor=connect.cursor() 
        cursor.execute('SELECT description FROM films WHERE id = (?)', (id_f, ))    
        connect.commit()
        description=(cursor.fetchall()[0][0])
        connect=sqlite3.connect('films.db')
        cursor=connect.cursor() 
        cursor.execute('SELECT photo_status FROM films WHERE id = (?)', (id_f, ))    
        connect.commit()
        photo_status=(cursor.fetchall()[0][0])
        connect=sqlite3.connect('films.db')
        cursor=connect.cursor() 
        cursor.execute('SELECT photo_id FROM films WHERE id = (?)', (id_f, ))    
        connect.commit()
        photo_id=(cursor.fetchall()[0][0])


        connect  = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute(f'SELECT id FROM users WHERE tg_id = ?', (message.chat.id,))
        connect.commit()
        id=(cursor.fetchall())[0][0]
        connect  = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute(f'SELECT name FROM users WHERE id = ?', (id,))
        connect.commit()
        name=(cursor.fetchall())[0][0]
        connect  = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute(f'SELECT tg_id FROM users WHERE id = ?', (id,))
        connect.commit()
        idd=(cursor.fetchall())[0][0]

        bot.send_message(logs,f'Админ `{name}` | `{id}` | `{idd}` создал новый фильм!', parse_mode='Markdown')
        if photo_status==1:
            bot.send_photo(logs,photo_id, f'🔥 Код: {message.text}\n\n🎥 Название: `{namead}`\n\n{description}',parse_mode='Markdown')
        else:  
            bot.send_message(logs,f'🔥 Код: {message.text}\n\n🎥 Название: `{namead}`\n\n{description}',parse_mode='Markdown')

       
    else:
        bot.send_message(message.chat.id,'Фильм не был создан')
        admin_menu(message)

def check(message):
    c=0
    c2=0
    for i in channel:
        chat = bot.get_chat_member(i[2], message.chat.id)
        c2=c2+1
        if chat.status == 'left':
            c=c+1
    if c!=0:
        inklava=types.InlineKeyboardMarkup()
        for i in channel:
            newitem=types.InlineKeyboardButton(text=i[0], url=i[1]) 
            inklava.add(newitem)
        button1=types.InlineKeyboardButton(text='✅ Я подписался',callback_data='subs')
        inklava.add(button1)
        check_sub = bot.send_message(message.chat.id, f'😶 Упс.. Для использования бота необходимо вступить в каналы (ссылки на канал ниже)\nПосле подписки - нажми на кнопку ниже',reply_markup=inklava)
       
    else: 
     
        return True

@bot.callback_query_handler(func= lambda callback: callback.data)
def call(callback):
    if callback.data=='subs':
        if check(callback.message):
            klava=types.ReplyKeyboardRemove()
            bot.send_sticker(callback.message.chat.id, "CAACAgIAAxkBAAEGoyhjiMNBrIScwUeaIPWGgs_OjOhi0gAChwIAAladvQpC7XQrQFfQkCsE", reply_markup=klava)
            user_menu(callback.message)

def admin_menu(message):
    
    bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEGpwljiiLN4R5EfBVCoNSEWAEjjojuTgACeAIAAladvQr8ugi1kX0cDCsE")
    klava=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=3)
    button1='➕ Добавить фильм'
    button2='📖 Список фильмов'
    button3='➖ Удалить фильм'
    button5='🏠 Меню'
    if message.chat.id==admin:
        button4='⚙️ Админы'
        button6='✍️ Реклама'
        klava.add(button1,button2,button3,button4,button5,button6)
    else:
        
        klava.add(button1,button2,button3,button5)
    bot.send_message(message.chat.id,'Вы в админ меню!',reply_markup=klava)

def user_menu(message):

    connect=sqlite3.connect('users.db')
    cursor=connect.cursor() 
    cursor.execute('SELECT name FROM users WHERE tg_id = (?)', (message.chat.id, ))    
    connect.commit()
    name=(cursor.fetchall()[0][0])

    klava=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
    button1='🔍 Найти фильм'
    button2='Заказать рекламу'
    klava.add(button1,button2)
    bot.send_message(message.chat.id,f'Главное меню:',reply_markup=klava)
 
bot.polling()



 