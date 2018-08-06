import json
import time
import csv
import logging
import argparse

import urllib.request
import urllib.parse
import os

logging.basicConfig(
    format='%(asctime)s\t%(levelname)s:\t%(message)s',
    level=logging.INFO
)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n', '--number', help='Number of users', type=int, default=1000
    )
    parser.add_argument(
        '--token', help='File with access_token', type=str,
        default='access_token'
    )
    parser.add_argument('--gid', help='Group id', type=str, default='34215577')
    parser.add_argument(
        '--folder', help='Folder to save photos', default='photos'
    )
    parser.add_argument(
        '-f', '--datafile', help='Csv file to text data', default='data.csv'
    )
    return parser.parse_args()

def get_token(token_file_name):
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
            if res['error']['error_code'] == 6:
                time.sleep(1)
                return exec(method, values, access_token)
            elif res['error']['error_code'] == 14:
                values['captcha_sid'] = res['error']['captcha_sid']
                logging.critical('You need enter captcha from this link')
                logging.critical(res['error']['captcha_img'])
                values['captcha_key'] = input('Input text from img: ')
                logging.info('Try to resend response')
                return exec(method, values, access_token)
            else:
                raise
        return res['response']

def get_user_info(access_token, user_id, photo_filename):
    fields = [
        'counters', 'crop_photo', 'followers_count',
        'has_photo', 'photo_id', 'sex', 'photo_200'
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
    if res['has_photo'] and 'crop_photo' in res:
        urllib.request.urlretrieve(
            res['photo_200'], 
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

def get_group_users(access_token, group_id, count=1000, offset=0):
    res = exec(
        'groups.getMembers',
        {
            'group_id': group_id,
            'count': count,
            'offset': offset
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

def get_full_user_info(access_token, user_id, dirname):
    logging.info('Getting user {} info'.format(user_id))
    user_info = get_user_info(
        access_token, user_id, os.path.join(dirname, str(user_id))
    )
    if user_info is None:
        return None
    photo_info = get_photo_info(access_token, user_info['photo_id'])
    logging.info('Success getting info')
    return compound_info(user_info, photo_info)

def get_df(access_token, user_id_list, filename, dirname):
    data = []
    logging.info('Start collecting info')
    try:
        for i, uid in enumerate(user_id_list):
            logging.info('Iteration {} user {}'.format(i, uid))
            info = get_full_user_info(access_token, uid, dirname)
            if info is not None:
                data.append(info)
    except:
        logging.critical('Some exception occured')
        logging.critical('Saving uid list in file userlist_exception')
        with open('userlist_exception', 'w') as output:
            output.write(', '.join(str(e) for e in user_id_list))
    finally:
        keys = data[0].keys()
        logging.info('Start saving info')
        with open(filename, 'w') as output:
            dict_writer = csv.DictWriter(output, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        logging.info('{} lines user\'s info is availible now'.format(len(data)))
    return data

def collect(n, group_id, data_file, token_file, folder):
    access_token = get_token(token_file)
    uids = []
    logging.info('Start collecting user ids from vk.com/overhear')
    for i in range(0, n, 1000):
        uids += get_group_users(access_token, group_id, min(n - i, 1000), i)
    assert len(uids) == len(set(uids))
    get_df(access_token, uids, data_file, folder)

if __name__ == '__main__':
    args = parse_args()
    if args.folder[0] != '/':
        args.folder = os.path.join(os.getcwd(), args.folder)
    if not os.path.exists(args.folder):
        os.mkdir(args.folder)
    collect(args.number, args.gid, args.datafile, args.token, args.folder)