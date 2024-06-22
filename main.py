import tkinter as tk
from tkinter import simpledialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib.parse
import queue


class WildberriesScraper:
    def __init__(self, base_url, second_url):
        self.base_url = base_url
        self.second_url = second_url
        self.driver = None

    def setup_driver(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)

    def open_page(self, url):
        self.driver.get(url)
        time.sleep(10)

    def get_total_goods(self):
        total_goods_element = self.driver.find_element(By.CSS_SELECTOR, 'div.total-goods[data-tag="totalGoods"]')
        total_goods_text = total_goods_element.text
        return total_goods_text

    def enter_keywords_on_second_page(self, keywords):
        search_area = self.driver.find_element(By.CSS_SELECTOR, 'textarea#search_area')
        search_area.send_keys(keywords)
        
    def click_search_button(self):
        search_button = self.driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary[type="submit"]')
        search_button.click()

    def get_keyword_counts(self, user_keywords):
        keyword_counts = {}
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'div.container table tr')[1:]
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            keyword = cells[0].text
            count = cells[1].text
            benefit = cells[4].text
            if keyword in user_keywords:
                keyword_counts[keyword] = (count, benefit)
        return keyword_counts

    def close_driver(self):
        self.driver.quit()

    def scrape(self, keywords):
        try:
            self.setup_driver()
            search_url = self.generate_search_url(keywords)
            self.open_page(search_url)
            total_goods_text = self.get_total_goods()
            print(f'Количество товаров (конкурентов): {total_goods_text}')
            
            self.open_page(self.second_url)
            self.enter_keywords_on_second_page(keywords)
            self.click_search_button()
            
            time.sleep(10)
            
            user_keywords = keywords.split()
            keyword_counts = self.get_keyword_counts(user_keywords)
            if keyword_counts:
                print("Результаты поиска:")
                for keyword, (count, benefit) in keyword_counts.items():
                    print(f'Ключевое слово: "{keyword}"')
                    print(f'Количество запросов: {count}')
                    print(f'Выгода: {benefit}')
                    print()
            else:
                print("По вашему запросу ничего не найдено.")
            
        finally:
            self.close_driver()

    def generate_search_url(self, keywords):
        query = urllib.parse.urlencode({'search': keywords})
        return f"{self.base_url}?{query}"

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

def close_app():
    root.destroy()
    

if __name__ == "__main__":
    base_url = 'https://global.wildberries.ru/catalog'
    second_url = 'https://wb.moytop.com/'

    root = tk.Tk()
    root.title("Операции")
    root.geometry("250x180")

    search_button = tk.Button(
        root, 
        text="Начать поиск", 
        command=threaded_search, 
        bg="blue", 
        fg="white", 
        width=20, 
        height=2,
        font=('Helvetica', 12, 'bold'))
    search_button.pack(pady=20)

    close_button = tk.Button(root, text="Закрыть приложение", command=close_app, bg="red", fg="white", width=20, height=2, font=('Helvetica', 12, 'bold'))
    close_button.pack(pady=10)

    root.mainloop()