from FinnScraper import FinnScraper
from tinydb import table, TinyDB
from Helper import send_message
import pretty_errors

db = TinyDB('datastore/house_data.json')
fs = FinnScraper("https://www.finn.no/realestate/homes/search.html?page={}&published=1&sort=PUBLISHED_DESC")
# fs = FinnScraper("https://www.finn.no/realestate/homes/search.html?page={}")
finn_codes = fs.get_ad_codes(npages=25, verbose=1)

ad_counter = 0
for finn_code in finn_codes:
    if db.contains(doc_id=finn_code):
        continue

    try:
        ad_dict = fs.parse_housing_page(finn_code)
    except Exception as e:
        send_message(f'Error: {str(e)}\n{str(e.__traceback__.tb_frame)}')
        continue

    db.insert(table.Document(ad_dict, doc_id=finn_code))
    ad_counter += 1

send_message(f'Added {ad_counter} new house data\nTotal Data: {len(db)}')

db.close()
fs.close_driver()