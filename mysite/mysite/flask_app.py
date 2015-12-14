from flask import Flask, request, url_for, render_template
import wikipedia
import nltk
from difflib import SequenceMatcher

app = Flask(__name__)
app.secret_key = 'This is really unique and secret'

@app.route('/')
def hello_person():
    return render_template('index.html') % (url_for('answer'),)
'''
    return """
        <head>
            <link href="http://fonts.googleapis.com/css?family=Raleway:400,200,500,600,700,800,300" rel="stylesheet" />
            <link href="default.css" rel="stylesheet" type="text/css" media="all" />
            <link href="fonts.css" rel="stylesheet" type="text/css" media="all" />
        </head>
        <body>
        <p>What Middle School Who, Where, When question do you have?</p>
        <form method="POST" action="%s"><input name="person" /><input type="submit" value="Go!" /></form>
        """ % (url_for('answer'),)
'''
@app.route('/answer', methods=['POST'])
def answer():
    originalQuestion = request.form["name"]
    questionToken = ""
    questionType = ""
    questionTag =  ""
    searchPhrase = ""

    questionToken = nltk.word_tokenize(originalQuestion)
    questionType = questionToken[0]  # Get the type of question Who, Where, When
    questionTag = nltk.pos_tag(questionToken)
    searchPhrase = createSearchPhrase(questionTag)
    result = searchWikipedi(searchPhrase)
    content = result.content
    modContent = content.replace("==","<br>")
    return render_template('answer.html') % (originalQuestion, result.title, modContent, url_for('hello_person'))
    '''
    if (questionType.lower() == "where"):
        theAnswer = findAnswer(content, searchPhrase)
        return render_template('answer.html') % (originalQuestion, result.title, theAnswer, url_for('hello_person'))
    else:
         return render_template('answer.html') % (originalQuestion, result.title, modContent, url_for('hello_person'))
    '''

#Create the phrase to search for Article on Wikipedia
def createSearchPhrase(questionTag):
	phrase = ""
	for tag in questionTag:
		#check type of word. If it is a word we want to search add to phrase
		if tag[1] == 'JJ' or tag[1] == 'NN' or tag[1] == 'VBN' or tag[1] == 'NNS' or tag[1] ==  'NNP':
			phrase += ' '
			phrase += tag[0]

	return phrase

def searchWikipedi(searchString):
	suggestion = wikipedia.suggest(searchString)
	if suggestion == None:
		searchResult = wikipedia.search(searchString, 20)
	else:
		searchResult = wikipedia.search(suggestion)
	try:
	    page = wikipedia.page(searchString, None, False, True, False)
	except wikipedia.exceptions.PageError:
	    bestArticle = evaluateSearchResults(searchResult, searchString)
	    page = wikipedia.page(bestArticle)
	return page


def evaluateSearchResults(searchResult, searchString):
	highestSimilarity = 0

	for result in searchResult:
		similiarity = 0
		similiarity = SequenceMatcher(None,result,searchString).ratio() * 100  #title similiarity
		try:
			summary = wikipedia.summary(result, 20)
			summary = summary.replace(".", " ")
			for word in searchString.split(" "):
				similiarity += summary.lower().split().count(word) #keyword first 20 sentences
				similiarity += result.lower().split().count(word) #keyword title
			if similiarity > highestSimilarity:
				bestArticle = result
				highestSimilarity = similiarity
		except wikipedia.exceptions.DisambiguationError as e:
		    if len(e.options) < 5:
    			for subOptions in e.options:
    				searchResult.append(subOptions)
		except wikipedia.exceptions.PageError as e:
			x = 1
	return bestArticle

def findAnswer(content, searchString):
    bestAnswer = ""
    highestAnswer = 0
    for sentence in content.split("."):
        curScore = 0
        tokenize = nltk.word_tokenize(sentence)
        tag = nltk.pos_tag(tokenize)
        for chunk in nltk.ne_chunk(tag):
            if hasattr(chunk, 'node'):
                if chunk.node == 'LOCATION':
                    for word in searchString.split(" "):
				        curScore += sentence.lower().split().count(word) #keyword first 20 sentences
				        if curScore > highestAnswer:
				            bestAnswer = sentence
				            highestAnswer = curScore
	return bestAnswer
