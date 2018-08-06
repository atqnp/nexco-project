import pandas as pd
import time
import csv
import itertools
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

url = "http://search.w-nexco.co.jp/route.php"

#new session
df = pd.read_csv('201807_ryokin1.csv')
df_edit = df.dropna(subset=['入口','出口'])
full_kei = []
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
    time.sleep(1)

    select_car_type = Select(driver.find_element_by_name("cartyp")).select_by_value("1")
    time.sleep(1)
    select_hour = Select(driver.find_element_by_id("sl_hour_id")).select_by_value("10")
    time.sleep(1)
    select_min = Select(driver.find_element_by_id("sl_min_id")).select_by_value("0")
    time.sleep(1)
    select_detour1 = Select(driver.find_element_by_id("detour1_id")).select_by_value("G1110")
    time.sleep(1)
    select_detour2 = Select(driver.find_element_by_id("detour2_id")).select_by_value("G6000")

    driver.find_element_by_css_selector(".submit-btn").send_keys("\n")
    time.sleep(3)
    driver.find_element_by_css_selector(".submit-btn").send_keys("\n")
    time.sleep(2)
    
    #wait for page to load
    time.sleep(3)
    driver.find_element_by_id("pritab3").click()
    #get the toll fee
    time.sleep(3)
    
    normal_toll = driver.find_element_by_css_selector("span.toll-normal").get_attribute("innerText")
    etc_toll = driver.find_element_by_css_selector("span.toll-etc").get_attribute("innerText")
    etc2_toll = driver.find_element_by_css_selector("span.toll-etc2").get_attribute("innerText")
    box1_toll = driver.find_element_by_xpath('//*[@class="etc-info pc-stay pos-etc_box"]/div[2]/div')
    span_box1 = box1_toll.find_elements_by_tag_name("span")
    box1 = []
    for span1 in span_box1:
        test1 = span1.get_attribute("innerText")
        box1.append(test1)
    if len(span_box1) == 1:
        box1.insert(0,0)
        box1.extend([0,0])
    box2_toll = driver.find_element_by_xpath('//*[@class="etc-info pc-stay pos-etc2_box"]/div[2]/div')
    span_box2 = box2_toll.find_elements_by_tag_name("span")
    box2 = []
    for span2 in span_box2:
        test2 = span2.get_attribute("innerText")
        box2.append(test2)
    if len(span_box2) == 1:
        box2.insert(0,0)
        box2.extend([0,0])

    #close session
    driver.quit()
    
    toll = [[row['入口']],[row['出口']],[normal_toll], [etc_toll], [etc2_toll], box1, box2]
    merged_toll = list(itertools.chain.from_iterable(toll))
    full_kei.append(merged_toll)
    time.sleep(10)
    
pd_toll_kei = pd.DataFrame(full_kei)
all_kei = pd_toll_kei[pd_toll_kei.columns[2:]].replace('[\$,円,分]', '', regex=True).astype(int)
with pd.ExcelWriter('toll kei.xlsx') as writer:
    pd_toll_kei.to_excel(writer, sheet_name='pd toll kei')
    all_kei.to_excel(writer, sheet_name='all kei)
