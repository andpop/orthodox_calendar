import os
import requests
import re
from datetime import datetime, timedelta
import locale

# Function definitions

def get_response_from_api(date):
    formatted_date = date.strftime("%d-%m-%Y")
    request_url = f"http://www.canto.ru/calendar/js/unicode.php?date={formatted_date}"
    response = requests.get(request_url)
    return response.text

def parse_response(response):
    regex = r'function\s+print_day\s*\(\s*\)\s*{([^}]*)}'
    match = re.search(regex, response)
    if match:
        saints = match.group(1).strip()
    else:
        saints = 'Unknown'
    
    saints = ' '.join([part.strip() for part in saints.split(';') if part.strip()])
    saints = re.sub(r'<[^>]+>', '', saints)
    
    matches = re.findall(r'"(.*?)"', saints)
    result_fragments = [match.strip() for match in matches if match.strip()]
    
    return ' '.join(result_fragments)

def get_saints(date):
    response = get_response_from_api(date)
    saints = parse_response(response)
    return saints

def out_table_header(out_file):
    with open(out_file, "a", encoding="utf-8") as file:  
        file.write('<table class="alignleft schedule">\n')
        file.write('<tbody>\n')

def out_table_footer(out_file):
    with open(out_file, "a", encoding="utf-8") as file:
        file.write('</tbody>\n')
        file.write('</table>\n')

def out_table_row(date, saints, worships, out_file):
    day_of_week_rus = date.strftime('%A').capitalize()
    day_month_name = date.strftime('%d %B')
    date_for_table = f"{day_of_week_rus}\n{day_month_name}"
    
    row_class = 'red' if date.weekday() == 6 else ''
    
    with open(out_file, "a", encoding="utf-8") as file:
        file.write(f'<!-- *********** {day_of_week_rus} ************************************************************ -->\n')
        file.write(f'<tr class="{row_class}">\n')
        file.write(f'<td>{date_for_table}</td>\n')
        file.write(f'<td>{saints}</td>\n')
        file.write(f'<td>{worships}</td>\n')
        file.write('</tr>\n')

# Main code

# Устанавливаем русскую локаль
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

current_directory = './'  # Adjust according to your environment
out_file = current_directory + 'table.html'

if __name__ == "__main__":
    if os.path.exists(out_file):
        os.remove(out_file)
    
    monday = datetime(2026, 2, 24)
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
