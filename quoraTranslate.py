# This is a python program to translate mined data from quora and get some kind of insight.

import csv

# Get the existing quora data in CSV format, ASCII encoded. Columns expected are
# Qid, Question, Views, Answers, AnsweredBy, FullTag.

# scrapeFile = input("Enter full path of the Quora Scrape Data: ")
scrapeFile = r"Q:\SVV_A3\Test_Expert\Workspace\CI Data Science\Scraped Data\Quora_Scrape_New.txt"

tagDictionary = {}
peopleDictionary = {}
peopleProfile = {}
peopleTags = {}
peopleTagRank = {}
peopleTagCount = {}
tagView = {}
tagAnswer = {}
first = True
with open(scrapeFile, newline='') as csvfile:
    csvReader = csv.reader(csvfile, delimiter='\t', quotechar='|')
    for row in csvReader:
        if first:
            first = False
            continue
        qid, question, views, answers, answeredby, fulltag = row
        tags = fulltag.split(';')
        if '' in tags:
            tags.remove('')
        for tag in tags:
            if tag not in tagView.keys():
                if views[-1:] == 'k':
                    tagView[tag] = float(views[:-1])* 1000
                else:
                    tagView[tag] = float(views)
            else:
                if views[-1:] == 'k':
                    tagView[tag] += float(views[:-1])* 1000
                else:
                    tagView[tag] += float(views)

            if tag not in tagAnswer.keys():
                tagAnswer[tag] = int(answers)
            else:
                tagAnswer[tag] += int(answers)
            if tag not in tagDictionary.keys():
                tagDictionary[tag] = 1
            else:
                tagDictionary[tag] += 1
        answerby = answeredby.split(';')
        #print(qid)
        for answers in answerby:
            if answers == '':
                continue
            if len(answers.split('$')) == 2:
                person = answers.split('$')[0]
                profile = answers.split('$')[1]
            else:
                person = answers.split('$')[0]

            if person == '':
                continue

            if person not in peopleProfile.keys():
                peopleProfile[person] = profile
            else:
                if peopleProfile[person] != profile:
                    peopleProfile[person] += "**"+profile

            if person not in peopleDictionary.keys():
                peopleDictionary[person] = 1
            else:
                peopleDictionary[person] += 1
            if '' in tags:
                tags.remove('')

            if person not in peopleTags.keys():
                peopleTags[person] = set(tags)
            else:
                peopleTags[person].union(set(tags))


maxTagValue = max(tagDictionary.values())

for person in peopleTags.keys():
    peopleTagCount[person] = len(peopleTags[person])
    rank = 0
    for tag in peopleTags[person]:
         rank += maxTagValue + 1 - tagDictionary[tag]
    peopleTagRank[person] = rank

print(peopleProfile)
print(peopleDictionary)
print(peopleTags)
print(peopleTagCount)
print(peopleTagRank)
print(tagView)
print(tagAnswer)
print(tagDictionary)

csvfile = open('person.csv', 'w', newline='', encoding='utf-8')
fieldnames = ['person', 'profile', 'answerCount', 'answerTags', 'answerTagCount', 'answerTagRank' ]
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

for person in peopleProfile.keys():
    writer.writerow({'person': person,
                    'profile': peopleProfile[person],
                    'answerCount': peopleDictionary[person],
                    'answerTags': str(peopleTags[person]),
                    'answerTagCount': peopleTagCount[person],
                    'answerTagRank': peopleTagRank[person]})
csvfile.close()

csvfile = open('tags.csv', 'w', newline='', encoding='utf-8')
fieldnames = ['tags', 'views', 'answered', 'count']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

for tag in tagDictionary.keys():
    writer.writerow({'tags': tag,
                    'views': tagView[tag],
                    'answered': tagAnswer[tag],
                    'count': tagDictionary[tag]})
csvfile.close()

#
# with open(scrapeFile, newline='') as csvfile:
#     csvReader = csv.reader(csvfile, delimiter='\t', quotechar='|')
#     tagRank = 0
#     first = True
#     for row in csvReader:
#         if first:
#             first = False
#             continue
#         qid, question, views, answers, answeredby, fulltag = row
#         tags = fulltag.split(';')
#         if '' in tags:
#             tags.remove('')
#         for tag in tags:
#             tagRank = maxTagValue + 1 + tagRank - tagDictionary[tag]
#         #print(tagRank)
#         tagRank = 0
