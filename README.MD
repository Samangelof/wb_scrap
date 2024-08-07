Проект реализует графический интерфейс пользователя (GUI) для поиска и анализа ключевых слов на сайте Wildberries. Используя библиотеки tkinter для создания GUI и selenium для автоматизации браузера, программа позволяет пользователям искать товары по ключевым словам, получать информацию о частоте запросов и выгода, а также сохранять все найденные ключевые слова в файл.

## Установка

1. Склонировать репозиторий:
    ```bash
    git clone https://github.com/your-username/wildberries-scraper.git
    cd wildberries-scraper
    ```

2. Создать и активировать виртуальное окружение:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate

    # macOS/Linux
    source venv/bin/activate
    ```

3. Установить зависимости:
    ```bash
    pip install -r requirements.txt
    ```

## Использование

4. Запустить скрипт:
    ```bash
    python scraper.py
    ```

5. **Заключительные шаги:**

    ```bash
    # Добавление файлов в репозиторий
    git add .
    git commit -m "Initial commit with scraper script and README"
    git branch -M main
    git remote add origin https://github.com/your-username/wildberries-scraper.git
    git push -u origin main
    ```
