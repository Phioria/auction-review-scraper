from printer import output_to_csv
from scraper import scrape_reviews

def main():
	reviews = scrape_reviews(company="Bidhaus", code="6801")
	output_to_csv(reviews)
	

if __name__ == "__main__":
	main()