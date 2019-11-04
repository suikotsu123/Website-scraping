import json
import requests
from lxml import html
from collections import OrderedDict
import argparse

debug = open("lol.txt","wb")

# miao = {"par", "tyo", "vie", "bcn", "mad"}
miao = {"vie"}

def parse(date1, date2):
	lists = []
	# try:
	for location in miao:
		url = "https://www.expedia.ca/Flights-Search?trip=roundtrip&leg1=from%3Ayul%2Cto%3A{0}%2Cdeparture%3A{1}TANYT&leg2=from%3A{0}%2Cto%3Ayul%2Cdeparture%3A{2}TANYT&passengers=adults%3A1%2Cchildren%3A0%2Cseniors%3A0%2Cinfantinlap%3AY&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.ca".format(location, date1, date2)
		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
		response = requests.get(url, headers=headers, verify=False)
		parser = html.fromstring(response.text)
		json_data_xpath = parser.xpath("//script[@id='cachedResultsJson']//text()")
		raw_json =json.loads(json_data_xpath[0] if json_data_xpath else '')
		flight_data = json.loads(raw_json["content"])
		flight_info  = OrderedDict()
		debug.write(response.content)
		
		price = 0
		for i in flight_data['legs'].keys():
			exact_price = flight_data['legs'][i].get('price',{}).get('totalPriceAsDecimal','')
			departure_location_city = flight_data['legs'][i].get('departureLocation',{}).get('airportCity','')
			if((price == 0 or price > exact_price) and departure_location_city == "Montreal"):
				price = exact_price
				departure_location_airport = flight_data['legs'][i].get('departureLocation',{}).get('airportCode','')
				
				departure_location_airport_code = flight_data['legs'][i].get('departureLocation',{}).get('airportCode','')
				
				arrival_location_airport = flight_data['legs'][i].get('arrivalLocation',{}).get('airportCode','')
				arrival_location_airport_code = flight_data['legs'][i].get('arrivalLocation',{}).get('airportCode','')
				arrival_location_city = flight_data['legs'][i].get('arrivalLocation',{}).get('airportCity','')
				airline_name = flight_data['legs'][i].get('carrierSummary',{}).get('airlineName','')
				
				no_of_stops = flight_data['legs'][i].get("stops","")
	
				if no_of_stops==0:
					stop = "Nonstop"
				else:
					stop = str(no_of_stops)+' Stop'
	
				departure = departure_location_airport+", "+departure_location_city
				arrival = arrival_location_airport+", "+arrival_location_city
				carrier = flight_data['legs'][i].get('timeline',[])[0].get('carrier',{})
				plane = carrier.get('plane','')
				plane_code = carrier.get('planeCode','')
				formatted_price = "{0:.2f}".format(exact_price)
	
				if not airline_name:
					airline_name = carrier.get('operatedBy','')
				
				departure_time = flight_data['legs'][i].get('departureTime',{}).get('date','') + '   ' + flight_data['legs'][i].get('departureTime',{}).get('time','')
				arrival_time = flight_data['legs'][i].get('arrivalTime',{}).get('date','') + '   ' + flight_data['legs'][i].get('arrivalTime',{}).get('time','')
	
		flight_info={'stops':stop,
			'ticket price':formatted_price,
			'departure':departure,
			'arrival':arrival,
			'airline':airline_name,
			'plane':plane,
			'Departure Time':departure_time,
			'Arrival Time': arrival_time,
			'plane code':plane_code
		}
		lists.append(flight_info)
	sortedlist = sorted(lists, key=lambda k: k['ticket price'],reverse=False)
	return sortedlist
		
	# except ValueError:
		# print ("Retrying...")
		
	return {"error":"failed to process the page",}

if __name__=="__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument('date1',help = 'DD/MM/YYYY')
	argparser.add_argument('date2',help = 'DD/MM/YYYY')

	args = argparser.parse_args()
	date1 = args.date1
	date2 = args.date2
	
	print (date1)
	print (date2)
	print ("Fetching flight details")
	scraped_data = parse(date1, date2)
	print ("Writing data to output file")
	with open('flight-results.json','w') as fp:
	 	json.dump(scraped_data,fp,indent = 4)