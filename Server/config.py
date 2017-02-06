API_VERSION = '3.0.42'
APP_VERSION = '3.28.0'
APP_BUILD = 'release'
UUID = 'AJDA7XkI9glLBWc85sk-nJ_6F0jqALu4AlY='
UA = 'osee2unifiedRelease/3.28.0 (iPhone; iOS 10.2; Scale/2.00)'
APP_ZA = 'OS=iOS&Release=10.2&Model=iPhone8,1&VersionName=3.28.0&VersionCode=558&Width=750&Height='
CLIENT_ID = '8d5227e0aaaa4797a763ac64e0c3b8'
APP_SECRET = b'ecbefbf6b17e47ecb9035107866380'

TOKEN_FILE = 'token.json'

ZHIHU_API_ROOT = 'https://api.zhihu.com'
PEOPLE_URL = 'https://www.zhihu.com/people/{}'
LIVE_URL = 'https://www.zhihu.com/live/{}'
LIVE_USER_URL = 'https://www.zhihu.com/lives/users/{}'
ZHUANLAN_URL = 'https://zhuanlan.zhihu.com/p/{}'
LOGIN_URL = ZHIHU_API_ROOT + '/sign_in'
CAPTCHA_URL = ZHIHU_API_ROOT + '/captcha'

DB_URI = 'sqlite:///user.db'

SPEAKER_KEYS = ['name', 'gender', 'headline', 'avatar_url', 'bio',
                'description']
LIVE_KEYS = ['id', 'feedback_score', 'seats', 'subject', 'fee',
             'description', 'status', 'starts_at', 'outline',
             'speaker_message_count', 'liked_num', 'tags', 'topics']
SEARCH_FIELDS = ['subject^5', 'outline^2', 'description', 'topic_names^10',
                 'tag_names^5']
SUGGEST_USER_LIMIT = 2
SUGGEST_LIMIT = 6
DOMAIN = 'http://localhost:8300'
