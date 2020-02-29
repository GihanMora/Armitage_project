import csv
import json
import re

import scrapy
from scrapy import signals
from scrapy.exceptions import CloseSpider
import pyap
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.project import get_project_settings
import os

class NCrawlerSpider(CrawlSpider):
    name = 'n_crawler' # Spider name
    # name = "my-crawler"

    rules = [
        Rule(LinkExtractor(), callback='parse_items', follow=True)]  # Follow any link scrapy finds (that is allowed) then pass to the parse_items func.
    #initializing the spider for each case
    def __init__(self, crawled_links, header_text, paragraph_text, telephone_numbers, addresses, emails,
                 social_media_links,iteration,crawl_limit,path_to_json, *args, **kwargs, ):
        """

        :param crawled_links: a list to store crawled links
        :param header_text: a list to store craweled header text
        :param paragraph_text: a list to store craweled paragraph text
        :param telephone_numbers: a list to store crawled telephone numbers
        :param addresses: a list to store crawled addresses
        :param emails: a list to store crawled emails
        :param social_media_links: a list to store crawled social media links
        :param iteration: iteration indicates which search result we are crawling
        :param crawl_limit: a limit on number of links to crawl
        :param args: from super class
        :param kwargs: from super class
        """
        super(NCrawlerSpider, self).__init__(*args, **kwargs)
        self.crawled_links = crawled_links
        self.header_text = header_text
        self.paragraph_text = paragraph_text
        self.social_media_links = social_media_links
        self.telephone_numbers = telephone_numbers
        self.emails = emails
        self.addresses = addresses
        self.iteration = iteration
        self.crawl_limit = crawl_limit
        self.path_to_json=path_to_json


        print('start ',self.start_urls)


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):#using signals to trigger at termination of crawler
        spider = super(NCrawlerSpider,cls).from_crawler(crawler,*args,**kwargs)
        crawler.signals.connect(spider.spider_closed,signal = signals.spider_closed)
        return spider

    def spider_closed(self, spider):#once spider done with crawling dump data to json files
        spider.logger.info('Spider closed dumping data: %s', spider.name)
        print('spider is closed dumping data.....')
        with open(self.path_to_json) as json_file:
            data_o = json.load(json_file)
        print(data_o)
        print('c l',self.crawled_links)
        # data_o[0]['crawled_links']= self.crawled_links,
        # data_o[0]['header_text'] = self.header_text,
        # data_o[0]['paragraph_text'] = self.paragraph_text,
        # data_o[0]['emails'] = self.emails,
        # data_o[0]['addresses'] = self.addresses,
        # data_o[0]['social_media_links'] = self.social_media_links,
        # data_o[0]['telephone_numbers'] = self.telephone_numbers,
        print(data_o)
        data_dict = data_o[0]
        # data = []#preparing data to dump
        n_depth_data={
             'crawled_links': self.crawled_links,
            'header_text': self.header_text,
            'paragraph_text': self.paragraph_text,
            'emails': self.emails,
            'addresses': self.addresses,
            'social_media_links': self.social_media_links,
            'telephone_numbers': self.telephone_numbers
                                   }
        data_dict.update(n_depth_data)
        data = []#preparing data to dump
        data.append(data_dict)
        # json_name = self.allowed_domains[0] + "_" + str(self.iteration) + "_data.json"#give json file name as domain + iteration
        # print('crawled_links',self.crawled_links)
        # print('emails', self.emails)
        # print('addresses', self.addresses)
        # print('social_media_links', self.social_media_links)
        # print('telephone_numbers', self.telephone_numbers)
        # print('header_text', self.header_text)
        # print('paragraph_text', self.paragraph_text)
        with open(self.path_to_json, 'w') as outfile:
            json.dump(data, outfile)

        # with open('extracted_json_files/' + json_name, 'w') as outfile:
        #     json.dump(data, outfile)#dumping data and save

        # with open('csv_results/data.csv', mode='w',encoding='utf8') as results_file:  # store search results in to a csv file
        #     results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #     results_writer.writerow([
        #         self.current_data['title'],
        #         self.current_data['link'],
        #         self.current_data['description'],
        #         self.crawled_links,
        #
        #         self.emails,
        #         self.addresses,
        #         self.social_media_links,
        #         self.telephone_numbers,
        #         self.header_text,
        #         self.paragraph_text,
        #     ])
        #     results_file.close()
    def parse_items(self, response):#paring to n depth

        print(response.request.headers['User-Agent'])#shows the current random agent using
        print('Got a response from %s.' % response.url)#shows current url crawling
        extracted_paragraph_text = response.xpath('//p//text()').extract()  # extracting paragraph text
        # print('from scrapy',extracted_paragraph_text)
        headers1 = response.xpath('//h1/text()').extract()  # extracting h1 text
        headers2 = response.xpath('//h2/text()').extract()  # extracting h2 text
        headers3 = response.xpath('//h3/text()').extract()  # extracting h3 text
        headers4 = response.xpath('//h4/text()').extract()  # extracting h4 text
        headers5 = response.xpath('//h5/text()').extract()  # extracting h5 text
        headers6 = response.xpath('//h6/text()').extract()  # extracting h6 text

        extracted_header_text = headers1 + headers2 + headers3 + headers4 + headers5 + headers6  # combining all header text
        self.crawled_links.append(response.url)#populating crawled link list
        self.header_text.extend(extracted_header_text)#populating header text list
        self.paragraph_text.extend(extracted_paragraph_text)#populating paragraph text list
        # print(extracted_header_text)
        soup = BeautifulSoup(response.body, "lxml")#get response body to extract further attributes
        # soup1 = BeautifulSoup(response.body, "html")
        # paras = soup1.find('p').getText()
        # print('from bs4',paras)
        all_text_in_page = ''
        blacklist = [
            '[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'style'

        ]
        text = soup.find_all(text=True)#extract and concatenate all text in the site
        for t in text:
            if t.parent.name not in blacklist:
                all_text_in_page += '{} '.format(t)

        pattern = '(?:(?:\+?61 )?(?:0|\(0\))?)?[2378] \d{4}[ -]?\d{4}'

        extracted_tp_numbers = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', all_text_in_page)#extracting tp numbers
        self.telephone_numbers.extend(extracted_tp_numbers)

        extracted_emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", all_text_in_page)#extracting emails
        self.emails.extend(extracted_emails)

        extracted_addresses = pyap.parse(all_text_in_page, country='US')#extracting addresses(Us address parser)
        extracted_addresses = [str(i) for i in extracted_addresses]
        self.addresses.extend(extracted_addresses)

        sm_sites = ['twitter.com', 'facebook.com', 'linkedin.com', 'youtube.com']
        extracted_sm_sites = []

        all_links = soup.find_all('a', href=True)#extracting social media links

        for sm_site in sm_sites:
            for link in all_links:
                if sm_site in link:
                    extracted_sm_sites.append(link)

        self.social_media_links.extend(extracted_sm_sites)

        if len(self.crawled_links)>self.crawl_limit:#checking crawling limit and if exceeded close the spider and dump data
            raise CloseSpider('maximum crawling limit exeeded')





def run_crawler(search_results,depth_limit,crawl_limit):#method used to run the crawler
    """

    :param search_results: links list of google search results
    :param depth_limit: the depth want to crawl
    :param crawl_limit: number of links want to crawl
    :return: data will be dumped into json files
    """

    if not os.path.exists('extracted_json_files'):
        os.makedirs('extracted_json_files')

    c = CrawlerProcess(
        get_project_settings()#get crawler settings as running from the script
    )
    for i,each_search_result in enumerate(search_results):#going for n depth for the each google search result
        print("started",i,each_search_result+"scraping in to n depth")

        #configuring the crawlers

        # lists for collecting crawling data
        crawled_links = []
        header_text = []
        paragraph_text = []
        telephone_numbers = []
        emails = []
        social_media_links = []
        addresses = []
        allowed_domains = each_search_result.split("/")[2]#getting allowed links from the starting urls itself
        print(allowed_domains)
        custom_settings = {'DEPTH_LIMIT':#setting depth limit of crawling
                               str(depth_limit),
                           }
        crawl_limit = crawl_limit# setting crawl limit aka number of links going to crawl
        c.crawl(NCrawlerSpider,start_urls = [each_search_result,], allowed_domains = [allowed_domains,],custom_settings=custom_settings,crawled_links=crawled_links,header_text = header_text,paragraph_text=paragraph_text,telephone_numbers = telephone_numbers,addresses=addresses,social_media_links=social_media_links,emails=emails,iteration = i,crawl_limit = crawl_limit)

    c.start()#letting all the crawlers to start and run simultaneously


def run_multiple_crawlers(json_list,depth_limit,crawl_limit):#method used to run the crawler
    """

    :param search_results: links list of google search results
    :param depth_limit: the depth want to crawl
    :param crawl_limit: number of links want to crawl
    :return: data will be dumped into json files
    """

    # if not os.path.exists('extracted_json_files'):
    #     os.makedirs('extracted_json_files')

    c = CrawlerProcess(
        get_project_settings()#get crawler settings as running from the script
    )
    for i,path_to_json in enumerate(json_list):#going for n depth for the each google search result
        with open(path_to_json) as json_file:
            data = json.load(json_file)
        json_file.close()
        print("started",i,data[0]['link']+"scraping in to n depth")

        #configuring the crawlers

        # lists for collecting crawling data
        crawled_links = []
        header_text = []
        paragraph_text = []
        telephone_numbers = []
        emails = []
        social_media_links = []
        addresses = []
        allowed_domains = data[0]['link'].split("/")[2]#getting allowed links from the starting urls itself

        custom_settings = {'DEPTH_LIMIT':#setting depth limit of crawling
                               str(depth_limit),
                           }
        crawl_limit = crawl_limit# setting crawl limit aka number of links going to crawl
        c.crawl(NCrawlerSpider,start_urls = [data[0]['link'],], allowed_domains = [allowed_domains,],custom_settings=custom_settings,crawled_links=crawled_links,header_text = header_text,paragraph_text=paragraph_text,telephone_numbers = telephone_numbers,addresses=addresses,social_media_links=social_media_links,emails=emails,iteration = i,crawl_limit = crawl_limit,path_to_json=path_to_json)

    c.start()#letting all the crawlers to start and run simultaneously


#To run this scrpit individually use following line and run the script
# run_crawler(list_of_urls,crawling_depth,crawling_limit)
# run_crawler(['https://www.axcelerate.com.au/','https://getatomi.com/','https://www.beautycoursesonline.com/','https://www.modernstar.com.au/','https://www.negotiations.com/'],5,5000)
