# Credit where it's due:
# https://www.reddit.com/r/Entrepreneur/comments/5frftl/followup_with_script_how_to_scrape_quora_for/

import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
import time

# Replace this with whatever topic page you'd like to scrape
# quoraTopicPage = 'https://www.quora.com/topic/Machine-Learning'
# quoraTopicPage  = 'https://www.quora.com/topic/Formal-Methods'
# quoraTopicsPage = ['https://www.quora.com/topic/Formal-Methods/all_questions', 'https://www.quora.com/topic/Formal-Verification/all_questions',
#                    'https://www.quora.com/topic/Model-Checking/all_questions',
#                    'https://www.quora.com/topic/Simulink/all_questions']
quoraTopicsPage = ['https://www.quora.com/topic/Blockchain-database/all_questions',
                   'https://www.quora.com/topic/Bitcoin/all_questions']

# Set a maximum number of questions to scrape
# numberOfQuestionsToScrape = 2000
numberOfQuestionsToScrape = 2000


def filterSearchResults(resultArray, minViewVolume, minRatio=20):
    '''Takes in an array of questions with stats, returns an array that's filtered'''
    filteredArray = []

    for result in resultArray:
        if (result[2] > minViewVolume) and (result[3] > minRatio):
            filteredArray.append(result)
    return filteredArray


def HTMLNumberToPlain(numberText):
    if '.' in numberText:
        periodIndex = numberText.index('.') + 3
        numberText = numberText.replace('.', '')
        numberText = numberText.replace('k', '')

        if len(numberText) > periodIndex:
            newNumberText = ''
            i = 0
            for ch in numberText:
                if i == periodIndex:
                    newNumberText += '.'
                newNumberText += ch
                i += 1
            return (int(newNumberText))

        else:
            while len(numberText) < periodIndex:
                numberText += '0'
            return (int(numberText))
    elif 'k' in numberText:
        numberText = numberText.replace('k','000')
        return (int(numberText))
    else:
        return int(numberText)


# Initialize webdriver



def scrapeInLoop(quoraTopicPage):
    driver = webdriver.Chrome()
    driver.get(quoraTopicPage)
    wait = WebDriverWait(driver, 30)


    numberOfQuestionsDiv = driver.find_element_by_class_name('TopicQuestionsStatsRow').get_attribute("innerHTML")
    numberOfQuestionsSoup = BeautifulSoup(numberOfQuestionsDiv, 'html.parser').strong.text
    numberOfQuestions = HTMLNumberToPlain(numberOfQuestionsSoup)

    # get div with all questions
    questionDiv = driver.find_element_by_class_name('layout_2col_main')
    questionHTML = questionDiv.get_attribute("innerHTML")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Allow time to update page
    time.sleep(3)

    # get questions again
    questionDiv = driver.find_element_by_class_name('layout_2col_main')
    newQuestionHTML = questionDiv.get_attribute("innerHTML")

    if newQuestionHTML == questionHTML:
        questionsScrapedSoFar = numberOfQuestions
    else:
        soup = BeautifulSoup(newQuestionHTML.encode("utf-8"), 'html.parser')
        questionsScrapedSoFarSoup = soup.find_all('a', class_='question_link')
        questionsScrapedSoFar = 0
        for q in questionsScrapedSoFarSoup:
            questionsScrapedSoFar += 1
        print(questionsScrapedSoFar)

    repeatCount = 0
    # Keep checking if there are new questions after scrolling down
    while (questionsScrapedSoFar < int(0.9 * numberOfQuestions)):
        questionHTML = newQuestionHTML
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        questionDiv = driver.find_element_by_class_name('layout_2col_main')
        newQuestionHTML = questionDiv.get_attribute("innerHTML")

        if newQuestionHTML != questionHTML:
            # Each time you scroll down, 20 more are added
            questionsScrapedSoFar += 10
            repeatCount = 0
            print(questionsScrapedSoFar)
        else:
            repeatCount += 1

        if repeatCount > 10:
            print("Quora stalled after scraping " + str(questionsScrapedSoFar) + " questions")
            break

        if questionsScrapedSoFar > numberOfQuestionsToScrape:
            break

    finalQuestions = questionDiv.get_attribute("innerHTML").encode("utf-8")

    # Get questions as strings
    soup = BeautifulSoup(finalQuestions, 'html.parser')
    questions = soup.find_all('a', class_='question_link')
    questionLinks = []
    for q in questions:
        questionLinks.append(q['href'])

    # Visit each question page to get stats
    questionStats = []

    # Need to add something in here in case quora messes up
    quest_no = 0
    csvfile = open('results.csv', 'a', newline='', encoding='utf-8')
    fieldnames = ['Qid', 'Question', 'Views', 'Answers','AnsweredBy','FullTag']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    i = 1
    for qLink in questionLinks:
        try:
            driver.get('https://www.quora.com' + qLink)

            # Get question text
            questionsText = driver.find_element_by_class_name('rendered_qtext').text.encode("utf-8")

            # Need to get number of answers
            try:
                numberOfAnswersText = driver.find_element_by_class_name('answer_count').text.split(" ")[0].replace(',',
                                                                                                                   '').replace(
                    '+', '')

            except:
                numberOfAnswersText = 1
                continue

            # Need to get number of views
            numberOfViewsText = driver.find_element_by_class_name('meta_num').text

            # Answered by:

            answeredBy = driver.find_elements_by_class_name("feed_item_answer_user")
            answeredByText = ""

            for answer in answeredBy:
                answeredByText = answeredByText + answer.text.split(',')[0] + "$" + ''.join(
                    answer.text.split(',')[1:]) + ";"

            # answeredByInfo = driver.find_elements_by_class_name("ActorNameCredential")
            # answeredByInfoText = ""
            # for byInfo in answeredByInfo:
            #     answeredByInfoText = answeredByInfoText + byInfo.text + ";"

            topicName = driver.find_elements_by_class_name("TopicName")
            topicNameText = ""
            for topic in topicName:
                topicNameText = topicNameText + topic.text + ";"

            # Calculate ratio for sorting
            # viewsToAnswersRatio = float(numberOfViewsText) / float(numberOfAnswersText)

            # questionStats.append([questionsText, float(numberOfAnswersText), float(numberOfViewsText), viewsToAnswersRatio])
            questionStats.append([questionsText, float(numberOfAnswersText), numberOfViewsText, answeredByText,
                                  topicNameText])
            quest_no += 1

            print(quest_no, questionsText)

            writer.writerow(
                {'Qid': i, 'Question': questionsText.decode('utf-8'), 'Views': numberOfViewsText,
                 'Answers': numberOfAnswersText,
                 'AnsweredBy': answeredByText,
                 'FullTag': topicNameText})
            i += 1

        except:
            e = sys.exc_info()
            print("Exception Detail %s" % e)
            continue
    driver.quit()


for topicPage in quoraTopicsPage:
    scrapeInLoop(topicPage)
