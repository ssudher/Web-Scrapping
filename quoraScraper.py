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
quoraTopicPage = 'https://www.quora.com/topic/Machine-Learning'

# Put your email and password in these variables, make sure to have the quotation marks around them
yourEmailAddress = "udpsunil1@gmail.com"
yourPassword = "###"

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
    else:
        return int(numberText)


# Initialize webdriver
driver = webdriver.Chrome()
driver.get(quoraTopicPage)
wait = WebDriverWait(driver, 30)

# Find sign-in by Google button and click it
#elem = driver.find_element_by_class_name("google_button")
#elem.click()
#time.sleep(2)
#window_before = driver.window_handles[0]
#window_after = driver.window_handles[1]

# Switch to login popup
#time.sleep(3)
#driver.switch_to_window(window_after)

# Enter Email address and submit
#emailInput = driver.find_element_by_xpath("//input[@id='Email']")
#emailInput.send_keys(yourEmailAddress)
#emailSubmit = driver.find_element_by_class_name("rc-button-submit").click()

#wait.until(EC.presence_of_element_located((By.ID, "Passwd")))

# Enter Password and submit
#pwInput = driver.find_element_by_xpath("//input[@id='Passwd']")
#pwInput.send_keys(yourPassword)
#pwSubmit = driver.find_element_by_id("signIn").click()

#time.sleep(10)
# Manually put in 2FA code here

# need to switch to first window again
#driver.switch_to_window(window_before)

# need to wait for original window to update
#wait.until(EC.presence_of_element_located((By.CLASS_NAME, "HomeMainFeedHeader")))

# navigate to topic page
## driver.get(quoraTopicPage)

# find total number of questions
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
csvfile = open('results.csv', 'w', newline='', encoding='utf-8')
fieldnames = ['Question', 'Views', 'Answers', 'answeredBy', 'topic name']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

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

        # Need to get number of views
        numberOfViewsText = driver.find_element_by_class_name('meta_num').text

        # Answered by:

        answeredBy = driver.find_elements_by_class_name("feed_item_answer_user")
        answeredByText = ""

        for answer in answeredBy:
            answeredByText = answeredByText + answer.text.split(',')[0]+ "$"+''.join(answer.text.split(',')[1:])+";"

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

        #questionStats.append([questionsText, float(numberOfAnswersText), float(numberOfViewsText), viewsToAnswersRatio])
        questionStats.append([questionsText, float(numberOfAnswersText), numberOfViewsText, answeredByText,
                              topicNameText ])
        quest_no += 1

        print(quest_no, questionsText)



        writer.writerow({'Question': questionsText.decode('utf-8'), 'Answers': numberOfAnswersText, 'Views': numberOfViewsText,
                         'answeredBy': answeredByText,
                         'topic name': topicNameText})



    except:
        e = sys.exc_info()
        print("Exception Detail %s" %e)

#sortedQuestionStats = sorted(filterSearchResults(questionStats, 100), key=lambda question: question[3], reverse=True)
sortedQuestionStats = questionStats

# Close the window
driver.quit()
#driver.close()

# Export data to CSV file in same location as this file
# results = []
# with open('results.csv', 'w', newline='', encoding='utf-8') as csvfile:
#     fieldnames = ['Question', 'Views', 'Answers', 'answeredBy', 'answered By Information', 'topic name']
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#     writer.writeheader()
#     for line in sortedQuestionStats:
#         #writer.writerow({'Question': line[0].decode('utf-8'), 'Answers': str(line[1]), 'Views': str(line[2]),'Views to Answers Ratio': str(line[3])})
#
#         writer.writerow({'Question': line[0].decode('utf-8'), 'Answers': str(line[1]), 'Views': str(line[2]),
#                          'answeredBy': str(line[3]),
#                          'answered By Information': str(line[4]),
#                          'topic name': line[5]})


