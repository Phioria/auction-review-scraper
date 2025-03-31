from datetime import datetime
import nltk
from nltk.corpus import stopwords
import re
import pandas as pd
from plotter import get_text_polarity

def clean_reviews(reviews):
	# Review text is in this basic format:
	# NameCity, StateAbbMonth Date, YYYYBody
	# It's an odd format. Let's first split on commas and only keep everything after the 2nd comma
	# Then lets drop the first 5 characters of each review which would be a space and the year.
	# Okay there are some issues here. In some cases the body of the text isn't after 2 commas
	# These cases seem to be when the auction company replies to reviews
	# New plan, split using the year. The first year a review existed for Bidhaus was 2019,
	# So we'll need to split on ", 20" to capture 2019 along with the 202x's
	# We will check to see if there is more than one occurance of ", 20" in the string
	# If so, it doesn't really change the downstream processing. Index 1 will still be the actual review
	# Index 2 would be the BidHaus review if we wanted it.
	# If there's only 1 occurance, then we can take the 2nd element of the split and
	# slice off the first three characters which would be the last two numbers in the year and a space
	# Then check the length of the string, if it's empty, skip this observation
	# Otherwise append

	# Download stopwords for later use in cleaning
	prep_nltk()

	cleaned_reviews = []
	for review in reviews:
		clean_review = review.split(sep=", 20", maxsplit=2)

		review_date = extract_date(clean_review)

		# Keep the 2nd element of the list which holds the review
		clean_review = clean_review[1]

		# In some cases, reviewers leave no comments, but BidHaus does comment
		# We should skip these
		# Format: YY Bidhaus Mmm DD
		if len(clean_review) == 17 and clean_review[3:10] == "Bidhaus":
			continue

		# Slice off the first 3 characters
		clean_review = clean_review[3:]
		# If the review has no text, then skip it
		if len(clean_review) == 0:
			continue

		clean_review = clean_review.lower()
		clean_review = remove_suffix(clean_review)

		sentiment_review = clean_for_sentiment(clean_review)
		polarity = get_text_polarity(sentiment_review)

		review_dict = {
			"date": review_date,
			"polarity": polarity,
			"text": clean_review	
		}

		cleaned_reviews.append(review_dict)
	
	review_df = pd.DataFrame(cleaned_reviews)
	return review_df


# Remove extraneous words and characters for sentiment analysis
def clean_for_sentiment(review):
	stop_words = set(stopwords.words('english'))
	review = re.sub(r'http\S+', ' ', review) # Remove URLs
	review = re.sub(r'[^A-Za-z\s]', ' ', review) # Remove special characters
	review = ' '.join(word for word in review.split() if word not in stop_words)
	return review

def clean_for_sentiment_bulk(reviews):
	cleaned_reviews = []
	for review in reviews:
		cleaned_reviews.append(clean_for_sentiment(review))
	return(cleaned_reviews)


# Remove the suffix of each review that states how helpful it was to others
def remove_suffix(review):
	helpful_idx = review.rfind("helpful")
	clean_review = review[:helpful_idx]
	return clean_review

def remove_suffix_bulk(reviews):
	cleaned_reviews = []
	for review in reviews:
		cleaned_reviews.append(remove_suffix(review))
	return cleaned_reviews


def extract_date(review):
	# Extract the date from both the first a second elements
	# Confirmed that all months use 3 characters and all dates use 2 characters
	# So the last 6 characters will always comprise the month and date
	month_date = review[0][-6:]
	month = month_date[:3]
	month = convert_month_abbr(month)
	date = month_date[-2:]
	year_prefix = "20"
	year_suffix = review[1][:2]
	year = year_prefix + year_suffix
	review_date = f"{year}-{month}-{date}"
	return review_date

# Expects a 3 character month abbreviation and returns a 2 digit month (in str format)
def convert_month_abbr(month):
	return(str(datetime.strptime(month, "%b").month).zfill(2))

# Ensure that stopwords have been downloaded
def prep_nltk():
	nltk.download("stopwords")
