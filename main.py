from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

class WildberriesScraper:
    def __init__(self, search_url):
        self.search_url = search_url
        self.driver = None

    def setup_driver(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)

    # 5 секунд для загрузки страницы
    def open_page(self):
        self.driver.get(self.search_url)
        time.sleep(10)  

    def get_total_goods(self):
        total_goods_element = self.driver.find_element(By.CSS_SELECTOR, 'div.total-goods[data-tag="totalGoods"]')
        total_goods_text = total_goods_element.text
        return total_goods_text

    def close_driver(self):
        self.driver.quit()

    def scrape(self):
        try:
            self.setup_driver()
            self.open_page()
            total_goods_text = self.get_total_goods()
            print(f'Количество товаров (конкурентов): {total_goods_text}')
        finally:
            self.close_driver()


# url должен быть динамичным
if __name__ == "__main__":
    url = 'https://global.wildberries.ru/catalog?search=платье+летнее+женское'
    scraper = WildberriesScraper(url)
    scraper.scrape()
