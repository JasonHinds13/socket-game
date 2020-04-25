import json

cardFile = open('cards.json','r')
questionCards = open('questionCards.json','w')
answerCards = open('answerCards.json','w')

all_data = json.load(cardFile)
question_data = []
answer_data = []

for data in all_data:
    if data['cardType'] == "A":
        answer_data.append(data)
    elif data['cardType'] == "Q":
        question_data.append(data)

questionCards.write(json.dumps(question_data))
answerCards.write(json.dumps(answer_data))

cardFile.close()
questionCards.close()
answerCards.close()
