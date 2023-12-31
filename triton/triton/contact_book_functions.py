import time
import difflib 
import sys
from pathlib import Path
from termcolor import colored

triton_path = Path(__file__).parent.parent
sys.path.append(str(triton_path))
# Внаслідок перейменування пакетів оновлено імпорт пакетів
from contact_book_classes import (
    AddressBook, 
    Name, 
    Phone, 
    Birthday, 
    Record, 
    Email, 
    Country, 
    City, 
    Street, 
    House,
    declare_view_format
)

contact_book = AddressBook()
filename = 'contact_book.bin'

exit_inputs = ['stop', 'break', '-'] # список з варіантами відповідей, якщо користувач хоче завершити виконання команди

user_inputs = ['y', 'yes', '+']  #список з варіантами відповідей, якщо користувач погоджується

CHANGING_FUNCS = ['Country', 'City', 'Street', 'House']


def error_handler(func):
    def inner(*args):
        try:
            result = func(*args)
            return result
        except KeyError:
            return colored(f"No user.", "red")
        # під час виконання різних методів виникають різні помилки ValueError. Тому пропоную їх перехоплювати у методах, 
        # щоб користувач знав у чому проблема. Крім того нам ще треба продумавти логіку для перехоплення помилок типу AttribiteError.
        except ValueError as e:
            return e
        except IndexError:
            return 'First you should enter the username and, if necessary, the required parameter'
        # Варто ще обробити помилки TypeError та AttribiteError. Вони точно будуть виникати під час роботи.
        except TypeError:
            return 'Wrong command or too many parameters are specified.'
        except AttributeError:
            return "User doesn't exist. First create a record about this user."
    return inner


# Додано програму, яка одразу після запуску завантажує contact_book з файлу та видає привітальне повідомлення.
def start():
    contact_book.load_from_file(filename)
    # Додаю невеликий привітальний текст. Тут в принципі можна й щось інше написати. І ще додав вивід кожного рядка за 1,5 секунди.
    invitation_text = [colored("I will help you organize your contact book.", "cyan"), 
                        colored("Using the command 'help', you can find out the list of available operations.", "cyan"),
                        colored("Let's start and enjoy!!!", "cyan") ]
    for string in invitation_text:
        time.sleep(1)
        print(string)

def info_text():
    info = 'To stop the execution enter one of these commands (stop, break, -)'
    print(info)

@error_handler
def helper(*args):
    res = ''
    for value in HANDLERS.values():
        res += f'{colored(value[0], "cyan")} : {colored(value[1], "yellow")}\n'
    return '\nType one of the available commands from the list below:\n\n' + res


@error_handler
def exit_command(*args):
    contact_book.save_to_file(filename) 
    return colored("\nYou've finished work with Contact book.", "yellow")


@error_handler
def data_input(class_, question):
    while True:
        try:
            answer = input(f'{question}: ')
            if answer.lower().strip() in exit_inputs:
                return 'exit'
            value = class_(answer.strip())
            return value
        except ValueError as e:
            print(e)


def no_user(name):
    return colored(f'There is no user with name {name}', "red")

def command_canceled():
    return colored('Command cancelled', "red")

@error_handler
def add_user_command(*args):
    info_text()
    name = data_input(Name, 'Enter the name of the new contact')
    if name == 'exit':
        return command_canceled()
    rec: Record = contact_book.get(str(name))
    if rec:
        return rec.add_user(name)
    rec = Record(name)
    return contact_book.add_record(rec)


@error_handler
def change_user_command(*args):
    info_text()
    name = data_input(Name, 'Enter the name of the contact you want to rename')
    if name == 'exit':
        return command_canceled()
    new_name = data_input(Name, 'Enter a new name of the contact')
    if new_name == 'exit':
        return command_canceled()
    return contact_book.change_rec_name(name, new_name)


@error_handler
def delete_rec_command(*args):
    info_text()
    name = data_input(Name, 'Enter the name of the contact you want to delete')
    if name == 'exit':
        return command_canceled()
    return contact_book.delete_rec(name)


@error_handler
def add_phone_command(*args):  # Додаємо номер телефону для вибраного користувача.
    info_text()
    name = data_input(Name, 'Enter the name of the contact whose phone you want to add')
    if name == 'exit':
        return command_canceled()
    rec: Record = contact_book.get(str(name))
    if rec:
        phone = data_input(Phone, 'Enter a phone which you want to add')
        if phone == 'exit':
            return command_canceled()
        return rec.add_phone(phone)
    return no_user(name)
    

@error_handler
def change_phone_command(*args):  # Додаємо номер телефону для вибраного користувача.
    info_text()
    name = data_input(Name, 'Enter the name of the contact whose phone you want to change')
    if name == 'exit':
        return command_canceled()
    rec: Record = contact_book.get(str(name))
    if rec:
        old_phone = data_input(Phone, 'Enter the phone you want to change')
        if old_phone == 'exit':
            return command_canceled()
        new_phone = data_input(Phone, 'Enter a new phone you want to add')
        if new_phone == 'exit':
            return command_canceled()
        return rec.change_phone(old_phone, new_phone)
    return no_user(name)


@error_handler
def delete_phone_command(*args):
    info_text()
    name = data_input(Name, 'Enter the name of the contact whose phone you want to delete')
    if name == 'exit':
        return command_canceled()
    rec: Record = contact_book.get(str(name))
    if rec:
        phone = data_input(Phone, 'Enter the phone you want to delete')
        if phone == 'exit':
            return command_canceled()
        return rec.delete_phone(phone)
    return no_user(name)


@error_handler
def add_birthday_command(*args):  # додаємо дату народження для користувача
    info_text()
    name = data_input(Name, 'Enter the name of the contact to whom you want to add birthday')
    if name == 'exit':
        return command_canceled()
    rec: Record = contact_book.get(str(name))
    if rec:
        birthday = data_input(Birthday, 'Enter the date of birth you want to add')
        if birthday == 'exit':
            return command_canceled()
        return rec.add_birthday(birthday)
    return colored(f'There is no contact with name {name}', "red")
    

@error_handler
def change_birthday_command(*args):
    info_text()
    name = data_input(Name, 'Enter the name of the contact whose birthday you want to change')
    if name == 'exit':
        return command_canceled()
    rec: Record = contact_book.get(str(name))
    if rec:
        birthday = data_input(Birthday, 'Enter a new date of birth')
        if birthday == 'exit':
            return command_canceled()
        return rec.change_birthday(birthday)
    return no_user(name)


@error_handler
def delete_birthday_command(*args):
    info_text()
    name = data_input(Name, 'Enter the name of the contact whose birthday you want to delete')
    if name == 'exit':
        return command_canceled()
    rec: Record = contact_book.get(str(name))
    return rec.delete_birthday()


@error_handler
def add_email_command(*args):  # додаємо e-mail для користувача
    info_text()
    name = data_input(Name, 'Enter the name of the contact to whom you want to add email')
    if name == 'exit':
        return command_canceled()
    rec: Record = contact_book.get(str(name))
    if rec:
        email = data_input(Email, 'Enter the email you want to add')
        if email == 'exit':
            return command_canceled()
        return rec.add_email(email)
    return no_user(name)
    

@error_handler
def change_email_command(*args):
    info_text()
    name = data_input(Name, 'Enter the name of the contact whose email you want to change')
    if name == 'exit':
        return command_canceled()
    rec: Record = contact_book.get(str(name))
    if rec:
        email = data_input(Email, 'Enter a new email you want to add')
        if email == 'exit':
            return command_canceled()
        return rec.change_email(email)


@error_handler
def delete_email_command(*args):
    info_text()
    name = data_input(Name, 'Enter the name of the contact whose email you want to delete')
    if name == 'exit':
        return command_canceled()
    rec: Record = contact_book.get(str(name))
    return rec.delete_email()


@error_handler
def days_to_birthday(*args):  # Повертає кількість днів до дня народження користувача.
    info_text()
    name = data_input(Name, 'Enter the name of the contact to know how many days left utill his/her birthday')
    if name == 'exit':
        return command_canceled()
    rec: Record = contact_book.get(str(name))
    if rec:
        return rec.days_to_birthday()
    else:
        return colored(f"User '{name}' doesn't exist. First create a record about this user.", "red")


@error_handler
def congrats_list_command(*args):  # Повертає список користувачів, які святкують ДН на протязі shift_days.
    if len(contact_book) == 0:  # Якщо словник порожній.
        return colored('Address book is now empty. Please add some users', "red")
    else:
        command_text = '''This command helps you to find out which users have a birthday during this period.
        \nEnter the number of days (an integer): '''
        text = colored(f'There are {len(contact_book)} users in address book', "yellow")
        print(text)
        shift_days = int(input(command_text))
        return contact_book.congrats_list(shift_days)


@error_handler
def birthdays_next_week(*args):  # Користувачі, котрі святкують ДН наступного тижня.
    return contact_book.next_week_birthdays()


@error_handler
def birthdays_current_week(*args):  # Користувачі, котрі святкують ДН поточного тижня.
    return contact_book.current_week_birthdays()


@error_handler
def birthdays_next_month(*args):  # Користувачі, котрі святкують ДН наступного місяця.
    return contact_book.next_month_birthdays()


@error_handler
def birthdays_current_month(*args):  # Користувачі, котрі святкують ДН поточного місяця.
    return contact_book.current_month_birthdays()


@error_handler
def how_long_user_live_command(*args):  # Функція повертає кількість прожитих днів користувачем.
    name = Name(input('Enter name of the user: '))
    rec: Record = contact_book.get(str(name))
    if rec:
        return rec.how_much_user_live()
    else:
        res = colored(f"User '{name}' doesn't exist. First create a record about this user.", "red")
        return res


@error_handler
def sort_by_name_command(args):
    return contact_book.sort_by_name()


@error_handler
def sort_by_age_command(args):
    return contact_book.sort_by_age()


@error_handler
def show_user_command(args):  # Пошук телефона вибраного користувача.
    name = data_input(Name, 'Enter the name of the contact')
    return contact_book.get_user(str(name))


@error_handler
def show_all_command(args):
    if len(contact_book) == 0:  # Якщо словник порожній.
        return colored('Address book is now empty. Please add some users', "red")
    else:
        print(colored(f'There are {len(contact_book)} users in address book', "yellow"))
        return contact_book.get_all_contacts()


def input_checking(func):
    def inner(class_, value):
        if class_ == Country or value in CHANGING_FUNCS:
            address = func(class_, value)
            return address
        print(colored(f'Do you want to include {value}?', "yellow"))
        answer = input('Y/N: ').strip()
        if answer.lower() in user_inputs:
            address = func(class_, value) 
            return address
        return None
    return inner
    # функція(декоратор) запитує в користувача чи хоче він записати інформацію поля класу повідомленням "Do you want to include {value}",
    # де 'value' це країна/місто/вулиця/будинок. Функція повертає екземпляр класу, якщо введене значення користувача
    # пройшло перевірку функцією 'address_input', або повертає 'exit', якщо користувач ввів одну з команд для виходу.
    # Якщо користувач відповів на питання 'Do you want to include {value}?' - ні, то повертає 'None'


@input_checking
def address_input(class_, value):
    while True: 
        try:
            address_value = input(f'Enter a {value}: ').strip()
            if address_value.lower() in exit_inputs:
                return 'exit'
            country = class_(address_value)
            return country
        except:
            print(colored('Wrong format, try again', "red"))
    # поки користувач не введе правильне значення або одну з команд для виходу, функція буде запитувати
    # користувача на введеня даних


def add_address(*args):
    info_text()
    name = Name(input('Enter the name of the contact: ').strip())
    #користувач вводить ім'я контакту 
    rec: Record = contact_book.get(str(name)) 
    #отримуємо інформацію про записаного користувача
    
    if rec: 
    #перевіряємо чи інсує запис з ім'ям, яке ввів користувач, якщо так, то продовжуємо
        city = None 
        street = None 
        house = None 
        # необов'язкові поля

        country = address_input(Country, 'country') #отримуємо значення, яке користувач хоче додати
        if country == 'exit': # перевіряємо чи функція повернула нам команду для закінчення додавання адреси
            return command_canceled() # якщо так, то зупиняємо команду та відповідаємо користувачеві
              
        city = address_input(City, 'city') #               ^
        if city == 'exit': #                               | (інформація зверху)
            rec.add_address(country, None, street, house)# |
            return command_canceled() #                    |
         
        street = address_input(Street, 'street') #         ^
        if street == 'exit': #                             | (інформація зверху)
            rec.add_address(country, city, None, house)#   |
            return command_canceled() #                   |
    
        house = address_input(House, 'house')#             ^
        if house == 'exit': #                              | (інформація зверху)
            rec.add_address(country, city, street, None)#  |
            return command_canceled() #                   |
            
        return rec.add_address(country, city, street, house) # записуємо адрес до інформації про людину
    return colored(f'There is no contact with name: {name}', "red") #повертаємо інформацію, якщо немає запису з ім'ям, яке ввів користувач


@error_handler
def change_country_command(*args):
    info_text()
    name = Name(input('Enter the name of the contact: ').strip())
    rec: Record = contact_book.get(str(name))
    country = address_input(Country, 'Country') #отримуємо значення, яке користувач хоче додати
    if country == 'exit': # перевіряємо чи функція повернула нам команду для закінчення додавання адреси
        return command_canceled()
    return rec.change_country(country)


@error_handler
def change_city_command(*args):
    info_text()
    name = Name(input('Enter the name of the contact: ').strip())
    rec: Record = contact_book.get(str(name))
    city = address_input(City, 'City')
    if city == 'exit':
        return command_canceled()
    return rec.change_city(city)


@error_handler
def change_street_command(*args):
    name = Name(input('Enter the name of the contact: ').strip())
    rec: Record = contact_book.get(str(name))
    street = address_input(Street, 'Street')
    if street == 'exit':
        return command_canceled()
    return rec.change_street(street)


@error_handler
def change_house_command(*args):
    name = Name(input('Enter the name of the contact: ').strip())
    rec: Record = contact_book.get(str(name))
    house = address_input(House, 'House')
    if house == 'exit':
        return command_canceled()
    return rec.change_house(house)


@error_handler
def delete_country_command(*args):
    name = data_input(Name, 'Enter the name of the contact whose country address you want to delete')
    if name == 'exit':
        return command_canceled()
    rec: Record = contact_book.get(str(name))
    return rec.delete_country()


@error_handler
def delete_city_command(*args):
    name = data_input(Name, 'Enter the name of the contact whose city address you want to delete')
    if name == 'exit':
        return command_canceled()
    rec: Record = contact_book.get(str(name))
    return rec.delete_city()


@error_handler
def delete_street_command(*args):
    name = data_input(Name, 'Enter the name of the contact whose street address you want to delete')
    if name == 'exit':
        return command_canceled()
    rec: Record = contact_book.get(str(name))
    return rec.delete_street()


@error_handler
def delete_house_command(*args):
    name = data_input(Name, 'Enter the name of the contact whose house address you want to delete')
    if name == 'exit':
        return command_canceled()
    rec: Record = contact_book.get(str(name))
    return rec.delete_house()

    # Додаю функцію для пошуку збігів у contactbook. Повертає список контактів, у яких присутній збіг.


@error_handler
def search_command(*args):  # Шукає задану послідовність символів у addressbook.
    if len(contact_book) == 0:  # Якщо словник порожній.
        command_text = colored(
        'Address book is now empty. Please add some users./nIt is very difficult to find a black cat in a dark room, especially if it is not there.',
        "yellow"
    ) 
        return command_text
    else:
        match = input(colored('Enter what you want to find. Two characters minimum: ', "yellow"))
        if len(match) < 2:
            return colored('Search is too short. Enter at least 2 symbols.', "red")
        return contact_book.search_match(match)


HANDLERS = {
    add_user_command: ('11', 'add user', 'new user', 'create user', '+'),
    add_phone_command: ('12', 'add phone'),
    add_birthday_command: ('13', 'add birthday', 'birthday'),
    add_email_command: ('14', 'add email', 'email'),
    add_address: ('15','add address', 'new address',),
    # редагування записів (21-28) 
    change_user_command: ('21', 'change user', 'change name'),
    change_phone_command: ('22', 'change phone',),
    change_birthday_command: ('23', 'change birthday',),
    change_email_command: ('24', 'change email',),
    change_country_command: ('25', 'change country'),
    change_city_command: ('26', 'change city', 'change town', 'change village'),
    change_street_command: ('27', 'change street',),
    change_house_command: ('28', 'change house',),
    delete_rec_command: ('31', 'delete user', 'delete contact',),
    delete_phone_command: ('32', 'delete phone', 'remove phone',),
    delete_birthday_command: ('33', 'delete birthday', 'remove birthday'),
    delete_email_command: ('34', 'delete email', 'remove email',),
    delete_country_command: ('35', 'delete country', 'remove country',),
    delete_city_command: ('36', 'delete city', 'remove city', 'delete town', 'remove town', 'delete village', 'remove village'),
    delete_street_command: ('37', 'delete street', 'remove street',),
    delete_house_command: ('38', 'delete house', 'remove house',),
    days_to_birthday: ('41', 'days to birthday', 'days to bd'),
    congrats_list_command: ('42', 'upcoming birthdays', 'closest birthdays'),
    birthdays_next_week: ('43', 'next week birthdays', 'next week'),
    birthdays_current_week: ('44', 'current week birthdays', 'current week'),
    birthdays_next_month: ('45', 'next month birthdays', 'next month'),
    birthdays_current_month: ('46', 'current month birthdays', 'current month'),
    how_long_user_live_command: ('47', 'how long user live'),
    sort_by_name_command: ('51', 'sort by name'),
    sort_by_age_command: ('53', 'sort by age'),
    show_all_command: ('55', 'show all', 'all phones', 'addressbook', 'contactbook', 'ірщц фдд'),
    show_user_command: ('66', 'show user', 'phone', 'number', 'show'),
    search_command: ('77', 'search', 'find', 'match', 'іуфкср', 'аштв', 'ьфеср'),
    exit_command: ('99', 'exit', 'bye', 'end', 'close', 'goodbye', 'учше'),
    helper: ('00', 'help', 'рудз')
}


@error_handler
def unknown_command(*args):
    if len(args) == 3:
        if 'birthday' or 'bd' in args[2]:
            command = f'{args[0]} {args[1]} {args[2]}'
    
    elif len(args) == 2:
        command = f'{args[0]} {args[1]}'

    else:
        command = args[0]

    possibilities = []

    for commands in HANDLERS.values():
        possibilities.extend([i for i in commands])
    
    n = 1
    cutoff = 0.7
    close_matches = difflib.get_close_matches(command, 
                possibilities, n, cutoff)
    
    if len(close_matches) != 0:
        return colored(f'Did you mean {close_matches[0]}?', "yellow")
    return colored('Unknown command. Try again', "red")


def parse_input(user_input, view_format):
    declare_view_format(view_format=view_format)

    for cmd, keywords in HANDLERS.items():
        for kwd in keywords:
            if user_input.lower().startswith(kwd):
                return cmd, user_input
    return unknown_command, user_input.strip().split()
