# coding=utf-8
from functools import partialmethod
from marshmallow import Schema, fields

from models import User, session
from config import DOMAIN
WIDTH = 45


def gen_pic_url(path):
    if not path.startswith('/'):
        path = '/' + path
    return '{}{}'.format(DOMAIN, path)


def truncate_utf8(str, width=WIDTH):
    return str[:width] + '...' if len(str) > width else str


class Item(object):
    def truncate(self, attr, obj):
        if attr not in obj:
            return ''
        return truncate_utf8(obj[attr], WIDTH)

    def get_pic_url(self, attr, obj, default=None):
        return gen_pic_url(obj.get(attr, default))


class UserSchema(Schema):
    id = fields.Integer()
    url = fields.Str()
    name = fields.Str()
    bio = fields.Method('truncate_bio')
    headline = fields.Method('truncate_headline')
    description = fields.Method('truncate_description')
    avatar_url = fields.Method('get_avatar_url')
    live_count = fields.Integer()
    type = fields.Str()
    truncate_headline = partialmethod(Item.truncate, 'headline')
    truncate_bio = partialmethod(Item.truncate, 'bio')
    truncate_description = partialmethod(Item.truncate, 'description')
    get_avatar_url = partialmethod(Item.get_pic_url, 'avatar_url')


class UserFullSchema(UserSchema):
    lives_url = fields.Str()
    speaker_id = fields.Str()
    gender = fields.Integer()
    bio = fields.Str()
    description = fields.Str()
    headline = fields.Str()
    gender = fields.Integer()


class LiveSchema(Schema):
    id = fields.Str()
    url = fields.Str()
    speaker = fields.Nested(UserSchema)
    subject = fields.Str()
    feedback_score = fields.Float()
    amount = fields.Float()
    seats_taken = fields.Integer()
    topics = fields.List(fields.String)
    cover = fields.Method('get_cover_url', allow_none=True)
    starts_at = fields.Method('get_start_time')
    outline = fields.Method('truncate_headline')
    description = fields.Method('truncate_description')
    liked_num = fields.Integer()
    type = fields.Str()
    truncate_headline = partialmethod(Item.truncate, 'headline')
    truncate_description = partialmethod(Item.truncate, 'description')
    get_cover_url = partialmethod(Item.get_pic_url, 'cover',
                                  default='/static/images/default-cover.png')

    def get_start_time(self, obj):
         return int(obj['starts_at'].strftime('%s'))


class LiveFullSchema(LiveSchema):
    speaker = fields.Nested(UserFullSchema)
    status = fields.Boolean()  # public(True)/ended(False)
    speaker_message_count = fields.Integer()
    tag_names = fields.Str()
    description = fields.Str()
    outline = fields.Str()
    zhuanlan_url = fields.Str(allow_none=True)


class TopicSchema(Schema):
    id = fields.Integer()
    url = fields.Str()
    avatar_url = fields.Method('get_avatar_url')
    name = fields.Str()
    best_answerers_count = fields.Integer()
    best_answers_count = fields.Integer()
    questions_count = fields.Integer()
    followers_count = fields.Integer()
    get_avatar_url = partialmethod(Item.get_pic_url, 'avatar_url')
