# fix sys path if you want to use this script individually
# pip install scrapy-user-agents
import ast
import csv
import json
import re
import threading
import time

import twisted

import pymongo
import scrapy
from azure.storage.queue import QueueClient
from bson import ObjectId
from scrapy import signals, Request
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

from os.path import dirname as up

# from crawl_n_depth.Simplified_System.Contact_persons_from_website.Extract_Org_Founders import main_founder_search_v2

three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)

from Simplified_System.Database.db_connect import refer_collection
from Simplified_System.website_contact_page_scrape.contact_page_scraper import get_cp_page_data
# from Simplified_System.Contact_persons_from_website.Extract_Org_Founders import main_founder_search_v2


def is_valid_tp(tp):
    ll = ''.join(filter(str.isdigit, tp))
    if(len(tp)>20):
        return False
    if('.' in tp):
        return False
    if ('12345678' in tp):
        return False
    elif (len(ll) == 10 and (ll[0] == '1' or ll[0] == '0')):
        return True
    elif (len(ll) == 11 and ll[0:2] == '61'):
        return True
    elif (len(ll) == 12 and ll[0:2] == '61'):
        return True
    elif ((len(ll) == 10 or len(ll) == 9) and (ll[0] == '0')):
        return True
    elif ((len(ll) == 10 or len(ll) == 11 or len(ll) == 12) and (ll[0:2] == '64')):
        return True
    else:return False


def getting_uniques(ad_list):
    mapping_list = []
    fixed_ad_list = []
    fixed_orginal_list = []
    fixed = []
    for y in ad_list:
        yt=y.replace(","," ")
        fixed.append((" ").join(yt.split()))
        mapping_list.append([y,(" ").join(yt.split())])

    fixed = list(set(fixed))
    for i in fixed:
        is_unique = True
        for j in fixed:
            if(i==j):continue
            if(i in j):
                is_unique=False
                break
        if(is_unique):
            fixed_ad_list.append(i)
    for each_i in fixed_ad_list:
        for each_map in mapping_list:
            if(each_map[1]==each_i):
                # print(each_map[0])
                fixed_orginal_list.append(each_map[0])
                break
    # print(ad_list)
    # print(fixed)
    # print(fixed_ad_list)
    # print(fixed_orginal_list)
    return fixed_orginal_list

def clean_add(add_list):
    cleaned_add = []
    for each_ad in add_list:
        if(' Act ' in each_ad or ' act ' in each_ad):
            continue
        if (' Sa ' in each_ad or ' sa ' in each_ad):
            continue
        if (' Wa ' in each_ad or ' wa ' in each_ad):
            continue
        if (' tas ' in each_ad or ' Tas ' in each_ad):
            continue
        w_ori_list = each_ad.split(" ")
        w_list = each_ad.lower().split(" ")
        if('level' in w_list):
            cl_ad = (" ").join(w_ori_list[w_list.index('level'):])
            each_ad = cl_ad
        if ('suite' in w_list):
            cl_ad = (" ").join(w_ori_list[w_list.index('suite'):])
            each_ad = cl_ad
        if ('unit' in w_list):
            cl_ad = (" ").join(w_ori_list[w_list.index('unit'):])
            each_ad = cl_ad
        if ('post' in w_list and 'box' in w_list):
            cl_ad = (" ").join(w_ori_list[w_list.index('post'):])
            each_ad = cl_ad
        if ('po' in w_list and 'box' in w_list):
            cl_ad = (" ").join(w_ori_list[w_list.index('po'):])
            each_ad = cl_ad

        each_ad = each_ad.replace('\\n','')
        each_ad = each_ad.replace('\n', '')
        each_ad = each_ad.replace('\\', '')
        each_ad = each_ad.replace('+', '')
        each_ad = each_ad.replace('<br','')
        each_ad = each_ad.replace('/>', '')
        cleaned_add.append(each_ad)
    return cleaned_add
def add_parser(text):
    extracted_addresses = []
    addregexau1 = re.compile(
        r"(?i)(\b(suite|level|unit)[,\s|.\s|,.|\s]*)?(\b(PO BOX|post box)[,\s|.\s|,.|\s]*)?(\b(\d{1,4}))(\b(?:(?!\s{5,}).){1,60})\b(New South Wales|Victoria|Queensland|Western Australia|South Australia|Tasmania|VIC|NSW|ACT|QLD|NT|SA|TAS|WA|Pymble).?[,\s|.\s|,.|\s]*(\b(\d{4})).?[,\s|.\s|,.|\s]*(\b(Australia|Au))?")

    addregexau2 = re.compile(
        r"(?i)(\b(suite|level|unit)[,\s|.\s|,.|\s]*)?(\b(PO BOX|post box)[,\s|.\s|,.|\s]*)?(\b(\d{1,4}))(\b(?:(?!\s{5,}).){0,25})\b(street|road|avenue|st|rd).?[,\s|.\s|,.|\s]*(\b(?:(?!\s{5,}).){0,25})[,\s|.\s|,.|\s]*(\b(\d{4})).?[,\s|.\s|,.|\s]*(\b(Australia|AU)).?")
    addregexau3 = re.compile(
        r"(?i)(\b(suite|level|unit)[,\s|.\s|,.|\s]*)?(\b(PO BOX|post box)[,\s|.\s|,.|\s]*)?(\b(\d{1,4}))(\b(?:(?!\s{5,}).){1,60})\b(New South Wales|Victoria|Queensland|Western Australia|South Australia|Tasmania|VIC|NSW|ACT|QLD|NT|SA|TAS|WA|Pymble).?[,\s|.\s|,.|\s]*(\b(Australia|Au))?[,\s|.\s|,.|\s]*(\b(\d{4})).?")
    addregexau4 = re.compile(
        r"(?i)(\b(suite|level|unit)[,\s|.\s|,.|\s]*)?(\b(PO BOX|post box)[,\s|.\s|,.|\s]*)?(\b(\d{1,4}))(\b(?:(?!\s{5,}).){0,25})\b(street|road|avenue|st|rd).?[,\s|.\s|,.|\s]*(\b(?:(?!\s{5,}).){0,25})[,\s|.\s|,.|\s]*\b(New South Wales|Victoria|Queensland|Western Australia|South Australia|Tasmania|VIC|NSW|ACT|QLD|NT|SA|TAS|WA).?[,\s|.\s|,.|\s]*(\b(Australia|AU)).?")
    addregexau5 = re.compile(
        r"(?i)(\b(suite|level|unit)[,\s|.\s|,.|\s]*)?(\b(PO BOX|post box)[,\s|.\s|,.|\s]*)?(\b(\d{1,4}))(\b(?:(?!\s{5,}).){0,25})\b(street|road|avenue|st|rd).?[,\s|.\s|,.|\s]*(\b(?:(?!\s{5,}).){0,25})[,\s|.\s|,.|\s]*\b(Sydney|Melbourne|Brisbane|Perth|Adelaide|Gold Coast|Newcastle|Canberra|Christchurch|Redcliffe|Clayton|Takapuna|Thebarton|Pymble|Waikato|Auckland|Wellington|Hamilton|Tauranga|Lower Hutt|	Dunedin|Palmerston North|Napier|Porirua|New Plymouth|Rotorua|Whangarei|Hibiscus Coast|Nelson|Invercargill|Hastings|Upper Hutt|Whanganui|Gisborne).?[,\s|.\s|,.|\s]*(\b(\d{4})).?")

    searchau1 = re.findall(addregexau1, text)
    searchau2 = re.findall(addregexau2, text)
    searchau3 = re.findall(addregexau3, text)
    searchau4 = re.findall(addregexau4, text)
    searchau5 = re.findall(addregexau5, text)
    searchau=searchau1+searchau2+searchau3+searchau4+searchau5
    for each in searchau:
        add_l = []
        add_r = list(each)
        for each_r in add_r:
            if (each_r.strip() not in add_l):
                # print(each_r,len(each_r.strip()))
                add_l.append(each_r.strip())
        # print(add_l)
        add_f = (" ").join(add_l).strip()
        extracted_addresses.append(add_f)
        # print("au", add_r)

    addregexnz1 = re.compile(
        r"(?i)(\b(suite|level|unit)[,\s|.\s|,.|\s]*)?(\b(PO BOX|post box)[,\s|.\s|,.|\s]*)?(\b(\d{1,4}))(\b(?:(?!\s{5,}).){1,60})\b(Northland|Auckland|Waikato|Bay of Plenty|Gisborne|Hawke's Bay|Taranaki|Manawatu-Whanganui|Wellington|Tasman|Nelson|Marlborough|West Coast|Canterbury|Otago|Southland).?[,\s|.\s|,.|\s]*(\b(\d{4})).?[,\s|.\s|,.|\s]*(\b(New zealand|Newzealand|Nz))?")
    addregexnz2 = re.compile(
        r"(?i)(\b(suite|level|unit)[,\s|.\s|,.|\s]*)?(\b(PO BOX|post box)[,\s|.\s|,.|\s]*)?(\b(\d{1,4}))(\b(?:(?!\s{5,}).){0,25})\b(street|road|avenue|st|rd).?[,\s|.\s|,.|\s]*(\b(?:(?!\s{5,}).){0,25})[,\s|.\s|,.|\s]*(\b(\d{4})).?[,\s|.\s|,.|\s]*(\b(New zealand|Newzealand|Nz)).?")
    addregexnz3 = re.compile(
        r"(?i)(\b(suite|level|unit)[,\s|.\s|,.|\s]*)?(\b(PO BOX|post box)[,\s|.\s|,.|\s]*)?(\b(\d{1,4}))(\b(?:(?!\s{5,}).){1,60})\b(Northland|Auckland|Waikato|Bay of Plenty|Gisborne|Hawke's Bay|Taranaki|Manawatu-Whanganui|Wellington|Tasman|Nelson|Marlborough|West Coast|Canterbury|Otago|Southland).?[,\s|.\s|,.|\s]*(\b(Australia|Au))?[,\s|.\s|,.|\s]*(\b(\d{4})).?")
    addregexnz4 = re.compile(
        r"(?i)(\b(suite|level|unit)[,\s|.\s|,.|\s]*)?(\b(PO BOX|post box)[,\s|.\s|,.|\s]*)?(\b(\d{1,4}))(\b(?:(?!\s{5,}).){0,25})\b(street|road|avenue|st|rd).?[,\s|.\s|,.|\s]*(\b(?:(?!\s{5,}).){0,25})[,\s|.\s|,.|\s]*\b(Northland|Auckland|Waikato|Bay of Plenty|Gisborne|Hawke's Bay|Taranaki|Manawatu-Whanganui|Wellington|Tasman|Nelson|Marlborough|West Coast|Canterbury|Otago|Southland).?[,\s|.\s|,.|\s]*(\b(New zealand|Newzealand|Nz)).?")
    searchnz1 = addregexnz1.findall(text)
    searchnz2 = addregexnz2.findall(text)
    searchnz3 = addregexnz3.findall(text)
    searchnz4 = addregexnz4.findall(text)
    searchnz = searchnz1 + searchnz2 + searchnz3 + searchnz4
    for each in searchnz:
        add_ln = []
        add_rn = list(each)
        for each_rn in add_rn:
            if (each_rn.strip() not in add_ln):
                add_ln.append(each_rn.strip())
        # print(add_l)
        add_fn = (" ").join(add_ln).strip()
        extracted_addresses.append(add_fn)
        # print("nz", add_nz)
    extracted_addresses = list(set(extracted_addresses))
    return extracted_addresses

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
        self.addresses_with_links = []
        self.header_text_with_links = []
        self.paragraph_text_with_links = []
        self.social_media_links_with_links = []
        self.telephone_numbers_with_links = []
        self.emails_with_links = []
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
        # print("old",self.addresses)
        self.addresses = getting_uniques(self.addresses)
        self.social_media_links = list(set(self.social_media_links))
        self.telephone_numbers = list(set(self.telephone_numbers))
        # print(self.social_media_links)

        fixed_addresses_with_sources = []
        for ad in self.addresses:
            for ad_s in self.addresses_with_links:
                if (ad in ad_s[0]):
                    # print(ad, ad_s[1])
                    fixed_addresses_with_sources.append([ad, ad_s[1]])
                    break
        fixed_tp_with_sources = []
        for tp in self.telephone_numbers:
            for tp_s in self.telephone_numbers_with_links:
                if (tp in tp_s[0]):
                    # print(ad, ad_s[1])
                    fixed_tp_with_sources.append([tp, tp_s[1]])
                    break

        fixed_sm_with_sources = []
        for sm in self.social_media_links:
            for sm_s in self.social_media_links_with_links:
                if (sm in sm_s[0]):
                    # print(sm, sm_s[1])
                    fixed_sm_with_sources.append([sm, sm_s[1]])
                    break

        fixed_em_with_sources = []
        for em in self.emails:
            for em_s in self.emails_with_links:
                if (em in em_s[0]):
                    # print(ad, ad_s[1])
                    fixed_em_with_sources.append([em, em_s[1]])
                    break

        fixed_ht_with_sources = []
        for ht in self.header_text:
            for ht_s in self.header_text_with_links:
                if (ht in ht_s[0]):
                    # print(ad, ad_s[1])
                    fixed_ht_with_sources.append([ht, ht_s[1]])
                    break

        fixed_pt_with_sources = []
        for pt in self.paragraph_text:
            for pt_s in self.paragraph_text_with_links:
                if (pt in pt_s[0]):
                    # print(ad, ad_s[1])
                    fixed_pt_with_sources.append([pt, pt_s[1]])
                    break
        print("with_links",self.addresses_with_links)
        print("fixed", fixed_addresses_with_sources)
        n_depth_data={
            'crawled_links': self.crawled_links,
            'header_text': self.header_text,
            'paragraph_text': self.paragraph_text,
            'emails': self.emails,
            'addresses': self.addresses,
            'social_media_links': self.social_media_links,
            'telephone_numbers': self.telephone_numbers,
            'website_addresses_with_sources':fixed_addresses_with_sources,
            'header_text_with_sources': fixed_ht_with_sources,
            'paragraph_text_with_sources': fixed_pt_with_sources,
            'emails_with_sources': fixed_em_with_sources,
            'social_media_links_with_sources': fixed_sm_with_sources,
            'telephone_numbers_with_sources': fixed_tp_with_sources,

        }
        # print("size", len(self.paragraph_text))
        # print("address",self.addresses)
        # print("addresses_with_links",fixed_addresses_with_sources)

        # for i in self.addresses:
        #     for j in self.addresses:
        #         if
        # print("telephone", self.telephone_numbers)
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

    # def start_requests(self):
    #     requests = []
    #     for item in self.start_urls:
    #         requests.append(Request(url=item, headers={'Referer': 'www.google.com'}))
    #     return requests

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
        if(len(extracted_header_text)):
            self.header_text_with_links.append([extracted_header_text,response.url])
        ##add url to paragraph
        # yield Request( headers={'Referer': response.url})





        self.paragraph_text.extend(extracted_paragraph_text)#populating paragraph text list
        if(len(extracted_paragraph_text)):
            self.paragraph_text_with_links.append([extracted_paragraph_text,response.url])
        soup = BeautifulSoup(response.body, "lxml")#get response body to extract further attributes
        all_text_in_page = ''
        blacklist = [
            '[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'style'

        ]
        text = soup.find_all(text=True)#extract and concatenate all text in the site
        text_strip = [t.strip() for t in text]
        text_adds = (" ").join(text_strip)

            # print(text)
        for t in text:
            if t.parent.name not in blacklist:
                all_text_in_page += '{} '.format(t)

        # if(response.url == 'https://www.beautycoursesonline.com/contact-us/'):
        #     print('note',all_text_in_page)
        extracted_tp_numbers = re.findall(r'[(]?[+]?[0-9][0-9 .\-\(\)]{8,}[0-9]', all_text_in_page)#extracting tp numbers
        filtered_tp = []
        for each_tp in extracted_tp_numbers:
            if (each_tp.count('(') == 1 and each_tp.count(')') == 0):
                each_tp = each_tp.replace('(', "")
            # print(tp)
            if(is_valid_tp(each_tp)):
                filtered_tp.append(each_tp)
        self.telephone_numbers.extend(filtered_tp)
        if (len(filtered_tp)):
            self.telephone_numbers_with_links.append([filtered_tp, response.url])

        extracted_emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", all_text_in_page)#extracting emails
        self.emails.extend(extracted_emails)
        if (len(extracted_emails)):
            self.emails_with_links.append([extracted_emails, response.url])

        # extracted_addresses = pyap.parse(all_text_in_page, country='US')#extracting addresses(Us address parser)
        # extracted_addresses = [str(i) for i in extracted_addresses]
        # self.addresses.extend(extracted_addresses)
        # print(all_text_in_page)
        adds_from_reg = add_parser(text_adds)
        adds_from_reg = clean_add(adds_from_reg)
        self.addresses.extend(adds_from_reg)
        if(len(adds_from_reg)):
            self.addresses_with_links.append([adds_from_reg,response.url])
        # if (response.url == 'https://www.2and2.com.au/contact'):
        #
        #     print(adds_from_reg)
        sm_sites = ['twitter.com', 'facebook.com', 'linkedin.com', 'youtube.com']
        extracted_sm_sites = []

        all_links = soup.find_all('a', href=True)#extracting social media links

        for link_i in all_links:
            link_s = link_i['href']
            if('twitter' in link_s or 'facebook' in link_s or 'linkedin' in link_s or 'youtube' in link_s or 'instagram' in link_s):
                extracted_sm_sites.append(link_s)
                print(link_s)


        self.social_media_links.extend(extracted_sm_sites)
        if(len(extracted_sm_sites)):
            self.social_media_links_with_links.append([extracted_sm_sites,response.url])

        if len(self.crawled_links)>self.crawl_limit:#checking crawling limit and if exceeded close the spider and dump data
            raise CloseSpider('maximum crawling limit exeeded')



# configure_logging()
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
    # mycol = refer_cleaned_collection()
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
        print("one done")
    # print("reactor is stopping")
    # reactor.callFromThread(reactor.stop)
    # print(' reactor stops',threading.currentThread().ident)
    reactor.stop()


# configure_logging()
runner = CrawlerRunner(get_project_settings())
@defer.inlineCallbacks
def run_sequential_crawlers_m_via_queue(depth_limit,crawl_limit):#method used to run the crawler
    """
    :param depth_limit: max depth want to crawl
    :param crawl_limit: max page count want to crawl
    :return:
    """
    try:
        mycol = refer_collection()
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        deep_crawling_client = QueueClient.from_connection_string(connect_str, "deep-crawling-queue")
        # mycol = refer_cleaned_collection()
        while (True):
            time.sleep(10)
            rows = deep_crawling_client.receive_messages()
            for msg in rows:
                # time.sleep(120)
                row = msg.content
                row = ast.literal_eval(row)
                print(row[0])
                entry_id = ObjectId(row[0])
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
                print("completed_crawling and message removing from the queue")
                deep_crawling_client.delete_message(msg)
                mycol.update_one({'_id': entry_id},
                                 {'$set': {'deep_crawling_state': 'Completed'}})
                if (len(paragraph_text) == 0):
                    get_cp_page_data([entry_id])
        # print("reactor is stopping")
        # reactor.callFromThread(reactor.stop)
        # print(' reactor stops',threading.currentThread().ident)
        reactor.stop()
    except Exception as e:
        print("Error has occured..try again!",e)

runner = CrawlerRunner(get_project_settings())
@defer.inlineCallbacks
def run_sequential_crawlers_m_via_queue_chain(depth_limit,crawl_limit):#method used to run the crawler
    """
    :param depth_limit: max depth want to crawl
    :param crawl_limit: max page count want to crawl
    :return:
    """
    try:
        mycol = refer_collection()
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        deep_crawling_client = QueueClient.from_connection_string(connect_str, "deep-crawling-queue")
        f_e_client = QueueClient.from_connection_string(connect_str, "feature-extraction-queue")
        # mycol = refer_cleaned_collection()
        while (True):
            time.sleep(10)
            rows = deep_crawling_client.receive_messages()
            for msg in rows:
                # time.sleep(120)
                row = msg.content
                row = ast.literal_eval(row)
                print(row[0])
                entry_id = ObjectId(row[0])
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
                print("completed_crawling and message removing from the queue")
                deep_crawling_client.delete_message(msg)
                mycol.update_one({'_id': entry_id},
                                  {'$set': {'deep_crawling_state': 'Completed'}})
                try:
                    if(len(paragraph_text)==0):
                        get_cp_page_data([entry_id])
                except Exception as e:
                    print("Exception Occured while extracting website contact page", e)
                # try:
                #     print("Getting website contacts")
                #     main_founder_search_v2(entry_id)
                # except Exception as e:
                #     print("Exception Occured while getting contacts from website",e)
                print("Adding to feature extraction queue")
                f_e_client.send_message([str(entry_id)],time_to_live=-1)
                mycol.update_one({'_id': entry_id},
                                  {'$set': {'feature_extraction_state': 'Incomplete'}})
        # print("reactor is stopping")
        # reactor.callFromThread(reactor.stop)
        # print(' reactor stops',threading.currentThread().ident)
        reactor.stop()
    except Exception as e:
        print("Error has occured..try again!",e)

def run_crawlers_m(id_list, depth_limit, crawl_limit):
    print("came")
    run_sequential_crawlers_m(id_list, depth_limit, crawl_limit)
    # print(reactor.running)

    reactor.run()

def run_crawlers_m_via_queue(depth_limit, crawl_limit):
    print("Reactor Started")
    run_sequential_crawlers_m_via_queue(depth_limit, crawl_limit)
    # print(reactor.running)

    reactor.run()

def run_crawlers_m_via_queue_chain(depth_limit, crawl_limit):
    print("Reactor Started")
    run_sequential_crawlers_m_via_queue_chain(depth_limit, crawl_limit)
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
