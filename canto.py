import os
import requests
import re
from datetime import datetime, timedelta
import locale
import subprocess


# Function definitions

def get_response_from_api(date):
    formatted_date = date.strftime("%d-%m-%Y")
    request_url = f"http://www.canto.ru/calendar/js/unicode.php?date={formatted_date}"
    response = requests.get(request_url)
    return response.text

def parse_response(response):
    # Ищем содержимое функции print_day
    if match := re.search(r'function\s+print_day\s*\(\s*\)\s*{([^}]*)}', response):
        saints = match.group(1).strip()
    else:
        return "Unknown"
    
    # Удаляем HTML-теги и разделяем по точкам с запятой
    saints = re.sub(r'<[^>]+>', '', saints)  # Убираем HTML-теги
    saints = ' '.join(part.strip() for part in saints.split(';') if part.strip())
    
    # Извлекаем текст внутри кавычек и возвращаем результат
    matches = re.findall(r'"(.*?)"', saints)
    return ' '.join(match.strip() for match in matches if match.strip())


def get_saints(date):
    response = get_response_from_api(date)
    saints = parse_response(response)
    return saints

def out_table_header(out_file):
    with open(out_file, "a", encoding="utf-8") as file:  
        file.write(f"""
<table class="alignleft schedule">
<tbody>
""")

def out_table_footer(out_file):
    with open(out_file, "a", encoding="utf-8") as file:
        file.write(f"""
</tbody>
</table>
""")

def out_table_row(date, saints, worships, out_file):
    day_of_week_rus = date.strftime('%A').capitalize()
    day_month_name = date.strftime('%d %B')
    date_for_table = f"{day_of_week_rus}\n{day_month_name}"
    
    row_class = 'red' if date.weekday() == 6 else ''
    
    with open(out_file, "a", encoding="utf-8") as file:
        file.write(f"""
<!-- *********** {day_of_week_rus} ************************************************************ -->
<tr class="{row_class}">
<td>{date_for_table}</td>
<td>{saints}</td>
<td>{worships}</td>
</tr>
 """)

# Main code

# Устанавливаем русскую локаль
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

current_directory = './'  # Adjust according to your environment
out_file = current_directory + 'table.html'

if __name__ == "__main__":
    if os.path.exists(out_file):
        os.remove(out_file)
    
    # Инициализируем переменную для хранения результата проверки
    monday = None

    # Цикл while для повторного запроса даты при некорректном вводе
    while monday is None:
        # Запрашиваем у пользователя ввод даты
        date_input = input("Start date (dd.mm.yyyy): ")

        try:
            # Пытаемся преобразовать строку в объект datetime с указанным форматом
            monday = datetime.strptime(date_input, "%d.%m.%Y")
        except ValueError:
            # Если возникла ошибка, выводим сообщение о некорректной дате
            print("\033[91mWrong date format!\033[0m")  # Вывод красного сообщения об ошибке


    out_table_header(out_file)
    
    for i in range(1, 8):
        date = monday + timedelta(days=i-1)
        print(f"Request {date.strftime('%d-%m-%Y')} ...")
        
        saints = get_saints(date)
        
        if i < 6:
            worships = "07:30 Часы. Божественная литургия\n16:30 Вечернее богослужение"
        elif i < 7:
            worships = "08:00 Часы. Божественная литургия\n16:30 Всенощное бдение"
        else:
            worships = "08:00 Часы. Божественная литургия\n16:30 Вечернее богослужение"
        
        out_table_row(date, saints, worships, out_file)
    
    out_table_footer(out_file)

    subprocess.run(['vim', 'table.html'])

