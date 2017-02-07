import asyncio

from sanic.exceptions import ServerError, NotFound
from sanic import Blueprint

from models import Live, User, session
from config import SUGGEST_LIMIT
from views.schemas import (
    LiveFullSchema, UserFullSchema, UserSchema, LiveSchema, TopicSchema)
from views.utils import marshal_with, str2date

bp = Blueprint('api', url_prefix='/api/v1')

@bp.route('/search')
@marshal_with([LiveSchema, UserSchema])
async def search(request):
    q = request.args.get('q')
    status = request.args.get('status')
    rs = User.suggest(q)
    if status is not None:
        status = status == 'ongoing'
    lives = await Live.ik_search(q, status, request.start, request.limit)
    rs.extend(lives)
    return rs


@bp.route('/suggest')
@marshal_with(LiveSchema)
async def suggest(request):
    q = request.args.get('q')
    lives = await Live.ik_suggest(q, request.limit)
    return lives


@bp.route('/explore')
@marshal_with(LiveFullSchema)
async def explore(request):
    from_ = str2date(request.args.get('from'))
    to = str2date(request.args.get('to'))
    order_by = request.args.get('order_by')
    lives = await Live.explore(from_, to, order_by, request.start,
                               request.limit)
    return lives


@bp.route('/live/<live_id>')
@marshal_with(LiveFullSchema)
async def live(request):
    live = await Live.get(live_id)
    return live.to_dict()


@bp.route('/hot_topics')
@marshal_with(TopicSchema)
async def topics(request):
    topics = await Live.get_hot_topics()
    return topics


@bp.route('/topic')
@marshal_with(LiveFullSchema)
async def topic(request):
    from_ = str2date(request.args.get('from'))
    to = str2date(request.args.get('to'))
    order_by = request.args.get('order_by')
    topic_name = request.args.get('topic')
    lives = await Live.explore(from_, to, order_by, request.start,
                              request.limit, topic_name)
    return lives


@bp.route('/users')
@marshal_with(UserFullSchema)
async def users(request):
    order_by = request.args.get('order_by', 'id')
    desc = bool(request.args.get('desc', 0))
    users = User.get_all(order_by, request.start, request.limit, desc)
    return users


@bp.route('/user/<user_id>')
@marshal_with([LiveFullSchema, UserFullSchema])
async def user(request, user_id):
    user = session.query(User).get(user_id)
    rs = [user.to_dict()]
    lives = await Live.ik_search_by_speaker_id(user_id,
                                               order_by='-starts_at')
    rs.extend(lives)
    return rs


@bp.route('/hot/weekly')
@marshal_with(LiveSchema)
async def hot_weekly(request):
    return await Live.get_hot_weekly()


@bp.route('/hot/monthly')
@marshal_with(LiveSchema)
async def hot_monthly(request):
    return await Live.get_hot_monthly()
