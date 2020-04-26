import json
import random

questionCards = open('data/questionCards.json', 'r')
answerCards = open('data/answerCards.json', 'r')

questions = json.load(questionCards)
answers = json.load(answerCards)

def getRandomQuestion():
	return questions[random.randint(0,len(questions))]

def getAnswerCards(numOfCards):
	return [answers[random.randint(0,len(answers))] for i in range(numOfCards)]

questionCards.close()
answerCards.close()
