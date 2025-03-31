import matplotlib.pyplot as plt
from textblob import TextBlob
from wordcloud import WordCloud

def get_text_polarity(review):
	blob = TextBlob(review)
	polarity = blob.sentiment.polarity
	return polarity

def generate_sentiment(reviews):
	positive_reviews = []
	neutral_reviews = []
	negative_reviews = []

	for review in reviews:
		blob = TextBlob(review)
		polarity = blob.sentiment.polarity
		if polarity > 0:
			positive_reviews.append(review)
		elif polarity < 0:
			negative_reviews.append(review)
		else:
			neutral_reviews.append(review)
	
	split_results = {
		"Positive":	positive_reviews,
		"Negative": negative_reviews,
		"Neutral": neutral_reviews
	}

	return split_results

def generate_wordcloud(text):
	wordcloud = WordCloud(width=800, height=400, background_color="white", collocations=False).generate(text)
	return(wordcloud)

def plot_wordcloud(wordcloud, title):
	plt.figure(figsize=(12, 6))
	plt.imshow(wordcloud, interpolation="bilinear")
	plt.axis("off")
	plt.title(title)
	plt.show()
