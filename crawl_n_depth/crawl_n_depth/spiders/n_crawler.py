import csv
import json
import re
import threading
import time

import twisted

import pymongo
from scrapy import signals
from scrapy.exceptions import CloseSpider
import pyap
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.project import get_project_settings
import os
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
import sys
sys.path.insert(0, 'F:/Armitage_project/crawl_n_depth/')
from Simplified_System.Database.db_connect import refer_collection



class NCrawlerSpider(CrawlSpider):
    name = 'n_crawler' # Spider name
    rules = [
        Rule(LinkExtractor(), callback='parse_items', follow=True)]  # Follow any link scrapy finds (that is allowed) then pass to the parse_items func.
    #initializing the spider for each case
    def __init__(self, crawled_links, header_text, paragraph_text, telephone_numbers, addresses, emails,
                 social_media_links,crawl_limit,entry_id, *args, **kwargs, ):
        """

        :param crawled_links: a list to store crawled links
        :param header_text: a list to store craweled header text
        :param paragraph_text: a list to store craweled paragraph text
        :param telephone_numbers: a list to store crawled telephone numbers
        :param addresses: a list to store crawled addresses
        :param emails: a list to store crawled emails
        :param social_media_links: a list to store crawled social media links
        :param crawl_limit: a limit on number of links to crawl
        :param entry_id: id of the current data record
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
        self.crawl_limit = crawl_limit
        self.entry_id=entry_id
        print('start ',self.start_urls)


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):#using signals to trigger at termination of crawler
        spider = super(NCrawlerSpider,cls).from_crawler(crawler,*args,**kwargs)
        crawler.signals.connect(spider.spider_closed,signal = signals.spider_closed)
        return spider

    def spider_closed(self, spider):#once spider done with crawling dump data to json files
        spider.logger.info('Spider closed dumping data: %s', spider.name)
        print('spider is closed dumping data.....')
        #remove duplicates
        self.crawled_links = list(set(self.crawled_links))
        self.header_text = list(set(self.header_text))
        self.paragraph_text = list(set(self.paragraph_text))
        self.emails = list(set(self.emails))
        self.addresses = list(set(self.addresses))
        self.social_media_links = list(set(self.social_media_links))
        self.telephone_numbers = list(set(self.telephone_numbers))
        print(self.social_media_links)
        n_depth_data={
             'crawled_links': self.crawled_links,
            'header_text': self.header_text,
            'paragraph_text': self.paragraph_text,
            'emails': self.emails,
            'addresses': self.addresses,
            'social_media_links': self.social_media_links,
            'telephone_numbers': self.telephone_numbers
                                   }
        print("size", len(self.paragraph_text))
        try:
            mycol = refer_collection()
            mycol.update_one({'_id': self.entry_id},
                             {'$set': n_depth_data})

            print("Successfully extended the data entry",self.entry_id)
        except Exception:
            print("Max document size reached..data is truncated!")
            n_depth_data['paragraph_text'] = self.paragraph_text[:5000]
            mycol = refer_collection()
            mycol.update_one({'_id': self.entry_id},
                             {'$set': n_depth_data})

            print("Successfully extended the data entry", self.entry_id)

    def parse_items(self, response):#paring to n depth

        print(response.request.headers['User-Agent'])#shows the current random agent using
        print('Got a response from %s.' % response.url)#shows current url crawling
        extracted_paragraph_text = response.xpath('//p//text()').extract()  # extracting paragraph text
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
        soup = BeautifulSoup(response.body, "lxml")#get response body to extract further attributes
        all_text_in_page = ''
        blacklist = [
            '[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'style'

        ]
        text = soup.find_all(text=True)#extract and concatenate all text in the site
        for t in text:
            if t.parent.name not in blacklist:
                all_text_in_page += '{} '.format(t)

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

        for link_i in all_links:
            link_s = link_i['href']
            if('twitter' in link_s or 'facebook' in link_s or 'linkedin' in link_s or 'youtube' in link_s or 'instagram' in link_s):
                extracted_sm_sites.append(link_s)
                print(link_s)


        self.social_media_links.extend(extracted_sm_sites)

        if len(self.crawled_links)>self.crawl_limit:#checking crawling limit and if exceeded close the spider and dump data
            raise CloseSpider('maximum crawling limit exeeded')



configure_logging()
runner = CrawlerRunner(get_project_settings())
@defer.inlineCallbacks
def run_sequential_crawlers_m(id_list,depth_limit,crawl_limit):#method used to run the crawler
    """

    :param id_list: list of id in the database entries wanted to crawl further
    :param depth_limit: max depth want to crawl
    :param crawl_limit: max page count want to crawl
    :return:
    """
    mycol = refer_collection()

    for entry_id in id_list:#going for n depth for the each google search result
        comp_data_entry = mycol.find({"_id": entry_id})
        data=[i for i in comp_data_entry]
        print(data)
        if(data[0]['link']=='None'):continue
        print(data[0]['link'])
        print("started",data[0]['_id'],data[0]['link']+" scraping in to n depth")

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
        print('allowed_dm',allowed_domains)

        custom_settings = {'DEPTH_LIMIT':#setting depth limit of crawling
                               str(depth_limit),
                           }
        crawl_limit = crawl_limit# setting crawl limit aka number of links going to crawl
        yield runner.crawl(NCrawlerSpider,start_urls = [data[0]['link'],], allowed_domains = [allowed_domains,],
                           custom_settings=custom_settings,crawled_links=crawled_links,header_text = header_text,
                           paragraph_text=paragraph_text,telephone_numbers = telephone_numbers,addresses=addresses,
                           social_media_links=social_media_links,emails=emails,crawl_limit = crawl_limit,
                           entry_id=entry_id)
    # print("reactor is stopping")
    # reactor.callFromThread(reactor.stop)
    # print(' reactor stops',threading.currentThread().ident)
    reactor.stop()

def run_crawlers_m(id_list, depth_limit, crawl_limit):
    run_sequential_crawlers_m(id_list, depth_limit, crawl_limit)
    # print(reactor.running)

    reactor.run()
    # try:
    #
    #     reactor.run()
    # except Exception:
    #     print("cannot restart")
    # time.sleep(0.5)
    # os.execl(sys.executable, sys.executable, *sys.argv)
        # reactor.stop()
    # except twisted.internet.error.ReactorNotRestartable:
    # print("twisted")

    # run_sequential_crawlers_m(id_list, depth_limit, crawl_limit)
    # run_sequential_crawlers_m(id_list, depth_limit, crawl_limit)
    # reactor.run()
    # print(reactor.running)
