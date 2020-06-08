import os
from flask import Flask, request, make_response
import json
from api import Api
from database import Log
from sendEmail import GMailClient
from pymongo import MongoClient
from plotManager import Plot

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    # print(req)
    res = processRequest(req)
    res = json.dumps(res, indent=4)
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
    session_id = req.get('session').split('/')[4]
    result = req.get("queryResult")
    intent = result.get("intent").get('displayName')
    query_text = result.get("queryText")
    parameters = result.get("parameters")
    name = parameters.get("name")
    email = parameters.get("email")
    db = configureDataBase()

    if intent == 'search_state':
        state = parameters.get("geo-state")
        state_data = Api().getStateData(state_name=state)
        deltaconfirmed = state_data[0]['deltaconfirmed']
        confirmed = state_data[0]['confirmed']
        active = state_data[0]['active']
        deltarecovered = state_data[0]['deltarecovered']
        recovered = state_data[0]['recovered']
        recovery_rate = round(int(recovered) / int(confirmed) * 100, 2)
        deltadeaths = state_data[0]['deltadeaths']
        deaths = state_data[0]['deaths']
        morality_rate = round(int(deaths) / int(confirmed) * 100, 2)
        lastupdatedtime = state_data[0]['lastupdatedtime']

        test_data = Api().getTestData(state_name=state)
        total_test = test_data[0]['total_tested']
        delta_test = test_data[0]['delta_test']
        positive = test_data[0]['positive']
        delta_positive = test_data[0]['delta_positive']
        positivity_rate = test_data[0]['positivity_rate']
        negative = test_data[0]['negative']
        uncomfirmed = test_data[0]['uncomfirmed']
        updated_on = test_data[0]['updated_on']

        webhook_response1 = "Total Cases".ljust(16) + ": {}".format(confirmed) + "\n" + \
                            "New Cases".ljust(16) + ": {}".format(deltaconfirmed) + "\n" + \
                            "Active Cases".ljust(16) + ": {}".format(active) + "\n" + \
                            "Total Recovered".ljust(16) + ": {}".format(recovered) + "\n" + \
                            "New Recovered".ljust(16) + ": {}".format(deltarecovered) + "\n" + \
                            "Recovery Rate".ljust(16) + ": {}%".format(recovery_rate) + "\n" + \
                            "Total Deaths".ljust(16) + ": {}".format(deaths) + "\n" + \
                            "New Deaths".ljust(16) + ": {}".format(deltadeaths) + "\n" + \
                            "Morality Rate".ljust(16) + ": {}%".format(morality_rate) + "\n" + \
                            "Last updated on".ljust(16) + ": {}".format(lastupdatedtime)

        webhook_response2 = "Total Tested".ljust(16) + ": {}".format(total_test) + "\n" + \
                            "New Tested".ljust(16) + ": {}".format(delta_test) + "\n" + \
                            "Total Positive".ljust(16) + ": {}".format(positive) + "\n" + \
                            "New Positive".ljust(16) + ": {}".format(delta_positive) + "\n" + \
                            "Positivity Rate".ljust(16) + ": {}%".format(positivity_rate) + "\n" + \
                            "Negative".ljust(16) + ": {}".format(negative) + "\n" + \
                            "Unconfirmed".ljust(16) + ": {}".format(uncomfirmed) + "\n" + \
                            "Last updated on".ljust(16) + ": {}".format(updated_on)

        telegram_text1 = '```\n' + webhook_response1 + '\n```'
        telegram_text2 = '```\n' + webhook_response2 + '\n```'

        Log().saveConversations(session_id, query_text, state, webhook_response1, intent, db)
        Log().saveConversations(session_id, query_text, state, webhook_response2, intent, db)
        return {

            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhook_response1
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            webhook_response2
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            "Do you want to see chart(s)?"
                        ]
                    }
                },
                {
                    "payload": {
                        "telegram": {
                            "text": telegram_text1,
                            "parse_mode": "Markdown"
                        }
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "payload": {
                        "telegram": {
                            "text": telegram_text2,
                            "parse_mode": "Markdown"
                        }
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "platform": "TELEGRAM",
                    "text": {
                        "text": [
                            "Do you want to see chart(s)?"
                        ]
                    }
                }
            ]
        }

    elif intent == 'search_state - yes':
        follow_up = req['queryResult']['outputContexts']
        for i in follow_up:
            if i['name'].split('/')[-1] == 'search_state-followup':
                state = i['parameters']['geo-state']

        state_data = Api().getStateData(state_name=state)
        active = state_data[0]['active']
        recovered = state_data[0]['recovered']
        deaths = state_data[0]['deaths']
        data = [active, recovered, deaths]
        labels = 'active', 'recovered', 'deaths'
        title = state
        file_path1 = Plot().donut_chart(data, labels, title, session_id)
        webhook_response1 = "https://radiant-thicket-13412.herokuapp.com/"+file_path1

        date, daily_confirmed, daily_active, daily_recovered, daily_deaths = Api().dailyStateData(state)

        if len(set(daily_confirmed)) == 1 and '0' in set(daily_confirmed):
            webhook_response2 = None
        else:
            file_path2 = Plot().bar_plot(date, daily_confirmed, x_label='Date', y_label='Confirmed',
                                         title='Daily Confirmed Cases', session_id=session_id)
            webhook_response2 = "https://radiant-thicket-13412.herokuapp.com/" + file_path2

        if len(set(daily_active)) == 1 and '0' in set(daily_active):
            webhook_response3 = None
        else:
            file_path3 = Plot().bar_plot(date, daily_active, x_label='Date', y_label='Active',
                                         title='Daily Active Cases', session_id=session_id)
            webhook_response3 = "https://radiant-thicket-13412.herokuapp.com/" + file_path3

        if len(set(daily_recovered)) == 1 and '0' in set(daily_recovered):
            webhook_response4 = None
        else:
            file_path4 = Plot().bar_plot(date, daily_recovered, x_label='Date', y_label='Recovered',
                                         title='Daily Recovered', session_id=session_id)
            webhook_response4 = "https://radiant-thicket-13412.herokuapp.com/" + file_path4

        if len(set(daily_deaths)) == 1 and '0' in set(daily_deaths):
            webhook_response5 = None
        else:
            file_path5 = Plot().bar_plot(date, daily_deaths, x_label='Date', y_label='Deaths', title='Daily Deaths',
                                         session_id=session_id)
            webhook_response5 = "https://radiant-thicket-13412.herokuapp.com/" + file_path5

        Log().saveConversations(session_id, query_text, state, webhook_response1, intent, db)
        Log().saveConversations(session_id, query_text, state, webhook_response2, intent, db)
        Log().saveConversations(session_id, query_text, state, webhook_response3, intent, db)
        Log().saveConversations(session_id, query_text, state, webhook_response4, intent, db)
        Log().saveConversations(session_id, query_text, state, webhook_response5, intent, db)

        return {
            "fulfillmentMessages": [
                {
                    "image": {
                        "imageUri": webhook_response1
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "image": {
                        "imageUri": webhook_response2
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "image": {
                        "imageUri": webhook_response3
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "image": {
                        "imageUri": webhook_response4
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "image": {
                        "imageUri": webhook_response5
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "platform": "TELEGRAM",
                    "text": {
                        "text": [
                            "Do you have any other queries?",
                        ],
                        "text": [
                            "Do you have any questions?",
                        ],
                        "text": [
                            "Is there anything else that I can help you with?"
                        ]
                    }
                },
                {
                    "payload": {
                        "metadata": {
                            "templateId": "9",
                            "contentType": "300",
                            "payload": [
                                {
                                    "caption": "Total Cases Distribution",
                                    "url": webhook_response1,
                                },
                                {
                                    "url": webhook_response2,
                                    "caption": "Daily Confirmed Cases"
                                },
                                {
                                    "caption": "Daily Active Cases",
                                    "url": webhook_response3
                                },
                                {
                                    "caption": "Daily Recovered",
                                    "url": webhook_response4
                                },
                                {
                                    "url": webhook_response5,
                                    "caption": "Daily Deaths"
                                }
                            ]
                        },
                        "platform": "kommunicate"
                    }
                },
                {
                    "payload": {
                        "message": "Do you have any other queries?",
                        "platform": "kommunicate"
                    }
                }
            ]
        }

    elif intent == 'search_district':
        district = parameters.get('geo-city')
        district_data = Api().getDistrictData(district_name=district)
        deltaconfirmed = district_data[0]['deltaconfirmed']
        confirmed = district_data[0]['confirmed']
        active = district_data[0]['active']
        deltarecovered = district_data[0]['deltarecovered']
        recovered = district_data[0]['recovered']
        recovery_rate = round(int(recovered) / int(confirmed) * 100, 2)
        deltadeaths = district_data[0]['deltadeaths']
        deaths = district_data[0]['deaths']
        morality_rate = round(int(deaths) / int(confirmed) * 100, 2)

        webhook_response = "Total Cases     : {}".format(confirmed) + "\n" + \
                           "New Cases       : {}".format(deltaconfirmed) + "\n" + \
                           "Active Cases    : {}".format(active) + "\n" + \
                           "Total Recovered : {}".format(recovered) + "\n" + \
                           "New Recovered   : {}".format(deltarecovered) + "\n" + \
                           "Recovery Rate   : {}%".format(recovery_rate) + "\n" + \
                           "Total Deaths    : {}".format(deaths) + "\n" + \
                           "New Deaths      : {}".format(deltadeaths) + "\n" + \
                           "Morality Rate   : {}%".format(morality_rate) + "\n"

        telegram_text = '```\n' + webhook_response + '\n```'
        Log().saveConversations(session_id, query_text, district, webhook_response, intent, db)
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
                            "Do you want to see chart(s)?"
                        ]
                    }
                },
                {
                    "payload": {
                        "telegram": {
                            "text": telegram_text,
                            "parse_mode": "Markdown"
                        }
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "platform": "TELEGRAM",
                    "text": {
                        "text": [
                            "Do you want to see chart(s)?"
                        ]
                    }
                }
            ]
        }

    elif intent == 'search_district - yes':
        follow_up = req['queryResult']['outputContexts']
        for i in follow_up:
            if i['name'].split('/')[-1] == 'search_district-followup':
                district = i['parameters']['geo-city']

        district_data = Api().getDistrictData(district_name=district)
        active = district_data[0]['active']
        recovered = district_data[0]['recovered']
        deaths = district_data[0]['deaths']
        data = [active, recovered, deaths]
        labels = 'active', 'recovered', 'deaths'
        title = district
        file_path1 = Plot().donut_chart(data, labels, title, session_id)
        webhook_response1 = "https://radiant-thicket-13412.herokuapp.com/" + file_path1

        date, total_confirmed, total_active, total_recovered, total_deaths = Api().totalDistrictData(district_name=district)

        if len(set(total_confirmed)) == 1 and '0' in set(total_confirmed):
            webhook_response2 = None
        else:
            file_path2 = Plot().bar_plot(date, total_confirmed, x_label='Date', y_label='Confirmed',
                                         title='Total Confirmed Cases', session_id=session_id)
            webhook_response2 = "https://radiant-thicket-13412.herokuapp.com/" + file_path2

        if len(set(total_active)) == 1 and '0' in set(total_active):
            webhook_response3 = None
        else:
            file_path3 = Plot().bar_plot(date, total_active, x_label='Date', y_label='Active',
                                         title='Total Active Cases', session_id=session_id)
            webhook_response3 = "https://radiant-thicket-13412.herokuapp.com/" + file_path3

        if len(set(total_recovered)) == 1 and '0' in set(total_recovered):
            webhook_response4 = None
        else:
            file_path4 = Plot().bar_plot(date, total_recovered, x_label='Date', y_label='Recovered',
                                         title='Total Recovered', session_id=session_id)
            webhook_response4 = "https://radiant-thicket-13412.herokuapp.com/" + file_path4

        if len(set(total_deaths)) == 1 and '0' in set(total_deaths):
            webhook_response5 = None
        else:
            file_path5 = Plot().bar_plot(date, total_deaths, x_label='Date', y_label='Deaths',
                                         title='Total Deaths', session_id=session_id)
            webhook_response5 = "https://radiant-thicket-13412.herokuapp.com/" + file_path5

        Log().saveConversations(session_id, query_text, district, webhook_response1, intent, db)
        Log().saveConversations(session_id, query_text, district, webhook_response2, intent, db)
        Log().saveConversations(session_id, query_text, district, webhook_response3, intent, db)
        Log().saveConversations(session_id, query_text, district, webhook_response4, intent, db)
        Log().saveConversations(session_id, query_text, district, webhook_response5, intent, db)

        return {
            "fulfillmentMessages": [
                {
                    "image": {
                        "imageUri": webhook_response1
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "image": {
                        "imageUri": webhook_response2
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "image": {
                        "imageUri": webhook_response3
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "image": {
                        "imageUri": webhook_response4
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "image": {
                        "imageUri": webhook_response5
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "platform": "TELEGRAM",
                    "text": {
                        "text": [
                            "Do you have any other queries?",
                        ],
                        "text": [
                            "Do you have any questions?",
                        ],
                        "text": [
                            "Is there anything else that I can help you with?"
                        ]
                    }
                },
                {
                    "payload": {
                        "metadata": {
                            "templateId": "9",
                            "contentType": "300",
                            "payload": [
                                {
                                    "caption": "Total Cases Distribution",
                                    "url": webhook_response1
                                },
                                {
                                    "url": webhook_response2,
                                    "caption": "Total Confirmed Cases"
                                },
                                {
                                    "caption": "Total Active Cases",
                                    "url": webhook_response3
                                },
                                {
                                    "caption": "Total Recovered",
                                    "url": webhook_response4
                                },
                                {
                                    "url": webhook_response5,
                                    "caption": "Total Deaths"
                                }
                            ]
                        },
                        "platform": "kommunicate"
                    }
                },
                {
                    "payload": {
                        "message": "Do you have any other queries?",
                        "platform": "kommunicate"
                    }
                }
            ]
        }

    elif intent == 'search_country':
        country = parameters.get('geo-country')
        country_data = Api().getCountryData(country_name=country)
        deltaconfirmed = country_data[0]['deltaconfirmed']
        confirmed = country_data[0]['confirmed']
        active = country_data[0]['active']
        critical = country_data[0]['critical']
        recovered = country_data[0]['recovered']
        recovery_rate = round(int(recovered) / int(confirmed) * 100, 2)
        deltadeaths = country_data[0]['deltadeaths']
        deaths = country_data[0]['deaths']
        morality_rate = round(int(deaths) / int(confirmed) * 100, 2)
        tests = country_data[0]['tests']

        webhook_response = "Total Cases   : {} ".format(confirmed) + "\n" + \
                           "New Cases     : {} ".format(deltaconfirmed) + "\n" + \
                           "Active Cases  : {} ".format(active) + "\n" + \
                           "Critical      : {} ".format(critical) + "\n" + \
                           "Recovered     : {} ".format(recovered) + "\n" + \
                           "Recovery Rate : {}%".format(recovery_rate) + "\n" + \
                           "Total Deaths  : {} ".format(deaths) + "\n" + \
                           "New Deaths    : {} ".format(deltadeaths) + "\n" + \
                           "Morality Rate : {}%".format(morality_rate) + "\n" + \
                           "Total Tested  : {} ".format(tests)
        telegram_text = '```\n' + webhook_response + '\n```'
        Log().saveConversations(session_id, query_text, country, webhook_response, intent, db)
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
                            "Do you want to see chart(s)?"
                        ]
                    }
                },
                {
                    "payload": {
                        "telegram": {
                            "text": telegram_text,
                            "parse_mode": "Markdown"
                        }
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "platform": "TELEGRAM",
                    "text": {
                        "text": [
                            "Do you want to see chart(s)?"
                        ]
                    }
                }
            ]
        }

    elif intent == 'search_country - yes':
        follow_up = req['queryResult']['outputContexts']
        for i in follow_up:
            if i['name'].split('/')[-1] == 'search_country-followup':
                country = i['parameters']['geo-country']
        country_data = Api().getCountryData(country_name=country)
        active = country_data[0]['active']
        recovered = country_data[0]['recovered']
        deaths = country_data[0]['deaths']
        data = [active, recovered, deaths]
        labels = 'active', 'recovered', 'deaths'
        title = country
        file_path1 = Plot().donut_chart(data, labels, title, session_id)
        webhook_response1 = "https://radiant-thicket-13412.herokuapp.com/" + file_path1
        Log().saveConversations(session_id, query_text, country, webhook_response1, intent, db)

        if country == 'India':
            date, daily_confirmed, daily_active, daily_recovered, daily_deaths = Api().dailyCountryData()
            if len(set(daily_confirmed)) == 1 and '0' in set(daily_confirmed):
                webhook_response2 = None
            else:
                file_path2 = Plot().bar_plot(date, daily_confirmed, x_label='Date', y_label='Confirmed',
                                             title='Daily Confirmed Cases', session_id=session_id)
                webhook_response2 = "https://radiant-thicket-13412.herokuapp.com/" + file_path2

            if len(set(daily_active)) == 1 and '0' in set(daily_active):
                webhook_response3 = None
            else:
                file_path3 = Plot().bar_plot(date, daily_active, x_label='Date', y_label='Active',
                                             title='Daily Active Cases', session_id=session_id)
                webhook_response3 = "https://radiant-thicket-13412.herokuapp.com/" + file_path3

            if len(set(daily_recovered)) == 1 and '0' in set(daily_recovered):
                webhook_response4 = None
            else:
                file_path4 = Plot().bar_plot(date, daily_recovered, x_label='Date', y_label='Recovered',
                                             title='Daily Recovered', session_id=session_id)
                webhook_response4 = "https://radiant-thicket-13412.herokuapp.com/" + file_path4

            if len(set(daily_deaths)) == 1 and '0' in set(daily_deaths):
                webhook_response5 = None
            else:
                file_path5 = Plot().bar_plot(date, daily_deaths, x_label='Date', y_label='Deaths', title='Daily Deaths',
                                             session_id=session_id)
                webhook_response5 = "https://radiant-thicket-13412.herokuapp.com/" + file_path5

            return {
                "fulfillmentMessages": [
                    {
                        "image": {
                            "imageUri": webhook_response1
                        },
                        "platform": "TELEGRAM"
                    },
                    {
                        "image": {
                            "imageUri": webhook_response2
                        },
                        "platform": "TELEGRAM"
                    },
                    {
                        "image": {
                            "imageUri": webhook_response3
                        },
                        "platform": "TELEGRAM"
                    },
                    {
                        "image": {
                            "imageUri": webhook_response4
                        },
                        "platform": "TELEGRAM"
                    },
                    {
                        "image": {
                            "imageUri": webhook_response5
                        },
                        "platform": "TELEGRAM"
                    },
                    {
                        "platform": "TELEGRAM",
                        "text": {
                            "text": [
                                "Do you have any other queries?",
                            ],
                            "text": [
                                "Do you have any questions?",
                            ],
                            "text": [
                                "Is there anything else that I can help you with?"
                            ]
                        }
                    },
                    {
                        "payload": {
                            "metadata": {
                                "templateId": "9",
                                "contentType": "300",
                                "payload": [
                                    {
                                        "caption": "Total Cases Distribution",
                                        "url": webhook_response1
                                    },
                                    {
                                        "url": webhook_response2,
                                        "caption": "Daily Confirmed Cases"
                                    },
                                    {
                                        "caption": "Daily Active Cases",
                                        "url": webhook_response3
                                    },
                                    {
                                        "caption": "Daily Recovered",
                                        "url": webhook_response4
                                    },
                                    {
                                        "url": webhook_response5,
                                        "caption": "Daily Deaths"
                                    }
                                ]
                            },
                            "platform": "kommunicate"
                        }
                    },
                    {
                        "payload": {
                            "message": "Do you have any other queries?",
                            "platform": "kommunicate"
                        }
                    }
                ]
            }
        return {
            "fulfillmentMessages": [

                {
                    "image": {
                        "imageUri": webhook_response1
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "platform": "ACTIONS_ON_GOOGLE",
                    "basicCard": {
                        "image": {
                            "imageUri": webhook_response1,
                            "accessibilityText": "Chart"
                        }
                    }
                },
                {
                    "platform": "ACTIONS_ON_GOOGLE",
                    "text": {
                        "text": [
                            "Do you have any other queries?",
                        ],
                        "text": [
                            "Do you have any questions?",
                        ],
                        "text": [
                            "Is there anything else that I can help you with?"
                        ]
                    }
                },
                {
                    "platform": "TELEGRAM",
                    "text": {
                        "text": [
                            "Do you have any other queries?",
                        ],
                        "text": [
                            "Do you have any questions?",
                        ],
                        "text": [
                            "Is there anything else that I can help you with?"
                        ]
                    }
                }
            ]
        }

    elif intent == 'search_world':
        world_data = Api().getWorldData()
        deltaconfirmed = world_data[0]['deltaconfirmed']
        confirmed = world_data[0]['confirmed']
        deltaactive = world_data[0]['deltaactive']
        active = world_data[0]['active']
        deltarecovered = world_data[0]['deltarecovered']
        recovered = world_data[0]['recovered']
        recovery_rate = round(int(recovered) / int(confirmed) * 100, 2)
        deltadeaths = world_data[0]['deltadeaths']
        deaths = world_data[0]['deaths']
        fatality_rate = world_data[0]['fatality_rate']
        webhook_response = "Total Cases      : {} ".format(confirmed) + "\n" + \
                           "New Cases        : {} ".format(deltaconfirmed) + "\n" + \
                           "Active Cases     : {} ".format(active) + "\n" + \
                           "New Active Cases : {} ".format(deltaactive) + "\n" + \
                           "Recovered        : {} ".format(recovered) + "\n" + \
                           "New Recovered    : {} ".format(deltarecovered) + "\n" + \
                           "Recovery Rate    : {}%".format(recovery_rate) + "\n" + \
                           "Total Deaths     : {} ".format(deaths) + "\n" + \
                           "New Deaths       : {} ".format(deltadeaths) + "\n" + \
                           "Fatality Rate    : {}%".format(fatality_rate)

        telegram_text = '```\n' + webhook_response + '\n```'
        Log().saveConversations(session_id, query_text, "Worldwide Data", webhook_response, intent, db)

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
                            "Do you want to see chart(s)?"
                        ]
                    }
                },
                {
                    "payload": {
                        "telegram": {
                            "text": telegram_text,
                            "parse_mode": "Markdown"
                        }
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "platform": "TELEGRAM",
                    "text": {
                        "text": [
                            "Do you want to see chart(s)?"
                        ]
                    }
                }
            ]
        }

    elif intent == 'search_world - yes':
        world_data = Api().getWorldData()
        active = world_data[0]['active']
        recovered = world_data[0]['recovered']
        deaths = world_data[0]['deaths']
        data = [active, recovered, deaths]
        labels = 'active', 'recovered', 'deaths'
        title = 'Total World Cases'
        file_path1 = Plot().donut_chart(data, labels, title, session_id)
        webhook_response1 = "https://radiant-thicket-13412.herokuapp.com/" + file_path1
        Log().saveConversations(session_id, query_text, "Worldwide Data", webhook_response1, intent, db)
        return {
            "fulfillmentMessages": [
                {
                    "image": {
                        "imageUri": webhook_response1
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "platform": "TELEGRAM",
                    "text": {
                        "text": [
                            "Do you have any other queries?",
                        ],
                        "text": [
                            "Do you have any questions?",
                        ],
                        "text": [
                            "Is there anything else that I can help you with?"
                        ]
                    }
                },
                {
                    "platform": "ACTIONS_ON_GOOGLE",
                    "basicCard": {
                        "image": {
                            "imageUri": webhook_response1,
                            "accessibilityText": "Chart"
                        }
                    }
                },
                {
                    "platform": "ACTIONS_ON_GOOGLE",
                    "text": {
                        "text": [
                            "Do you have any other queries?",
                        ],
                        "text": [
                            "Do you have any questions?",
                        ],
                        "text": [
                            "Is there anything else that I can help you with?"
                        ]
                    }
                }
            ]
        }

    elif intent == 'today_cases':
        today_summary = Api().getTodayData()
        telegram_text = "State".ljust(5) + "|" + "Conf.".rjust(5) + "|" + "Rec.".rjust(5) + "|" + "Died".rjust(5) + "|\n"
        telegram_text += "-" * 24 + "\n"
        default_text = '*********'
        for data in today_summary:
            default_text += "*********\n" + "State         : {} ".format(data['state']) + "\n" + \
                            "New Cases      : {} ".format(data['deltaconfirmed']) + "\n" + \
                            "Recovered        : {} ".format(data['deltarecovered']) + "\n" + \
                            "Deaths     : {} ".format(data['deltadeaths']) + "\n*********"

            telegram_text += data['statecode'].ljust(5, ' ') + "|" + data['deltaconfirmed'].rjust(5, ' ') + "|" + data[
                'deltarecovered'].rjust(5, ' ') + "|" + data['deltadeaths'].rjust(5, ' ') + "|" + "\n"

        telegram_text = '```\n' + telegram_text + '\n```'
        webhook_response = default_text+'*********'

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
                            "Do you have any other queries?",
                        ],
                        "text": [
                            "Do you have any questions?",
                        ],
                        "text": [
                            "Is there anything else that I can help you with?"
                        ]
                    }
                },
                {
                    "payload": {
                        "telegram": {
                            "text": telegram_text,
                            "parse_mode": "Markdown"
                        }
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "platform": "TELEGRAM",
                    "text": {
                        "text": [
                            "Do you have any other queries?",
                        ],
                        "text": [
                            "Do you have any questions?",
                        ],
                        "text": [
                            "Is there anything else that I can help you with?"
                        ]
                    }
                }
            ]
        }

    elif intent == 'zone':
        state = parameters.get("geo-state")
        zone_data = Api().getZoneData(state)
        text = "Here is the zone wise breakup of state {}".format(state) + "\n\n"
        text += "District".ljust(16) + "| " + "Zone".ljust(6) + "\n"
        text += "-" * 28 + "\n"
        for zone in zone_data:
            if zone['zone'] == 'Green':
                text += zone['district'].ljust(16) + "| " + zone['zone'].ljust(6) + ' 🟢 ' + "\n"
            elif zone['zone'] == 'Red':
                text += zone['district'].ljust(16) + "| " + zone['zone'].ljust(6) + ' 🔴 ' + "\n"
            elif zone['zone'] == 'Orange':
                text += zone['district'].ljust(16) + "| " + zone['zone'].ljust(6) + ' 🟠 ' + "\n"
        telegram_text = '```\n' + text + '\n```'
        webhook_response = text

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
                            "Do you have any other queries?",
                        ],
                        "text": [
                            "Do you have any questions?",
                        ],
                        "text": [
                            "Is there anything else that I can help you with?"
                        ]
                    }
                },
                {
                    "payload": {
                        "telegram": {
                            "text": telegram_text,
                            "parse_mode": "Markdown"
                        }
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "platform": "TELEGRAM",
                    "text": {
                        "text": [
                            "Do you have any other queries?",
                        ],
                        "text": [
                            "Do you have any questions?",
                        ],
                        "text": [
                            "Is there anything else that I can help you with?"
                        ]
                    }
                }
            ]
        }

    elif intent == "containment_area":
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Please Share your location"
                        ]

                    }
                },
                {
                    "payload": {
                        "google": {
                            "expectUserResponse": True,
                            "systemIntent": {
                                "intent": "actions.intent.PERMISSION",
                                "data": {
                                    "@type": "type.googleapis.com/google.actions.v2.PermissionValueSpec",
                                    "optContext": "To address you by name and know your location",
                                    "permissions": [
                                        "NAME",
                                        "DEVICE_PRECISE_LOCATION"
                                    ]
                                }
                            }
                        }
                    }
                }
            ]
        }

    elif intent == "user_location":
        webhook_response = "Hello"
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
                            "Do you have any other queries?",
                        ],
                        "text": [
                            "Do you have any questions?",
                        ],
                        "text": [
                            "Is there anything else that I can help you with?"
                        ]
                    }
                },
                {
                    "platform": "ACTIONS_ON_GOOGLE",
                    "text": {
                        "text": [
                            "Do you have any other queries?",
                        ],
                        "text": [
                            "Do you have any questions?",
                        ],
                        "text": [
                            "Is there anything else that I can help you with?"
                        ]
                    }
                }
            ]
        }

    elif intent == "summary":
        state = parameters.get("geo-state")
        country = parameters.get("geo-country")
        if state:
            state_summary = Api().getStateSummary(state)
            telegram_text = "District".ljust(10) + "|" + "Conf.".rjust(5) + "|" + "Actv.".rjust(5) + "|" + "Rec.".rjust(
                5) + "|" + "Died".rjust(5) + "|\n"
            telegram_text += "-" * 24 + "\n"
            default_text = '*********'
            for summary in state_summary:
                default_text += "*********\n" + "District         : {} ".format(summary['district']) + "\n" + \
                                    "Total Cases      : {} ".format(summary['confirmed']) + "\n" + \
                                    "Active Cases     : {} ".format(summary['active']) + "\n" + \
                                    "Recovered        : {} ".format(summary['recovered']) + "\n" + \
                                    "Total Deaths     : {} ".format(summary['deceased']) + "\n*********"

                telegram_text += str(summary['district']).ljust(10, ' ') + "|" + str(summary['confirmed']).rjust(5,
                                                                                                        " ") + "|" + str(
                    summary['active']).rjust(5, ' ') + "|" + str(summary['recovered']).rjust(5, ' ') + "|" + str(
                    summary['deceased']).rjust(5, ' ') + "|" + "\n"
            telegram_text = '```\n' + telegram_text + '\n```'
            webhook_response = default_text+'*********'
        else:
            country_summary = Api().getCountrySummary()
            telegram_text = "St".ljust(2) + "|" + "Conf.".rjust(6) + "|" + "Actv.".rjust(6) + "|" + "Rec.".rjust(
                6) + "|" + "Died".rjust(4) + "|\n"
            telegram_text += "-" * 24 + "\n"
            default_text = '*********'
            for summary in country_summary:
                default_text += "*********\n" + "State            : {} ".format(summary['state']) + "\n" + \
                                "Total Cases      : {} ".format(summary['confirmed']) + "\n" + \
                                "Active Cases     : {} ".format(summary['active']) + "\n" + \
                                "Recovered        : {} ".format(summary['recovered']) + "\n" + \
                                "Total Deaths     : {} ".format(summary['deaths']) + "\n*********"

                telegram_text += str(summary['statecode']).ljust(2, ' ') + "|" + str(summary['confirmed']).rjust(6,
                                                                                                     ' ') + "|" + str(
                    summary['active']).rjust(6, ' ') + "|" + str(summary['recovered']).rjust(6, ' ') + "|" + str(
                    summary['deaths']).rjust(4, ' ') + "|" + "\n"

            telegram_text = '```\n' + telegram_text + '\n```'
            webhook_response = default_text+'*********'

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
                            "Do you want me to send the detailed report on your e-mail address?"
                        ]

                    }
                },
                {
                    "payload": {
                        "telegram": {
                            "text": telegram_text,
                            "parse_mode": "Markdown"
                        }
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "platform": "TELEGRAM",
                    "text": {
                        "text": [
                            "Do you want to send the detailed report on your e-mail address?"
                        ]
                    }
                }
            ]
        }

    elif intent == "send_email":
        fulfillmentText = result.get("fulfillmentText")
        Log().saveConversations(session_id, query_text, parameters, fulfillmentText, intent, db)
        Log().saveContactDetails(name, email, db)
        configureEmail(name, email)
        return True

    elif intent == "Welcome" or intent == "continue_conversation" or intent == "end_conversation" or intent == "faq" or intent == "Fallback":
        fulfillmentText = result.get("fulfillmentText")
        Log().saveConversations(session_id, query_text, None, fulfillmentText, intent, db)
        return True


# if __name__ == "__main__":
#     app.run(port=5000, debug=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port, host='0.0.0.0')
