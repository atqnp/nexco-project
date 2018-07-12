import time
import csv
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

url = "http://search.w-nexco.co.jp/"


#new session
driver = webdriver.Chrome()

#navigate to the page
driver.get(url)

#fill in the form for all field
in_field = driver.find_element_by_name("tnm")
in_field.send_keys("豊前")
out_field = driver.find_element_by_name("fnm")
out_field.send_keys("佐賀大和")
#軽自動車=1, 普通車=2, 中型車=3, 大型車=4, 特大車=5
select_car_type = Select(driver.find_element_by_name("cartyp")).select_by_value("4")

#select = Select(driver.find_element_by_id("dropDown"))
#options = select.options
#for index in range(0, len(options) - 1):
#    select.select_by_index(index)

select_hour = Select(driver.find_element_by_id("sl_hour_id")).select_by_value("10")
select_min = Select(driver.find_element_by_id("sl_min_id")).select_by_value("0")

#click submit button
driver.find_element_by_css_selector(".submit-btn").send_keys("\n")

#wait for page to load
time.sleep(10)

#get the toll fee
normal_toll = driver.find_element_by_css_selector("span.toll-normal").get_attribute("innerText")
etc_toll = driver.find_element_by_css_selector("span.toll-etc").get_attribute("innerText")
etc2_toll = driver.find_element_by_css_selector("span.toll-etc2").get_attribute("innerText")

driver.find_element_by_css_selector(".etclist").click()

time.sleep(5)

#if car type 1 and 2
#kyujitsu_toll = driver.find_element_by_xpath('//*[@id="etc_box1_5"]/div[2]/div/div/dl[1]/dd/span').get_attribute("innerText")
#shinya_toll = driver.find_element_by_xpath('//*[@id="etc_box1_5"]/div[2]/div/div/dl[2]/dd/span').get_attribute("innerText")
#per30_toll = driver.find_element_by_xpath('//*[@id="etc_box1_5"]/div[2]/div/div/dl[3]/dd[2]/dl[1]/dd/span').get_attribute("innerText")
#per50_toll = driver.find_element_by_xpath('//*[@id="etc_box1_5"]/div[2]/div/div/dl[3]/dd[2]/dl[2]/dd/span').get_attribute("innerText")

kyujitsu_toll = 0
shinya_toll = driver.find_element_by_xpath('//*[@id="etc_box1_5"]/div[2]/div/div/dl[1]/dd/span').get_attribute("innerText")
per30_toll = driver.find_element_by_xpath('//*[@id="etc_box1_5"]/div[2]/div/div/dl[2]/dd[2]/dl[1]/dd/span').get_attribute("innerText")
per50_toll = driver.find_element_by_xpath('//*[@id="etc_box1_5"]/div[2]/div/div/dl[2]/dd[2]/dl[2]/dd/span').get_attribute("innerText")

#close session
driver.quit()

#toll = [normal_toll, etc_toll, etc2_toll, kyujitsu_toll, shinya_toll, per30_toll, per50_toll]
toll = [normal_toll, etc_toll, etc2_toll, kyujitsu_toll, shinya_toll, per30_toll, per50_toll]
toll
