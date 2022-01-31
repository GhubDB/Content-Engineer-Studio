from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# options = webdriver.ChromeOptions()
# options.add_experimental_option("detach", True)
# driver = webdriver.Chrome(options=options)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))





driver.get('https://getstream.io/chat/demos/messaging/')

# login = driver.find_element(By.CLASS_NAME, 'str-chat__message-text-inner str-chat__message-simple-text-inner')
# login.send_keys('bluegrey')

# login = driver.find_element(By.ID, 'old-password')
# login.send_keys('reverberate3')
# login.send_keys('\n')

# driver.get('https://kemono.party/favorites')


messages = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "str-chat__message-text-inner str-chat__message-simple-text-inner"))
)

# releases = favourites.find_elements_by_class_name('user-card ')
for message in messages:
    content = message.find_elements(By.CLASS_NAME, 'str-chat__message-text-inner str-chat__message-simple-text-inner')
    print(content.text)












'''driver.get('https://kemono.party/account/login')

login = driver.find_element(By.ID, 'old-username')
login.send_keys('bluegrey')

login = driver.find_element(By.ID, 'old-password')
login.send_keys('reverberate3')
login.send_keys('\n')

driver.get('https://kemono.party/favorites')

try:
    favourites = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "card-list__items"))
    )

    releases = favourites.find_elements_by_class_name('user-card ')
    for release in releases:
        name = release.find_element(By.CLASS_NAME, 'user-card__name')
        updated = release.find_element(By.CLASS_NAME, 'user-card__updated')
        print(name.text)
        print(updated.text)

except:
    print('error')'''



# driver.maximize_window()

# timestamp = driver.find_element_by_xpath(//*[@id="page"]/div[3]/div[2]/article[1]/div[4]/time)