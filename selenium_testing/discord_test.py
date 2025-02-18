import unittest
from selenium import webdriver
from appium.options.windows import WindowsOptions
from selenium.webdriver.remote.client_config import ClientConfig


class SimpleDiscordTests(unittest.TestCase):
    
    @classmethod

    def setUpClass(self):
        # set up Appium
        app_path = "C:/Users/beth/AppData/Local/Discord/Update.exe"
        app_options = { "app": app_path,
                        "app_working_dir": "C:/Users/beth/Downloads/"
                      }
        driver_url = 'http://127.0.0.1:4723'
        client_cfg = ClientConfig(driver_url)

        # define runtime options
        try:
            discord_options = WindowsOptions().load_capabilities(app_options)
        except Exception as e:
            print("Unable to update options argument: %s"%e)
            exit(1)

        # Connect to webdriver and application
        try:
            self.driver = None
            self.driver = webdriver.Remote(command_executor=driver_url,
                                           options=discord_options)
        except Exception as e:
            print("unable to connect to WinAppDriver: %s"%e)
            exit(1)

        try:
            self.discord_app = None
            self.discord_app = self.driver.find_element_by_name("Discord")
        except Exception as e:
            print("Unable to find discord: %s"%e)
            exit(1)

    @classmethod
    def tearDownClass(self):
        self.driver.quit()

    def test_initialize(self):
        pass

    def test_post(self):
        pass


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleDiscordTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
