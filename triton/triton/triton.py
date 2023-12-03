import sys
from pathlib import Path

triton_path = Path(__file__).parent.parent
sys.path.append(str(triton_path))

from contact_book_main import main as main_contactbook
from notes_main import main as main_notebook
from sort_folder import main as main_sorter

invitation_text = '''\nHello! I'm TRITON!!!\nI will help you organise your work!\nLet's start and enjoy!!!'''
main_menu_text = '''\nYou're on Main Menu now.
I have three useful branches that wiil definitely make your life easier:
1. Contact Book
2. Notebook
3. File sorter'''

def check_view_input(args):
    options = [1, 2]
    try:
        res = int(args)
        if not res in options:
            raise ValueError
        return res
    except (TypeError, ValueError) as err:
        print('Wrong input, type only 1 or 2')
        return 'stop'


def main():
    print(invitation_text)
    while True:
        print(main_menu_text)
        view_format = check_view_input(
            input("\nEnter number (1: to show results in str format or 2: to show result in rich table format): ").strip()
        )
        if view_format == 'stop':
            continue
        user_input = input("\nEnter number from 1, 2 or 3 to start work with branch(press 0 to exit): ")
        if user_input == '1':
            print()
            main_contactbook(view_format)
        elif user_input == '2':
            main_notebook()
        elif user_input == '3':
            print(main_sorter())

        elif user_input == '0':
            confirm = input('\nAre you sure you want to finish work with Personal Assistant? Type (Y/N): ')
            if confirm.lower() != 'y':
                print()
                continue  
            else: 
                break
        
        else:
            print('\nUnknown command. Type command from the list.\n')
            
        
if __name__ == "__main__":
    main()