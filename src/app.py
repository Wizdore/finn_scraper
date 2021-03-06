from FinnScraper import FinnScraper
from tinydb import table, TinyDB
from Helper import send_message
import pretty_errors
import os
from tqdm import tqdm
from datetime import date

today = date.today()
# dd/mm/YY
todays_date = today.strftime("%d/%m/%Y")

db_path = os.path.split(os.path.realpath(__file__))[0] +'/datastore/house_data.json'

db = TinyDB(db_path)
fs = FinnScraper("https://www.finn.no/realestate/homes/search.html?page={}&published=1&sort=PUBLISHED_DESC")
# fs = FinnScraper("https://www.finn.no/realestate/homes/search.html?page={}")

try:
    finn_codes = fs.get_ad_codes(npages=25, verbose=1)
except Exception as e:
    send_message(f'Error: {str(e)}\n{str(e.__traceback__.tb_frame)}')
    if len(finn_codes) == 0:
        db.close()
        fs.close_driver()
        exit()

ad_counter = 0
for finn_code in tqdm(finn_codes):
    if db.contains(doc_id=finn_code):
        continue

    try:
        ad_dict = fs.parse_housing_page(finn_code)
        ad_dict['scraping_date'] = todays_date
    except Exception as e:
        send_message(f'Error: {str(e)}\n{str(e.__traceback__.tb_frame)}')
        continue

    db.insert(table.Document(ad_dict, doc_id=finn_code))
    ad_counter += 1

send_message(f'Added {ad_counter} new house data\nTotal Data: {len(db)}')

db.close()
fs.close_driver()
