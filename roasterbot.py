import re
import requests
import json
import os
from flask import Flask,request
from twilio.rest import TwilioRestClient
import twilio.twiml


app = Flask(__name__)
_list = 'https://raw.githubusercontent.com/RoasterBot/lockhouse/gh-pages/coffees/list'
greeting_list = ['hello', 'hello!', 'hey', 'hey!', 'hi', 'hi!', 'hola', 'yo', 'yo!']

@app.route("/", methods=['GET','POST'])
def hello():

    resp = twilio.twiml.Response()
    _body = request.values.get('Body', '')
    _words = _body.split(' ')
    _message = ''
    _media = None
    
    if _words[0].lower() == 'cmd' or _words[0].lower() == 'cmds':
        _message = help()
    elif _words[0].lower() == 'deliveries' or _words[0].lower() == 'delivery' \
          or _words[0].lower() == 'delivery info':
        _message = 'More info coming soon!'
        _media = 'http://upload.wikimedia.org/wikipedia/commons/c/c8/US_bike_messenger_stamp_1902.jpg'
    elif len(_words[0]) == 2 and _words[0] not in greeting_list:  #a request for product info
        _message = get_product_info( _words[0] )[0]
        _media = get_product_info( _words[0] )[1]
    elif _words[0].lower == 'order':
        _message = order(_body)
    else:
        _message = get_greeting(_words)
        _message += list_info()
        _message += get_salutation()
    
    if _media != None:
        with resp.message(_message) as m:
            m.media( _media )
    else:
        resp.message(_message)
    return str(resp)


def order(body):
    '''
    This is where we route the order to a workflow. At a minimum we forward an
    SMS message, email, phone call. Etc.

    The destination should probably be stored in the environment; e.g., 
    ENV['SMS_ORDER_NUMBER']
    '''
    return 'Success'


@app.route("/help",methods=['GET', 'POST'])
def help():
    _message = "Help is on the way! \nCommands:\n CMD > This message > DELIVERIES > " \
            "Location and times for drop-offs \n Two-Letter Code > " \
            " Details and price of coffee. \n ORDER CODE qty (1-10 lbs) " \
            " Placing an order for 1-10 lbs."
    return _message




def list_info():
    _resp = requests.get(_list)
    return _resp.text




@app.route("/coffee", methods=['GET','POST'])
def get_product_info(prefix):
    '''
     prefix needs to be 2 characters
    
     convention for url is PREFIX.md where PREFIX is all upper case.
    '''
    _url = 'https://raw.githubusercontent.com/RoasterBot/lockhouse/gh-pages/coffees/%s.md' % (prefix.upper() )
    response = requests.get(_url)
    content = response.text
    message = content.split('::')[0]
    if message == 'Not Found':
        return ('Sorry, I didn\'t see %s. This is what we have today:%s' % \
                (prefix, list_info()) , None)
    
    media = content.split('::')[1]
    return (message,media)
    


def get_greeting(words):
    fw = words[0]
    if fw.lower() in greeting_list:
        greeting = 'Well, \"%s\" back atcha, friend! ' % fw
    elif fw.lower() == 'coffee' or fw.lower() == 'coffee!':
        greeting = 'We love coffee, too! '
    elif fw.lower() == 'coffee?' or fw.lower() == 'got coffee?':
        greeting = 'You bet! '
    else:
        greeting =  'Hey hey, Friend! '
    return greeting

def get_salutation():
    return '--Roasterbot\nhttp://lockhouse.coffee'

if __name__ == "__main__":
    app.run(debug=True)
