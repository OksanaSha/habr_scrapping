import requests
import bs4
import re


KEYWORDS = {'дизайн', 'фото', 'web', 'python'}
HEADERS = {'Cookie': '_ym_uid=1630962253553488165; _ym_d=1633192614; '
                     '_ga=GA1.2.1760852164.1633192615; hl=ru; fl=ru; '
                     '__gads=ID=93737d18d543d139:T=1633192616:S=ALNI_MZMQJl0wighgx3-LsvdwybFkZVHYg; '
                     'feature_streaming_comments=true; '
                     '_gid=GA1.2.236121156.1639925865; habr_web_home=ARTICLES_LIST_ALL; _ym_isad=2; _gat=1',
           'Accept-Language': 'ru-RU,ru;q=0.9',
           'Sec-Fetch-Dest': 'document',
           'Sec-Fetch-Mode': 'navigate',
           'Sec-Fetch-Site': 'same-origin',
           'Sec-Fetch-User': '?1',
           'Cache-Control': 'max-age=0',
           'If-None-Match': 'W/"270ce-eRssEsorMvohTe0P6Y/tmvZo9C8"',
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/96.0.4664.93 Safari/537.36',
           'sec-ch-ua-mobile': '?0'
           }

def find_date(article):
    date_with_time = article.find(class_='tm-article-snippet__datetime-published')
    date = date_with_time.contents[0]['title']
    return date.split(',')[0]

def get_article_preview(article):
    article_prev_v1 = article.find('div', class_='article-formatted-body article-formatted-body_version-1')
    if article_prev_v1:
        article_prev = article_prev_v1.text
    else:
        article_prev_v2 = article.find('div', class_='article-formatted-body article-formatted-body_version-2')
        article_prev_list = [text_prev.text for text_prev in article_prev_v2.find_all('p')]
        article_prev = ' '.join(article_prev_list)
    return article_prev

def find_keywords(article):
    info_dict = []
    title = article.find('a', class_='tm-article-snippet__title-link')
    title_text = title.find('span').text
    hubs = article.find_all('a', class_='tm-article-snippet__hubs-item-link')
    hubs = [hub.find('span').text.lower() for hub in hubs]
    article_prev = get_article_preview(article)
    if keywords_in_article(title_text, hubs, article_prev):
        date = find_date(article)
        href = title['href']
        url = 'https://habr.com' + href
        info_dict = [date, title_text, url]
    return info_dict

def keywords_in_article(title, hubs, preview, keywords=KEYWORDS):
    title_words = set(re.findall('\w+', title.lower()))
    article_prev_words = set(re.findall('\w+', preview.lower()))
    hubs_words = set(re.findall('\w+', ' '.join(hubs)))
    if keywords & (title_words | article_prev_words | hubs_words):
        return True

if __name__ == '__main__':
    response = requests.get('https://habr.com/ru/all/', headers=HEADERS)
    response.raise_for_status()
    text = response.text
    soup = bs4.BeautifulSoup(text, features='html.parser')
    articles = soup.find_all(class_="tm-articles-list__item")
    for article in articles:
        article_info = find_keywords(article)
        if article_info:
            print('{0} - {1} - {2}'.format(*article_info))
    print('----Finish----')