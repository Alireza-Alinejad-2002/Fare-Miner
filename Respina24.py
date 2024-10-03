import requests, csv
from datetime import datetime
from myfunctions import ToJalali, GetGMTDateTime

# Gets flight fares for domestic routes
def GetDomesticFare_respina(origin, destination, distance, ratio, date=str(datetime.now().date()), output=None):
    
    print(f'{date}: Getting the data for {origin} => {destination}')
    
    if output is None: 
        output = origin + '_' + destination + '_'
    url = "https://respina24.ir/flight/availability"
    
    headers = {
        "Content-Type": "application/json",
    }
    
    payload = {
        "from": origin,
        "to": destination,
        "departureDate": date,
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        #print(data) #add
        itineraries = data.get('list', [])
        if itineraries is None or itineraries == []:
            print(f'No flight on {date}')

        with open(output + '.csv', 'a', newline='') as csvfile:
            fieldnames = ['From', 'To', 'Total Time, hr:min',
                        'Total Distance, km', 'Class',
                        'Departure Date and Time', 'Arrival Date and Time',
                        'Aircraft Type', 'Airline',
                        'Cost (Toman)', 'Toman to USD Rate', 'Cost (USD)']
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if csvfile.tell() == 0:
                writer.writeheader()
         
            for itinerary in itineraries:
                fare = itinerary.get('adultPrice')
                airline = itinerary.get('airlineName')
                aircraft = itinerary.get('aircraft')
                cabin = itinerary.get('cobin') + ' ' + itinerary.get('class')
                departureDatetime = datetime.strptime(itinerary.get('departureDate') + ' ' + itinerary.get('departureTime'), '%Y-%m-%d %H:%M') 
                arrivalDatetime = datetime.strptime(itinerary.get('departureDate') + ' ' + itinerary.get('arrivalTime'), '%Y-%m-%d %H:%M') 
                flightDuration = itinerary.get('flightDuration') 
                
                writer.writerow({
                    'From': origin,
                    'To': destination,
                    'Total Time, hr:min': flightDuration,
                    'Total Distance, km': distance,
                    'Class': cabin,
                    'Departure Date and Time': ToJalali(departureDatetime),
                    'Arrival Date and Time': ToJalali(arrivalDatetime),
                    'Aircraft Type': aircraft, 
                    'Airline': airline,
                    'Cost (Toman)': fare / 10,
                    'Toman to USD Rate': ratio,
                    'Cost (USD)': '{:.2f}'.format((fare/10)*ratio),
                })
                
    else:
        print('Failed to retrieve flight data. \nStatus code: ', response.status_code)
    

# Gets flight fares for international routes
def GetInterFare_respina(origin, destination, distance, ratio, date=str(datetime.now().date()), output=None):
    
    print(f'{date}: Getting the data for {origin} => {destination}')
    print(f'Press Ctrl + C to stop the script if you\'re happy with the results')
    
    if output is None: 
        output = origin + '_' + destination + '_' + str(datetime.now().date())
    firstUrl = "https://respina24.ir/internationalflight/getFlightAjax"
    secondUrl = "https://respina24.ir/internationalflight/getFlightAjax2"
    thirdUrl = "https://respina24.ir/internationalflight/getFlightAjaxPagination"
 
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
    }
    cabinTypes = {"1": "Economy", "3": "Business", "5": "First"}
    for cabinType in cabinTypes.keys():
            
        firstPayload = {
            "adult":"1",
            "child":"0",
            "infant":"0",
            "cabinType": cabinType,
            "tripType":"1",
            "itineries":[{
                "from":origin,"to":destination,
                "date":date,
                "fromIsCity":1,"toIsCity":1}],
            "cache":"1",
            "indexFlight":0,
            "searchId":0
        }
        
        response = requests.post(firstUrl, headers=headers, json=firstPayload)
        if response.status_code == 200:
            data = response.json()
            apilist = data.get('list', {})
            apiIds = apilist.keys()
            print(f'apiIds:\n{apiIds}')
            search_id = data.get('search_id')
            
            for apiId in apiIds:
                secondPayload = {
                    "api_id": apiId,
                    "api_name": "api",
                    "search_id": search_id
                } 
            
                secondResponse = requests.post(secondUrl, json=secondPayload, headers=headers)
                    
            if secondResponse.status_code == 200: 
                for stop in range(2):
                    
                    thirdPayload = {
                        "searchId": search_id,
                        "page": 1,
                        "filter": {
                            "outboundStops": [
                                str(stop)
                            ]
                        }
                    } 
                    
                    thirdResponse = requests.post(thirdUrl, json=thirdPayload, headers=headers)
                    data = thirdResponse.json()
                    flights = data.get('flights', [])
                    if flights is None or flights == []:
                        print(f'No {cabinTypes[cabinType]} {stop} stop  flight on {date}')
                    else:
                        print(f'{len(flights)} {cabinTypes[cabinType]} {stop} stop flights...')
                    with open(output + '.csv', 'a', newline='') as csvfile:
                        fieldnames = ['From', 'Stop', 'To', 'Total Time, hr:min',
                                    'Total Distance, km', 'Class',
                                    'Departure Date and Time (GMT)', 'Arrival Date and Time (GMT)',
                                    'Aircraft Type', 'Airline', 'Cost (Toman)',
                                    'Toman to USD Rate', 'Cost (USD)', 'Flight Number']
                        
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        if csvfile.tell() == 0:
                            writer.writeheader()
                        
                        for flight in flights:
                            masir = flight.get('masir', [])
                            legs = masir[0].get('legs', [])
                            outboundStops = flight.get('outboundStops')
                            
                            fare = flight.get('adultPrice')
                            cabin = legs[0].get('cabinTypeValue') 
                            airline = masir[0].get('AirlineName')
                            duration = masir[0].get('JourneyDuration')
                            flightNumbers = masir[0].get('flightNumbers')
                            
                            departureCity = masir[0].get('fromCityName')
                            departureAirport = masir[0].get('from')
                            departureDateTime = masir[0].get('DepartureDateTime') 
                            
                            if outboundStops == 1:
                                stopCity = legs[0].get('toCityName')
                                stopAirport = legs[0].get('to')
                                stopString = stopCity + ' (' + stopAirport + ')'
                            else: 
                                stopString = ''
                               
                            arrivalCity = masir[0].get('to')
                            arrivalAirport = masir[0].get('toCityName') 
                            arrivalDateTime = masir[0].get('ArrivalDateTime') 
                            writer.writerow({
                                'From': departureCity + ' (' + departureAirport + ')',
                                'Stop': stopString,
                                'To': arrivalCity + ' (' + arrivalAirport + ')',
                                'Total Time, hr:min': duration,
                                'Total Distance, km': distance,
                                'Class': cabin,
                                'Departure Date and Time (GMT)': GetGMTDateTime(departureCity, datetime.fromisoformat(departureDateTime)),
                                'Arrival Date and Time (GMT)': GetGMTDateTime(arrivalCity , datetime.fromisoformat(arrivalDateTime)),
                                'Aircraft Type': '', 
                                'Airline': airline,
                                'Cost (Toman)': fare / 10,
                                'Toman to USD Rate': ratio,
                                'Cost (USD)': '{:.2f}'.format((fare/10)*ratio),
                                'Flight Number': flightNumbers,
                            })
            else:
                print("getFlightAjax2 Failed")    
        else:
            print("getFlightAjax Failed")