from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import pandas as pd
from bs4 import BeautifulSoup
import time

def setup_driver():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(10)  # General implicit wait for all elements
    return driver

def get_page_data(driver, url, retries=3):
    attempts = 0
    while attempts < retries:
        try:
            driver.get(url)
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "resultsTable")) 
            )
            WebDriverWait(driver, 30).until(
                lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "#resultsTable tr")) >= 51  # Check for at least 51 rows
            )
            return driver.page_source
        except TimeoutException:
            if attempts < retries - 1:  
                print(f"Retry {attempts + 1} for URL: {url}")
                time.sleep(10)  
            attempts += 1
        except Exception as e:
            print(f"Error encountered: {e}")
            break
    raise Exception(f"Failed to load page after {retries} attempts")

def parse_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    table_html = soup.find("table", id="resultsTable")
    if table_html:
        return pd.read_html(str(table_html))[0]
    return pd.DataFrame()

def main():
    driver = setup_driver()
    all_data = pd.DataFrame()

    try:
        for i in range(1, 204):  
            url = f"https://www.investing.com/stock-screener/?sp=country::5|sector::a|industry::a|equityType::a|exchange::a%3Ceq_market_cap;{i}"
            html = get_page_data(driver, url)
            df = parse_data(html)
            if not df.empty:
                all_data = pd.concat([all_data, df], ignore_index=True)

    finally:
        driver.quit()

   
    print("Data collected from all pages:")
    print(all_data.head(50))  
    print("\nOverall table info:")
    all_data.info()  
    all_data.to_csv("Screen_results.csv", index=False)

if __name__ == "__main__":
    main()