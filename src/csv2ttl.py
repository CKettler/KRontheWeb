import codecs
import csv
import sys

from iribaker import to_iri
from rdflib import (
    Dataset, URIRef, Literal, Namespace,
    RDF as rdf, RDFS as rdfs, OWL as owl, XSD)


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


data = Namespace('http://data.krw.d2s.labs.vu.nl/group1/resource/')

# other namespaces
dbr = Namespace('http://dbpedia.org/resource/')
dbo = Namespace('http://dbpedia.org/ontology/')
org = Namespace('https://www.w3.org/ns/org#')
geo = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
review = Namespace('http:/www.purl.org/stuff/rev#')

# The URI for our graph
graph_uri = URIRef('http://data.krw.d2s.labs.vu.nl/group1/resource/graph')

# We initialize a dataset, and bind our namespaces
dataset = Dataset()
dataset.bind('g01vocab', data)
dataset.bind('dbr', dbr)
dataset.bind('dbo', dbo)
dataset.bind('org', org)
dataset.bind('geo', geo)



def build_graph_for_areas(graph, areas_csv):
    VARIABELE_IDX = 0
    GEBIEDCODE_IDX = 1
    WAARDE_IDX = 2
    LABEL_IDX = 3
    DEFINITIE_IDX = 4
    GEBIEDNAAM_IDX = 5
    SDNAAM_IDX = 6

    graph.add((dbr.Neighbourhood, rdfs.subClassOf, dbo.Area))
    graph.add((dbr.City, rdfs.subClassOf, dbo.Area))
    graph.add((data['City_part'], rdfs.subClassOf, dbo.Area))

    graph.add((data['City_part'], rdf.type, rdfs.Class))
    graph.add((data['City_part'], dbo.isPartOf, dbr.City))

    graph.add((dbr.Neighbourhood, dbo.isPartOf, data['City_part']))

    visited = []
    with open(areas_csv, "r") as csvfile:
        csv_contents = UnicodeReader(csvfile)
        csv_contents.next()
        count = 0
        for row in csv_contents:
            # Progress
            count += 1
            if count % 10000 == 0:
                print "Progress: " + str(count)

            variable = row[VARIABELE_IDX]
            vb_entity = URIRef(to_iri(data + variable))
            if variable not in visited:
                visited.append(variable)
                def_literal = Literal(row[DEFINITIE_IDX], lang='nl')
                label_literal = Literal(row[LABEL_IDX], lang='nl')
                graph.add((vb_entity, rdf.type, rdf.Property))
                graph.add((vb_entity, rdfs.isDefinedBy, def_literal))
                graph.add((vb_entity, rdfs.label, label_literal))

            try:
                try:
                    int(row[GEBIEDNAAM_IDX])
                    continue
                except ValueError:
                    pass

                gb_code = row[GEBIEDCODE_IDX]
                gb_name = row[GEBIEDNAAM_IDX]
                sd_name = row[SDNAAM_IDX]

                area = URIRef(to_iri(data + gb_name))
                value = Literal(
                    float(row[WAARDE_IDX]), datatype=XSD['decimal'])

                graph.add((area, rdf.type, rdfs.Class))
                graph.add((area, vb_entity, value))
                graph.add((area, data['areaCode'], Literal(
                    row[GEBIEDCODE_IDX], datatype=XSD['string'])))
                graph.add((area, rdf.type, org.Site))
                if gb_code == 'STAD':
                    graph.add((area, rdf.type, dbo.City))
                    graph.add((area, owl.sameAs, dbr.Amsterdam))
                else:
                    if gb_code + " " + gb_name == sd_name:
                        subarea_val = Literal("Amsterdam", lang='nl')
                        subarea_uri = URIRef(to_iri(data + 'Amsterdam'))
                        graph.add(
                            (subarea_uri, rdf.type, data['City_part']))
                    else:
                        try:
                            literal = "Amsterdam " + sd_name.split()[1]
                            subarea_val = Literal(literal, lang='nl')
                            subarea_uri = URIRef(to_iri(data + literal))
                            graph.add(
                                (subarea_uri, rdf.type, dbr.Neighbourhood))
                        except IndexError:
                            continue
                    graph.add((area, dbo.isPartOf, subarea_uri))
                    graph.add((subarea_uri, rdfs.label, subarea_val))

            except ValueError:
                pass
    return graph


def build_graph_for_restaurants(graph, restaurants_csv):
    GEBIEDCODE_IDX = 0
    GEBIEDNAAM_IDX = 1
    LONGITUDE_IDX = 2
    LATITUDE_IDX = 3
    BUSINESS_ID_IDX = 4
    BUSINESS_NAME_IDX = 5
    REVIEW_COUNT_IDX = 6
    RATING_IDX = 7
    PRICE_IDX = 8

    graph.add((dbo.Restaurant, rdfs.subClassOf, dbr.Business))
    graph.add((dbr.Business, rdfs.subClassOf, org.Organization))

    with open(restaurants_csv, "r") as csvfile:
        csv_contents = UnicodeReader(csvfile)
        csv_contents.next()
        count = 0
        for row in csv_contents:
            # Progress
            count += 1
            if count % 10000 == 0:
                print "Progress: " + str(count)

            gb_name = row[GEBIEDNAAM_IDX]
            restaurant_name = row[BUSINESS_NAME_IDX]
            longitude = row[LONGITUDE_IDX] \
                if row[LONGITUDE_IDX] != 'None' else None
            latitude = row[LATITUDE_IDX] \
                if row[LONGITUDE_IDX] != 'None' else None
            area = URIRef(to_iri(data + gb_name))
            restaurant = URIRef(to_iri(data + restaurant_name))

            graph.add((area, org.siteOf, restaurant))
            graph.add((area, data['locationOf'], restaurant))

            graph.add((restaurant, rdf.type, rdfs.Class))
            graph.add((restaurant, rdf.type, dbo.Restaurant))
            if longitude and latitude:
                graph.add((restaurant, geo.lat, Literal(
                    float(longitude), datatype=XSD['decimal'])))
                graph.add((restaurant, geo.logn, Literal(
                    float(latitude), datatype=XSD['decimal'])))

            graph.add((restaurant, org.hasSite, area))
            graph.add((restaurant, data['locatedIn'], area))

            graph.add((restaurant, review.minRating, Literal(
                1, datatype=XSD['integer'])))
            graph.add((restaurant, review.maxRating, Literal(
                5, datatype=XSD['integer'])))
            graph.add((restaurant, review.rating, Literal(
                float(row[RATING_IDX]), datatype=XSD['decimal'])))
            graph.add((restaurant, review.totalVotes, Literal(
                int(row[REVIEW_COUNT_IDX]), datatype=XSD['integer'])))
            graph.add((restaurant, data['hasPrice'], Literal(
                row[PRICE_IDX], datatype=XSD['string'])))
            graph.add((restaurant, data['businessID'], Literal(
                row[BUSINESS_ID_IDX], datatype=XSD['string'])))

    return graph


if __name__ == '__main__':
    areas_csv = sys.argv[1]
    restaurants_csv = sys.argv[2]
    graph = dataset.graph(graph_uri)

    graph = build_graph_for_areas(graph, areas_csv)
    graph = build_graph_for_restaurants(graph, restaurants_csv)

    print("Saving graph in turtle format...")
    with open('graph.ttl', 'w') as f:
        graph.serialize(f, format='turtle')
    print("Done!")
