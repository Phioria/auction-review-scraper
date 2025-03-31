from datetime import datetime
import pprint

def print_reviews(reviews):
	pprint(reviews)

def print_num_reviews(reviews):
	print(f"Scraped {len(reviews)} reviews.\n")

def output_to_csv(reviews):
	current_time = datetime.now()
	timestamp_string = current_time.strftime("%Y%m%d_%H%M%S")
	filename = f"bidhaus_reviews_{timestamp_string}.csv" 
	reviews.to_csv(filename, index=False)
	n_reviews = len(reviews)
	print(f"{n_reviews} reviews written to {filename}")
