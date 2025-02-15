from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Set up ChromeDriver
chrome_driver_path = "C:/Users/beth/bin/chromedriver.exe"
cdriver_options = webdriver.ChromeOptions()
service = Service(chrome_driver_path)
#service = Service(ChromeDriverManager().install())
if service is None:
    print("ERROR: unable to load chromedriver")
    exit(1)

driver = webdriver.Chrome()
if driver is None:
    print("ERROR: unable to connect to Chrome driver")
    exit(1)

driver.implicitly_wait(5)

# Navigate to a website
driver.get("https://www.example.com")
print(driver.title)

more_info = driver.find_element(By.LINK_TEXT, "More information...")
more_info.click()

# Wait for the page to load
driver.implicitly_wait(5)

# Verify the results
results = driver.find_elements(By.CSS_SELECTOR, "div#search div.g")
print(f"Found {len(results)} results.")

# Close the browser
driver.quit()
