from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time, requests, os

file_path = '/Users/zakporat/Desktop/SoleScout/output/listings-nikeairforce1.xlsx'

data = pd.read_excel(file_path)

links = data['Link'].tolist()
shoeName = data['Shoe Details'].tolist()

for link, name in zip(links, shoeName):
  # link, name = links[0], shoeName[0]

  options = webdriver.ChromeOptions()

  options.add_argument('--headless')

  driver = webdriver.Chrome(options=options)

  driver.get(link)

  time.sleep(.5)

  driver.execute_script("window.scrollBy(0, 150);")

  driver.execute_script("window.scrollBy(0, 150);")

  time.sleep(.5)

  imageContainer = driver.find_element(By.XPATH, '//*[@id="__next"]/div[5]/div[2]/main/div[1]/div/div/div/div[1]/div/div[4]/div/div/div')
  imgTags = [img.get_attribute('src') for img in imageContainer.find_elements(By.TAG_NAME, 'img')]

  mainDir = "image-output"
  subDir = f"{name}-images"
  fullPath = os.path.join(mainDir, subDir)

  if not os.path.exists(fullPath):
      os.makedirs(fullPath)

  for idx, img_url in enumerate(imgTags):
      response = requests.get(img_url)
      if response.status_code == 200:
          with open(os.path.join(fullPath, f"image_{idx}.jpg"), 'wb') as f:
              f.write(response.content)
          print(f"Added image_{idx}.jpg to {fullPath}")

