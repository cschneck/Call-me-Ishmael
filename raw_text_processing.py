###########################################################################
# Pre-processing raw text

# Date: November 2017
###########################################################################
import os
import re
import nltk # Natural Language toolkit
from nltk.tokenize import sent_tokenize, word_tokenize # form tokens from words/sentences
import string
########################################################################
## READING AND TOKENIZATION OF RAW TEXT (PRE-PROCESSING)

basic_pronouns = "I Me You She He Him It We Us They Them Myself Yourself Himself Herself Itself Themselves My your Her Its Our Their His"

def readFile(filename):
	file_remove_extra = []
	with open(filename, "r") as given_file:
		string_words = given_file.read()
		string_words = string_words.replace("\n", " ")
		string_words = string_words.replace(";" , " ")
		string_words = string_words.replace("--", " ")
		string_words = string_words.replace("Mr.", "Mr") # period created breaks when spliting
		string_words = string_words.replace("Ms.", "Ms")
		string_words = string_words.replace("Mrs.", "Mrs")
		string_words = string_words.replace("Dr.", "Dr")
		string_words = re.sub(r'[\x90-\xff]', '', string_words, flags=re.IGNORECASE) # remove unicode
		string_words = re.sub(r'[\x80-\xff]', '', string_words, flags=re.IGNORECASE) # remove unicode
		file_remove_extra = string_words.split(' ')
		file_remove_extra = filter(None, file_remove_extra) # remove empty strings from list
	return file_remove_extra

def tokenizeSentence(string_sentence):
	'''EXAMPLE
	{60: 'After rather a long silence, the commander resumed the conversation.'}
	'''
	tokens_sentence_dict = {} # returns dict with {token location in text #: sentence}
	tokens_sent = string_sentence.split('.')
	for i in range(len(tokens_sent)):
		if tokens_sent[i] != '':
			tokens_sentence_dict[i] = tokens_sent[i].strip() #adds to dictionary and strips away excess whitespace
	#print(tokens_sentence_dict)
	return tokens_sentence_dict

def partsOfSpeech(token_dict):
	'''EXAMPLE
	60: ('After rather a long silence, the commander resumed the conversation.', 
	[('After', 'IN'), ('rather', 'RB'), ('a', 'DT'), ('long', 'JJ'), ('silence', 'NN'),
	 (',', ','), ('the', 'DT'), ('commander', 'NN'), ('resumed', 'VBD'), ('the', 'DT'), 
	 ('conversation', 'NN'), ('.', '.')])}
	'''
	from subprocess import check_output
	for key, value in token_dict.iteritems():
		no_punc = value.translate(None, string.punctuation) # remove puncuation from part of speech tagging
		print(value)
		print("./3_run_text.sh '{0}'\n".format(value))
		result = check_output(["echo", "hello world"])
		print(result)
		pos_tagged = check_output(["./3_run_text.sh", value])
		print(pos_tagged)
		if "docker not running, required to run syntaxnet" not in pos_tagged:
			pos_tagged = process_POS_conll(pos_tagged) # process conll output from shell
			print(pos_tagged)
			token_dict[key] = (value, pos_tagged) # adds part of speech tag for each word in the sentence
		else:
			print("\n\tWARNING: docker not running, cannot run syntaxnet for POS, exiting")
			exit()
	return token_dict

def process_POS_conll(conll_output):
	pos_processed = conll_output
	start_data = 0
	print("PROCESS FUNCTION")
	#or i in range(len(conll_output)):
	#	if conll_output[i] == 'INFO:tensorflow:Seconds elapsed in evaluation:':
	#		start_data = i # save the index of the start of the data (typically 102)
	#pos_processed = graph_data[start_data+2:] # splice all data for just the graphable data (+2 to not include 'DATA:') 
	return pos_processed

def mostCommonPronouns(raw_text):
	# returns a dictionary of the most common pronouns in the text with their occureance #
	#{'it': 1291, 'him': 213, 'yourself': 16, 'his': 519, 'our': 292, 'your': 122}

	pronoun_common = {}
	from collections import Counter

	raw_words = re.findall(r'\w+', raw_text)

	total_words = [word.lower() for word in raw_words]
	word_counts = Counter(total_words)
		
	tag_pronoun = ["PRP", "PRP$"]

	for word in word_counts:
		captilize_options = [word.capitalize(), word.lower()] # dealing with ME seen as NN instead of PRP
		for options in captilize_options:
			if nltk.pos_tag(nltk.word_tokenize(options))[0][1] in tag_pronoun: # if word is a pronoun, then store it
				if options.lower() in basic_pronouns.lower().split():
					pronoun_common[word.lower()] = word_counts[word]

	# testing that it found the right pronouns (not in basic_pronouns)
	#if len(pronoun_common.keys()) != len(basic_pronouns.lower().split()):
	#	for found in pronoun_common.keys():
	#		if found not in basic_pronouns.lower().split():
	#			print("\n\tWARNING: INCORRECT PRONOUNS FOUND ==> {0}\n".format(found))

	return pronoun_common

def indexPronoun(token_dict, pronoun_dict):
	# stores pronoun and location in sentence for each sentence
	#{0: (['I'], [8]), 1: (['my', 'me'], [3, 21]), 2: (['I'], [5])}

	index_pronoun_dict = {}
	pronouns_in_txt = pronoun_dict.keys()
	for index, sentence in token_dict.iteritems():
		pronoun_in_sentence = []
		pronoun_location = []
		#print("sentence # {0}".format(index))
		#print(sentence.split())
		for word_index in range(len(sentence.split())):
			if sentence.split()[word_index].lower() in pronouns_in_txt:
				#print("pronoun ----> {0}".format(sentence.split()[word_index]))
				pronoun_in_sentence.append(sentence.split()[word_index])
				pronoun_location.append(word_index)
		index_pronoun_dict[index] = (pronoun_in_sentence, pronoun_location)
	#print("\ntotal pronouns to find = {0}".format(sum(pronoun_dict.values())))
	#print("total pronouns found = {0}".format(sum(len(value) for key, value in index_pronoun_dict.items())))
	return index_pronoun_dict

def indexProperNoun(token_dict):
	# stores noun and location in sentence for each sentence
	pass

########################################################################
## Output data into csv
def outputCSV(filename, token_sentence_dict, pronouns_dict):
	given_file = os.path.basename(os.path.splitext(filename)[0]) # return only the filename and not the extension
	output_filename = "{0}_data.csv".format(given_file.upper())
	import csv
	with open(output_filename, 'w+') as txt_data:
		fieldnames = ['sentence_index', 'sentence', 'pronouns', 'pronouns_index']
		writer = csv.DictWriter(txt_data, fieldnames=fieldnames)
		writer.writeheader() 
		for index in range(len(token_sentence_dict)):
			writer.writerow({'sentence_index': index, 'sentence': token_sentence_dict[index], 'pronouns': str(pronouns_dict[index][0]).strip("[]"), 'pronouns_index': str(pronouns_dict[index][1]).strip("[]")})
	print("CSV output saved as {0}".format(output_filename))

########################################################################
## Parse Arguments, running main

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description="flag format given as: -F <filename>")
	parser.add_argument('-F', '-filename', help="filename from Raw_Text directory")
	args = parser.parse_args()

	filename = args.F

	if filename is None:
		print("\n\tWARNING: File not given to tokenize, exiting...\n")
		exit()

	tokens_in_order = readFile(filename)
	tokens_as_string = " ".join(tokens_in_order)
	tokens_as_string = tokens_as_string.translate(None, "\r")

	# return the most common pronouns in the text (TODO: Automate)
	most_common_pronouns_dict = mostCommonPronouns(tokens_as_string)
	#print(most_common_pronouns_dict)
	#print("\n")
	
	token_sentence_dict = tokenizeSentence(tokens_as_string)
	#print(token_sentence_dict) # TODO: switch to namedTuples

	pronouns_dict = indexPronoun(token_sentence_dict, most_common_pronouns_dict)
	print(pronouns_dict)
	# save output to csv
	#outputCSV(filename, token_sentence_dict, pronouns_dict)

	dict_parts_speech = partsOfSpeech(token_sentence_dict)
	print("\n")
	print(dict_parts_speech)
	
	#TODO Next: import local file to predict male/female (he/she) with a given list of names
	#x number of sentences around to find proper noun
	#from sklearn.externals import joblib # save model to load
	#loaded_gender_model = joblib.load('name_preprocessing/gender_saved_model_0.853992787223.sav')
	#test_name = ["Nemo"]
	#print(loaded_gender_model.score(test_name))
	#run gender tag once on the entire text, tag male/female and use for predictions
