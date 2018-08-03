import json

import urllib.request
import urllib.parse

def get_token(token_file_name='/home/common_swift/programming/likepredictor/access_token'):
    with open(token_file_name, 'r') as f:
        return f.read().rstrip()

def exec(method, values, access_token):
    vk_api_url = 'https://api.vk.com/method/{}'
    values['version'] = '5.8'
    values['access_token'] = access_token
    data = urllib.parse.urlencode(values).encode('ascii')
    req = urllib.request.Request(vk_api_url.format(method), data)
    response = urllib.request.urlopen(req)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
        encoding = response.info().get_content_charset('utf-8')
        res = json.loads(the_page.decode(encoding))
        print(res)
        print()
        print()
        print(res['response'])
        print()
        print()
        return res['response']

def get_user_info(access_token, user_id, photo_filename):
    res = exec(
        'users.get', 
        {
            'user_ids': user_id,
            'fields': 'counters,crop_photo,followers_count,has_photo,photo_id,relation,sex'
        },
        access_token
    )
    if res[0]['has_photo']:
        urllib.request.urlretrieve(res[0]['crop_photo']['photo']['photo_130'], photo_filename)
        return res
    else:
        return None

def get_photo_info(access_token, photo_id):
    res = exec(
        'photos.getById',
        {
            'photos': photo_id,
            'extended': '1'
        },
        access_token
    )
    return res

def get_group_users(access_token, group_id, count=1000):
    res = exec(
        'groups.getMembers',
        {
            'group_id': group_id,
            'count': count
        },
        access_token
    )
    return res

def main():
    access_token = get_token('/home/common_swift/programming/VkLikePredictor/token')
    group_id = '34215577'
    user_info = get_user_info(access_token, '22164718', './photos/22164718')
    print(user_info)
    photo_info = get_photo_info(
        access_token, 
        user_info[0]['photo_id']
    )
    print(photo_info)
    group_members = get_group_users(access_token, group_id, 5)

if __name__ == '__main__':
    main()