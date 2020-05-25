import requests
import json


class Api:
    def __init__(self):
        pass

    def makeApiRequestForState(self, state_name):
        url = "https://api.covid19india.org/data.json"
        response = requests.request("GET", url)
        js = json.loads(response.text)
        state_wise = js['statewise']
        confirmed, deltaconfirmed, active, recovered, deltarecovered, deaths, deltadeaths = self.getStateData(state_wise,
                                                                                                         state_name)
        return confirmed, deltaconfirmed, active, recovered, deltarecovered, deaths, deltadeaths

    def getStateData(self, statewise_data, state_name):
        state_name = state_name.capitalize()
        for i in range(len(statewise_data)):
            if statewise_data[i]['state'] == state_name:
                confirmed = statewise_data[i]['confirmed']
                deltaconfirmed = statewise_data[i]['deltaconfirmed']
                active = statewise_data[i]['active']
                recovered = statewise_data[i]['recovered']
                deltarecovered = statewise_data[i]['deltarecovered']
                deaths = statewise_data[i]['deaths']
                deltadeaths = statewise_data[i]['deltadeaths']

        return confirmed, deltaconfirmed, active, recovered, deltarecovered, deaths, deltadeaths

    def makeApiRequestForDistrict(self, district_name):
        url = "https://api.covid19india.org/state_district_wise.json"
        response = requests.request("GET", url)
        district_wise = json.loads(response.text)
        confirmed, deltaconfirmed, active, recovered, deltarecovered, deaths, deltadeaths = self.getDistrictData(
            district_wise, district_name)
        return confirmed, deltaconfirmed, active, recovered, deltarecovered, deaths, deltadeaths

    def getDistrictData(self, districtwise_data, district_name):
        district_name = district_name.capitalize()
        for key, value in districtwise_data.items():
            if district_name in districtwise_data[key]['districtData']:
                confirmed = districtwise_data[key]['districtData'][district_name]['confirmed']
                deltaconfirmed = districtwise_data[key]['districtData'][district_name]['delta']['confirmed']
                active = districtwise_data[key]['districtData'][district_name]['active']
                recovered = districtwise_data[key]['districtData'][district_name]['recovered']
                deltarecovered = districtwise_data[key]['districtData'][district_name]['delta']['recovered']
                deaths = districtwise_data[key]['districtData'][district_name]['deceased']
                deltadeaths = districtwise_data[key]['districtData'][district_name]['delta']['deceased']
        return confirmed, deltaconfirmed, active, recovered, deltarecovered, deaths, deltadeaths

    def makeApiRequestForCounrty(self, country_name):
        url = "https://covid-193.p.rapidapi.com/statistics"
        querystring = {"country": country_name}
        headers = {
            'x-rapidapi-host': "covid-193.p.rapidapi.com",
            'x-rapidapi-key': "402e0c53bbmsh57ccc36c23433adp120789jsnda5a9d462961"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)

        js = json.loads(response.text)
        result = js['response'][0]

        confirmed = result['cases']['total']
        deltaconfirmed = result['cases']['new']
        active = result['cases']['active']
        recovered = result['cases']['recovered']
        deaths = result['deaths']['total']
        deltadeaths = result['deaths']['new']
        tests = result['tests']['total']

        return confirmed, deltaconfirmed, active, recovered, deaths, deltadeaths, tests

    def makeApiWorldwide(self):
        url = "https://covid-19-statistics.p.rapidapi.com/reports/total"
        headers = {
            "x-rapidapi-host": "covid-19-statistics.p.rapidapi.com",
            "x-rapidapi-key": "402e0c53bbmsh57ccc36c23433adp120789jsnda5a9d462961"
        }
        response = requests.request("GET", url, headers=headers)
        js = json.loads(response.text)
        result = js.get('data')

        confirmed = result['confirmed']
        deltaconfirmed = result['confirmed_diff']
        active = result['active']
        deltaactive = result['active_diff']
        recovered = result['recovered']
        deltarecovered = result['recovered_diff']
        deaths = result['deaths']
        deltadeaths = result['deaths_diff']
        fatality_rate = result['fatality_rate']

        return confirmed, deltaconfirmed, active, deltaactive, recovered, deltarecovered, deaths, deltadeaths, fatality_rate