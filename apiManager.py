import requests
import json
import logging
from datetime import datetime


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler('apiManager.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class Api:
    def __init__(self):
        self.national_data = "https://api.covid19india.org/data.json"
        self.state_daily = "https://api.covid19india.org/states_daily.json"
        self.districts_daily = "https://api.covid19india.org/districts_daily.json"
        self.state_districts_wise = "https://api.covid19india.org/state_district_wise.json"
        self.state_test_data = "https://api.covid19india.org/state_test_data.json"
        self.zone_data = "https://api.covid19india.org/zones.json"

    def getStateData(self, state_name):
        # url = "https://api.covid19india.org/data.json"
        url = self.national_data
        try:
            response = requests.request("GET", url)
            logger.info('getStateData connection successful')
        except ConnectionRefusedError:
            logger.exception("Connection refused")
            logger.info('getStateData connection failed')
            return None
        else:
            data = json.loads(response.text)
            statewise_data = data['statewise']
            for i in range(len(statewise_data)):
                if statewise_data[i]['state'] == state_name:
                    state_data = []
                    info = {
                        "confirmed": statewise_data[i]['confirmed'],
                        "deltaconfirmed": statewise_data[i]['deltaconfirmed'],
                        "active": statewise_data[i]['active'],
                        "recovered": statewise_data[i]['recovered'],
                        "deltarecovered": statewise_data[i]['deltarecovered'],
                        "deaths": statewise_data[i]['deaths'],
                        "deltadeaths": statewise_data[i]['deltadeaths'],
                        "lastupdatedtime": statewise_data[i]['lastupdatedtime']
                    }
                    state_data.append(info)
                    logging.info('getStateData stats retrieval: SUCCESS')
                    break
            else:
                logger.info(state_name+" state not found")
                logger.info('getStateData stats retrieval: FAILED')
                return None
            return state_data

    def dailyStateData(self, state_name):
        # url = "https://api.covid19india.org/states_daily.json"
        url = self.state_daily
        try:
            response = requests.request("GET", url)
            logger.info('dailyStateData connection successful')
        except ConnectionRefusedError:
            logger.exception("Connection refused")
            logger.info('dailyStateData connection failed')
            return None
        else:
            data = json.loads(response.text)
            time_series = data['states_daily']

            with open('state_code.json') as f:
                state_name_code = json.load(f)

            for key, value in state_name_code.items():
                if value == state_name:
                    state_code = key.lower()
                    break
            else:
                state_code = None
                logger.debug(state_name + " state not found")

            date = []
            daily_confirmed = []
            daily_recovered = []
            daily_deaths = []

            if state_code:
                for i in time_series[144:]:
                    if i['date'] not in date:
                        date.append(i['date'])
                    if i['status'] == 'Confirmed':
                        daily_confirmed.append(i[state_code])
                    if i['status'] == 'Recovered':
                        daily_recovered.append(i[state_code])
                    if i['status'] == 'Deceased':
                        daily_deaths.append(i[state_code])
                logger.info('dailyStateData stats retrieval: SUCCESSFUL')

                date = [date.replace('-20', '') for date in date]

                daily_active = []
                zip_object = zip(daily_confirmed, daily_recovered, daily_deaths)
                for list1_i, list2_i, list3_i in zip_object:
                    daily_active.append(str(int(list1_i) - int(list2_i) - int(list3_i)))

                return date, daily_confirmed, daily_active, daily_recovered, daily_deaths

            else:
                logger.info('dailyStateData stats retrieval: FAILED')
                return None

    def getDistrictData(self, district_name):
        # url = "https://api.covid19india.org/state_district_wise.json"
        url = self.state_districts_wise
        try:
            response = requests.request("GET", url)
            logger.info('getDistrictData connection successful')
        except ConnectionRefusedError:
            logger.exception("Connection refused")
            logger.info('getDistrictData connection failed')
            return None
        else:
            districtwise_data = json.loads(response.text)
            for key, value in districtwise_data.items():
                if district_name in districtwise_data[key]['districtData']:
                    district_data = []
                    info = {
                        "confirmed": districtwise_data[key]['districtData'][district_name]['confirmed'],
                        "deltaconfirmed": districtwise_data[key]['districtData'][district_name]['delta']['confirmed'],
                        "active": districtwise_data[key]['districtData'][district_name]['active'],
                        "recovered": districtwise_data[key]['districtData'][district_name]['recovered'],
                        "deltarecovered": districtwise_data[key]['districtData'][district_name]['delta']['recovered'],
                        "deaths": districtwise_data[key]['districtData'][district_name]['deceased'],
                        "deltadeaths": districtwise_data[key]['districtData'][district_name]['delta']['deceased']
                    }
                    district_data.append(info)
                    logging.info('getDistrictData stats retrieval: SUCCESS')
                    break
            else:
                logger.info(district_name+" district not found")
                logger.info('getDistrictData stats retrieval: FAILED')
                return None
            return district_data

    def totalDistrictData(self, district_name):
        # url = "https://api.covid19india.org/districts_daily.json"
        url = self.districts_daily
        try:
            response = requests.request("GET", url)
            logger.info('totalDistrictData connection successful')
        except ConnectionRefusedError:
            logger.exception("Connection refused")
            logger.info('totalDistrictData connection failed')
            return None
        else:
            data = json.loads(response.text)
            time_series = data['districtsDaily']
            for key, value in time_series.items():
                if district_name in data['districtsDaily'][key].keys():
                    date = []
                    total_confirmed = []
                    total_recovered = []
                    total_deaths = []
                    total_active = []
                    for i in data['districtsDaily'][key][district_name][10:]:
                        date.append(i['date'])
                        total_confirmed.append(i['confirmed'])
                        total_deaths.append(i['deceased'])
                        total_recovered.append(i['recovered'])
                        total_active.append(i['active'])
                    date = [datetime.strptime(i, '%Y-%m-%d') for i in date]
                    date = [str(datetime_object.date().day) + " " + datetime_object.date().strftime("%b") for datetime_object in
                            date]
                    logging.info('totalDistrictData stats retrieval: SUCCESS')
                    break
            else:
                logger.info(district_name + " district not found")
                logger.info('totalDistrictData stats retrieval: FAILED')
                return None
            return date, total_confirmed, total_active, total_recovered, total_deaths

    def getCountryData(self, country_name):
        url = "https://covid-193.p.rapidapi.com/statistics"
        querystring = {"country": country_name}
        headers = {
            'x-rapidapi-host': "covid-193.p.rapidapi.com",
            'x-rapidapi-key': "402e0c53bbmsh57ccc36c23433adp120789jsnda5a9d462961"
        }
        try:
            response = requests.request("GET", url, headers=headers, params=querystring)
            logger.info('getCountryData connection successful')
        except ConnectionRefusedError:
            logger.exception("Connection refused")
            logger.info('getCountryData connection failed')
            return None
        else:
            js = json.loads(response.text)
            result = js['response'][0]

            country_data = []
            info = {
                "confirmed": result['cases']['total'],
                "deltaconfirmed": result['cases']['new'],
                "active": result['cases']['active'],
                "critical": result['cases']['critical'],
                "recovered": result['cases']['recovered'],
                "deaths": result['deaths']['total'],
                "deltadeaths": result['deaths']['new'],
                "tests": result['tests']['total']
            }
            country_data.append(info)
            logging.info('getCountryData stats retrieval: SUCCESS')
            return country_data

    def dailyCountryData(self):
        # url = "https://api.covid19india.org/data.json"
        url = self.national_data
        try:
            response = requests.request("GET", url)
            logger.info('dailyCountryData connection successful')
        except ConnectionRefusedError:
            logger.exception("Connection refused")
            logger.info('dailyCountryData connection failed')
            return None
        else:
            data = json.loads(response.text)
            time_series = data['cases_time_series']
            date = []
            daily_confirmed = []
            daily_recovered = []
            daily_deaths = []
            daily_active = []
            for i in time_series[92:]:
                date.append(i['date'])
                daily_confirmed.append(i['dailyconfirmed'])
                daily_deaths.append(i['dailydeceased'])
                daily_recovered.append(i['dailyrecovered'])
                daily_active.append(int(i['totalconfirmed']) - int(i['totalrecovered']) - int(i['totalrecovered']))
            logging.info('dailyCountryData stats retrieval: SUCCESS')
            return date, daily_confirmed, daily_active, daily_recovered, daily_deaths

    def getWorldData(self):
        url = "https://covid-19-statistics.p.rapidapi.com/reports/total"
        headers = {
            "x-rapidapi-host": "covid-19-statistics.p.rapidapi.com",
            "x-rapidapi-key": "402e0c53bbmsh57ccc36c23433adp120789jsnda5a9d462961"
        }
        try:
            response = requests.request("GET", url, headers=headers)
            logger.info('getWorldData connection successful')
        except ConnectionRefusedError:
            logger.exception("Connection refused")
            logger.info('getWorldData connection failed')
            return None
        else:
            js = json.loads(response.text)
            result = js.get('data')

            world_data = []
            info = {
                "confirmed": result['confirmed'],
                "deltaconfirmed": result['confirmed_diff'],
                "active": result['active'],
                "deltaactive": result['active_diff'],
                "recovered": result['recovered'],
                "deltarecovered": result['recovered_diff'],
                "deaths": result['deaths'],
                "deltadeaths": result['deaths_diff'],
                "fatality_rate": result['fatality_rate']
            }
            logging.info('getWorldData stats retrieval: SUCCESS')
            world_data.append(info)
            return world_data

    def getTestData(self, state_name):
        # url = "https://api.covid19india.org/state_test_data.json"
        url = self.state_test_data
        try:
            response = requests.request("GET", url)
            logger.info('getTestData connection successful')
        except ConnectionRefusedError:
            logger.exception("Connection refused")
            logger.info('getTestData connection failed')
            return None
        else:
            test_data = json.loads(response.text)
            state_wise_test_data = test_data.get('states_tested_data')
            try:
                target_state_test_data = list(filter(lambda person: person['state'] == state_name, state_wise_test_data))
            except KeyError:
                logger.debug(state_name + " state not found")
                logger.info('getTestData stats retrieval: FAILED')
                return None
            else:
                recent_data = target_state_test_data[-1]
                one_day_before_data = target_state_test_data[-2]

                test_data = []
                info = {
                    "total_tested": recent_data['totaltested'],
                    "positive": recent_data['positive'],
                    "negative": recent_data['negative'],
                    "uncomfirmed": recent_data['unconfirmed'],
                    "positivity_rate": round((int(recent_data['positive']) / int(recent_data['totaltested'])) * 100, 2),
                    "updated_on": recent_data['updatedon']
                }
                try:
                    delta_test = int(recent_data['totaltested']) - int(one_day_before_data['totaltested'])
                except TypeError:
                    delta_test = ''
                try:
                    delta_positive = int(recent_data['positive']) - int(one_day_before_data['positive'])
                except TypeError:
                    delta_positive = ''

                info["delta_test"] = delta_test
                info["delta_positive"] = delta_positive
                test_data.append(info)
                logging.info('getTestData stats retrieval: SUCCESS')
                return test_data

    def getTodayData(self):
        url = self.national_data
        try:
            response = requests.request("GET", url)
            logger.info('getTodayData connection successful')
        except ConnectionRefusedError:
            logger.exception("Connection refused")
            logger.info('getTodayData connection failed')
            return None
        else:
            data = json.loads(response.text)
            state_wise = data['statewise']
            today_summary = []
            for i in state_wise:
                if i['deltaconfirmed'] == 0 and i['deltarecovered'] == 0 and i['deltadeaths'] == 0:
                    pass
                else:
                    info = {
                        "deltaconfirmed": i['deltaconfirmed'],
                        "deltarecovered": i['deltarecovered'],
                        "deltadeaths": i['deltadeaths'],
                        "state": i['state'],
                        "statecode": i['statecode']
                    }
                    today_summary.append(info)
                    logging.info('getTodayData stats retrieval: SUCCESS')
            return today_summary

    def getZoneData(self, state_name):
        url = self.zone_data
        try:
            response = requests.request("GET", url)
            logger.info('getZoneData connection successful')
        except ConnectionRefusedError:
            logger.exception("connect refused")
            logger.info('getZoneData connection failed')
            return None
        else:
            data = json.loads(response.text)
            zone_data = data['zones']
            try:
                target_state_zone_data = list(filter(lambda state: state['state'] == state_name, zone_data))
            except KeyError:
                logger.exception(self, state_name+ " state not found")
                logger.info('getZoneData stats retrieval: FAILED')
                return None
            else:
                zone_wise = []
                for i in target_state_zone_data:
                    info = {
                        "district": i['district'],
                        "zone": i['zone'],
                    }
                    zone_wise.append(info)
                    logging.info('getZoneData stats retrieval: SUCCESS')
                return zone_wise

    def getContainmentData(self, location):
        key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJtYWlsSWRlbnRpdHkiOiJ2aXZla3Zpa2FzaC44MDhAZ21haWwuY29tIn0.enPk60nVl_4A6JkfV465DkkyRn8uTct8oQFhQeKn7gw"
        API_ENDPOINT = 'https://data.geoiq.io/dataapis/v1.0/covid/locationcheck'
        payload = {"key": key,
                   "latlngs": location}
        json_payload = json.dumps(payload)
        r = requests.post(url=API_ENDPOINT, data=json_payload)
        containment_data = json.loads(r.text).get('data')
        return containment_data

    def getStateSummary(self, state_name):
        # url = 'https://api.covid19india.org/districts_daily.json'
        url = self.districts_daily
        try:
            response = requests.request("GET", url)
            logger.info('getStateSummary connection successful')
        except ConnectionRefusedError:
            logger.exception("Connection refused")
            logger.info('getStateSummary connection failed')
            return None
        else:
            data = json.loads(response.text)
            districts_daily = data['districtsDaily']
            try:
                filtered_dict = {key: value for (key, value) in districts_daily.items() if state_name in key}
            except KeyError:
                logger.exception(state_name + " state not found")
                logger.info('getStateSummary stats retrieval: FAILED')
                return None
            else:
                target_state_districts_data = list(filtered_dict.values())
                district_wise_data = []
                for key, value in target_state_districts_data[0].items():
                    info = {
                        "district": key,
                        "active": value[-1]['active'],
                        "confirmed": value[-1]['confirmed'],
                        "deceased": value[-1]['deceased'],
                        "recovered": value[-1]['recovered']

                    }
                    district_wise_data.append(info)
                    logging.info('getStateSummary stats retrieval: SUCCESS')
                return district_wise_data

    def getCountrySummary(self):
        # url = "https://api.covid19india.org/data.json"
        url = self.national_data
        try:
            response = requests.request("GET", url)
            logger.info('getCountrySummary connection successful')
        except ConnectionRefusedError:
            logger.exception("Connection refused")
            logger.info('getCountrySummary connection failed')
            return None
        else:
            data = json.loads(response.text)
            state_wise = data['statewise']
            state_wise_data = []
            for state in state_wise:
                info = {
                    "state": state['state'],
                    "statecode": state['statecode'],
                    "confirmed": state['confirmed'],
                    "deltaconfirmed": state['confirmed'],
                    "active": state['active'],
                    "recovered": state['recovered'],
                    "deltarecovered": state['deltarecovered'],
                    "deaths": state['deaths'],
                    "deltadeaths": state['deltadeaths']
                }
                state_wise_data.append(info)
                logging.info('getCountrySummary stats retrieval: SUCCESS')
            return state_wise_data
