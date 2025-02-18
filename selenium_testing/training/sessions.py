from selenium import webdriver
import time

driver_started = False

try:
    chrome_driver = webdriver.Chrome()
    driver_started = True
except Exception as e:
    print("Failure to start the Selenium Chrome Driver: %s"%e)

time.sleep(3)

if driver_started:
    chrome_driver.quit()
