from scraper import ChartsScraper

filename = "dataset.csv"

scraper = ChartsScraper()
scraper.scrape()
scraper.data2csv(filename)
