import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from datetime import datetime
pd.set_option('display.max_rows', None)

URL = "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
results = soup.find(id="post-body-8087922975012177708")

all_h3 = soup.find_all('h3')

equipment_types_auto_tmp = []
equipment_types_auto = []

for h3 in all_h3:
    if not 'Ukraine' in h3.get_text() and not 'Russia' in h3.get_text():
        equipment_type = h3.get_text().partition("(")[0]
        equipment_type = re.sub(r"\s$", "", equipment_type)
        equipment_types_auto_tmp.append([equipment_type])
        
for i in equipment_types_auto_tmp:
    if i not in equipment_types_auto:
        equipment_types_auto.append(i)
        
equipment_types_auto = [val for sublist in equipment_types_auto for val in sublist]
equipment_types_auto.remove('')

equipment_types_auto

equipment_subtypes_auto_tmp = []
equipment_subtypes_auto = []

all_li = soup.find_all('li', attrs={'class': None})

for li in all_li:
    equipment_subtype = re.search(r'(.*):', li.get_text())
    if equipment_subtype is not None:
        equipment_subtype = equipment_subtype.group(0)
        equipment_subtype = re.sub("^ \d+", "", equipment_subtype)
        equipment_subtype = re.sub(":", "", equipment_subtype)
        equipment_subtype = re.sub(r"^\s", "", equipment_subtype)
        equipment_subtypes_auto_tmp.append([equipment_subtype])

for i in equipment_subtypes_auto_tmp:
    if i[0] not in equipment_subtypes_auto:
        equipment_subtypes_auto.append(i[0])

equipment_subtypes_auto

status_types_auto_tmp = []
status_types_auto = []

all_a = soup.find_all('a')

for a in all_a:
    status = re.search(r"\((.*)\)", a.get_text())
    if status is not None: 
        status = status.group(0)
        status = re.sub("\(", "", status)
        status = re.sub("\)", "", status)
        status = re.search(r"([^\,]+$)", status)
        status = status.group(0)        
        status = re.sub(r"^\s", "", status)
        status_types_auto_tmp.append([status])

for i in status_types_auto_tmp:
    if i[0] not in status_types_auto:
        status_types_auto.append(i[0])

status_types_auto

for h3 in all_h3:
    if h3.get_text().count('Ukraine') == 1:
        all_russian = h3.find_all_previous()
        all_ukraine = h3.find_all_next()

all_russian_all_ukraine = [all_russian, all_ukraine]

list_tmp = []

country = 'RUS'

for section in all_russian_all_ukraine:
        
    if all_russian_all_ukraine.index(section) == 1:
        country = 'UKR'
    
    for element in section:

        if element.name == 'h3':
            
            for equipment_type_i in equipment_types_auto:
                
                equipment_type = element.get_text().partition("(")[0]
                equipment_type = re.sub(r"\s$", "", equipment_type)
                
                if equipment_type_i == equipment_type:
                    current_type = equipment_type_i
                
            ul = element.nextSibling.nextSibling
            
            try:
              li_list = ul.find_all('li')
            except:
                pass
            
            for li in li_list:
                li_a_list = li.find_all('a')
                
                for equipment_subtype_i in equipment_subtypes_auto:
                    
                    equipment_subtype = re.search(r'(.*):', li.get_text())
                    if equipment_subtype is not None:
                        
                        equipment_subtype = equipment_subtype.group(0)
                        equipment_subtype = re.sub("^ \d+", "", equipment_subtype)
                        equipment_subtype = re.sub(":", "", equipment_subtype)
                        equipment_subtype = re.sub(r"^\s", "", equipment_subtype)
                        
                        if equipment_subtype_i == equipment_subtype:
                            current_subtype = equipment_subtype_i
                
                for status_i in status_types_auto:
                
                    for single_report in li_a_list:
                        current_a_text = single_report.get_text()
                        current_a_text = re.sub("\(", "", current_a_text)
                        current_a_text = re.sub("\)", "", current_a_text)  
                        current_a_text = re.search(r"([^\,]+$)", current_a_text)
                        current_a_text = current_a_text.group(0)
                        current_a_text = re.sub(r"^\s", "", current_a_text)
                        if status_i == current_a_text:
                            list_tmp.append([country, current_type, current_subtype, current_a_text, single_report['href']])

df = pd.DataFrame(list_tmp, columns=['country', 'equipment_type', 'equipment_subtype', 'satus', 'source'])

cwd = os.getcwd()
now = datetime.now()
dt_string = now.strftime("%Y%m%d%H%M")
path = cwd + '/export_' + dt_string + '.csv'
df.to_csv(path)