import pandas as pd
import time
import csv
from selenium import webdriver
from bs4 import BeautifulSoup as soup
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

#options = Options()
#options.add_argument('--headless')

url = "http://search.w-nexco.co.jp/route.php"



#new session
df = pd.read_csv('201807_ryokin1.csv')
df_edit = df.dropna(subset=['入口','出口'])
full = []
for index, row in df_edit.iterrows():
    
    #navigate to the page
    driver = webdriver.Chrome()
    driver.get(url)

    #get the fill in form
    in_field = driver.find_element_by_name("fnm")
    in_field.send_keys(row['入口'])
    time.sleep(1)
    out_field = driver.find_element_by_name("tnm")
    out_field.send_keys(row['出口'])

    select_car_type = Select(driver.find_element_by_name("cartyp")).select_by_value("1")
    select_hour = Select(driver.find_element_by_id("sl_hour_id")).select_by_value("10")
    select_min = Select(driver.find_element_by_id("sl_min_id")).select_by_value("0")
    select_detour1 = Select(driver.find_element_by_id("detour1_id")).select_by_value("G1110")
    select_detour2 = Select(driver.find_element_by_id("detour2_id")).select_by_value("G7000")

    driver.find_element_by_css_selector(".submit-btn").send_keys("\n")
    time.sleep(3)
    driver.find_element_by_css_selector(".submit-btn").send_keys("\n")
    time.sleep(2)
    try:
        pass
    except UnexpectedAlertPresentException:
        alert = driver.switch_to_alert()
        alert.accept()
    #wait for page to load
    time.sleep(3)
    #get the toll fee
    normal_toll = driver.find_element_by_css_selector("span.toll-normal").get_attribute("innerText")
    etc_toll = driver.find_element_by_css_selector("span.toll-etc").get_attribute("innerText")
    etc2_toll = driver.find_element_by_css_selector("span.toll-etc2").get_attribute("innerText")

    #driver.find_element_by_css_selector(".etclist").click()

    time.sleep(5)

#if car type 1 and 2
#kyujitsu_toll = driver.find_element_by_xpath('//*[@id="etc_box1_5"]/div[2]/div/div/dl[1]/dd/span').get_attribute("innerText")
#shinya_toll = driver.find_element_by_xpath('//*[@id="etc_box1_5"]/div[2]/div/div/dl[2]/dd/span').get_attribute("innerText")
#per30_toll = driver.find_element_by_xpath('//*[@id="etc_box1_5"]/div[2]/div/div/dl[3]/dd[2]/dl[1]/dd/span').get_attribute("innerText")
#per50_toll = driver.find_element_by_xpath('//*[@id="etc_box1_5"]/div[2]/div/div/dl[3]/dd[2]/dl[2]/dd/span').get_attribute("innerText")


#kyujitsu_toll = 0
#shinya_toll = driver.find_element_by_xpath('//*[@id="etc_box1_5"]/div[2]/div/div/dl[1]/dd/span').get_attribute("innerText")
#per30_toll = driver.find_element_by_xpath('//*[@id="etc_box1_5"]/div[2]/div/div/dl[2]/dd[2]/dl[1]/dd/span').get_attribute("innerText")
#per50_toll = driver.find_element_by_xpath('//*[@id="etc_box1_5"]/div[2]/div/div/dl[2]/dd[2]/dl[2]/dd/span').get_attribute("innerText")


#close session
    driver.quit()

#toll = [normal_toll, etc_toll, etc2_toll, kyujitsu_toll, shinya_toll, per30_toll, per50_toll]
    
    toll = [row['入口'],row['出口'],normal_toll, etc_toll, etc2_toll]
    full.append(toll)
    time.sleep(10)

with open("highwayryokin.csv","w", newlin = '') as f:
    writer = csv.writer(f)
    writer.writerows(full)
