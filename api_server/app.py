from flask import Flask, request
from flask_cors import CORS

from api_server.skeleton import Wiki, ArXiv, Medium, Website, Youtube
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
CORS(app)

@app.route('/', methods=["GET"])
def link(): 
    url : str = request.args.get('url')
    if(url is None):
        return "pass me a link!", 200
    app.logger.info(url)
    if('en.wikipedia.org' in url):
        return Wiki(url).getJSONString()
    elif('arxiv.org' in url):
        return ArXiv(url).getJSONString()
    elif('medium.com' in url):
        return Medium(url).getJSONString()
    elif('youtube.com/watch?v=' in url or 'youtu.be' in url):
        return Youtube(url).getJSONString()
    else:
        return Website(url).getJSONString()


def create_app(test_config=None):
    if test_config is not None:
        app.config.update(test_config)
    return app