from flask_frozen import Freezer
from app import app

freezer = Freezer(app)

if __name__ == '__main__':
    freezer.freeze()

# Notes on using Freeze
# This will generate the static files for deployment to a static host/Pages
# We have to add .html to the end of each route in the app.py in order to have it work
# Also it doesn't put the static path for css/js for some reason
