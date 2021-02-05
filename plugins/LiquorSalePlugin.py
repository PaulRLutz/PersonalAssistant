from base_classes.Plugin import Plugin
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
from pyvirtualdisplay import Display
import os
import wget
import datetime
from dateutil.relativedelta import relativedelta
from urllib.error import HTTPError
import re
import collections
import pickle
import traceback

LiquorItem = collections.namedtuple("LiquorItem", "name volume price sale")

class LiquorSalePlugin(Plugin):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.update_data()

  def cmd_get_current_liquor_sales(self):
    user_sale_watches = self.get_user_sale_watches()
    year = datetime.datetime.now().strftime("%Y")
    month = datetime.datetime.now().strftime("%m")
    liquor_sales, start_date, end_date = self.get_cached_liquor_sales(year, month)
    end_date_string = end_date.strftime("%B %d")

    final_sale_string = ""
    for liquor_sale in liquor_sales:
      for contains_string in user_sale_watches["contains"]:
        if contains_string in liquor_sale.name.lower():
          final_sale_string += self.get_sale_string(liquor_sale, end_date_string) + "\n"
      for matches_string in user_sale_watches["matches"]:
        if matches_string.lower() == liquor_sale.name.lower():
          final_sale_string += self.get_sale_string(liquor_sale, end_date_string) + "\n"

    return True, final_sale_string.strip()

  def get_sale_string(self, liquor_sale, end_date_string):
    return f"Sale on {liquor_sale.name} ({liquor_sale.volume}), now {liquor_sale.price}, down {liquor_sale.sale}. Ends on {end_date_string}."
  def get_cached_liquor_sales(self, year, month):
    for filename in os.listdir(self.DATA_FOLDER()):
      if filename.endswith(".liquor_sales") and filename.startswith(f"{year}_{month}"):
        start_date = datetime.datetime.fromtimestamp(float(filename.split("_")[2]))
        end_date = datetime.datetime.fromtimestamp(float(filename.split("_")[3][:-7]))
        return pickle.load(open(self.DATA_FOLDER() + os.sep + filename, "rb")), start_date, end_date

  def get_user_sale_watches(self):
    user_sale_watches = {"contains":[],"matches":[]}
    for key, value in self.assistant.liquor_sale_plugin_config_dict.items():
      if key.startswith("sale_watch"):
        if "contains" in value.keys():
          user_sale_watches["contains"].append(value["contains"])
        elif "matches" in value.keys():
          user_sale_watches["matches"].append(value["matches"])

    return user_sale_watches

  def get_stored_sales_files(self):
    stored_sales_files = []
    for filename in os.listdir(self.DATA_FOLDER()):
      if not filename.endswith(".liquor_sales"):
        continue
      else:
        stored_sales_files.append(filename)
    return stored_sales_files
  
  def update_data(self):
    self.download_pdfs(self.get_stored_sales_files())
    for filename in os.listdir(self.DATA_FOLDER()):
      if filename.endswith(".pdf"):
        self.parse_pdf(self.DATA_FOLDER() + os.sep + filename)
    self.delete_pdfs()

  def download_pdfs(self, stored_sales_files):
    url_start = "http://www.finewineandgoodspirits.com/static/pdf/monthlyInStoreSale/FWGS_"
    url_end = ".pdf"

    for month_delta in [0, 1, 2]:
      date = datetime.datetime.now()
      date = date + relativedelta(months=month_delta)
      month_string = date.strftime("%m")
      year_string = date.strftime("%Y")
      sales_already_stored = False
      for stored_sales_file in stored_sales_files:
        stored_sales_file_year = stored_sales_file.split("_")[0]
        stored_sales_file_month = stored_sales_file.split("_")[1]
        if stored_sales_file_year == year_string and stored_sales_file_month == month_string:
          sales_already_stored = True
          self.log.debug("don't download pdf, sales already stored")
          break
      if sales_already_stored:
        continue
      url = url_start + year_string + month_string + url_end
      try:
        filename = wget.download(url, out=self.DATA_FOLDER())
      except HTTPError:
        self.log.warn(f"coudln't get liquor sales for year/month: {year_string}/{month_string}")

  def delete_pdfs(self):
    for filename in os.listdir(self.DATA_FOLDER()):
      if filename.endswith(".pdf"):
        os.remove(self.DATA_FOLDER() + os.sep + filename)

  def setup_virtual_display(self):
    display = Display(visible=0, size=(2560, 1440))
    display.start()
    return display

  def parse_pdf(self, filename):
    if os.sep in filename:
      pdf_name = filename.split(os.sep)[-1]
    else:
      pdf_name = filename
    
    year_month_string = pdf_name.split("_")[1].split(".")[0]
    year_string = year_month_string[:4]
    month_string = year_month_string[4:]

    display = self.setup_virtual_display()

    liquor_items = []
    driver = webdriver.Firefox()
    try:
      folder_name = os.getcwd()
      driver.get(f"file://{folder_name}{os.sep}{filename}")
      time.sleep(2)

      thru_string = driver.find_element_by_xpath("//div[contains(text(), 'thru')]").text
      starting_date = datetime.datetime.strptime(thru_string.split(" thru ")[0], "%B %d, %Y")
      ending_date = datetime.datetime.strptime(thru_string.split(" thru ")[1], "%B %d, %Y")

      for page_element in driver.find_elements_by_class_name("page"):
        driver.execute_script("arguments[0].scrollIntoView()", page_element)
        time.sleep(.5)
  
      body_text_list = driver.find_elements_by_xpath("//body")[0].text.split("\n")
  
      for i, line in enumerate(body_text_list):
        if "..." in line and "CONTAINS" not in line:
          name = line.strip().rstrip(".").strip()
          volume = body_text_list[i+1].strip()
          price = body_text_list[i+2].strip()
          sale = body_text_list[i+3].strip()
          liquor_items.append(LiquorItem(name, volume, price, sale))

      pickle.dump(liquor_items, open(self.DATA_FOLDER() + os.sep + f"{year_string}_{month_string}_{starting_date.timestamp()}_{ending_date.timestamp()}.liquor_sales", "wb"))
    except:
      self.log.error("problem parsing liquor page")
      self.log.error(traceback.format_exc())
      driver.quit()
      display.stop()
