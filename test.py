import re
import json

data = open("all.txt", "r", encoding='utf8')

equipment_list = []

for line in data:
    equipment = re.match("^.*\"equipment\":\"(.*?)\".*$", line)
    value = equipment.group(1)
    equipment_list.append(value)

equipment_list = set(equipment_list)

for eq in equipment_list:
    print(eq)
