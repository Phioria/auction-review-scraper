from cleaner import clean_reviews
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def scrape_reviews(company, code):
	if not isinstance(company, str):
		raise TypeError("Argument `company` expects a string")
	# Technically, code should be a string representation of a number.
	# We'll just pass it in as a string so there's no need to cast
	if not isinstance(code, str):
		raise TypeError("Argument `code` expects a string")
	
	driver = selenium_init()
	reviews = scrape_liveauctioneers(company=company, code=code, driver=driver)
	return reviews


# This function expects the webdriver executable to be present in the same directory as this function
def selenium_init():
	_WEBDRIVER = "chromedriver.exe"
	options = Options()
	options.add_argument("--headless")
	service = Service(executable_path=_WEBDRIVER)
	driver = webdriver.Chrome(options=options, service=service)
	return driver

def scrape_liveauctioneers(company, code, driver):
	BASEURL = "https://www.liveauctioneers.com/auctioneer"
	TARGET_URL = f"{BASEURL}/{code}/{company}/reviews"

	# Load the page
	driver.get(TARGET_URL)
	wait = WebDriverWait(driver, 10) # 10 seconds max wait
	wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="catalogDesktopReviewCard"]')))
	wait_for_reviews_to_stabilize(driver)

	all_reviews = []

	# Scrape and add reviews from the first page
	#all_reviews.extend(extract_reviews(driver))
	all_reviews.extend(extract_reviews(driver))

	# Navigate through additional pages and scrape
	while True:
		try:
			# Find the 'Next' button and click it
			next_button = driver.find_element(By.XPATH, '//a[contains(@aria-label, "Next Page")]')
			driver.execute_script("arguments[0].click();", next_button)
			wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="catalogDesktopReviewCard"]')))
			wait_for_reviews_to_stabilize(driver)
			all_reviews.extend(extract_reviews(driver))
		except:
			# If we can't find the "Next" button, then we were already on the last page
			break
	
	driver.quit()
	
	# Clean reviews before returning
	cleaned_reviews = clean_reviews(all_reviews)
	return cleaned_reviews


# This function extracts reviews from the current page
# Since liveauctioneers uses pagination, this will allow
# Us to iteratively scrape all reviews
def extract_reviews(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
	# Note that the data-testid disappears at a mobile breakpoint
	# Won't be a problem here, just something to keep in mind for other applications
    review_elements = soup.find_all(attrs={'data-testid': 'catalogDesktopReviewCard'})
    reviews = [review.get_text(separator=" ", strip=True) for review in review_elements]
    return reviews

# def extract_reviews_and_stars(driver):
# 	soup = BeautifulSoup(driver.page_source, "html.parser")
# 	review_elements = soup.find_all(attrs={'data-testid': 'catalogDesktopReviewCard'})
# 	review_data = []
# 	for el in review_elements:
# 		review = el.get_text(strip=True)
# 		stars = el.find_all("svg", attrs={'data-icon': "star"})
# 		filled_stars = [s for s in stars if 'wKGHl' in s.get('class', [])]
# 		rating = len(filled_stars)
# 		current_data = {
# 			"text": review,
# 			"rating": rating
# 		}
# 		review_data.append(current_data)

# 	return review_data

def infer_stars(star_elements, polarity):
	# I have run into a road block getting the actual star rating from these reviews
	# It is based on svg fill color, but the only way I've been able to single out
	# different star states is using classes present. The class names are never
	# the same, though, so this isn't super useful.
	# The basic idea of this function is to infer the number of stars based on
	# The class name changes from star to star along with sentiment analysis.
	# We know that if the first star has one color class, and the second star
	# has a different color class, then the first one is an actual star and the
	# second and all following are not stars.
	# The only cases where this is a problem are when there are zero stars or five stars.
	# Since these are polar opposites in sentiment, a simple sentiment analysis should reveal if it is
	# zero or 5 stars.
	# At the end of the day, this might not even be that useful.
	# Knowing if the review was positive or negative might be enough, and we don't need the star count
	# for that.
	num_stars = 0
	fill_classes = []
	for star in star_elements:
		star_classes = star.get('class', [])
		fill_class = star_classes[3]
		fill_classes.append(fill_class)
	num_unique_classes = len(list(set(fill_classes)))
	
	# If we have 2 color classes, then we can easily calculate the number of stars
	if num_unique_classes == 2:
		print('asdf')
		first_class = fill_classes[0]
		num_stars = fill_classes.count(first_class)
	elif num_unique_classes == 1: # In this case we'll have to rely on sentiment analysis
		if polarity > 0:
			num_stars = 5
	else:
		Warning(f"Star element had {num_unique_classes} color classes but expected 1 or 2.")
	return num_stars


# After updating the code to use explicit wait conditions, some reviews weren't being captured
# This function aims to solve this issue
def wait_for_reviews_to_stabilize(driver, poll_interval=0.5, max_wait=10):
    start_time = time.time()
    last_count = 0

    while True:
        current_count = len(driver.find_elements(By.CSS_SELECTOR, '[data-testid="catalogDesktopReviewCard"]'))
        if current_count == last_count and current_count > 0:
            break
        last_count = current_count
        if time.time() - start_time > max_wait:
            print("Warning: timeout while waiting for reviews to stabilize")
            break
        time.sleep(poll_interval)
