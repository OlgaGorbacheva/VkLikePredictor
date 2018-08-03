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
    res = res[0]
    if res['has_photo']:
        urllib.request.urlretrieve(res['crop_photo']['photo']['src_small'], photo_filename)
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
	info = {}
	info['uid'] = user_info['uid']
	info['sex'] = user_info['sex']
	info['user_photos'] = user_info['counters']['user_photos']
	info['videos'] = user_info['counters']['videos']
	info['pages'] = user_info['counters']['pages']
	info['groups'] = user_info['counters']['groups']
	info['gifts'] = user_info['counters']['gifts']
	info['followers'] = user_info['counters']['followers']
	info['photos'] = user_info['counters']['photos']
	info['friends'] = user_info['counters']['friends']
	info['audios'] = user_info['counters']['audios']
	info['likes'] = photo_info['likes']['count']
	info['timestamp'] = photo_info['created']
	return info

def get_full_user_info(access_token, user_id):
	user_info = get_user_info(access_token, user_id, './photos/{}'.format(user_id))
	if user_info is None:
		return None
	photo_info = get_photo_info(access_token, user_info['photo_id'])
	return compound_info(user_info, photo_info)

def get_df(access_token, user_id_list):
	data = []
	for uid in user_id_list:
		info = get_full_user_info(access_token, uid)
		if info is not None:
			data.append(info)
	print(data)

def main():
    access_token = get_token()
    group_id = '34215577'
    group_members = get_group_users(access_token, group_id, 5)
    # print(group_members)
    get_df(access_token, group_members)

if __name__ == '__main__':
    main()