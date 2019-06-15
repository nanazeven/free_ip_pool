from flask import Flask, g, jsonify
from setting import REDIS_KEY_HTTPS, REDIS_KEY_HTTP
from db import RedisClient


__all__ = ['app']

app = Flask(__name__)

def get_db():
    if 'db' not in g:
        g.db = RedisClient()
    return g.db

@app.route('/')
def index():
    return '<h1> Proxy api </h1><h3>/get_http|https<h3/>'

@app.route('/get_http')
def get_proxy_http():
    db = get_db()
    res = {'count':db.count_valid(REDIS_KEY_HTTP),'proxy':db.randow(REDIS_KEY_HTTP)}
    return jsonify(res)

@app.route('/get_https')
def get_proxy_https():
    db = get_db()
    res = {'count':db.count_valid(REDIS_KEY_HTTPS),'proxy':db.randow(REDIS_KEY_HTTPS)}
    return jsonify(res)


