import os

# Read table names from environment variables, with fallback to defaults for local development
LINES_TABLE_NAME = os.environ.get("LINES_TABLE_NAME", "LinesDB")
LINES_PROPERTY_TABLE_NAME = os.environ.get("LINES_PROPERTY_TABLE_NAME", "LineProperty")
CIRCLES_TABLE_NAME = os.environ.get("CIRCLES_TABLE_NAME", "Circles")
HOME_WIDGETS_TABLE_NAME = os.environ.get("HOME_WIDGETS_TABLE_NAME", "HomeWidgets")