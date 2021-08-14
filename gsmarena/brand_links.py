from selenium import webdriver
import pandas as pd
import time as t


prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("prefs", prefs)
browser = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)


catalog_pages = []
cache_path = ''
main_path = 'https://www.gsmarena.com/makers.php3'
t.sleep(5)
browser.get(cache_path + main_path)
brands = browser.find_elements_by_class_name('st-text')[0]
brands = brands.find_elements_by_tag_name('table')[0]
brands = brands.find_elements_by_tag_name('tbody')
brands = brands[0].find_elements_by_tag_name('a')

brands_df = pd.DataFrame()
for brand in brands:
    name = brand.text.split('\n')
    link = brand.get_attribute('href')
    brands_df = brands_df.append({'name':name[0], 'dev_num':name[1], 'link':link}, ignore_index=True)


for brand_link in brands_df['link'].to_list():
    print('going for', brand_link)
    t.sleep(5)
    browser.get(cache_path + brand_link)
    nav_pages = browser.find_elements_by_class_name('nav-pages')
    try:
        max_page = nav_pages[0].text.split('\n')[-1]
    except:
        max_page = 1
    brands_df.loc[brands_df['link']==brand_link, 'max_page'] = int(max_page)

brands_df['max_page'] = brands_df['max_page'].astype(int)
brands_df.to_csv('brands_real.csv', index=False)
