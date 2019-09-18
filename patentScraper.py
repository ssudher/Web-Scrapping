# -*- coding: utf-8 -*-
import csv
import RAKE
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

# get patent list from a csv file assuming third column is the patent link.

patent_set = set([])

# csvfile = open('patent_search.csv', 'r')
csvfile = open('c:\\users\\e533268\\desktop\\patent\\SoftwareTesting_Matlab_VCast_Ldra.csv', 'r', encoding='utf-8')
fields = ['id', 'title', 'assignee', 'inventor/author', 'priority date', 'filing/creation date', 'publication date',
          'grant date', 'result link']
reader = csv.DictReader(csvfile, fieldnames=fields)
first = True
for row in reader:
    if first:
        first = False
        continue
    else:
        patent_set.add(row['result link'])

csvfile.close()
total_patents = len(patent_set)
index = 1
# csvfile = open('patents.csv', 'w', newline='', encoding='utf-8')
csvfile = open('c:\\users\\e533268\\desktop\\patent\\SoftwareTesting_Matlab_VCast_Ldra_Abstract.csv', 'w', newline='',
               encoding='utf-8')
fieldnames = ['patent_id', 'title', 'patent_link', 'authors', 'abstract', 'tags']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

# Initialize webdriver
driver = webdriver.Chrome()

for patentPage in patent_set:
    # Replace this with whatever topic page you'd like to scrape
    # patentPage = 'https://patents.google.com/patent/US8561177B1/en'
    print("scraping {0} of {1}".format(index, total_patents))
    index += 1
    print(patentPage)
    driver.get(patentPage)
    wait = WebDriverWait(driver, timeout=30, poll_frequency=5)
    # navigate to topic page

    # find total number of questions
    patent_id = driver.find_element_by_xpath("//*[name()='h2']").text
    try:
        abstract = driver.find_element_by_class_name('abstract').get_attribute("innerHTML")
    except Exception:
        print("Unable to fetch abstract for patent_id:" + patent_id)
        abstract = "Not Available"

    authors = driver.find_element_by_class_name('important-people').text.split('Current Assignee')[0]
    title = driver.find_element_by_id('title').text
    Rake = RAKE.Rake(".\\SmartStoplist.txt")
    tags = Rake.run(abstract)

    #print(patent_id)
    #print(abstract)
    #print(authors)
    #print(title)

    writer.writerow({'patent_id': patent_id,
                     'title': title,
                     'patent_link': patentPage,
                     'authors': authors,
                     'abstract': abstract,
                     'tags': tags[:len(tags) // 3]})
    csvfile.flush()
driver.quit()
