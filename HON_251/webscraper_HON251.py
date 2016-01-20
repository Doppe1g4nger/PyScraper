# Daniel Dopp
# danieldopp@uky.edu

# Purpose: given a list of websites, output the words from most to least common
# Preconditions: A text file with a list of URL's to be scraped and two text files containing all english words as well as a text file of stop words
# Postconditions: A text file containing data from individual webpages and a summation of all webpages as well as a 
# text file containing all 'garbage' data

# Import Beautiful Soup to parse html documents and request to retrieve html documents, datetime for timestamps
from bs4 import BeautifulSoup
from urllib import request, error
from datetime import datetime
# Define dictionary sorting function
def dict_sort(dictionary):
	# Create static list to place dict values into
	word_list = []
	# Put dict items into list in value key tuple pairs
	for key, value in dictionary.items():
		word_list.append((value, key))
	# Sort word list from largest to smallest based on first tuple item and return sorted list of tuples
	word_list.sort(reverse = True)
	return word_list
# Define data writing function
def data_write(data_list, file):
	# initialize incrementor for total number of errors encountered
	num_errors = 0
	# for each value and key in a list of tuples, try to write to the given file, if unable to increment error counter
	for value, key in data_list:
		try:
			file.write(str(value) + ' ' + key + '\n')
		except UnicodeEncodeError:
			num_errors += 1
	# Print the number of errors encountered for each write cycle
	print('There were', num_errors, 'UnicodeEncodeErrors encountered for this data set')
# Define main function
def main():
	# Set sites seen counter
	sites_seen = 0
	# Format time data
	current_date = datetime.now().isoformat().replace(':', '-')
	current_date = current_date.replace('.', '-')
	# Create file to store word data in named collated_data_ + current time
	data_file = open('collated_data_' + current_date + '.txt', 'x')
	# Create file to store garbage data in named garbage_ + current time
	garbage_file = open('garbage_' + current_date + '.txt', 'x')
	# Create file to store all words total appearance times for wordcloud generation
	cloud_file = open('cloud_'+ current_date + '.txt', 'x')
	# Open two files containing comprehensive lists of english words, a file containing the websites to be parsed, and a file containing stop words
	wordlist1 = open("wordlist.txt")
	wordlist2 = open('wordsEn.txt')
	websites = open('websites.txt')
	stopwords = open('stopwords.txt')
	# Create dictionary to store sum of all useful english words from all website into and all garbage into
	all_word_dict = {}
	all_garbage_dict = {}
	# Create an empty set to add english words to and an empty set to add stop words to, and a set for seen websites
	stop_words = set()
	english_words = set()
	seen_sites = set()
	# Add stop words from file to set, close file
	for word in stopwords:
		stop_words.add(word.strip().lower())
	stopwords.close()
	# Add all words from first file into set, close file
	for word in wordlist1:
		english_words.add(word.strip().lower())
	wordlist1.close()
	# Add words from second file that were not in first file to set, close file
	for word in wordlist2:
		if not word.strip().lower() in english_words:
			english_words.add(word.strip().lower())
	wordlist2.close()
	# For each website in websites file
	for site in websites:
		# Format website URL
		site = site.strip()
		if site in seen_sites:
			print('Duplicate page skipped')
		else:
			# Create empty dictionary to store usefule english words in and dict to store garbage in
			word_dict = {}
			garbage_dict = {}
			# Try to request website, use browser header identifier to avoid 403 Error
			try:
				webpage = request.Request(site, headers={'User-Agent': 'Mozilla/5.0'})
				# Open requested website
				html = request.urlopen(webpage)
				# Create soup object from opened webpage
				soup = BeautifulSoup(html, 'html.parser')
				# Remove javascript from website data
				for script in soup('script'):
					script.decompose()
				# Create string of all text on the webpage
				soup_string = soup.get_text()
				# Split string into list of words based on whitespace seperation
				words = soup_string.split()
				# For each word in the words list, format, and if english, not a stop word, not empty string, or a number
				# add to word dictionary and all word dictionary, otherwise add to garbage dictionary and all garbage dictionary
				for word in words:
					word = word.strip('.,!?:;\'\"/\\()[]{}#%@$^&*_-+|><').lower()
					if (not word in stop_words) and (word in english_words) and (word != ''):
						word_dict[word] = word_dict.get(word, 0) + 1
						all_word_dict[word] = all_word_dict.get(word, 0) + 1
					else:
						number = True
						for char in word:
							if not char in {'1','2','3','4','5','6','7','8','9','0'}:
								number = False
						if number and word != '':
							word_dict[word] = word_dict.get(word, 0) + 1
							all_word_dict[word] = all_word_dict.get(word, 0) + 1
						else:
							garbage_dict[word] = garbage_dict.get(word, 0) + 1
							all_garbage_dict[word] = all_garbage_dict.get(word, 0) + 1
				# Create list to place sorted dictionary items into
				sorted_words = dict_sort(word_dict)
				# Add heading data to data file
				data_file.write(soup.title.string + '\n' + 'Accessed: ' + datetime.now().isoformat() + '\n' + site + '\n' * 2)
				# Try to place words into file by number of appearances, skip if unable to
				data_write(sorted_words, data_file)
				# Write new line to file for formatting
				data_file.write('\n')
				# Sort garbage file to catch unused words
				sorted_garbage = dict_sort(garbage_dict)
				# Add heading data to garbage file
				garbage_file.write(soup.title.string + '\n' + 'Accessed: ' + datetime.now().isoformat() + '\n' + site + '\n' * 2)
				# Try to place garbage words into file, skip if unable to
				data_write(sorted_garbage, garbage_file)
				# Write new line to garbage file for formatting
				garbage_file.write('\n')
				# Add site to set of sites covered
				seen_sites.add(site)
				# Increment site seen counter
				sites_seen += 1
			# If site can not be opened print error message
			except error.HTTPError:
				print(site, 'could not be opened')
	# Close websites file
	websites.close()
	# Create list to place words from all articles into
	all_sorted_words = dict_sort(all_word_dict)
	# Write message to indicate concatenation
	data_file.write('\nTHE CONCATENATION OF THIS DATA RESULTS IN:' + '\n' * 2)
	# Try to write concatenated data to file, skip if unable to, close file
	data_write(all_sorted_words, data_file)
	data_file.close()
	# Create list to place garbage from all articles into
	all_sorted_garbage = dict_sort(all_garbage_dict)
	garbage_file.write('\nTHE CONCATENATION OF THIS DATA RESULTS IN:' + '\n' * 2)
	# Try to write concatenated garbage to file, skip if unable to, close file
	data_write(all_sorted_garbage, garbage_file)
	garbage_file.close()
	# Write relevant data to wordcloud file, close file
	for appearance, word in all_sorted_words:
		total = (word + ' ') * appearance
		cloud_file.write(total)
	cloud_file.close()
	# Print how many sites were parsed through
	print(sites_seen, 'sites parsed in total')
# Execute main function
main()