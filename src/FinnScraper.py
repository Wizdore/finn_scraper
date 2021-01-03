from bs4 import BeautifulSoup as bs
from selenium import webdriver
import time


class FinnScraper:
    def __init__(self, url):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome('chromedriver', options=chrome_options)
        self.url = url

    def close_driver(self):
        self.driver.quit()


    def get_ad_codes(self, npages=50, verbose=0):
        all_codes = []

        for page_no in range(1, npages+1):
            page_url = self.url.format(page_no)

            self.driver.get(page_url)
            soup = bs(self.driver.page_source, 'html.parser')
            ad_links = soup.find_all('a', attrs={'class': 'ads__unit__link'})
            # Only take id's that are old homes and not project ads
            ad_codes = [int(ad['id']) for ad in ad_links if 'homes' in ad['href'].split('/')]

            if verbose:
                print(f'Indexed: {len(ad_codes)} from {page_url}')

            all_codes.extend(ad_codes)
            time.sleep(0.2)

        return list(set(all_codes))

    def parse_housing_page(self, finn_code):
        ## Getting the raw page
        detail_page = "https://www.finn.no/realestate/homes/ad.html?finnkode={}".format(finn_code)
        self.driver.get(detail_page)
        soup = bs(self.driver.page_source, 'html.parser')

        ad_main = soup.find('div', attrs={"class": "u-word-break"})

        try:
            price = ad_main.find(
                lambda tag: tag.name == 'span' and tag.has_attr('class') and tag['class'] == ['u-t3']).string
        except AttributeError:
            # print(f'No house details found with {finn_code} finncode')
            return

        price = int(''.join(price.split()[:-1]))

        ad_dict = {
            "id": finn_code,
            "title": ad_main.find('h1').string,
            "address": ad_main.find('p', attrs={'class': 'u-caption'}).string,
            "price": price
        }

        ## Parsing number of rooms, bed rooms, total space and other info
        other_features = ad_main.find_all('dl', attrs={'class': 'definition-list'})
        for feature_vec in other_features:
            feature_vec = feature_vec.get_text().split('\n')

            ## basic data cleaning
            feature_vec = [''.join(x.strip()) for x in feature_vec if len(x) > 0]

            if len(feature_vec) < 2:
                continue
            for k, v in zip(feature_vec[0::2], feature_vec[1::2]):
                if len(k) == 0 or len(v) == 0:
                    continue
                ad_dict[k] = v

        facilities = []
        try:
            for item in ad_main.find_all('ul', attrs={'class': 'list'}):
                flts = item.get_text().strip().split('\n')
                for item in flts:
                    item = item.split('/')
                    facilities.extend(item)
        except AttributeError:
            pass
            # ad_dict['facilities'] = None
        else:
            ad_dict['facilities'] = list(set(facilities))

        ## Parsing textual data in the ad body
        more_info = []
        try:
            for paragraph in ad_main.find('div', attrs={"data-controller": "moreKeyInfo"}).find_all('p'):
                for lines in paragraph.get_text().strip():
                    more_info.extend(lines.strip())
        except AttributeError:
            pass

        try:
            for paragraph in ad_main.find('div', attrs={"id": "collapsableTextContent"}).find_all('p'):
                for lines in paragraph.get_text().strip().split('\n'):
                    more_info.extend(lines.strip())
        except AttributeError:
            pass

        if len(more_info) > 5:
            ad_dict['description'] = ''.join(more_info)

        try:  # Get the latitude and longitude from the attached map in the post
            mapinfo = soup.find('a', attrs={"data-controller": "trackMap"})
            lat = mapinfo['href'].split('&')[1].split('=')[1]
            lon = mapinfo['href'].split('&')[2].split('=')[1]
        except AttributeError:
            # print('cant find map')
            pass
        else:
            ad_dict['lat'] = lat
            ad_dict['lon'] = lon

        return ad_dict