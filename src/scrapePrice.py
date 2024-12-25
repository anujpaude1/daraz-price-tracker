import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pprint import pformat
import json
import time,datetime
from selenium.webdriver import DesiredCapabilities
from urllib.parse import urlparse

import asyncio

class DarazScraper:
    def __init__(self):
        # Initialize undetected_chromedriver with the required options
        options = uc.ChromeOptions()
        options.page_load_strategy = 'none'
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        options.headless=True
        
        self.driver = uc.Chrome(options=options, enable_cdp_events=True, chrome_options=options)
        self.driver.maximize_window()
        
        
        # Open the Daraz homepage
        homepage_url = "https://www.daraz.com.np/"
        self.driver.get(homepage_url)
        
        # Wait for the homepage to load completely
        homepage_timeout = 5  # seconds
        wait = WebDriverWait(self.driver, homepage_timeout)
        wait.until(EC.presence_of_element_located((By.ID, "topActionHeader")))
        print("Homepage loaded successfully.")
        
        time.sleep(4)
    
    def get_product_details(self, product_url):
        try :
            self.driver.get(product_url)
            
            wait = WebDriverWait(self.driver, 10)
            current_price_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".pdp-price_type_normal")))
            current_price = current_price_element.text.strip()
            
            main_image_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".pdp-mod-common-image.gallery-preview-panel__image")))
            main_image_url = main_image_element.get_attribute('src')
            
            # Extract product name
            name_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".pdp-mod-product-badge-title")))
            product_name = name_element.text.strip()
            
            # Extract original price (if available)
            try:
                original_price_element = self.driver.find_element(By.CSS_SELECTOR, ".pdp-price_type_deleted")
                original_price = original_price_element.text.strip()
            except:
                original_price = None

            # Get the final URL after redirection
            final_url = self.driver.current_url
            
            # Extract product ID from the URL
            parsed_url = urlparse(final_url)
            product_id = parsed_url.path.split('products/')[-1].split('.html')[0]
            
            return {
                "Current Price": current_price,
                "Original Price": original_price,
                "Image URL": main_image_url,
                "Product Name": product_name,
                "Final URL": final_url[:final_url.find('.html') + 5],
                "Product ID": product_id
            }
        except Exception as e:
            print(f"An error occurred: {e}")
            raise e
    
    def close(self):
        self.driver.quit()

    def __del__(self):
        self.driver.quit()



# Example usage:
if __name__ == "__main__":
    scraper = DarazScraper()
    product_url = "https://www.daraz.com.np/products/sunisa-water-beauty-air-pad-cc-cream-lightweight-long-lasting-foundation-for-flawless-skin-i174376401-s1195850829.html"
    details = scraper.get_product_details(product_url)
    print(details)
    scraper.close()