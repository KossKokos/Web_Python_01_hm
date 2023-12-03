import sys
from pathlib import Path

triton_path = Path(__file__).parent.parent
sys.path.append(str(triton_path))

from contact_book_functions import parse_input, exit_command, start

from rich.table import Table
from rich.console import Console
# Внаслідок перейменування пакетів оновлено імпорт пакетів



def main(view_format):
    start()
    while True:
        example_table = Table()
        console = Console()
        
        user_input = input("\nTo see the list of available commands, type 'help' or '00'\nEnter your command and args (separated by 'space bar'): ")
        
        cmd, data = parse_input(user_input, view_format)
        
        result = cmd(data)
        if view_format == 1:
            print(result)
        else:
            if type(result) == type(example_table):
                console.print(result)
            else:
                print(result)
        # Вихід з бота пропоную роботи не через Enter, бо це може бути випадково зроблене. А лише якщо користувач введе команду на вихід
        if cmd == exit_command:  
            break

if __name__ == "__main__":
    main()