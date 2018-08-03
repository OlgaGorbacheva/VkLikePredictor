import json
import time
import csv
import logging

import urllib.request
import urllib.parse

logging.basicConfig(filename='collectingdata.log',level=logging.INFO)

def get_token(
    token_file_name='/home/common_swift/programming/likepredictor/access_token'
    ):
    with open(token_file_name, 'r') as f:
        return f.read().rstrip()
    logging.info('Reached accsess tocken')

def exec(method, values, access_token):
    logging.info('Method {} started'.format(method))
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
        if 'error' in res:
            logging.error(
                'vk api error with msg: {}'.format(res['error']['error_msg'])
            )
            time.sleep(1)
            return exec(method, values, access_token)
        return res['response']

def get_user_info(access_token, user_id, photo_filename):
    fields = [
        'counters', 'crop_photo', 'followers_count',
        'has_photo', 'photo_id', 'sex'
    ]
    res = exec(
        'users.get', 
        {
            'user_ids': user_id,
            'fields': ','.join(fields)
        },
        access_token
    )
    res = res[0]
    if res['has_photo']:
        urllib.request.urlretrieve(
            res['crop_photo']['photo']['src_small'], 
            photo_filename
        )
        logging.info(
            'Photo {} is saved in {}'.format(res['photo_id'], photo_filename)
        )
        return res
    else:
        logging.info('User {} has no photo'.format(user_id))
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
    res = res[0]
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
    return res['users']

def compound_info(user_info, photo_info):
    counters = [
        'user_photos', 'videos', 'pages', 
        'groups', 'gifts', 'followers', 
        'photos', 'friends', 'audios'
    ]
    info = {
        c: user_info['counters'][c] if c in user_info['counters'] else None 
        for c in counters
    }
    info['uid'] = user_info['uid']
    info['sex'] = user_info['sex']
    info['likes'] = photo_info['likes']['count']
    info['timestamp'] = photo_info['created']
    return info

def get_full_user_info(access_token, user_id):
    logging.info('Getting user {} info'.format(user_id))
    user_info = get_user_info(
        access_token, user_id, './photos/{}'.format(user_id)
    )
    if user_info is None:
        return None
    photo_info = get_photo_info(access_token, user_info['photo_id'])
    logging.info('Success getting info')
    return compound_info(user_info, photo_info)

def get_df(access_token, user_id_list, filename = 'data.csv'):
    data = []
    logging.info('Start collecting info')
    for uid in user_id_list:
        info = get_full_user_info(access_token, uid)
        if info is not None:
            data.append(info)
    keys = data[0].keys()
    logging.info('Start saving info')
    with open(filename, 'w') as output:
        dict_writer = csv.DictWriter(output, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    logging.info('{} lines user\'s info is availible now'.format(len(data)))
    return data

def collect():
    access_token = get_token()
    group_id = '34215577'
    uids = []
    logging.info('Start collecting user ids from vk.com/overhear')
    for i in range(10):
    	uids += get_group_users(access_token, group_id, offset=i*1000)
    assert len(uids) == len(set(uids))
    get_df(access_token, uids)

if __name__ == '__main__':
    collect()