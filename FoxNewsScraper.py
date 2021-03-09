import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pandas as pd
import time
import urllib.robotparser
from datetime import date

url = 'https://www.foxnews.com/'
USER_AGENT = 'github.com/SmmnsMo'
headers = {"user-agent": USER_AGENT}
page = requests.get(url, headers = headers)
soup = BeautifulSoup(page.content, 'html.parser')

rp = urllib.robotparser.RobotFileParser()
rp.set_url(f"{url}robots.txt")
rp.read()
rrate = rp.request_rate(USER_AGENT)
rp.crawl_delay("*")

if rp.crawl_delay(USER_AGENT) != None:
    delay = rp.crawl_delay(USER_AGENT)
else: 
    delay = 5

links = []
titles = []
categories = []
descriptions = []
article_body = []

labels = ['Titles', 'Links', 'Categories', 'Description', 'Article Body']

def followed_link(link):
    page = requests.get(link, headers = headers)
    soup2 = BeautifulSoup(page.content, 'html.parser')
    return soup2

def category(link):
    return re.findall(r"(?<=\.com/)(.*?)(?=\/)",link)[0]

def get_body(link):
    article = followed_link(link).find(class_='article-body').find_all('p')
    body = []
    for i in range(0, len(article)):
        body.append(article[i].text)
    return ' '.join(body).replace('\xa0',' ')

def main():
    #Hot Topic Link
    links.append(soup.find(class_ = 'rotate-items').a.get('href'))

    #Content 1 link
    links.append(soup.find('main', class_ = 'main-content').find(class_ = 'article story-1').h2.a.get('href'))

    #Section 2 links (banners)
    section_2 = soup.find('div', class_ = 'collection collection-spotlight').find_all('h2')
    #Section 2 links (no banners)
    section_2_no_banners = soup.find('div', class_ = 'collection collection-spotlight').find_all('li')
    #Section 3 links
    section_3 = soup.find('div', class_ = 'main main-secondary').find_all('article')

    #Section 1 links
    section_1 = soup.find('main', class_ = 'main-content').find(class_ = 'related').find_all('a')
    section_2 = soup.find('div', class_ = 'collection collection-spotlight').find_all('h2')
    section_2_no_banners = soup.find('div', class_ = 'collection collection-spotlight').find_all('li')
    section_3 = soup.find('div', class_ = 'main main-secondary').find_all('article')
    sections = [section_1, section_2, section_2_no_banners, section_3]

    for i in sections:
        for j in i:
            if i == section_1:
                links.append(j.get('href'))
            else:
                links.append(j.a.get('href'))

    collection_sections = ['business', 'politics', 'u-s', 'world', 'sports', 'opinion', 'entertainment', 'technology', 'crime']

    for section in collection_sections:
        h2_list = soup.find(class_ = f'collection collection-section {section}').find_all('h2')
        for i in range(0,len(h2_list)):
            links.append('https:'+h2_list[i].a.get('href'))

    #Note that Foxbusiness.com == business label.
    #Need to write a conditional to label all of these types as business
    for i in links:
        if 'business' in i:
            categories.append('business')
        else:
            categories.append(category(i))

    #To keep track of what date these were posted
    today = date.today()
    todays_date = (date.strftime(today, '%m/%d/%y'))

    for link in links:
        if 'video.foxnews.com' in link:
            links.remove(link)
            pass
        else:
            titles.append(followed_link(link).find('h1').text)
            article_body.append(get_body(link))

            if followed_link(link).find('h2') == None:
                descriptions.append('None')
            else:
                descriptions.append(followed_link(link).find('h2').text)

            time.sleep(delay)


    df = pd.DataFrame(data = [titles, links, categories, descriptions, article_body], index = labels).T
    df['Date'] = todays_date

if __name__ == '__main__':
    main()