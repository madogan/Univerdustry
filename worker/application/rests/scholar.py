import requests

from application import logger
from bs4 import BeautifulSoup as Bs


BASE_URL = "https://scholar.google.com"
HEADERS = {
    "Host": "scholar.google.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/webp,*/*;q=0.8",
    "Accept-Language": "tr,tr-TR;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "TE": "Trailers"
}


def get_org_href(tree):
    org_href = tree.select_one("div.gs_ob_inst_r a")

    if org_href:
        org_href = org_href.get("href")

    return org_href


def get_organization_page(domain, proxy=None):
    global HEADERS
    global BASE_URL

    if proxy is not None:
        proxies = {
            f'{proxy.split(":")[0].strip()}': proxy
        }
    else:
        proxies = None

    response = requests.get(
        f"{BASE_URL}/scholar?q={domain}", headers=HEADERS, proxies=proxies
    )

    logger.info(f'{response.status_code} {response.reason}')

    tree = Bs(response.content, "lxml")
    org_href = get_org_href(tree)

    if not org_href:
        return None, None

    response = requests.get(f"{BASE_URL}{org_href}", headers=HEADERS,
                            proxies=proxies)

    if not response.ok:
        return None, None

    tree = Bs(response.content, "lxml")

    return tree, org_href


def get_next_page(org_page, counter, org_href, proxy=None):
    try:
        after_author = org_page.select_one(
            ".gs_btnPR"
        ).attrs["onclick"].split("\\")[-3][3:]
        org_href_2 = "&".join(org_href.split("&")[:-2])
    except KeyError:
        return None

    global HEADERS
    global BASE_URL

    if proxy is not None:
        proxies = {
            f'{proxy.split(":")[0].strip()}': proxy
        }
    else:
        proxies = None

    response = requests.get(
        f'{BASE_URL}{org_href_2}&after_author={after_author}'
        f'&astart={counter}',
        headers=HEADERS, proxies=proxies
    )

    logger.info(f'{response.status_code} {response.reason}')

    tree = Bs(response.content, "lxml")

    if tree.select_one(".gsc_pgn_ppn").text == "1-10":
        return None

    return tree


def get_authors(organization_page_tree):
    try:
        return organization_page_tree.select(".gsc_1usr")
    except Exception as e:
        return None


def parse_author(author):
    href = str(author.select_one(".gs_ai_pho").attrs["href"])

    author_name_s1 = str(author.select_one("img").attrs["alt"])
    author_name_s2 = author_name_s1.strip()
    author_name = " ".join(author_name_s2.split())

    result = {
        "id": href.split("=")[-1],
        "name": author_name,
        "img": dict(author.select_one("img").attrs)
    }

    return result
