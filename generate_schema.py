import json
from main import getSchema
import sys
from graphql.utils import schema_printer

def generate_schema(schema):
    my_schema_str = schema_printer.print_schema(schema)
    fp = open("schema.graphql", "w")
    fp.write(my_schema_str)
    fp.close()

if __name__ == "__main__":
    generate_schema(getSchema())