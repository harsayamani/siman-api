from pusher import Pusher
from dotenv import load_dotenv
import os
load_dotenv('.env')

class PusherNotification :
    def __init__(self) :
        self.pusher_client = Pusher(
            app_id = os.environ.get('APP_ID'),
            key = os.environ.get('KEY'),
            secret = os.environ.get('SECRET'),
            cluster = os.environ.get('CLUSTER'),
            ssl = True
        )
    
    def sendNotification(self, channel, event, data) :
        self.pusher.trigger(channel, event, data)