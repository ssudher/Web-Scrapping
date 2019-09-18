# This is a python program to translate mined data from stackExchange and get some kind of insight.

import csv

# Get the existing quora data in CSV format, ASCII encoded. Columns expected are
# Qid, Vote, Views, Person, Reputation, Tags

# scrapeFile = input("Enter full path of the Quora Scrape Data: ")
scrapeFile = r"Q:\SVV_A3\Test_Expert\Workspace\CI Data Science\Scraped Data\Machine.Learning.Stackexchange.txt"

tagView = {}
tagReputation = {}
tagCount = {}
personReputation = {}
personTags = {}
personTagCount = {}
personQViewCount = {}

first = True  # required to ignore the header

with open(scrapeFile, newline='') as csvfile:
    csvReader = csv.reader(csvfile, delimiter='\t', quotechar='|')
    for row in csvReader:
        if first:
            first = False
            continue
        if len(row) != 6:
            continue
        qid, vote, views, person, reputation, fulltag = row
        tags = fulltag.split(' ')

        print(row)

        for tag in tags:
            if tag not in tagView.keys():
                tagView[tag] = int(views)
            else:
                tagView[tag] += int(views)

            if reputation != '':
                if tag not in tagReputation.keys():
                    tagReputation[tag] = int(reputation)
                else:
                    tagReputation[tag] += int(reputation)

            if tag not in tagCount.keys():
                tagCount[tag] = 1
            else:
                tagCount[tag] += 1

            if person != '':
                if person not in personTags.keys():
                    personTags[person] = tag
                else:
                    personTags[person] += ";" + tag

        if reputation != '' and person != '':
            if person not in personReputation.keys():
                personReputation[person] = int(reputation)
            else:
                personReputation[person] += int(reputation)

        if person != '':
            if person not in personQViewCount.keys():
                personQViewCount[person] = int(views)
            else:
                personQViewCount[person] += int(views)

for person in personTags.keys():
    personTagCount[person] = len(personTags[person].split(";"))


print(tagView)
print(tagReputation)
print(tagCount)
print(personReputation)
print(personTags)
print(personTagCount)
print(personQViewCount)


csvfile = open('mlearning_person.csv', 'w', newline='', encoding='utf-8')
fieldnames = ['person', 'reputation', 'tags', 'tagCount', 'qViewCount']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

for person in personTags.keys():
    writer.writerow({'person': person,
                     'reputation': personReputation[person],
                     'tags': personTags[person],
                     'tagCount': str(personTagCount[person]),
                     'qViewCount': personQViewCount[person]})
csvfile.close()

csvfile = open('mlearning_tags.csv', 'w', newline='', encoding='utf-8')
fieldnames = ['tags', 'view', 'reputation', 'count']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

for tag in tagView.keys():
    if tag not in tagReputation.keys():
        temp = -1
    else:
        temp = tagReputation[tag]
    writer.writerow({'tags': tag,
                     'view': tagView[tag],
                     'reputation': temp,
                     'count': tagCount[tag]})
csvfile.close()

