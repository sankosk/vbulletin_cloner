import requests
import collections
import hashlib
import urllib

"""
Extended by : Esteban Montes
Original wrapper code: https://github.com/Arsenalist/Python-Client-for-vBulletin-Mobile-API
"""

class Vbulletin:

    def __init__(self, client_options):
        self.client_options = client_options
        self.init_api()

    def init_api(self):
        # Initialize connection using init_info
        params = {
            'api_s': self.client_options['apikey'],
            'clientname': self.client_options['clientname'],
            'clientversion': self.client_options['clientversion'],
            'platformname': self.client_options['platformname'],
            'platformversion': self.client_options['platformversion'],
            'uniqueid': self.client_options['uniqueid']
        }
        self.init_info = self.make_request(params, 'api_init', 'GET')        


    def to_qs(self, params):
        od = collections.OrderedDict(sorted(params.items()))
        ret = ''
        for i, item in enumerate(od.iteritems()):
            ret = ret + item[0] + "=" + urllib.quote_plus(item[1])
            if i != (len(od.items()) - 1):
                ret = ret + '&'
        return ret

    def create_sign(self, params):
        params_qs = self.to_qs(params)
        unsigned = params_qs + self.init_info['apiaccesstoken'] + str(self.init_info['apiclientid']) + self.init_info['secret'] + self.client_options['apikey']
        return hashlib.md5(unsigned).hexdigest()


    def utf8encode(self, params):
        encoded = {}
        for key, value in params.iteritems():
            encoded[key] = value.encode('utf8')
        return encoded


    def make_request(self, params, api_m, method):
        params = self.utf8encode(params)
        params['api_m'] = api_m
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        # Request must be signed for every call other than api_init
        if api_m != 'api_init' and self.init_info != None:
            # Sign must not contain api_c and api_s so we add those parameters later
            # For a post, do not sign any request parameters
            if method == 'POST':
                params['api_sig'] = self.create_sign({})

            elif method == 'GET':
                params['api_sig'] = self.create_sign(params)

            params['api_c'] = str(self.init_info['apiclientid'])
            params['api_s'] = self.init_info['apiaccesstoken']

        params_qs = urllib.urlencode(params)
        if method == 'POST':
            r = requests.post(self.client_options['forumurl'] + '/api.php', data=params)
        elif method == 'GET':
            r = requests.get(self.client_options['forumurl'] + '/api.php?' + params_qs, headers)
        else:
            raise Exception("Only POST and GET supported for now, but others are easy to add")

        print r

        return r.json()



    def login(self, username, password):
        # login using login_login
        params = {
            'vb_login_password': password,
            'vb_login_username': username
        }
        result = self.make_request(params, 'login_login', 'POST')
        if 'session' not in result or 'userid' not in result['session'] or int(result['session']['userid']) == 0:
            raise Exception("Login failed", result)            

    def post_new_thread(self, forum_id, subject, message):
        # Create a new thread using newthread_postthread
        params = {
            'forumid': forum_id,
            'message': message,
            'subject': subject
        }
        result = self.make_request(params, 'newthread_postthread', 'POST')
        #print result

        if 'show' in result and 'threadid' in result['show']:
            return result['show']['threadid']
        else:
            raise Exception("Could not create new thread.", result)            

    def post_new_answer(self, threadId, message):
        params = {
        't':threadId,
        'message':message,
        }
        result = self.make_request(params, 'newreply_postreply', 'POST')

    def register_new_user(self, username, password, email):
        params = {
            'agree':'true',
            'username':username,
            'email':email,
            'emailconfirm':email,
            'password':password,
            'passwordconfirm':password,
            'month':'4',
            'year':'1996',
            'day':'11'
        }

        result = self.make_request(params, 'register_addmember', 'POST')

    def logout(self):
        return self.make_request({}, 'login_logout', 'GET')


client_options = {
    'apikey': 'LH0RwXtv',
    'forumurl': 'http://127.0.0.1/foro',
    'clientname': 'someclient',
    'clientversion': '1',
    'platformname': '1',
    'platformversion': '1',
    'uniqueid': 'someuniqueid'
}

client_options1 = {
    'apikey': 'XMX7BauV',
    'forumurl': 'http://probandoclonador.x10host.com/upload',
    'clientname': 'someclient',
    'clientversion': '1',
    'platformname': '1',
    'platformversion': '1',
    'uniqueid': 'someuniqueid'
}

v = Vbulletin(client_options)
#v.login('admin', 'admin2')
# forum id, subject, message
#print v.post_new_thread('2', 'ABCDEEEEE EFG', 'This is a message creado de forma automatizada.')
#v.post_new_answer('6','A ver si de una puta vez rula anda')
#v.register_new_user("kulodevaca", "kakapedoculopis", "wowhyrulian@hotmail.com")
#v.logout()
