import os
import scrapy
import requests

from urllib.parse import unquote


class MarmaraUniversityAuthorsSpider(scrapy.Spider):
    name = "marmara_edu_tr"
    base_url = "https://scholar.google.com"
    organization_id = None
    base_query_url = "https://scholar.google.com/citations?" \
                     "hl=tr&view_op=search_authors&mauthors="
    num_generator = (num for num in range(10, 9999999999999, 10))
    paginator_url = "https://scholar.google.com/citations?" \
                    "view_op=search_authors&hl=tr&mauthors={domain}" \
                    "&after_author={last_author_id}&astart={num}"
    operator_url = os.getenv("OPERATOR_URL")

    def start_requests(self):
        # We use university domain in order to find authors which
        # in that university on Google Scholar.
        domains = ['marmara.edu.tr']
        # Request to authors listed page for every university.
        for domain in domains:
            yield scrapy.Request(url=(self.base_query_url + domain),
                                 callback=self.parse,
                                 meta={"university_domain": domain})

    def parse(self, response):
        # This is Google defined unique id.
        self.organization_id = self.get_organization_id(response)
        
        # Get author sections in page.
        author_sections = response.css(".gsc_1usr")

        # Extract necessary data for author and yield it.
        for author_section in author_sections:
            requests.post(f"{self.operator_url}/univerdustry/add/author",
                          json={"author_name":
                                self.get_author_name(author_section)})

        # If next page button is not disabled, request to next page.
        next_page_button = self.get_next_page_button(response)
        if next_page_button.attrib.get('disabled', '') != 'disabled':
            next_page_url = self.paginator_url\
                .format(domain=response.meta["university_domain"],
                        last_author_id=next_page_button.attrib["onclick"]
                                       .split('\\')[-3][3:],
                        num=next(self.num_generator))
            yield scrapy.Request(next_page_url, callback=self.parse,
                                 meta={"first": False,
                                       "university_domain":
                                           response.meta["university_domain"]})

    def get_next_page_url(self, next_page_button):
        return self.base_url + unquote(next_page_button.attrib["onclick"]
                                       .split("=")[-1])[1:-1]

    @staticmethod
    def get_next_page_button(response):
        return response.xpath('//*[@id="gsc_authors_bottom_pag"]/div/button[2]')

    @staticmethod
    def get_author_name(author_section):
        return author_section.css("h3.gs_ai_name a::text").get()

    @staticmethod
    def get_organization_id(response):
        if response.meta.get("first", True) is not False:
            result = response.xpath('//*[@id="gsc_sa_ccl"]/div[1]/h3/a')\
                             .xpath('@href')
            if len(result) == 1:
                organization_id = response\
                    .xpath('//*[@id="gsc_sa_ccl"]/div[1]/h3/a')\
                    .xpath('@href')[0].get().split("=")[-1]
                return organization_id
            else:
                return None
