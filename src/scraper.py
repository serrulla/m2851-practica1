import datetime
import urllib2
from bs4 import BeautifulSoup
import re
import time


class ChartsScraper():

    def __init__(self):
        self.url = "https://musicchartsarchive.com"
        self.headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}
        self.data = [['Position', 'Title', 'Album Artist', 'Artist', 'Date']]
        self.startTime = 1979
        self.now = datetime.datetime.now()

    def __download_html(self, url, num_retries=2):
        request = urllib2.Request(url, headers=self.headers)
        try:
            html = urllib2.urlopen(request).read()
        except urllib2.URLError as e:
            print('Download error:', e.reason)
            html = None

            if num_retries > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    # retry 5XX HTTP errors
                    return download(url, num_retries - 1)
        return html

    def __get_charts_links(self, html):
        bs = BeautifulSoup(html, 'html.parser')
        divs = bs.findAll("div", {"class": "chart-month-list"})
        charts_links = []
        
        for div in divs:
            anchors = div.findAll("a")
            for a in anchors:
                href = a['href']
                # Preppend '/' if needed
                if href[0] != '/':
                    href = '/' + href
                charts_links.append(href)

        return charts_links

    def __scrape_example_data(self, html):
        bs = BeautifulSoup(html, 'html.parser')
        trs = bs.findAll('tr')

        for tr in trs:
            example_data = []
            tds = tr.findAll('td')
            for td in tds:
                # Last cell is empty
                if td == tds[0] or td == tds[1]:
                    example_data.append(td.text)
                # If the datum is the ARTIST (index 2), save both Album Artist and Artist fields
                if td == tds[2]:
                    if td.next_element is not None and td.next_element.name == 'a':
                        example_data.append(td.next_element.text)
                        example_data.append(td.text)
                    else:
                        example_data.append(td.text)
                        example_data.append(td.text)
            current_date = bs.find('h1', {'id': 'page-title'}).text
            date = re.search("([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))", current_date)
            example_data.append(date.group(1))
            # Store the data
            self.data.append(example_data)

    def __get_decades_links(self, html):
        bs = BeautifulSoup(html, 'html.parser')
        anchors = bs.findAll('a', href=True)
        years_links = []
        for a in anchors:
            # Match a year from 1900 to 2099
            if re.match("(19|20)[0-9][0-9]s", a.text.strip()):
                href = a['href']
                # Preppend '/' if needed
                if href[0] != '/':
                    href = '/' + href
                years_links.append(href)

        return years_links

    def __get_years_links(self, html):
        bs = BeautifulSoup(html, 'html.parser')
        singles_div = bs.find('div', {'class': 'chart-year-list'})
        divs = singles_div.findAll('div', {'class': 'chart-year'})
        years_links = []
        for d in divs:
            a = d.next_element
            if a.name == 'a':
                # Match a year from 1900 to 2099
                if re.match("(19|20)[0-9][0-9]", a.text.strip()):
                    href = a['href']
                    # Preppend '/' if needed
                    if href[0] != '/':
                        href = '/' + href
                    years_links.append(href)

        return years_links

    def scrape(self):
        print "Web Scraping of music charts data from " + \
              "'" + self.url + "'..."

        print "This process could take roughly 30 minutes.\n"

        # Start timer
        start_time = time.time()

        # Download HTML
        html = self.__download_html(self.url)
        bs = BeautifulSoup(html, 'html.parser')

        charts_links = []

        # Get the links of each decade
        decades_links = self.__get_decades_links(html)
        # For each decade, get each year's links
        for d in decades_links:
            print "Found link to a decade: " + self.url + d
            years_links = self.__get_years_links(self.__download_html(self.url+d))

            # For each year, get its charts' links
            for y in years_links:
                print "Found link to a year: " + self.url + y
                html = self.__download_html(self.url + y)
                current_year_chart_weeks = self.__get_charts_links(html)
                charts_links.append(current_year_chart_weeks)

            # Uncomment this break in case of debug mode
            #break

        # For each chart, extract its data
        for i in range(len(charts_links)):
            for j in range(len(charts_links[i])):
                print "scraping chart data: " + self.url + \
                      charts_links[i][j]
                html = self.__download_html(self.url + \
                                            charts_links[i][j])
                self.__scrape_example_data(html)
                # break

        # Show elapsed time
        end_time = time.time()
        print "\nelapsed time: " + \
              str(round(((end_time - start_time) / 60), 2)) + " minutes"

    def data2csv(self, filename):
        # Overwrite to the specified file.
        # Create it if it does not exist.
        file = open("../csv/" + filename, "w")

        # Dump all the data with CSV format
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                file.write(self.data[i][j] + ";")
            file.write("\n")
