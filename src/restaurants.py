import csv
import requests
import sys

ENDPOINTS = {
    "Gmaps": "https://maps.googleapis.com/maps/api/geocode/json",
    "Yelp": "https://api.yelp.com/v3/businesses/search"
}

YELP_HEADERS = {"Authorization": "Bearer 2FTQZ7z5UZoBCahmyDFJPiKcoyKXDv_gi-uopZb1gsljG3ftEal2BQbahnI8vP6GcyrgwWo-Gkl1zik5a587Y2Q_74r4ggJAlNgc3uzzfx-DzP1Y0v6AZFfc1gvqWHYx"}

dataset_path = sys.argv[1]

VARIABELE_IDX = 0
GEBIEDCODE_IDX = 1
WAARDE_IDX = 2
LABEL_IDX = 3
DEFINITIE_IDX = 4
GEBIEDNAAM_IDX = 5
SDNAAM_IDX = 6

with open('out.csv', 'w') as outfile:
    writer = csv.writer(outfile)
    writer.writeline(['gebiedcode15', 'gebiednaam', 'longitude', 'latitude', 'business_id', 'business_name', 'review_count', 'rating', 'price'])
    with open(dataset_path, "r") as csvfile:
        reader = csv.reader(csvfile)
        header = reader.next()
        count = 0
        for row in reader:
            area_name = row[GEBIEDNAAM_IDX]
            if "amsterdam" not in area_name.lower():
                area_name = "Amsterdam " + area_name
            gdata = {
                "address": area_name,
                "key": "AIzaSyB7WV0a3v5O2chUUsUtmE1YyhlcSKrljPM"}
            gresp = requests.get(ENDPOINTS["Gmaps"], params=gdata)
            location = gresp.json()["results"][0]["geometry"]["location"]
            longitude = location["lng"]
            latitude = location["lat"]

            offset = 0
            margin = 50
            radius = 500
            ydata = {
                "longitude": longitude,
                "latitude": latitude,
                "limit": margin,
                "radius": radius,
                "categories": "restaurants"}
            yresp = requests.get(
                ENDPOINTS["Yelp"], params=ydata, headers=YELP_HEADERS)
            total = yresp.json()["total"]
            if total == 0:
                continue

            if total > margin:
                while yresp.json()["businesses"]:
                    for business in yresp.json()["businesses"]:
                        writer.writeline(
                            row[GEBIEDCODE_IDX],
                            row[GEBIEDNAAM_IDX],
                            business['coordinates']['longitude'],
                            business['coordinates']['latitude'],
                            business['id'],
                            business['name'],
                            business['review_count'],
                            business['rating'],
                            business['price'])
                    offset += margin
                    ydata = {
                        "longitude": longitude,
                        "latitude": latitude,
                        "limit": margin,
                        "radius": radius,
                        "categories": "restaurants",
                        "offset": offset}
