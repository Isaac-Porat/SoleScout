from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time, re, time, spacy, os
import pandas as pd

class OfferUpScraper:

  def __init__(self, shoe_type, distance, delivery_method, zipcode, price_percentage_evaluation, reference_price):
    self.shoe_type = shoe_type.lower()
    self.distance = distance
    self.delivery_method = delivery_method
    self.zipcode = zipcode
    self.price_percentage_evaluation = float(price_percentage_evaluation)
    self.reference_price = reference_price
    self.driver = None
    self.nlp = spacy.load("en_core_web_sm")
    self.scraped_shoe_listings = []
    self.desired_shoes = []

  def setup_driver(self):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    print(f"Setting up driver for Firefox...")
    self.driver = webdriver.Chrome(options=options)

  def construct_url(self):
    base_url = "https://offerup.com/search?"
    shoe_search_param = f"{self.shoe_type.replace(' ', '+')}"
    distance_search_param = self.distance if 5 <= self.distance <= 30 else None
    delivery_method_search_param = self.delivery_method if self.delivery_method in ["p", "s", "p_s"] else None
    if not distance_search_param or not delivery_method_search_param or len(str(self.zipcode)) != 5:
      raise ValueError("Invalid parameters for URL construction")
    print(f"Constructing url...")
    return f"{base_url}q={shoe_search_param}&DISTANCE={distance_search_param}&DELIVERY_FLAGS={delivery_method_search_param}"

  def scrape_listings(self):
    self.setup_driver()
    constructed_url = self.construct_url()
    self.driver.get(constructed_url)

    # Scraper
    self.driver.get(self.construct_url())
    print(f"Scraping listings...")

    try:
      location = self.driver.find_element(By.XPATH, '//*[@id="__next"]/div[5]/div[2]/main/div[2]/div/div[1]/button')
      ActionChains(self.driver).click(location).perform()

      locationToInput = self.driver.find_element(By.XPATH, '/html/body/div[3]/div[3]/div/div[3]/div/div/div[3]/div[2]/button')
      ActionChains(self.driver).click(locationToInput).perform()

      inputField = self.driver.find_element(By.XPATH, '/html/body/div[3]/div[3]/div/form/div[4]/div/div/div[4]/div[1]/div/div/input')
      ActionChains(self.driver).click(inputField).perform()

      inputField.clear()

      ActionChains(self.driver).click(inputField).perform()

      inputField.send_keys(self.zipcode)

      applyButton = self.driver.find_element(By.XPATH, '/html/body/div[3]/div[3]/div/form/div[5]/button')
      ActionChains(self.driver).click(applyButton).perform()

      time.sleep(3)

      exitToMainPage = self.driver.find_element(By.XPATH, '/html/body/div[3]/div[3]/div/div[1]/button')
      ActionChains(self.driver).click(exitToMainPage).perform()
    except:
      raise ValueError("Failed to set location...")

    self.scraped_shoe_listings = []

    try:
      while True:
        initial_len = len(self.scraped_shoe_listings)
        i = 1
        while True:
          try:
            xpath = f'//*[@id="__next"]/div[5]/div[2]/main/div[3]/div/div[1]/div/a[{i}]'
            post = self.driver.find_element(By.XPATH, xpath)
            aria_label = post.get_attribute("aria-label")
            href = post.get_attribute("href")
            if href.startswith("https://www.bing.com"):
                i += 1
                continue
            if (aria_label, href) not in self.scraped_shoe_listings:
                self.scraped_shoe_listings.append((aria_label, href))
            i += 1
          except:
            break
        self.driver.execute_script("window.scrollBy(0, 10000);")
        self.driver.implicitly_wait(1)
        if initial_len == len(self.scraped_shoe_listings):
          break
    except Exception as e:
      print(e)
      raise ValueError("Failed to scrape shoe listings...")

    self.driver.quit()

  def clean_listings(self):
    print(f"Cleaing listings...")
    try:
      for listing in self.scraped_shoe_listings:

        # Clean data
        shoeInfo, postLink = listing

        rawShoeDetails, location = shoeInfo.split("  in ")

        shoeDetailsWithoutPrice = " ".join(rawShoeDetails.split(" ")[:-1])

        price = rawShoeDetails.split(" ")[-1].replace("$", "").replace(",", "")

        shoe = [shoeDetailsWithoutPrice, location, price, postLink]

        # Natural Language Processing
        preProcessedShoeDetailsWithoutPrice = re.sub(r'\W+', ' ', shoeDetailsWithoutPrice.lower())
        preProcessedDesiredShoeType = re.sub(r'\W+', ' ', self.shoe_type.lower())

        shoeDetailsDoc = self.nlp(preProcessedShoeDetailsWithoutPrice)

        desiredShoeTypeDoc = self.nlp(preProcessedDesiredShoeType)

        for token1 in desiredShoeTypeDoc:

          for token2 in shoeDetailsDoc:

            if token1.lemma_ == token2.lemma_:

              if None not in shoe:
                price = float(shoe[2])
                lowerBound = self.reference_price * (1 - self.price_percentage_evaluation)
                upperBound = self.reference_price * (1 + self.price_percentage_evaluation)
                if lowerBound <= price <= upperBound:
                  self.desired_shoes.append(shoe)
    except Exception as e:
      print(e)
      raise ValueError("Failed to clean shoe listings...")

  def save_to_excel(self):
    df = pd.DataFrame(self.desired_shoes, columns=['Shoe Details', 'Location', 'Price', 'Link'])
    excel_path = f'/Users/zakporat/Desktop/SoleScout/output/listings-{self.shoe_type.replace(" ", "")}.xlsx'
    if os.path.exists(excel_path):
        existing_df = pd.read_excel(excel_path)
        combined_df = pd.concat([existing_df, df], ignore_index=True).drop_duplicates(subset=['Link'])
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            combined_df.to_excel(writer, index=False)
    else:
        df.to_excel(excel_path, index=False)
    print(f"Data saved to {excel_path}")
    return excel_path

  def run(self):
    try:
      self.scrape_listings()
      self.clean_listings()
    finally:
      if self.driver:
          self.driver.quit()


