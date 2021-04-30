from selenium import webdriver
from selenium.webdriver.chrome.options import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
import csv
import pandas as panda
from datetime import datetime as dt


co = webdriver.ChromeOptions()
co.add_argument("log-level=3")
co.add_argument("--headless")
a = re.compile('(#[0-9]+)PlayersBUSTED AT: ([0-9\.x]+)DATE: ([a-zA-Z,0-9: ]+) GMT')



def get_proxies():
    driver = webdriver.Chrome(executable_path='/Users/gudkov/PycharmProjects/Test/chromedriver_mac')
    driver.get("https://free-proxy-list.net/")
    driver.find_element_by_name("proxylisttable_length").click()
    driver.find_element_by_xpath("//select[@name='proxylisttable_length']/option[@value='80']").click()
    driver.find_element_by_xpath("//table[@id='proxylisttable']/tfoot/tr/th[4]/select").click()
    driver.find_element_by_xpath("//option[@value='DE']").click()
    PROXIES = []
    proxies = driver.find_elements_by_xpath("//table[@id='proxylisttable']/tbody/tr")
    for p in proxies:
        result = p.text.split(" ")
        #if result[-1] == "yes":
        PROXIES.append(result[0]+":"+result[1])

    driver.close()
    return PROXIES


ALL_PROXIES = get_proxies()
#ALL_PROXIES = list(panda.read_csv('socks5.txt',header=None)[0])
print(ALL_PROXIES)


def proxy_driver(PROXIES, co=co):
    prox = Proxy()

    if PROXIES:
        pxy = PROXIES[-1]
    else:
        print("--- Proxies used up. Downloading New List (%s)" % len(PROXIES))
        PROXIES = get_proxies()
        pxy = PROXIES[-1]


    prox.proxy_type = ProxyType.MANUAL
    prox.http_proxy = pxy
    prox.socks_proxy = pxy
    prox.ssl_proxy = pxy
    prox.no_proxy = None

    capabilities = webdriver.DesiredCapabilities.CHROME
    prox.add_to_capabilities(capabilities)

    driver = webdriver.Chrome(options=co,
                              desired_capabilities=capabilities,
                              executable_path='chromedriver_mc21')

    return driver




pd = proxy_driver(ALL_PROXIES)
#pd.set_page_load_timeout(15)
running = True
dat = panda.read_csv('kek.csv', header=None)
next_game = dat[0].str.replace('#', '').astype(int).max() + 1




while running:
    wait = WebDriverWait(pd, 30)
    try:
        resultFile = open("kek.csv", 'a')
        wr = csv.writer(resultFile, dialect='excel')
        for i in range(next_game, next_game + 10000):
            url = 'https://www.bustabit.com/game/' + str(i)


            pd.get(url)
            #time.sleep(4)
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, "h5")))

            res_text = ''
            data1 = pd.find_elements_by_tag_name('h4') + pd.find_elements_by_tag_name('h5')
            for row in data1:
                res_text += row.text
            m = re.findall(a, res_text)
            print(m)
            if m == []:
                resultFile.close()
                print(1/0)

            wr.writerow(m[0])
            next_game += 1
    except:
        pd.close()
        new = ALL_PROXIES.pop()
        pd = proxy_driver(ALL_PROXIES)
        #pd.set_page_load_timeout(15)
        print("--- Switched proxy to: %s" % new)
        time.sleep(1)
