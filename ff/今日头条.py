import requests
from urllib.parse import urlencode
import os
from hashlib import md5

def get_page(offset):
    params={
        'offset':offset,
        'format':'json',
        'keyword':'true',
        'count':'20',
        'cur_tab':'1'
    }
    url='http://www.toutiao.com/search_content/?'+urlencode(params)
    try:
        response=requests.get(url)
        if response.status_code==200:
            return response.json()
    except requests.ConnectionError:
        return None
def get_img(json):
    '''
    图片解析
    :return:
    '''
    if json.get('data'):
        for item in json.get('data'):
            title=item.get('title')
            images=item.get('image_list')
            if images:
                for image in images:
                    yield {
                        'image':'http:'+image.get('url'),
                        'title':title
                    }
            else:
                yield None

def save_img(item):
    if item:
        if not os.path.exists(item.get('title')):
            os.mkdir(item.get('title'))
        try:
            response=requests.get(item.get('image'))
            if response.status_code==200:
                file_path='{0}/{1}.{2}'.format(item.get('title'),md5(response.content).hexdigest(),'jpg')
                if not os.path.exists(file_path):
                    with open(file_path,'wb') as f:
                        f.write(response.content)
                else:
                    print('Already Downloaded',file_path)
        except requests.ConnectionError:
            print('Failed to Save Image')


from multiprocessing.pool import Pool

def main(offset):
    json=get_page(offset)
    for item in get_img(json):
        print(item)
        save_img(item)

GROUP_START=1
GROUP_END=20
if __name__ == '__main__':
    pool=Pool()
    groups=([x*20 for x in range(GROUP_START,GROUP_END+1)])
    pool.map(main,groups)
    pool.close()
    pool.join()

