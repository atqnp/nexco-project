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

df = pd.read_csv('ryokin_test.csv')
df_edit = df.dropna(subset=['入口','出口'])

#new session
class FeeList(object):
    def __init__(self):
        self.buttonlist = []

class AllToll(FeeList):
    def __init__(self, cartype_val):
        FeeList.__init__(self)
        self.cartype_val = cartype_val
        
    def get_toll(self, cartype_val):
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

            select_car_type = Select(driver.find_element_by_name("cartyp")).select_by_value(cartype_val)
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
            driver.find_element_by_id("pritab9").click()
            #get the toll fee
            time.sleep(3)
            
            def norm_toll():
                normal_toll = driver.find_element_by_css_selector("span.toll-normal").get_attribute("innerText")
                etc_toll = driver.find_element_by_css_selector("span.toll-etc").get_attribute("innerText")
                etc2_toll = driver.find_element_by_css_selector("span.toll-etc2").get_attribute("innerText")
                return normal_toll, etc_toll, etc2_toll
            
            def box_toll():
                box1_toll = driver.find_element_by_xpath('//*[@class="etc-info pc-stay pos-etc_box"]/div[2]/div')
                span_box1 = box1_toll.find_elements_by_tag_name("span")
                box1 = []
                for span1 in span_box1:
                    test1 = span1.get_attribute("innerText")
                    box1.append(test1)
                box2_toll = driver.find_element_by_xpath('//*[@class="etc-info pc-stay pos-etc2_box"]/div[2]/div')
                span_box2 = box2_toll.find_elements_by_tag_name("span")
                box2 = []
                for span2 in span_box2:
                    test2 = span2.get_attribute("innerText")
                    box2.append(test2)
                    
                def normal_case():
                    if len(span_box1) == 1:
                        box1.insert(0,0)
                        box1.extend([0,0])
                    if len(span_box2) == 1:
                        box2.insert(0,0)
                        box2.extend([0,0])
                    
                def big_case():
                    if len(span_box1) == 1:
                        box1.extend([0,0])
                    if len(span_box2) == 1:
                        box2.extend([0,0])
                
                if cartype_val == "1" or cartype_val == "2":
                    run_case = normal_case()
                else:
                    run_case = big_case()
                return  box1, box2
            
            get_norm_toll = norm_toll()
            get_box_toll = list(itertools.chain.from_iterable(box_toll()))

            #close session
            driver.quit()
    
            toll = [[row['入口']],[row['出口']], get_norm_toll, get_box_toll]
            merged_toll = list(itertools.chain.from_iterable(toll))
            self.buttonlist.append(merged_toll)
            time.sleep(10)
        return self.buttonlist
    
    
    
kei = AllToll("1").get_toll("1")
normal = AllToll("2").get_toll("2")
chugata = AllToll("3").get_toll("3")
ogata = AllToll("4").get_toll("4")
toku = AllToll("5").get_toll("5")
