import tkinter as tk
from tkinter import simpledialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib.parse
import queue
import json
import threading
from categories import categories


MAX_PAGE = 125

class WildberriesScraper:
    def __init__(self, base_url, second_url):
        self.base_url = base_url
        self.second_url = second_url
        self.driver = None

    def setup_driver(self):
        options = Options()
        # скрыть браузер
        options.add_argument('--headless')
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def open_page(self, url):
        print(f"Открытие страницы: {url}")
        self.driver.get(url)
        time.sleep(10)

    def get_total_goods(self):
        print("Получение общего количества товаров...")
        total_goods_element = self.driver.find_element(By.CSS_SELECTOR, 'div.total-goods[data-tag="totalGoods"]')
        total_goods_text = total_goods_element.text
        return total_goods_text

    def enter_keywords_on_second_page(self, keywords):
        print("Ввод ключевых слов на второй странице...")
        search_area = self.driver.find_element(By.CSS_SELECTOR, 'textarea#search_area')
        search_area.send_keys(keywords)

    def click_search_button(self):
        print("Нажатие кнопки поиска...")
        search_button = self.driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary[type="submit"]')
        search_button.click()

    def get_keyword_counts(self, user_keywords):
        print("Получение количества ключевых слов...")
        keyword_counts = {}
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'div.container table tr')[1:]
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            keyword = cells[0].text
            count = cells[1].text
            benefit = cells[4].text
            category = self.get_category_name(keyword)
            if keyword in user_keywords:
                keyword_counts[keyword] = (count, benefit, category)
        return keyword_counts

    def get_all_keywords(self, page=1):
        print("Получение всех ключевых слов...")
        all_keywords = []
        while page <= MAX_PAGE:  
            print(f"Открытие страницы {page}...")
            self.open_page(f"{self.second_url}?search=&page={page}")
            time.sleep(5)
            rows = self.driver.find_elements(By.CSS_SELECTOR, 'div.container table tr')[1:]
            if not rows:
                break
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                keyword = cells[0].text
                count = cells[1].text
                benefit = cells[4].text
                all_keywords.append((keyword, count, benefit))
            next_button = self.driver.find_elements(By.CSS_SELECTOR, 'div.pages div.page.next a')
            if not next_button or 'следующая' not in next_button[0].text:
                break
            page += 1
        return all_keywords

    def close_driver(self):
        print("Закрытие браузера...")
        self.driver.quit()

    def scrape(self, keywords):
        start_time = time.time()
        try:
            print("Настройка драйвера...")
            self.setup_driver()
            search_url = self.generate_search_url(keywords)
            self.open_page(search_url)
            total_goods_text = self.get_total_goods()
            print(f'Количество товаров (конкурентов): {total_goods_text}')

            self.open_page(self.second_url)
            self.enter_keywords_on_second_page(keywords)
            self.click_search_button()

            time.sleep(5)

            keyword_counts = self.get_keyword_counts(keywords)
            if keyword_counts:
                print("Результаты поиска:")
                for keyword, (count, benefit, category) in keyword_counts.items():
                    print(f'Ключевое слово: "{keyword}"')
                    print(f'Количество запросов: {count}')
                    print(f'Выгода: {benefit}')
                    print(f'Категория товара: {category}')
                    print()
            else:
                print("По вашему запросу ничего не найдено.")

        finally:
            self.close_driver()
            end_time = time.time()
            print(f"Время выполнения скрипта: {end_time - start_time:.2f} секунд")

    def generate_search_url(self, keywords):
        query = urllib.parse.urlencode({'search': keywords})
        return f"{self.base_url}?{query}"

    def get_category_name(self, keyword):
        for pattern, category in categories.items():
            if pattern.search(keyword):
                return category
        return 'другое'

    def scrape_all_keywords(self):
        start_time = time.time()
        try:
            self.setup_driver()
            all_keywords = self.get_all_keywords()
            if all_keywords:
                print("Все ключевые слова:")
                data = []
                for i, (keyword, count, benefit) in enumerate(all_keywords, start=1):
                    print(f"{i}. Ключевое слово: {keyword}, Количество запросов: {count}, Выгода: {benefit}")
                    data.append({
                        'Ключевое слово': keyword,
                        'Количество запросов': count,
                        'Выгода': benefit
                    })
                with open('all_keywords.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print("Данные сохранены в all_keywords.json")
            else:
                print("Ключевые слова не найдены.")
        finally:
            self.close_driver()
            end_time = time.time()
            print(f"Время выполнения скрипта: {end_time - start_time:.2f} секунд")


def on_search():
    keywords = simpledialog.askstring("Input", "Введите ключевые слова для поиска:")
    if keywords:
        scraper = WildberriesScraper(base_url, second_url)
        scraper.scrape(keywords)
    else:
        print("Вы не ввели ключевые слова.")

def threaded_search():
    keywords_queue = queue.Queue()

    def get_keywords():
        keywords = simpledialog.askstring("Input", "Введите ключевые слова для поиска:")
        keywords_queue.put(keywords)

    root.after(0, get_keywords)

    def wait_for_keywords():
        try:
            keywords = keywords_queue.get_nowait()
            if keywords:
                scraper = WildberriesScraper(base_url, second_url)
                scraper.scrape(keywords)
            else:
                print("Вы не ввели ключевые слова.")
        except queue.Empty:
            root.after(100, wait_for_keywords)

    root.after(100, wait_for_keywords)

def start_all_keywords_scraper():
    scraper = WildberriesScraper(base_url, second_url)
    threading.Thread(target=scraper.scrape_all_keywords).start()

def close_app():
    root.destroy()


if __name__ == "__main__":
    base_url = 'https://global.wildberries.ru/catalog'
    second_url = 'https://wb.moytop.com/'

    root = tk.Tk()
    root.title("Операции")
    root.geometry("250x290")

    search_button = tk.Button(
        root,
        text="Начать поиск",
        command=threaded_search,
        bg="blue",
        fg="white",
        width=20,
        height=2,
        font=('Helvetica', 12, 'bold'))
    search_button.pack(pady=10)

    all_keywords_button = tk.Button(
        root,
        text="Все ключевые слова",
        command=start_all_keywords_scraper,
        bg="yellow",
        fg="black",
        width=20,
        height=2,
        font=('Helvetica', 12, 'bold'))
    all_keywords_button.pack(pady=10)

    close_button = tk.Button(root, text="Закрыть приложение", command=close_app, bg="red", fg="white", width=20, height=2, font=('Helvetica', 12, 'bold'))
    close_button.pack(pady=10)

    root.mainloop()
