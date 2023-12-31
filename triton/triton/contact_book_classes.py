import sys
from pathlib import Path

from abc import ABC, abstractmethod
from collections import UserDict, defaultdict
from datetime import datetime
import pickle  # модуль для зберігання та читання інформації.
import re

from rich.table import Table
from termcolor import colored

triton_path = Path(__file__).parent.parent
countries_txt = triton_path / 'countries.txt'

class ConsoleView(ABC):

    table_columns = ['Name', 'Phones', 'Birthday', 'Email', 'Address']

    @abstractmethod
    def view_users_info(self):
        pass

    @abstractmethod
    def view_user_info(self):
        pass

    @abstractmethod
    def view_messages(self):
        pass

    @abstractmethod
    def view_some_info(self):
        pass


class RecordStrView(ConsoleView):

    def view_users_info(self, data):
        result = ''
        for contact in data:
            info = colored(f"User: {contact[0]} \
| phones: {contact[1]} \
| birthday: {contact[2] if contact[2] != None else ''} \
| email: {contact[3] if contact[3] != None else ''} \
| address: {contact[4] if contact[4] != None else ''}\
/{contact[5] if contact[5] != None else ''}\
/{contact[6] if contact[6] != None else ''}\
/{contact[7] if contact[7] != None else ''}\n", "cyan")
            result += info
        return result
    
    def view_user_info(self, data):
        return colored(f"User: {data[0]} \
| phones: {data[1]} \
| birthday: {data[2] if data[2] != None else ''} \
| email: {data[3] if data[3] != None else ''} \
| address: {data[4] if data[4] != None else ''}\
/{data[5] if data[5] != None else ''}\
/{data[6] if data[6] != None else ''}\
/{data[7] if data[7] != None else ''}", "cyan")

    def view_messages(self, message: str):
        return colored(message, "green")
    
    def view_some_info(self, info: str):
        return colored(info, "light_yellow")


class RecordRichView(ConsoleView):

    def view_users_info(self, data):
        users_table = Table(title="Contacts' info")
        columns_name = self.table_columns
        for col in columns_name:
            users_table.add_column(col, justify='left', style='magenta')
        for contact in data:
            main_info = contact[:4]
            address_info = ' / '.join(contact[4::])
            users_table.add_row(*main_info, address_info)
        return users_table
    
    def view_user_info(self, data):
        user_table = Table(title="Contact's info")
        columns_name = self.table_columns
        for col in columns_name:
            user_table.add_column(col, justify='left', style='magenta')
        main_info = data[:4]
        address_info = ' / '.join(data[4::])
        user_table.add_row(*main_info, address_info)
        return user_table
        

    def view_messages(self, data: str):
        messages_table = Table(title='Result Messages')
        messages_table.add_column("Message", justify="left", style="magenta")
        messages_table.add_column("Time", justify="left", style="cyan")
        messages_table.add_row(data, datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
        return messages_table
    
    def view_some_info(self, data: str):
        return colored(data, "light_yellow")
    

class UserView:
    """Classic users_view"""

    # __instance = None
    __view_formats = {1: RecordStrView(), 2: RecordRichView()}
    view_choice = 1
    view_format: RecordStrView | RecordRichView = None
    
    def get_view_format(self):
        self.view_format = self.__view_formats.get(self.view_choice)
        return self.view_format

def declare_view_format(view_format):
    global users_view
    users_view = UserView()
    users_view.view_choice = view_format
    users_view.get_view_format()
    return users_view
    

class Field:
    def __init__(self, value) -> None:
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value
       
    @value.setter
    def value(self, value):
        self.__value = value

    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return str(self)


class Name(Field):

    @Field.value.setter
    def value(self, value):
        if not re.match(r'[A-z\d _\.\(\)\/\\\,]{1,20}', value):
            print(colored('Wrong format.', "red"))
            raise ValueError
        self._Field__value = value


# Для перевірки на правильність введення номеру телефону, використовуємо регулярний вираз, що українські номери 
# обов'язково мають починатися з '+380' і ще 9 цифр. 
class Phone(Field):

    @Field.value.setter
    def value(self, value):
        if not re.match(r'^\+380\d{9}$', value):
            print(colored('Wrong format. Phone number should be in the format +380XXXXXXXXX.', "red"))
            raise ValueError
        self._Field__value = value


# Для перевірки на правильність введення дати народження, необхідно щоб ми записували ці об'єкти як об'єкти
# типу datetime у форматі '%d.%m.%Y'. Це необхідно щоб одразу запобігти введенню 'дивних' даних на кшталт
# "2/2/42", '50.20.2000' чи навіть '29.02.2001'.
# Також варто уникати дат народження, які є у майбутньому. Це враховано у методі add_birthday класу Record.
class Birthday(Field):

    @Field.value.setter
    def value(self, value):
        try:
            self._Field__value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            print(colored('Wrong format. Enter birthday in format dd.mm.YYYY. Days in range(31), month in range(12)', "red"))
            raise ValueError
        if self.value >= datetime.now().date():
            print(colored('The user has not been born yet.', "red"))
            raise ValueError
        
    def __str__(self):
        return self.value.strftime('%d.%m.%Y')


# Для перевірки на правильність введення email пропоную використати регулярний вираз, який був у нас у автоперевірці.
class Email(Field):

    @Field.value.setter
    def value(self, value):
        if not re.match(r'[A-Za-z]{1}[\w.]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}\b', value):
            print(colored('Wrong format. Email should be in the format xxxxxx@xxx.xx', "red"))
            raise ValueError
        self._Field__value = value


class Country(Field):

    @Field.value.setter
    def value(self, value):
        with open(countries_txt, 'r') as fh:
            readlines = fh.readlines()
            for line in readlines:
                if value.lower() == 'russia':
                    self._Field__value = 'a terrorist country'
                    return ''
                elif value.lower() == line.lower().strip():
                    lst_value = value.lower().strip().split(' ')
                    capitalize_value = [i.capitalize() for i in lst_value]
                    self._Field__value = ' '.join(capitalize_value)
                    return ''
            raise ValueError
        
    # Магічний метод 'setter', який перевіряє на правильність введеного користувачем значення і записує у поле 'self.__value' значення, якщо
    # введена країна існує.


class City(Field):

    @Field.value.setter
    def value(self, value):
        if not re.match(r'^[A-z]{2,25}$', value):
            raise ValueError
        self._Field__value = value
    # Магічний метод 'setter', який перевіряє на правильність введеного користувачем значення і записує у поле 'self.__value' значення, якщо
    # введений населений пункт складається тільки з літер та має довжину не менше 2-ох літер.


class Street(Field):

    @Field.value.setter
    def value(self, value):
        if not re.match(r'^[A-z\d\.\-\(\)\:\_\,\/ ]{2,25}$', value):
            raise ValueError
        self._Field__value = value
    # Магічний метод 'setter', який перевіряє на правильність введеного користувачем значення і записує у поле 'self.__value' значення, якщо
    # назва введеної вулиці починається з літери та може містити тільки цифри та букви.


class House(Field):

    @Field.value.setter
    def value(self, value):
        if not re.match(r'[ A-z\d\-\\\/\.]{1,15}', value):
            raise ValueError
        self._Field__value = value
    # Магічний метод 'setter', який перевіряє на правильність введеного користувачем значення і записує у поле 'self.__value' значення, якщо
    # введені назва/номер будинку складається з літер або цифр.


class Record:
    def __init__(self, name: Name, phone: Phone = None, birthday: Birthday = None, email: Email = None, 
                 country: Country = None, city: City = None, street: Street = None, house: House = None) -> None:
        self.name = name
        self.phones = []
        if phone:
            self.phones.append(phone)
        self.birthday = birthday
        self.email = email
        self.country = country
        self.city = city
        self.street = street
        self.house = house

    def add_user(self, name: Name):
        # view: RecordRichView | RecordStrView = self.view_formats.get(view_format)
        if not name.value:
            self.name = name
            return users_view.view_format.view_messages(f"Record for user {name} was created")
        return users_view.view_format.view_messages(f"Record for user {name} already exist in this address book")
    
    # Функція додає телефон до списку телефонів користувача. Перевіряє чи вже введено такий телефон раніше.
    def add_phone(self, phone: Phone):
        if phone.value not in [phone_.value for phone_ in self.phones] and len(self.phones) <= 3:
            self.phones.append(phone)
            return users_view.view_format.view_messages(f"phone {phone} was added to contact {self.name}")
        
        return users_view.view_format.view_messages(
            f"phone: {phone} is already registered for user {self.name} and you can add only 5 phone numbers"
        )

    def change_phone(self, old_phone: Phone, new_phone: Phone):        
        for idx, p in enumerate(self.phones):
            if old_phone.value == p.value:
                self.phones[idx] = new_phone
                return users_view.view_format.view_messages(f'Old phone: {old_phone} was changed to new: {new_phone}')
        
        return users_view.view_format.view_messages(f"Phone: {old_phone} is not present in {self.name}'s phones")
    
    def delete_phone(self, phone):
        for p in self.phones:
            if phone.value == p.value:
                self.phones.remove(p)
                return users_view.view_format.view_messages(f'Phone: {phone} in contact {self.name} was deleted successfully')
        
        return users_view.view_format.view_messages(f"Phone: {phone} is not present in {self.name}'s list of phones")

    # Функція додає дату народження користувача. Враховано, що дата народження не може бути у майбутньому.
    def add_birthday(self, birthday: Birthday):
        if self.birthday:
            return users_view.view_format.view_messages(
                f'Birthday for user {self.name} already exists. Use command "change birthday".'
            )
        self.birthday = birthday
        return users_view.view_format.view_messages(f'Birthday for user {self.name} was added successfully.')
        
    def change_birthday(self, birthday: Birthday):
        self.birthday = birthday
        return users_view.view_format.view_messages(f'Birthday for contact {self.name} was changed successfully')
    
    def delete_birthday(self):
        if not self.birthday:
            return users_view.view_format.view_messages(f"You haven't included birthday for contact {self.name} yet")
        
        self.birthday = None
        return users_view.view_format.view_messages(f'Birthday for contact {self.name} was successfully deleted')

    # Функція додає email користувача. Перевірка на правильність прописана у класі Email.
    def add_email(self, email: Email):
        if not self.email:
            self.email = email
            return users_view.view_format.view_messages(f'E-mail for user {self.name} was added successfully')
        
        return users_view.view_format.view_messages('Email for contact {self.name} already exists. Use command "change email"')
    
    def change_email(self, email: Email):
        self.email = email
        return users_view.view_format.view_messages(f'Email for contact {self.name} was changed successfully')
    
    def delete_email(self):
        if not self.email:
            return users_view.view_format.view_messages(f"You haven't included birthday for contact {self.name} yet")
        
        self.email = None
        return users_view.view_format.view_messages(f'Email for contact {self.name} was deleted successfully')
    
    def days_to_birthday(self):  # Функція повертає кількість днів до дня народження користувача.
        if not self.birthday:
            return users_view.view_format.view_messages(f'No data for birthday of user {self.name}')
        
        today = datetime.now().date()
        try:
            bd_current_year = self.birthday.value.replace(year=today.year)
            bd_next_year = self.birthday.value.replace(year=today.year + 1)
        except ValueError:
            bd_current_year = self.birthday.value.replace(today.year, 2, 28)
            bd_next_year = self.birthday.value.replace(today.year + 1, 2, 28)
        diff_years = today.year - self.birthday.value.year
        if (bd_current_year - today).days == 0:
            return users_view.view_format.view_messages(f"Today {self.name} celebrate {diff_years} birthday. Don't forget to buy a gift.")
        elif (bd_current_year - today).days > 0:
            diff_days = (bd_current_year - today).days
            return users_view.view_format.view_messages(f"There are {diff_days} days left until the {self.name}'s {diff_years} birthday")
        diff_days = (bd_next_year - today).days
        return users_view.view_format.view_messages(f"There are {diff_days} days left until the {self.name}'s {diff_years + 1} birthday")
    
    def days_to_birthday_int_numbers(self) -> int:  # Функція повертає кількість днів до дня народження користувача.
        if not self.birthday:
             return -1 # якщо дати народження нема, то повертає -1
        
        today = datetime.now().date()
        try:
            bd_current_year = self.birthday.value.replace(year=today.year)
            bd_next_year = self.birthday.value.replace(year=today.year + 1)
        except ValueError:
            bd_current_year = self.birthday.value.replace(today.year, 2, 28)
            bd_next_year = self.birthday.value.replace(today.year + 1, 2, 28)
        if (bd_current_year - today).days == 0:
            return 0
        elif (bd_current_year - today).days > 0:
            diff_days = (bd_current_year - today).days
            return diff_days
        diff_days = (bd_next_year - today).days
        return diff_days
    
    def add_address(self, country: Country, city: City = None, street: Street = None, house: House = None):
        self.country = country
        self.city = city
        self.street = street
        self.house = house
        return users_view.view_format.view_messages(f'Address for user {self.name} was added successfully')
    # метод добавляє адресу проживання у поле self.address
        
    def how_much_user_live(self):
        if not self.birthday:
            return users_view.view_format.view_messages(str(-1))
        else:
            today = datetime.now().date()
            res = (today - self.birthday.value).days
            if res == -1:
                return users_view.view_format.view_messages(f'No data for birthday of user {self.name}')
            elif res <= -2:
                return users_view.view_format.view_messages(f"Wrong data about user {self.name} birthday. The user has not been born yet.")
            elif res >= 35000:
                return users_view.view_format.view_messages(f"User {self.name} has already lived {res} days. Or maybe he's already dead?")
            else:
                return users_view.view_format.view_messages(f"User {self.name} has already lived {res} days")
            
    def how_much_user_live_int(self):
        today = datetime.now().date()
        res = (today - self.birthday.value).days
        return res
        
    def change_country(self, country: Country):
        self.country = country
        return users_view.view_format.view_messages(f'Country address for user {self.name} was changed successfully')
    
    def delete_country(self):
        if not self.country:
            return users_view.view_format.view_messages('You have not included country address yet')
        self.country = None
        return users_view.view_format.view_messages(f'Country address for contact {self.name} was deleted successfully')
    
    def change_city(self, city: City):
        self.city = city
        return users_view.view_format.view_messages(f'City address for user {self.name} was changed successfully')
    
    def delete_city(self):
        if not self.city:
            return users_view.view_format.view_messages('You have not included city address yet')
        self.city = None
        return users_view.view_format.view_messages(f'City address for contact {self.name} was deleted successfully')
    
    def change_street(self, street: Street):
        self.street = street
        return users_view.view_format.view_messages(f'Street address for user {self.name} was changed successfully')
    
    def delete_street(self):
        if not self.street:
            return users_view.view_format.view_messages('You have not included street address yet')
        
        self.street = None
        return users_view.view_format.view_messages(f'Street address for contact {self.name} was deleted successfully')

    def change_house(self, house: House):

        self.house = house
        return users_view.view_format.view_messages((f'House address for user {self.name} was changed successfully'))
    
    def delete_house(self):
        if not self.house:
            return users_view.view_format.view_messages('You have not included house address yet')
        
        self.house = None
        return users_view.view_format.view_messages(f'House address for contact {self.name} was deleted successfully')
      
    # Рядкове представлення для одного запису у contact_book
    def info_list_format(self) -> list:
        phones = ', '.join(str(phone) for phone in self.phones) if self.phones != [] else 'empty'
        return [
            str(self.name), 
            phones, 
            str(self.birthday) if self.birthday != None else 'empy', 
            str(self.email) if self.email != None else 'empty', 
            str(self.country) if self.country != None else 'empty', 
            str(self.city) if self.city != None else 'empty', 
            str(self.street) if self.street != None else 'empty', 
            str(self.house) if self.house != None else 'empty'
        ]

    def user_info(self):
        return users_view.view_format.view_user_info(self.info_list_format())

    def __str__(self) -> str:
        return f"User: {self.name} \
| phones: {', '.join(str(p) for p in self.phones)} \
| birthday: {self.birthday if self.birthday != None else ''} \
| email: {self.email if self.email != None else ''} \
| address: {self.country if self.country != None else ''}\
/{self.city if self.city != None else ''}\
/{self.street if self.street != None else ''}\
/{self.house if self.house != None else ''} "


class AddressBook(UserDict):

    # str_view_format = RecordStrView()
    # rich_view_format = RecordRichView()
    # view_formats = {1: str_view_format, 2: rich_view_format}
    # format_view: RecordStrView | RecordRichView = None

    def add_record(self, record: Record):
        self.data[str(record.name)] = record
        return users_view.view_format.view_messages(f"Contact {record.name} was added successfully")
    
    def change_rec_name(self, old_name: Name, new_name: Name):
        for key in self.data.keys():
            if key == old_name.value:
                old_rec = self.data.pop(key)
                old_rec.name = new_name
                self.data.update({str(new_name): old_rec})
                return users_view.view_format.view_messages(f'Contact with name {old_name} was changed to name {new_name}')
        return users_view.view_format.view_messages((f'There is not contact with name: {old_name}'))
    
    def delete_rec(self, name: Name):
        for key in self.data.keys():
            if str(key) == name.value:
                self.data.pop(key)
                return users_view.view_format.view_messages(f'Contact with name: {name} was deleted successfully')
        return users_view.view_format.view_messages(f'There is not contact with name: {name}')
    
    def save_to_file(self, filename):
        with open(filename, mode="wb") as file:
            pickle.dump(self.data, file)
            print(colored("\nContack book has saved.", "green"))

    def load_from_file(self, filename):
        try:
            with open(filename, 'rb') as f:
                self.data = pickle.load(f)
                print(colored("\nContact book has loaded.", "green"))
        except (FileNotFoundError, pickle.UnpicklingError):
            with open(filename, 'wb') as f:
                self.data = {}
                pickle.dump(self.data, f)

    def search_match(self, match):
        found_match = []
        for item in self.data.values():
            if match in str(item):
                found_match.append(item.info_list_format())
        if len(found_match) == 0:  # Якщо не знайшло збігів
            return users_view.view_format.view_messages(f"\nNo matches found for '{match}' in whole addressbook")
        else:
            print(users_view.view_format.view_some_info(f"\nWe found matches for '{match}' in {len(found_match)} contacts in whole contactbook: "))
            return users_view.view_format.view_users_info(found_match) # '\n'.join(el for el in found_match)

    def congrats_list(self, shift_days, record: Record = None):
        congrats_dict = {}
        for record in self.data.values():
            res = record.days_to_birthday_int_numbers()
            if 0 <= res <= shift_days:
                congrats_dict[str(record.name)] = res
        new_dict = defaultdict(list)
        for rec, res in congrats_dict.items():
            rec: Record = self.data.get(rec)
            new_dict[res].append(rec.info_list_format())
        sorted_list = sorted(new_dict.items())
        if len(congrats_dict) == 0:
            return users_view.view_format.view_messages(f'No users are celebrating birthday in the next {shift_days} days')
        else:
            almost_list = []
            for el in sorted_list:
                almost_list.append(el[1])
            congrats_list = []
            for lst in almost_list:
                for el in lst:
                    congrats_list.append(el)
            print(users_view.view_format.view_some_info(
                f'\n{len(congrats_dict)} users are celebrating their birthday in the next {shift_days} days: '
                )
            )
            return users_view.view_format.view_users_info(congrats_list) # '\n'.join(el for el in congrats_list)
        
    def next_week_birthdays(self):
        next_week_dict = {}
        today = datetime.now().date().weekday()
        for record in self.data.values():
            res = record.days_to_birthday_int_numbers()
            if (7 - today) <= res < (14 - today):
                next_week_dict[str(record.name)] = res
        new_dict = defaultdict(list)
        for rec, res in next_week_dict.items():
            rec: Record = self.data.get(rec)
            new_dict[res].append(rec.info_list_format())
        sorted_list = sorted(new_dict.items())
        if len(next_week_dict) == 0:
            return users_view.view_format.view_messages(f'No users are celebrating birthday in the next week')
        else:
            almost_list = []
            for el in sorted_list:
                almost_list.append(el[1])
            congrats_list = []
            for lst in almost_list:
                for el in lst:
                    congrats_list.append(el)
            print(users_view.view_format.view_some_info(f'\n{len(congrats_list)} users are celebrating their birthday in the next week: '))
            return users_view.view_format.view_users_info(congrats_list) #'\n'.join(el for el in congrats_list)
    
    def current_week_birthdays(self):
        current_week_dict = {}
        today = datetime.now().date().weekday()
        for record in self.data.values():
            res = record.days_to_birthday_int_numbers()
            if 0 <= res < 7 - today:
                current_week_dict[str(record.name)] = res
        new_dict = defaultdict(list)
        for rec, res in current_week_dict.items():
            rec: Record = self.data.get(rec)
            new_dict[res].append(rec.info_list_format())
        sorted_list = sorted(new_dict.items())
        if len(current_week_dict) == 0:
            return users_view.view_format.view_messages(f'No users are celebrating birthday in the current week')
        else:
            almost_list = []
            for el in sorted_list:
                almost_list.append(el[1])
            congrats_list = []
            for lst in almost_list:
                for el in lst:
                    congrats_list.append(el)
            print(users_view.view_format.view_some_info(
                f'\n{len(congrats_list)} users are celebrating their birthday in the current week: '
                )
            )
            return users_view.view_format.view_users_info(congrats_list) #'\n'.join(el for el in congrats_list)

    def next_month_birthdays(self, record: Record = None):
        next_month_dict = {}
        current_month = datetime.now().date().month
        for record in self.data.values():
            if not record.birthday:
                continue
            else:
                if current_month == 12:
                    if record.birthday.value.month == current_month - 11:
                        next_month_dict[str(record.name)] = record.birthday.value.day
                    new_dict = defaultdict(list)
                    for rec, res in next_month_dict.items():
                        rec: Record = self.data.get(rec)
                        new_dict[res].append(rec.info_list_format())
                    sorted_list = sorted(new_dict.items())
                else:    
                    if record.birthday.value.month == current_month + 1:
                        next_month_dict[str(record.name)] = record.birthday.value.day
                    new_dict = defaultdict(list)
                    for rec, res in next_month_dict.items():
                        rec: Record = self.data.get(rec)
                        new_dict[res].append(rec.info_list_format())
                    sorted_list = sorted(new_dict.items())
        if len(next_month_dict) == 0:
            return users_view.view_format.view_messages(f'No users are celebrating birthday in the next month')
        else:
            almost_list = []
            for el in sorted_list:
                almost_list.append(el[1])
            congrats_list = []
            for lst in almost_list:
                for el in lst:
                    congrats_list.append(el)
            print(users_view.view_format.view_some_info(
                f'\n{len(congrats_list)} users are celebrating their birthday in the next month: '
                )
            )
            return users_view.view_format.view_users_info(congrats_list) #'\n'.join(el for el in congrats_list)
        
    def current_month_birthdays(self, record: Record = None):
        current_month_dict = {}
        current_month = datetime.now().date().month
        for record in self.data.values():
            if not record.birthday:
                continue
            else:
                if record.birthday.value.month == current_month:
                    current_month_dict[str(record.name)] = record.birthday.value.day
        new_dict = defaultdict(list)
        for rec, res in current_month_dict.items():
            rec: Record = self.data.get(rec)
            new_dict[res].append(rec.info_list_format())
        sorted_list = sorted(new_dict.items())
        if len(current_month_dict) == 0:
            return users_view.view_format.view_messages(f'No users are celebrating birthday in the current month')
        else:
            almost_list = []
            for el in sorted_list:
                almost_list.append(el[1])
            congrats_list = []
            for lst in almost_list:
                for el in lst:
                    congrats_list.append(el)
            print(users_view.view_format.view_some_info(
                f'\n{len(congrats_list)} users are celebrating their birthday in the current month: '
                )
            )
            return users_view.view_format.view_users_info(congrats_list) #'\n'.join(el for el in congrats_list)

    def sort_by_name(self, record: Record=None):  # Функція сортує по імені всю книгу контактів.
        contactbook_dict = {}
        for record in self.data.values():
            contactbook_dict[record.name.value] = record.info_list_format()
        print(users_view.view_format.view_some_info('\nYour contactbook is sorted due to the name of users: \n'))
        sorted_contcact_book = sorted(contactbook_dict.values())
        return users_view.view_format.view_users_info(sorted_contcact_book) #'\n'.join(el for el in sorted(contactbook_dict.values()))

    def sort_by_age(self, record: Record=None):  # Функція сортує contactbook по віку користувача.
        contactbook_dict = {}
        for record in self.data.values():
            if record.birthday:
                res = record.how_much_user_live_int()
                contactbook_dict[str(record.name)] = res
        new_dict = defaultdict(list)
        for rec, res in contactbook_dict.items():
            rec: Record = self.data.get(rec)
            new_dict[res].append(rec.info_list_format())
        sorted_list = sorted(new_dict.items(), reverse=True)
        if len(contactbook_dict) == 0:
            return users_view.view_format.view_messages(f'No data for birthday in all records.')
        else:
            almost_list = []
            for el in sorted_list:
                almost_list.append(el[1])
            contactbook_list = []
            for lst in almost_list:
                for el in lst:
                    contactbook_list.append(el)
        print(users_view.view_format.view_some_info('\nYour contactbook is sorted due to the age of users: \n'))
        return users_view.view_format.view_users_info(contactbook_list) #'\n'.join(el for el in contactbook_list)

    def __repr__(self):
        return str(self)

    def user_info_list(self) -> list:  # Рядкове представлення для усіх записів у contact_book
        return [r.info_list_format() for r in self.data.values()]

    def get_user(self, name: str):
        rec = self.data.get(str(name))
        return users_view.view_format.view_user_info((rec.info_list_format()))

    def get_all_contacts(self):
        return users_view.view_format.view_users_info(self.user_info_list())
