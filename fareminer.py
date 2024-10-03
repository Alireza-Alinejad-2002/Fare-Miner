import argparse
from myfunctions import (
    GetDates,
    GetFlightDistance,
    GetGMTDateTime,
    get_dollar,
)
from Respina24 import GetDomesticFare_respina, GetInterFare_respina
from Alibaba import GetDomesticFare_alibaba, GetInterFare_alibaba

# How to use: --> python ./fareminer.py -d thr tbz -s 2023-11-03 -e 2023-11-18 <--

parser = argparse.ArgumentParser()
parser.add_argument("origin", type=str, help="Departure city IATA code like THR, TBZ")
parser.add_argument(
    "destination", type=str, help="Arrival city IATA code like THR, TBZ"
)
parser.add_argument(
    "--domestic", "-d", action="store_true", help="Get fares for domestic flights"
)
parser.add_argument(
    "--international",
    "-i",
    action="store_true",
    help="Get fares for internationl flights",
)
parser.add_argument(
    "--start",
    "-s",
    type=str,
    help="Date range start (2023-10-09) (leave emtpy for getting today' flights )",
)
parser.add_argument(
    "--end",
    "-e",
    type=str,
    help="Date range end (2023-10-01) (leave it if you want to get the fares only on the start date)",
)
parser.add_argument("--output", "-o", type=str, help="output path")
args = parser.parse_args()
try:
    distance = GetFlightDistance(args.origin, args.destination)
except:
    distance = 0
    print("GetFlightDistance doesn't respond.")
try:
    ratio = get_dollar()
except:
    ratio = 2.37e-05
    print("get_dollar doesn't respond.")

if args.domestic:
    dates = GetDates(args.start, args.end)
    for date in dates:
        # GetDomesticFare_respina(args.origin, args.destination, distance, ratio = get_dollar(), date=date, output=args.output)
        GetDomesticFare_alibaba(
            args.origin,
            args.destination,
            distance,
            ratio,
            date=date,
            output=args.output,
        )


elif args.international:
    dates = GetDates(args.start, args.end)
    for date in dates:
        # GetInterFare_respina(args.origin, args.destination, distance, ratio = get_dollar(), date=date, output=args.output)
        GetInterFare_alibaba(
            args.origin,
            args.destination,
            distance,
            ratio,
            date=date,
            output=args.output,
        )
else:
    print("Determine your flight type (international/domestic)")
