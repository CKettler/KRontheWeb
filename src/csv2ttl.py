import csv
import sys

from iribaker import to_iri
from rdflib import Dataset, URIRef, Literal, Namespace, RDF, RDFS, OWL, XSD

dataset_path = sys.argv[1]

VARIABELE_IDX = 0
GEBIEDCODE_IDX = 1
WAARDE_IDX = 2
LABEL_IDX = 3
DEFINITIE_IDX = 4
GEBIEDNAAM_IDX = 5
SDNAAM_IDX = 6

# A namespace for our resources
data = 'http://data.krw.d2s.labs.vu.nl/group1/resource/'
DATA = Namespace(data)
# DBPEDIA namespace
dbpedia = 'http://dbpedia.org/resource/'
DBPEDIA = Namespace(dbpedia)
# A namespace for our vocabulary items (schema information,
# RDFS, OWL classes and properties etc.)
vocab = 'http://data.krw.d2s.labs.vu.nl/group1/vocab/'
VOCAB = Namespace(vocab)

# The URI for our graph
graph_uri = URIRef('http://data.krw.d2s.labs.vu.nl/group1/resource/example')

# We initialize a dataset, and bind our namespaces
dataset = Dataset()
dataset.bind('g01data', DATA)
dataset.bind('g01vocab', VOCAB)

# We then get a new graph object with our URI from the dataset.
graph = dataset.graph(graph_uri)

city_type = URIRef(to_iri(data + "City"))
area_type = URIRef(to_iri(data + "Area"))

visited = []
with open(dataset_path, "r") as csvfile:
    csv_contents = csv.reader(csvfile)
    header = csv_contents.next()
    # Let's iterate over the dictionary, and create some triples
    # Let's pretend we know exactly what the 'schema' of our CSV file is
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
            def_literal = Literal(row[DEFINITIE_IDX], datatype=XSD['string'])
            label_literal = Literal(row[LABEL_IDX], datatype=XSD['string'])
            graph.add((vb_entity, RDFS.isDefinedBy, def_literal))
            graph.add((vb_entity, RDFS.label, label_literal))

        try:
            try:
                gb = int(row[GEBIEDNAAM_IDX])
                continue
            except ValueError:
                pass

            gb_code = row[GEBIEDCODE_IDX]
            gb_name = row[GEBIEDNAAM_IDX]
            sd_name = row[SDNAAM_IDX]

            area = URIRef(to_iri(data + gb_name))
            value = Literal(float(row[WAARDE_IDX]), datatype=XSD['float'])

            # All set... we are now going to add the triples to our graph
            graph.add((area, vb_entity, value))

            if gb_code == 'STAD':
                graph.add((area, RDF.type, city_type))
                graph.add((area, OWL.sameAs, DBPEDIA.Amsterdam))
            else:
                graph.add((area, RDF.type, area_type))
                if gb_code + " " + gb_name == sd_name:
                    subarea_val = Literal("Amsterdam", datatype=XSD['string'])
                else:
                    try:
                        literal = "Amsterdam " + sd_name.split()[1]
                        subarea_val = Literal(literal, datatype=XSD['string'])
                    except IndexError:
                        continue
                graph.add((area, VOCAB['areaOf'], subarea_val))

        except ValueError:
            pass

    print "Saving file..."
    with open('out.ttl', 'w') as f:
        graph.serialize(f, format='turtle')
    print "Done!"
