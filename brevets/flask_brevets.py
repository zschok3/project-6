"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config
import logging

import os 

###
# Globals
###

app = flask.Flask(__name__)
app.debug = True if "DEBUG" not in os.environ else os.environ["DEBUG"]
port_num = True if "PORT" not in os.environ else os.environ["PORT"]
app.logger.setLevel(logging.DEBUG)

API_ADDR = os.environ["API_ADDR"]
API_PORT = os.environ["API_PORT"]
API_URL = f"http://{API_ADDR}:{API_PORT}/api/"

def get_brevet():
    """
    Obtains the newest document in the "lists" collection in database
    by calling the RESTful API.
    Returns title (string) and items (list of dictionaries) as a tuple.
    """
    # Get documents (rows) in our collection (table),
    # Sort by primary key in descending order and limit to 1 document (row)
    # This will translate into finding the newest inserted document.
    app.logger.debug("GET_BREVET_CALL")
    lists = requests.get(f"{API_URL}/brevets").json()

    # lists should be a list of dictionaries.
    # we just need the last one:
    brevets = lists[-1]
    return brevets["distance"], brevets["begin_date"], brevets["control_times"]

def insert_brevet(distance, begin_date, control_times):
    """
    Inserts a new to-do list into the database by calling the API.
    
    Inputs a title (string) and items (list of dictionaries)
    """
    _id = requests.post(f"{API_URL}/brevets", json={"distance": distance, "begin_date": begin_date, "control_times": control_times}).json()
    return _id
 


###
# Pages
###
# Set up Flask app


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404

#####   MongoDB Functions #####


API_ADDR = os.environ["API_ADDR"]
API_PORT = os.environ["API_PORT"]
API_URL = f"http://{API_ADDR}:{API_PORT}/api/"


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))
    # FIXME!
    # Right now, only the current time is passed as the start time
    # and control distance is fixed to 200
    # You should get these from the webpage!
    # control = request.args.get('')
    time = request.args.get('begin')
    app.logger.debug(f"time={time}")

    cntrl = request.args.get('cntrl')
    app.logger.debug(f"cntrl={cntrl}")

    open_time = acp_times.open_time(km, cntrl, arrow.get(time)).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(km, cntrl, arrow.get(time)).format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)


@app.route("/insert", methods=["POST"])
def insert():
    """
    /insert : inserts a to-do list into the database.
    Accepts POST requests ONLY!
    JSON interface: gets JSON, responds with JSON
    """
    # app.logger.debug(request.json)
    try:
    # Read the entire request body as a JSON
    # This will fail if the request body is NOT a JSON.
        input_json = request.json
        # if successful, input_json is automatically parsed into a python dictionary!

        distance = input_json["distance"]
        begin_date = input_json["begin_date"]
        control_times = input_json["control_times"]

        app.logger.debug("INSERTING:")
        app.logger.debug({"distance": distance,
        "begin_date": begin_date,
        "control_times": control_times})
        brevet_id = insert_brevet(distance,begin_date,control_times)

        app.logger.debug(f"BREVET_ID: {brevet_id}")
        return flask.jsonify(result={},
                        message="Inserted!", 
                        status=1, # This is defined by you. You just read this value in your javascript.
                        mongo_id=brevet_id)
    except:
        # The reason for the try and except is to ensure Flask responds with a JSON.
        # If Flask catches your error, it means you didn't catch it yourself,
        # And Flask, by default, returns the error in an HTML.
        # We want /insert to respond with a JSON no matter what!
        return flask.jsonify(result={},
                        message="Oh no! Server error!", 
                        status=0, 
                        mongo_id='None')


@app.route("/fetch", methods=["GET"])
def fetch():
    """
    /fetch : fetches the newest to-do list from the database.
    Accepts GET requests ONLY!
    JSON interface: gets JSON, responds with JSON
    """
    try:
        distance, begin_date, control_times = get_brevet()

        app.logger.debug("FETCHING:")
        app.logger.debug({"distance": distance,
        "begin_date": begin_date,
        "control_times": control_times})


        return flask.jsonify(
                result={
        "distance": distance,
        "begin_date": begin_date,
        "control_times": control_times
        }, 
                status=1,
            message="Successfully fetched a to-do list!")
    except:
        return flask.jsonify(
                result={}, 
                status=0,
                message="Something went wrong, couldn't fetch any lists!")


#############

if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    app.run(port=port_num, host="0.0.0.0")
