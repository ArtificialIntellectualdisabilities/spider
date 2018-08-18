from urllib.parse import urlencode
import requests
from pyquery import PyQuery as pq
from pymongo import MongoClient
base_url='https://m.weibo.cn/api/container/getIndex?'
headers={
    'Host':'m.weibo.cn',
    'Referer':'https://weibo.com/',
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest'
}


def get_page(page):
    params={
        'type':'uid',
        'value':'2830678474',
        'containerid':'1076032830678474',
        'page':page
    }
    url=base_url+urlencode(params)
    try:
        response=requests.get(url,headers=headers)
        if response.status_code==200:
            return response.json()
    except requests.ConnectionError as e:
        print('Error',e.args)

def parse_page(json):
    '''
    去除正文中的HTML标签
    :param json:
    :return:
    '''
    if json:
        items=json.get('data').get('cards')
        for item in items:
            item=item.get('mblog')
            weibo={}
            try:
                weibo['id']=item.get('id')
            except:
                weibo['id']=None
            try:
                weibo['text']=pq(item.get('text')).text()
            except:
                weibo['text']=None
            try:
                weibo['attitudes']=item.get('attitudes_count')
            except:
                weibo['attitudes']=None
            try:
                weibo['comments']=item.get('comment_count')
            except:
                weibo['comments']=None
            try:
                weibo['reposts']=item.get('reposts_count')
            except:
                weibo['reposts']=None
            yield weibo

def create_database():

    client=MongoClient()
    db=client['spider']
    return db['weibo']

def save_to_mongo(result,table):
    if table.insert(result):
        print('Save to Mongo')


if __name__ == '__main__':
    collection=create_database()
    for page in range(1,11):
        json=get_page(page)
        results=parse_page(json)
        for result in results:
            print(result)
            save_to_mongo(result=result,table=collection)
