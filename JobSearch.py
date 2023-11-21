from bs4 import BeautifulSoup as bs4
import requests
import math
import pandas as pd
import time
import random
import concurrent.futures

class JobScraper:
    def __init__(self, maxDelay:int =1):
        '''
        Parameters
        searchString: str
            Job Title or Employer.
        location: str
            Job location.
        maxPages: int
            Maximum number of pages to be scraped. Each page contains 25 results.
        sort: str
            'D' = Sort by date posted
            'M' = sort by best match
        maxDelay: int, default = 0
            Max number of seconds of delay for the scraping of a single posting.
        '''
        self._urlSearchList=[]
        self._headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}
        self._max_delay = maxDelay
        self._jobs = []
        self._urlsList = []
    
    def parseUrl(self, request:list):
        for r in request: 
            for key, value in r.items():
                self._urlSearchList.append('https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring={}&sort=M&locationstring={}'.format(key,value))
        return self._urlSearchList
    @staticmethod
    def _numPages(self,maxPages:int, urls_list:list) -> int:
        r = requests.get(urls_list)
        soup = bs4(r.content, 'html.parser')
        x=soup.find('span', class_='found').get_text().replace(',','')
        self.pagesfound = math.ceil(int(x)/25)
        maxPage=maxPages 
        if maxPage>self.pagesfound:maxPage=self.pagesfound
        else:maxPage=maxPages
        return maxPage

    def _extract_urls(self, maxPages:int , request: list) -> list:     
        urls_list:list = self.parseUrl(request)
        for i in range(len(urls_list)):
            maxPage:int = self._numPages(self,maxPages, urls_list[i])
            urlPage:list = []
            for page in range(maxPage):              
                url="{}&page={}".format(urls_list[i], page+1)
                with requests.Session() as request:
                    r = request.get(url)
                soup = bs4(r.content, 'html.parser')
                urls = soup.find_all('a', class_='resultJobItem')
                for url in urls:
                    href = url.parent.a.get('href')
                    u=href.split(';')
                    urlPage.append('https://www.jobbank.gc.ca{}'.format(u[0]))
            self._urlsList.append(urlPage)
        return self._urlsList

    def _extract_page(self, url: str) -> list:
        with requests.Session() as request:
            r = request.get(url)
        soup = bs4(r.content, 'html.parser')
        return self._transform_page(soup,url)

    def _transform_page(self, soup: bs4,url: str) -> list:
 
        try:
            minSalary = soup.find(
                'span', property='minValue').text.strip().replace('\n', '')
        except:
            minSalary = None
        try:
            maxSalary = soup.find(
                'span', property='maxValue').text.strip().replace('\n', '')
        except:
            maxSalary = None
        try:
            payType = soup.find(
                'span', property='unitText').text.strip().replace('\n', '')
        except:
            payType = None
        try:
            title = soup.find(
                'span', property='title').text.strip().replace('\n', '')
        except:
            title = None
        try:
            company = soup.find(
                'span', property='hiringOrganization').text.strip().replace('\n', '')
        except:
            company = None
        try:
            location = soup.find(
                'span', property='joblocation').text.strip().replace('\n', '')
        except:
            location = None
        try:
            noc = soup.find(
                'span', class_='noc-no').text.strip().replace('\n', '')
        except:
            noc = None
        try:
            description = soup.find(
                'span', property='description').text.strip().replace('\n', '')
        except:
            description = None
        try:
            employmentType = soup.find(
                'span', property='employmentType').text.strip().replace('\n', '')
        except:
            employmentType = None
        try:
            WageURL = soup.find(
                'a', id='j_id_2z_3_i8').text.strip().replace('\n', '')
        except:
            WageURL = None
        if minSalary is not None or maxSalary is not None:  
            try:
                job = {
                    'Job Title': title,
                    'Job Location': location,
                    'Hiring Company': company,
                    'Minimum Salary': minSalary,
                    'Maximum Salary': maxSalary,
                    'Pay Type': payType,
                    'Employment Type': employmentType,
                    'Job Description': description,
                    'Wage Report URL': WageURL,
                    'NOC': noc,
                    'URL': url,
                }
                self._jobs.append(job)
            except:
                pass
        return self._jobs

    def scrape_url(self,maxPages, request) -> list:
        return self._extract_urls(maxPages,request)

    def scrape(self,urls:list) -> list:  
        self.jobDf: list = []
        for url in urls:
            self._jobs = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=32) as ex:
                futures: list = []   
                for u in url:
                    if self._max_delay > 0:
                        time.sleep(random.randint(0, self._max_delay))
                    futures.append(ex.submit(self._extract_page, url=u))
                for futures in concurrent.futures.as_completed(futures):
                    pass
                df: pd.DataFrame = pd.DataFrame(self._jobs)
                df.drop_duplicates(inplace=True)
                self.jobDf.append(df)
        return self.jobDf
    @staticmethod
    def parseRequest(request: str):
        response = request.split(';')
        return response
    @staticmethod
    def multipleJobs(jobList: list):
        if  len(jobList) > 1: 
            return True
        else:
            return False

