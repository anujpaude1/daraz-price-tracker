from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import json
import time

# Set Chrome options
options = Options()
options.page_load_strategy = 'none'
options.add_argument("start-maximized")
# Set a normal user agent string (simulating a real browser)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")

# Disable WebGL to avoid detection based on graphics capabilities
options.add_argument("--disable-webgl")

# Disable the automation flag (some websites detect Selenium by this)
options.add_argument("--disable-blink-features=AutomationControlled")

# Disable extensions to avoid detection
options.add_argument("--disable-extensions")

# Uncomment the next line to run in headless mode
# options.add_argument('--headless')  
options.add_argument('--disable-gpu')

# Enable logging of network events in Chrome
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

# Initialize the WebDriver
service = Service('/usr/bin/chromedriver')  # Replace with the path to your ChromeDriver
driver = webdriver.Chrome(service=service, options=options)

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

try:
    # Step 1: Open the Daraz homepage
    homepage_url = "https://www.daraz.com.np/"
    driver.get(homepage_url)

    # Use a timeout for the homepage to load, after which we proceed to the product page
    homepage_timeout = 5  # seconds
    wait.until(EC.presence_of_element_located((By.ID, "topActionHeader")))
    print("Homepage loading delayed or ignored.")

    # Step 2: Navigate to the specific product URL
    product_url = "https://www.daraz.com.np/products/sunisa-water-beauty-air-pad-cc-cream-lightweight-long-lasting-foundation-for-flawless-skin-i174376401-s1195850829.html"
    driver.get(product_url)

    try:
        # Wait for the product page to load or for 20 seconds (whichever is first)
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
    except:
        # Stop loading if the timeout is exceeded
        driver.execute_script("window.stop();")
        print("Product page loading stopped due to timeout.")

    print("Product page loaded or forcefully stopped.")

    # Additional delay to ensure XHR requests are completed
    time.sleep(2)

    # Get all logged performance logs
    logs = driver.get_log('performance')

    # Step 3: Look for XHR requests to the desired URL
    for entry in logs:
        log = json.loads(entry['message'])['message']
        if log['method'] == 'Network.responseReceived':
            url = log['params']['response']['url']
            if url.startswith("https://acs-m.daraz.com.np/h5/mtop.global.detail.web.getdetailinfo/1.0/"):
                # Fetch the response body
                request_id = log['params']['requestId']
                response_body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                print(f"URL: {url}")
                print("Response Body:")
                print(json.dumps(response_body, indent=2))
                break


finally:
    # Close the WebDriver
    driver.quit()
