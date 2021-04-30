from selenium import webdriver
import pandas as pd
import datetime as dt
from datetime import timedelta
username = 'email'
password = 'pass'
browser = webdriver.Chrome(executable_path='')
browser.get('https://appmagic.rocks/dashboards/....')


def create_chart_csv(csv_name_suffix=''):
    ## Getting Chart Data
    test = browser.find_elements_by_xpath("//*[@class='highcharts-graph']")
    plot_str = test[-1].get_attribute('d')
    plot_list = plot_str.replace('M', 'L')[2:].split(' L ')
    plot_list = [i.split(' ') for i in plot_list]
    plot_df = pd.DataFrame(plot_list).astype(float)
    #plot_df['dates'] = pd.date_range(end=dt.date.today() - timedelta(1), periods=len(plot_df), freq='1d')

    last_date = dt.date.today() - timedelta(1)
    plot_df['0_shifted'] = plot_df[0].shift(1)
    plot_df['diff'] = plot_df[0] - plot_df['0_shifted']
    plot_df['diff_real'] = (plot_df['diff'] / plot_df['diff'].min()).fillna(0).astype(int)
    plot_df.loc[len(plot_df) - 1, 'dates'] = last_date
    for i in range(len(plot_df) - 2, -1, -1):
        plot_df.loc[i, 'dates'] = plot_df.loc[i + 1, 'dates'] - timedelta(int(plot_df.loc[i + 1, 'diff_real']))

    ## Getting value mappers
    bands = browser.find_elements_by_xpath("//*[@class='highcharts-plot-band ']")
    last_band_child = str(len(bands) - 4 - 1)
    action = webdriver.ActionChains(browser)
    plot_end = browser.find_element_by_css_selector(
    f".highcharts-plot-bands-1 > .highcharts-plot-band:nth-child({last_band_child})")
    action.move_to_element(plot_end).click().perform()
    val_element = browser.find_element_by_xpath("//*[@class='units sub-headline font-bold']")
    date_element = browser.find_element_by_xpath("//*[@class='tooltip-date sub-headline']")
    val = val_element.text
    date = date_element.text

    print(val, date)
    ## transforming values
    multiplier = float(val.replace(',', '')) / \
                 plot_df[plot_df['dates'] == dt.datetime.strptime(date, '%d %b %Y, %a').date()][1].values[0]
    plot_df[2] = plot_df[1] * multiplier
    print(plot_df.head(10))
    print(plot_df.tail(10))

    ## saving csv
    proj_element = browser.find_element_by_xpath("//*[@class='text-blue-hovered ng-binding ng-scope']")
    stats_list = browser.find_elements_by_xpath("//*[@class='ng-binding ng-scope']")
    ids = [proj_element.text] + [i.text for i in stats_list[1:-1]]
    plot_df.to_csv('./appmagic_data/' + '_'.join(ids) + '_' + csv_name_suffix + '.csv', index=False)
    return None

while True:
    try:
        csv_name_suffix = input('\n type name suffix \n')
        print('you typed: ', csv_name_suffix)
        create_chart_csv(csv_name_suffix)
    except:
        pass