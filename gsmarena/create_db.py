from selenium import webdriver
import pandas as pd
import time as t
import re


cache_path = ''
main_path = 'https://www.gsmarena.com/'
brands_links = pd.read_csv('brands_real.csv')
#brands_links = brands_links[brands_links[brands_links['name']=='TOSHIBA'].index[0]:]


prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("prefs", prefs)
browser = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)

catalog_pages = {}
for index, row in brands_links.iterrows():
    catalog_pages[row['name']] = [row['link']]
    link_num = re.findall(r'[0-9]+', row['link'])[0]
    link_gen = re.sub('-[0-9]+\.php', '', row['link'])
    catalog_pages[row['name']] += [link_gen + '-f-' + link_num + '-0-p' + str(i) + '.php' for i in range(2, row['max_page']+1)]


def add_phones(manufacturer, phone_pages):
    all_phones = pd.DataFrame()
    for page in phone_pages:
        print('going for', cache_path , page)
        t.sleep(5)
        browser.get(cache_path + page)
        if 'error' in browser.title.lower():
            print('cache not available')
            print('going for', page)
            browser.get(page)
            if 'error' in browser.title.lower():
                print('main not available')
                pass
        phone_name = browser.find_elements_by_class_name('specs-phone-name-title')[0].text
        print('now reading', phone_name)
        test = browser.find_element_by_id('specs-list')
        all_tables = test.find_elements_by_tag_name('table')
        phone = pd.DataFrame()
        for table in all_tables:
            main_title = table.find_elements_by_tag_name('th')[0].text
            sub_titles = table.find_elements_by_class_name('ttl')
            specs = table.find_elements_by_class_name('nfo')
            for sub_title, spec in zip([st.text for st in sub_titles],[s.text for s in specs]):
                phone = phone.append({'manufacturer': manufacturer,
                                      'phone_name': phone_name,
                                      'main_title': main_title,
                                      'sub_title': sub_title,
                                      'spec': spec}, ignore_index=True)
        all_phones = all_phones.append(phone)
    return all_phones


phone_db = pd.DataFrame()
#phone_db = pd.read_csv('phone_db.csv')
for brand, brand_pages in catalog_pages.items():
    phone_pages = []
    for brand_page in brand_pages:
        print('going for', cache_path, brand_page)
        t.sleep(5)
        browser.get(cache_path + brand_page)
        phones = browser.find_elements_by_class_name('makers')[0]
        phones = phones.find_elements_by_tag_name('ul')[0]
        phones = phones.find_elements_by_tag_name('li')
        for phone in phones:
            link = phone.find_elements_by_tag_name('a')[0].get_attribute('href')
            phone_pages += [link]
    phone_db = phone_db.append(add_phones(brand, phone_pages))
    phone_db.to_csv('phone_db.csv', index=False)
