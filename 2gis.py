import json
import logging
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from apscheduler.schedulers.blocking import BlockingScheduler

driver = webdriver.Chrome(executable_path="C:\chromedriver.exe")
handles = driver.window_handles
ENTER = Keys.ENTER
wait = WebDriverWait(driver, 15)
# Создание объекта логгера
logger = logging.getLogger(__name__)

# Установка уровня логирования
logger.setLevel(logging.INFO)

# Создание обработчика (запись в файл)
file_handler = logging.FileHandler('log_file.log')

file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')

file_handler.setFormatter(formatter)

# Добавление обработчика в логгер
logger.addHandler(file_handler)


class Tima:
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path="C:\chromedriver.exe")
        self.wait = WebDriverWait(self.driver, 15)
        self.url_list = [
            "https://2gis.ru/ufa/firm/70000001044506651/tab/reviews",
            "https://2gis.ru/ufa/firm/2393065583018885/tab/reviews",
            "https://2gis.ru/ufa/firm/2393066583119255/tab/reviews",
        ]
        self.load_cookies()

    def save_cookies(self):
        # Сохранение куки в файл json
        with open('cookies.json', 'w', encoding='utf-8') as f:
            json.dump(self.driver.get_cookies(), f)

    def load_cookies(self):
        try:
            # Загрузка куки из файла json после открытия первой ссылки
            self.driver.get(self.url_list[0])
            with open('cookies.json', 'r', encoding='utf-8') as f:
                cookies = json.load(f)
                for cookie in cookies:
                    if 'expiry' in cookie:
                        del cookie['expiry']
                    self.driver.add_cookie(cookie)
        except FileNotFoundError:
            pass

    def get_services(self, url):
        try:
            self.driver.get(url)
            all_services = self.wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, '_8xepcx9')))
            services = [item.text for item in all_services]
            logger.info(f"Успешно получены данные с URL: {url}")
            return services
        except Exception as e:
            logger.error(f"Произошла ошибка получения данных с URL: {url}")
            logger.exception(e)
            raise

    def get_address(self):
        try:
            click = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, '_2lcm958')))
            click.click()
            address_element = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, '_er2xx9')))
            address = str(address_element.text)
            logger.info("Успешно получен адрес")
            return address
        except Exception as e:
            logger.error("Произошла ошибка получения адреса")
            logger.exception(e)
            raise

    def save_to_db(self, address_list, address):
        try:
            # Подключение к базе данных и создание если она не существует
            conn = sqlite3.connect('my_data_4.db')
            c = conn.cursor()

            # Создание таблицы, если она не существует
            c.execute('''CREATE TABLE IF NOT EXISTS my_data_4 (address TEXT, feedback TEXT)''')

            c.execute("INSERT INTO my_data_4 (address) VALUES (?)", (address,))
            for add in address_list:
                c.execute("INSERT INTO my_data_4 (feedback) VALUES (?)", (add,))
            # Сохранение изменений и закрытие соединения
            conn.commit()
            conn.close()
            logger.info("Данные успешно сохранены в базе данных")
        except Exception as e:
            logger.error("Произошла ошибка сохранения данных в базу данных")
            logger.exception(e)
            raise

    def menu_display(self):
        try:
            for url in self.url_list:
                services = self.get_services(url)
                add = self.get_address()
                self.save_to_db(services, add)

            logger.info("Программа выполнена успешно")
        except:
            logger.error("Произошла ошибка при выполнении программы")
            raise

        finally:
            # Сохранение кук в файл json
            self.save_cookies()
            # Закрытие браузера
            self.driver.quit()


def test_2gis():
    browser = Tima()
    browser.menu_display()


scheduler = BlockingScheduler()
# можно использовать для быстро проверки периодичности (40сек)
scheduler.add_job(test_2gis, 'interval', seconds=40)
# основное условие по задания (с пн-чт с 9-18 часов)
scheduler.add_job(test_2gis, 'cron', day_of_week='mon-fri', hour='9-18')

if __name__ == '__main__':
    scheduler.start()
