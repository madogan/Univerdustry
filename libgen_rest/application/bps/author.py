from flask import Blueprint, jsonify, current_app, requestimport urllib3from bs4 import BeautifulSoupfrom application import logger, scholaryimport base64import reauthor_bp = Blueprint("author_bp", __name__)@author_bp.route("/", methods=["GET"])def query():    query = request.args.get('query')    nextPageToken = request.args.get('next_page_token')    if query is None:        bad_result = {            'success': False,            'message': "Required parameters does not exist."        }        return jsonify(bad_result)    result = {        'success': True,    }    current_page = 1    if nextPageToken is not None:        current_page = int(str(base64.b64decode(nextPageToken).decode("utf-8", "ignore")).split('-')[1])    http = urllib3.PoolManager()    response = http.request('GET', 'https://libgen.is/scimag/?q=' + query + '&page=' + str(current_page))    html_text = response.data    soup = BeautifulSoup(html_text, 'html.parser')    try:        totalValue = str(soup.find('div', attrs={'style': 'float:left'}).getText()).split(" ")[0]    except:        result['data'] = []        return jsonify(result)    totalPageDobule = int(totalValue) / 25    totalPage = int(int(totalValue) / 25)    nextPage = None    if totalPage != totalPageDobule:        totalPage += 1    if current_page < totalPage:        nextPage = current_page+1    if nextPage is not None:        nextPageToken = base64.b64encode(('univerdustry-'+str(nextPage)).encode("utf-8")).decode('utf-8')        result['next_page_token'] = nextPageToken    counter = 0    articles = []    for link in soup.find_all('tr'):        if counter == 0:            counter += 1            continue        item = link.find_all('td')        author = str(item[0]).replace('<td>', '').replace('</td>', '').split(';')        urlForGet = item[4].find_all('li')        href = urlForGet[1].find_all('a', href=True)[0]['href']        responseForPdf = http.request('GET', href)        pdfPage = BeautifulSoup(responseForPdf.data, 'html.parser')        pdfUrl = pdfPage.find_all('td', {'align': 'center'})[0].find_all('a', href=True)[0]['href']        yearIndex = str(responseForPdf.data).find('Year: ')        year = str(responseForPdf.data)[yearIndex+6:yearIndex+10]        title = item[1].find_all('a')[0].text        info = {            'author': author,            'year': year,            'url': pdfUrl,            'title': title        }        articles.append(info)    result['data'] = articles    return jsonify(result)