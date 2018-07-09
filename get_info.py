import json

import urllib.request
import urllib.parse

vk_api_url = 'https://api.vk.com/method/{}'
user_get = 'users.get'
photo_get = 'photos.getById'
version = '5.52'
fields = 'counters,crop_photo,followers_count,has_photo,photo_id,relation,sex'


def get_token(token_file_name='/home/common_swift/programming/likepredictor/access_token'):
    with open(token_file_name, 'r') as f:
        return f.read().rstrip()

def get_user_info(access_token, user_id, photo_filename):
    values = {
        'user_id': user_id,
        'access_token':access_token,
        'fields': fields,
        'v':version
    }
    data = urllib.parse.urlencode(values).encode('ascii')
    req = urllib.request.Request(vk_api_url.format(user_get), data)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
        encoding = response.info().get_content_charset('utf-8')
        res = json.loads(the_page.decode(encoding))
        if res['response'][0]['has_photo']:
            urllib.request.urlretrieve(res['response'][0]['crop_photo']['photo']['photo_130'], photo_filename)
            return res
        else:
            return None

def get_photo_info(access_token, photo_id):
    values = {
        'access_token':access_token,
        'photos': photo_id,
        'v':version,
        'extended': '1',
    }
    data = urllib.parse.urlencode(values).encode('ascii')
    req = urllib.request.Request(vk_api_url.format(photo_get), data)
    response = urllib.request.urlopen(req)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
        encoding = response.info().get_content_charset('utf-8')
        res = json.loads(the_page.decode(encoding))
        return res

def main():
    access_token = get_token()
    user_info = get_user_info(access_token, '22164718', './photos/22164718')
    print(user_info)
    photo_info = get_photo_info(
        access_token, 
        user_info['response'][0]['photo_id']
    )
    print(photo_info)

if __name__ == '__main__':
    main()