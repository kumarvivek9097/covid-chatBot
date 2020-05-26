from flask import Flask, request, make_response
import json
from api import Api
from database import Log
from sendEmail import GMailClient
from pymongo import MongoClient
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def configureDataBase():
    client = MongoClient("mongodb+srv://vivek:kr$vivek808@cluster0-whmbf.mongodb.net/test?retryWrites=true&w=majority")
    return client.get_database('chatbotDB')


def configureEmail(name, email):
    mailclient = GMailClient()
    mailclient.sendEmail(name, email)
    return True


def processRequest(req):
    sessionID = req.get('responseId')
    result = req.get("queryResult")
    intent = result.get("intent").get('displayName')
    query_text = result.get("queryText")
    parameters = result.get("parameters")
    name = parameters.get("name")
    email = parameters.get("email")
    db = configureDataBase()

    if intent == 'search_state':
        state = parameters.get("geo-state")
        confirmed, deltaconfirmed, active, recovered, deltarecovered, deaths, deltadeaths = Api().makeApiRequestForState(state_name=state)
        webhook_response = "Total Cases  : (↑{}) {}".format(deltaconfirmed, confirmed) + "\n" + \
                           "Active : {}".format(active) + "\n" + \
                           "Recovered : (↑{}) {}".format(deltarecovered, recovered) + "\n" + \
                           "Deaths : (↑{}) {}".format(deltadeaths, deaths)

        Log().saveConversations(sessionID, query_text, state, webhook_response, intent, db)
        return {

            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhook_response
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            "Do you want me to send the detailed report on your e-mail address? Type.. \n 1. Yes \n 2. Not now "
                        ]

                    }
                }
            ]
        }

    elif intent == 'search_district':
        district = parameters.get('geo-city')
        confirmed, deltaconfirmed, active, recovered, deltarecovered, deaths, deltadeaths = Api().makeApiRequestForDistrict(district_name=district)
        webhook_response = "Total Cases  : (↑{}) {}".format(deltaconfirmed, confirmed) + "\n" + \
                           "Active : {}".format(active) + "\n" + \
                           "Recovered : (↑{}) {}".format(deltarecovered, recovered) + "\n" + \
                           "Deaths : (↑{}) {}".format(deltadeaths, deaths)

        Log().saveConversations(sessionID, query_text, district, webhook_response, intent, db)
        # log.saveCases( "country", fulfillmentText, db)
        return {

            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhook_response
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            "Do you want me to send the detailed report on your e-mail address? Type.. \n 1. Yes \n 2. Not now "
                        ]

                    }
                }
            ]
        }

    elif intent == 'search_country':
        country = parameters.get('geo-country')
        confirmed, deltaconfirmed, active, recovered, deaths, deltadeaths, tests = Api().makeApiRequestForCounrty(country_name=country)
        webhook_response = "Total Cases  : (↑{}) {}".format(deltaconfirmed, confirmed) + "\n" + \
                           "Active : {}".format(active) + "\n" + \
                           "Recovered : {}".format( recovered) + "\n" + \
                           "Deaths : (↑{}) {}".format(deltadeaths, deaths) + "\n" + \
                           "Total Tested : {}".format(tests)

        Log().saveConversations(sessionID, query_text, country, webhook_response, intent, db)
        # log.saveCases( "country", fulfillmentText, db)
        return {

            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhook_response
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            "Do you want me to send the detailed report on your e-mail address? Type.. \n 1. Yes \n 2. Not now "
                        ]

                    }
                }
            ]
        }

    elif intent == 'search_world':
        confirmed, deltaconfirmed, active, deltaactive, recovered, deltarecovered, deaths, deltadeaths, fatality_rate = Api().makeApiWorldwide()
        webhook_response = "Total Cases  : (↑{}) {}".format(deltaconfirmed, confirmed) + "\n" + \
                           "Active : (↑{}) {}".format(deltaactive, active) + "\n" + \
                           "Recovered : (↑{}) {}".format(deltarecovered, recovered) + "\n" + \
                           "Deaths : (↑{}) {}".format(deltadeaths, deaths) + "\n" + \
                           "Fatality Rate : {}".format(fatality_rate)

        Log().saveConversations(sessionID, query_text, "Worldwide Data",webhook_response, intent, db)
        # # log.saveCases( "country", fulfillmentText, db)
        return {

            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhook_response
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            "Do you want me to send the detailed report on your e-mail address? Type.. \n 1. Yes \n 2. Not now "
                        ]

                    }
                }
            ]
        }

    elif intent == "send_email":
        fulfillmentText = result.get("fulfillmentText")
        Log().saveConversations(sessionID, query_text, parameters, fulfillmentText, intent, db)
        Log().saveContactDetails(name, email, db)
        configureEmail(name, email)
        return True

    elif intent == "Welcome" or intent == "continue_conversation" or intent == "end_conversation" or intent == "faq" or intent == "Fallback":
        fulfillmentText = result.get("fulfillmentText")
        Log().saveConversations(sessionID, query_text, None, fulfillmentText, intent, db)
        return True


if __name__ == "__main__":
    app.run(port=5000, debug=True, host='0.0.0.0')
