import json


with open('all_keywords.json', 'r', encoding='utf-8') as file:
    data = json.load(file)


for item in data:
    keyword = item.get("Ключевое слово")
    print(f'{keyword}')