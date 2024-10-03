import requests, csv
from datetime import datetime, timedelta
from myfunctions import ToJalali, GetGMTDateTime, export_data
from time import sleep

Airlines = {
    "ماهان": "Mahan Air",
    "ایران ایر": "Iran Air",
    "زاگرس": "Zagros Airline",
    "کیش ایر": "Kish Air",
    "کاسپین": "Caspian Airlines",
    "آتا": "ATA Airlines",
    "سهند": "Saha Airlines",
    "آسمان": "Aseman Airlines",
    "تابان": "Taban Air",
    "پارس جت": "Pars Jet Airways",
    "وارش": "Varesh Airlines",
    "قشم ایر": "Qeshm Air",
    "ایران ایرتور": "Iran Airtour",
    "چابهار": "Chabahar Airlines",
    "کارون": "Karun Air",
    "پویا": "Pouya Air",
    "اروان": "Air One Airline",
    "ساها": "Saha Airlines",
    "سپهران": "Sepehran",
    "": "-",
}

flight_classes = {
    "اکونومی": "Economy",
    "بیزینس": "Business",
    "پرمیوم اکونومی": "Premium Economy",
    "پرمیوم بیزینس": "Premium Business",
    "فرست": "First class",
    "پرمیوم فرست": "Premium First",
    "": "-",
}

Aircrafts = {
    "TRS": "Train",
    "77W": "BOEING 777-300ER",
    "332": "Airbus A330-200",
    "7M8": "Boeing 737 MAX 8",
    "320": "Airbus A320",
    "321": "Airbus A321",
    "73J": "Boeing 737-900ER",
    "32B": "Airbus A321-200",
    "738": "Boeing 737-800",
    "787": "Boeing 787 Dreamliner",
    "744": "Boeing 747-400",
    "763": "Boeing 767-300ER",
    "77L": "Boeing 777-200LR",
    "788": "Boeing 787-8",
    "789": "Boeing 787-9",
    "CRJ": "Bombardier CRJ900",
    "E75": "Embraer E175",
    "E90": "Embraer E190",
    "ATR": "ATR 72-600",
    "DH8D": "De Havilland Dash 8-400",
    "MD88": "McDonnell Douglas MD-88",
    "MD90": "McDonnell Douglas MD-90",
    "220": "Airbus A220-100",
    "319": "Airbus A319",
    "318": "Airbus A318",
    "310": "Airbus A310",
    "300": "Airbus A300-600R",
    "380": "Airbus A380-800",
    "7478": "Boeing 747-8 Intercontinental",
    "777X": "Boeing 777X",
    "757": "Boeing 757-200",
    "767": "Boeing 767-400ER",
    "ERJ": "Embraer ERJ-145",
    "F100": "Fokker 100",
    "B1900": "Beechcraft 1900D",
    "C172": "Cessna 172",
    "351": "Airbus A350-1000",
    "359": "Airbus A350-900",
    "73H": "Boeing 737-800",
    "343": "Airbus A340-300",
    "32A": "Airbus A320",
}

Airports = {
    "SAW": "Istanbul",
    "DXB": "Dubai",
    "IKA": "Tehran",
    "HAM": "Hamburg",
    "FRA": "Frankfurt",
    "VIE": "Vienna",
    "IST": "Istanbul",
    "DOH": "Doha",
    "LHR": "London",
    "ESB": "Ankara",
    "BCN": "Barcelona",
    "MUC": "Munich",
    "DUS": "Düsseldorf",
    "": "-",
}
City_name_d = {"bnd": "Bandar Abbas", "thr": "Tehran"}
City_name_i = {"ham": "HAMALL", "thr": "IKA"}


# Gets flight fares for domestic routes
def GetDomesticFare_alibaba(
    origin, destination, distance, ratio, date=str(datetime.now().date()), output=None
):
    print(f"{date}: Getting the data for {origin} => {destination}")

    if output is None:
        output = origin + "-" + destination

    request_header = {'Content-Type': 'application/json'}
    payload = {
        "origin": origin,
        "destination": destination,
        "departureDate": date,
        "adult": 1,
        "child": 0,
        "infant": 0,
    }
    request = requests.post(
        "https://ws.alibaba.ir/api/v1/flights/domestic/available",
        headers=request_header,
        json=payload,
    )
    i = 0
    while request.status_code != 200:
        i += 1
        if i == 5:
            break
        request = requests.post(
            "https://ws.alibaba.ir/api/v1/flights/domestic/available",
            headers=request_header,
            json=payload,
        )
        sleep(2)
    if request.status_code == 200:
        requestId = request.json()["result"]["requestId"]
        url = f"https://ws.alibaba.ir/api/v1/flights/domestic/available/{requestId}"
        response = requests.get(url)
        sleep(3)
        i = 0
        while response.status_code != 200:
            i += 1
            if i == 5:
                break
            response = requests.get(url)
            sleep(5)
        if response.status_code == 200:
            data = response.json()
            itineraries = data["result"]["departing"]
            if itineraries is None or itineraries == []:
                print(f"No flight on {date}")

            domestic_data = []
            for itinerary in itineraries:
                item = {}
                try:
                    if itinerary["statusName"] == "تکمیل ظرفیت":
                        continue
                    fare = itinerary["priceAdult"]
                    airline = itinerary["airlineName"]
                    if airline in Aircrafts:
                        airline = Airlines[airline]
                    aircraft = itinerary["aircraft"]
                    cabin = itinerary["classTypeName"]
                    departureDatetime = datetime.strptime(
                        itinerary["leaveDateTime"], "%Y-%m-%dT%H:%M:%S"
                    )
                    arrivalDatetime = datetime.strptime(
                        itinerary["arrivalDateTime"], "%Y-%m-%dT%H:%M:%S"
                    )
                    flightDuration = arrivalDatetime - departureDatetime

                    item["From"] = City_name_d[origin]
                    item["To"] = City_name_d[destination]
                    item["Total Time, hr:min"] = flightDuration
                    item["Total Distance, km"] = distance
                    item["Class"] = flight_classes[cabin]
                    item["Departure Date and Time"] = ToJalali(departureDatetime)
                    item["Arrival Date and Time"] = ToJalali(arrivalDatetime)
                    item["Aircraft Type"] = aircraft
                    item["Airline"] = Airlines[airline]
                    item["Cost (Toman)"] = fare / 10
                    item["Toman to USD Rate"] = ratio
                    item["Cost (USD)"] = "{:.2f}".format((fare / 10) * ratio)
                    domestic_data.append(item)
                except:
                    print("Something went wrong for a ticket.")
            export_data(domestic_data, output, "Domestic")
        else:
            print(
                "Failed to retrieve flight data. \nStatus code: ", response.status_code
            )
    else:
        print("Failed to retrieve flight data. \nStatus code: ", request.status_code)


# Gets flight fares for international routes
def GetInterFare_alibaba(
    origin, destination, distance, ratio, date=str(datetime.now().date()), output=None
):
    print(f"{date}: Getting the data for {origin} => {destination}")

    if output is None:
        output = origin + "-" + destination

    flightclasses = ["Economy", "Business"]
    for flightclass in flightclasses:
        print(f"{flightclass} Flights:")
        payload = {
            "infant": 0,
            "child": 0,
            "adult": 1,
            "departureDate": f"{date}",
            "origin": City_name_i[origin],
            "destination": City_name_i[destination],
            "flightClass": f"{flightclass}",
            "userVariant": "pricing-ist-v1-control",
        }
        request = requests.post(
            "https://ws.alibaba.ir/api/v1/flights/international/proposal-requests",
            json=payload,
        )
        i = 0
        while request.status_code != 200:
            i += 1
            if i == 3:
                break
            request = requests.post(
                "https://ws.alibaba.ir/api/v1/flights/international/proposal-requests",
                json=payload,
            )
            sleep(4)
        if request.status_code == 200:
            requestId = request.json()["result"]["requestId"]
            url = f"https://ws.alibaba.ir/api/v1/flights/international/proposal-requests/{requestId}"
            response = requests.get(url)
            sleep(7)
            i = 0
            while not response.json()["result"]["proposals"]:
                i += 1
                if i == 3:
                    break
                response = requests.get(url)
                sleep(8)
            if response.status_code == 200:
                data = response.json()
                itineraries = data["result"]["proposals"]
                if itineraries is None or itineraries == []:
                    print(f"No flight on {date}")

                inter_data = []
                i = 0
                for itinerary in itineraries:
                    item = {}
                    try:
                        i += 1
                        if (
                            len(itinerary["leavingFlightGroup"]["flightDetails"]) > 2
                        ):  # flights with 1 stop or less
                            i = i - 1
                            continue
                        if i > 24:  # 25 first tickets
                            continue
                        fare = itinerary["total"]
                        airline = itinerary["leavingFlightGroup"]["airlineName"]
                        aircraft_1 = itinerary["leavingFlightGroup"]["flightDetails"][
                            0
                        ]["aircraft"]
                        aircraft_2 = itinerary["leavingFlightGroup"]["flightDetails"][
                            1
                        ]["aircraft"]
                        if aircraft_1 in Aircrafts:
                            aircraft_1 = Aircrafts[aircraft_1]
                        if aircraft_2 in Aircrafts:
                            aircraft_2 = Aircrafts[aircraft_2]
                        flightNumber_1 = itinerary["leavingFlightGroup"][
                            "flightDetails"
                        ][0]["flightNumber"]
                        flightNumber_2 = itinerary["leavingFlightGroup"][
                            "flightDetails"
                        ][1]["flightNumber"]
                        departureCity = itinerary["leavingFlightGroup"][
                            "originCityName"
                        ]
                        departureAirport = itinerary["leavingFlightGroup"]["origin"]
                        stopCity = itinerary["leavingFlightGroup"]["flightDetails"][0][
                            "destinationName"
                        ]
                        stopAirport = itinerary["leavingFlightGroup"]["flightDetails"][
                            0
                        ]["destination"]
                        arrivalCity = itinerary["leavingFlightGroup"][
                            "destinationCityName"
                        ]
                        arrivalAirport = itinerary["leavingFlightGroup"]["destination"]
                        dep = datetime.strptime(
                            itinerary["leavingFlightGroup"]["departureDateTime"],
                            "%Y-%m-%dT%H:%M:%S",
                        )
                        departureDatetime = dep + timedelta(
                            hours=3, minutes=30
                        )  # Tehran(GMT+03:30)
                        arr = datetime.strptime(
                            itinerary["leavingFlightGroup"]["arrivalDateTime"],
                            "%Y-%m-%dT%H:%M:%S",
                        )
                        arrivalDatetime = arr + timedelta(hours=1)  # Hamburg(GMT+01:00)
                        duration = arrivalDatetime - departureDatetime

                        # my_list = [
                        #     departureCity,
                        #     departureAirport,
                        #     stopCity,
                        #     stopAirport,
                        #     arrivalCity,
                        #     arrivalAirport,
                        #     duration,
                        #     distance,
                        #     departureDatetime,
                        #     arrivalDatetime,
                        #     aircraft_1,
                        #     aircraft_2,
                        #     airline,
                        #     fare,
                        #     flightNumber_1,
                        #     flightNumber_2,
                        # ]
                        # for i in range(len(my_list)):
                        #     if my_list[i] is None or my_list[i] == []:
                        #         my_list[i] = "-"

                        item["From"] = departureCity + f" ({departureAirport})"
                        item["Stop"] = stopCity + f" ({stopAirport})"
                        item["To"] = arrivalCity + f" ({arrivalAirport})"
                        item["Total Time, hr:min"] = duration
                        item["Total Distance, km"] = distance
                        item["Class"] = flightclass
                        item["Departure Date and Time"] = departureDatetime  # GMT
                        item["Arrival Date and Time"] = arrivalDatetime  # GMT
                        item["Aircraft Type"] = aircraft_1 + " - " + aircraft_2
                        item["Airline"] = airline
                        item["Cost (Toman)"] = fare / 10
                        item["Toman to USD Rate"] = ratio
                        item["Cost (USD)"] = "{:.2f}".format((fare / 10) * ratio)
                        item["Flight Number"] = flightNumber_1 + " - " + flightNumber_2
                        inter_data.append(item)
                    except Exception as e:
                        print("Something went wrong for a ticket.", e)
                export_data(inter_data, output, "International")

            else:
                print(
                    "Failed to retrieve flight data. \nStatus code: ",
                    response.status_code,
                )
        else:
            print(
                "Failed to retrieve flight data. \nStatus code: ", request.status_code
            )
