from backend.offer_up_scraper import OfferUpScraper
from multiprocessing import Pool

def run_scraper(args):
    shoe_type, distance, delivery_method, zipcode, price_percentage_evaluation, reference_price = args
    scraper = OfferUpScraper(shoe_type, distance, delivery_method, zipcode, price_percentage_evaluation, reference_price)
    scraper.run()
    scraper.save_to_excel()

def run_multiple_scrapers(scraper_args_list):
    with Pool(processes=len(scraper_args_list)) as pool:
        pool.map(run_scraper, scraper_args_list)

if __name__ == "__main__":
    scraper_args_list = [
        ("nike air force 1", 10, "p", 94613, "0.2", 100),
        ("nike air jordan 4", 10, "p", 94613, "0.2", 100),
    ]
    run_multiple_scrapers(scraper_args_list)


