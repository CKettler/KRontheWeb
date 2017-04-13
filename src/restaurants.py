import codecs
import csv
import cStringIO
import requests
import sys
import time

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


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def request_retry(endpoint, params, headers=None, times=3):
    count = 0
    while count < times:
        if headers:
            resp = requests.get(endpoint, params=params, headers=headers)
        else:
            resp = requests.get(endpoint, params=params)
        try:
            resp.raise_for_status()
            return resp
        except:
            times += 1
            time.sleep(1)
    print("Could not connect to Yelp API after 3 tries.")


visited = []
with open('restaurants.csv', 'w') as outfile:
    writer = UnicodeWriter(outfile)
    writer.writerow(['gebiedcode15', 'gebiednaam', 'longitude', 'latitude', 'business_id', 'business_name', 'review_count', 'rating', 'price'])
    with open(dataset_path, "r") as csvfile:
        reader = csv.reader(csvfile)
        header = reader.next()
        count = 0
        for row in reader:
            if row[GEBIEDCODE_IDX] == 'STAD' or 'onbekend' in row[GEBIEDNAAM_IDX].lower() or row[GEBIEDCODE_IDX] in visited:
                continue

            radius = 500
            if row[GEBIEDCODE_IDX] + " " + row[GEBIEDNAAM_IDX] == row[SDNAAM_IDX]:
                radius = 2000

            area_name = row[GEBIEDNAAM_IDX]
            if "amsterdam" not in area_name.lower():
                area_name = "Amsterdam " + area_name
            print("Getting data for area: " + area_name)

            gdata = {
                "address": area_name,
                "key": "AIzaSyB7WV0a3v5O2chUUsUtmE1YyhlcSKrljPM"}
            gresp = request_retry(ENDPOINTS["Gmaps"], gdata)
            time.sleep(1)

            try:
                location = gresp.json()["results"][0]["geometry"]["location"]
            except IndexError:
                visited.append(row[GEBIEDCODE_IDX])
                continue
            longitude = location["lng"]
            latitude = location["lat"]

            offset = 0
            margin = 50
            ydata = {
                "longitude": longitude,
                "latitude": latitude,
                "limit": margin,
                "radius": radius,
                "categories": "restaurants"}
            yresp = request_retry(
                ENDPOINTS["Yelp"], params=ydata, headers=YELP_HEADERS)
            time.sleep(1)
            total = yresp.json()["total"]
            businesses = yresp.json()["businesses"]
            print("Got " + str(total) + " results in total.")
            if total == 0:
                visited.append(row[GEBIEDCODE_IDX])
                continue

            if total > margin:
                while businesses:
                    for business in businesses:
                        writer.writerow([
                            row[GEBIEDCODE_IDX],
                            row[GEBIEDNAAM_IDX],
                            str(business['coordinates']['longitude']),
                            str(business['coordinates']['latitude']),
                            business.get('id'),
                            business.get('name'),
                            str(business.get('review_count', '')),
                            str(business.get('rating', '')),
                            business.get('price', '')])
                    offset += margin
                    if offset >= 1000:
                        print("Reached 1000 limit for this area.")
                        break
                    ydata = {
                        "longitude": longitude,
                        "latitude": latitude,
                        "limit": margin,
                        "radius": radius,
                        "categories": "restaurants",
                        "offset": offset}
                    yresp = request_retry(
                        ENDPOINTS["Yelp"], params=ydata, headers=YELP_HEADERS)
                    time.sleep(1)
                    businesses = yresp.json()["businesses"]

            visited.append(row[GEBIEDCODE_IDX])