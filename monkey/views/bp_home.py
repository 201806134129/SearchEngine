import sys

from sanic import Blueprint
sys.path.append("..")
from jinja2 import Environment, PackageLoader, select_autoescape
from sanic.response import html, json, text

from config import Config
from common.doc_search import doc_search

bp_home = Blueprint(__name__)
bp_home.static('/statics', Config.BASE_DIR + '/statics/')

# 开启异步特性  要求3.6+
enable_async = sys.version_info >= (3, 6)

# jinjia2 config
env = Environment(
    loader=PackageLoader('views.bp_home', '../templates'),
    autoescape=select_autoescape(['html', 'xml', 'tpl']),
    enable_async=enable_async)


async def template(tpl, **kwargs):
    template = env.get_template(tpl)
    rendered_template = await template.render_async(**kwargs)
    return html(rendered_template)


@bp_home.route('/')
async def index(request):
    return await template('index.html')


@bp_home.route('/search')
async def index(request):
    query = str(request.args.get('q', '')).strip()
    if query:
        mongo_db = request.app.mongo_db
        result = await doc_search(query=query, mongo_db=mongo_db)
        return await template('search.html', title=query, result=result)
    else:
        return await template('index.html')
