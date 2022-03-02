from flask import Flask, request, abort
from dotenv import load_dotenv
import os
import datetime
from utils.discordAIP import BaseRequest
from pymongo import MongoClient

app = Flask(__name__)


load_dotenv()
app.connection_url = os.getenv('MONGO')
app.token = os.getenv('TOKEN')
app.vote_webhook = os.getenv('VOTE')
app.autho = os.getenv('PASSWORD')


client = MongoClient(app.connection_url)
db = client.tgk_database
collection = db.Votes

@app.route('/webhook', methods=['POST'])
async def webhook():

    if request.method == 'POST':
            vote_info = request.json
            if str(request.headers['Authorization']) != str(app.autho): return 'unauthorized', 401

            filter = {"_id": int( vote_info['user'])}
            data = collection.find_one(filter)


            if not data:

                data = {"_id": int(vote_info['user']), 'last_vote': datetime.datetime.utcnow(),'total_vote': 1, 'streak':1, 'reminded': False}

                collection.insert(data)
                
                await BaseRequest.get_member(vote_info['user'], app.token, data['total_vote'], app.vote_webhook)
                
                return 'success', 200
            
            if (datetime.datetime.now() - data['last_vote']).total_seconds() > 108000:
                data['streak'] = 1
            else:
                data['streak'] += 1
            
            data['total_vote'] += 1
            data['reminded'] = False
            data['last_vote'] = datetime.datetime.utcnow()

            collection.update_one(filter, {"$set": data})


            await BaseRequest.get_member(vote_info['user'], app.token, data['total_vote'], app.vote_webhook)

            return 'success', 200

    else:
        abort(400)

@app.route("/")
async def index():
    if request.method == 'POST' or 'GET':
        return 'success', 200
    return '<h1 id="heading1">Welcome to&nbsp;Gamblers Kingdom Webpage</h1>\n<iframe src="https://canary.discord.com/widget?id=785839283847954433&theme=dark" width="350" height="500" allowtransparency="true" frameborder="0" sandbox="allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts"></iframe>'

if __name__ == "__main__":
    #app.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(app.connection_url))
    # app = motor.motor_asyncio.AsyncIOMotorClient(str(app.connection_url))
    # app.get_io_loop = asyncio.get_running_loop
    # app.db = app["tgk_database"]
    # app.vote = Document(app.db, "Votes")
    app.run()


# res = await BaseRequest.get_user(vote_info['user'], app.token)
# print(res)