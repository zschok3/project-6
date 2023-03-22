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
import requests 

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
    control_lists = requests.get(f"{API_URL}/brevets").json()
    brevet = control_lists[-1]
    app.logger.debug("BREVET")
    app.logger.debug(brevet)
    return brevet["brev_dist"], brevet["begin_date"], brevet["checkpoints"]

def insert_brevet(brev_dist, begin_date, checkpoints):
    _id = requests.post(f"{API_URL}/brevets", json={"brev_dist": brev_dist, "begin_date": begin_date, "checkpoints": checkpoints}).json()
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

    time = request.args.get('begin')
    app.logger.debug(f"time={time}")

    brevet_dist = request.args.get('brevet_dist', 999, type=float)
    app.logger.debug(f"brevet_dist={brevet_dist}")

    open_time = acp_times.open_time(km, brevet_dist, arrow.get(time)).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(km, brevet_dist, arrow.get(time)).format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)


@app.route("/insert", methods=["POST"])
def insert():
    """
    /insert : inserts a to-do list into the database.
    Accepts POST requests ONLY!
    JSON interface: gets JSON, responds with JSON
    """
    try:
        input_json = request.json
        app.logger.debug(f"INPUT_JSON: {input_json}")
        brev_dist = input_json["brev_dist"] 
        begin_date = input_json["begin_date"] 
        checkpoints = input_json["checkpoints"] 
        app.logger.debug({"brev_dist": brev_dist, "begin_date": begin_date, "checkpoints": checkpoints})
        # Insert brevet data into database
        brev_id = insert_brevet(brev_dist, begin_date, checkpoints)

        app.logger.debug(f"BREV_ID = {brev_id}")

        return flask.jsonify(result={},
                        message="Inserted!", 
                        status=1,
                        mongo_id=brev_id)
    except:
        return flask.jsonify(result={},
                        message="Server error", 
                        status=0, 
                        mongo_id='None')

@app.route("/fetch", methods=["GET"])
def fetch():
    """
    /fetch : fetches the newest to-do list from the database.
    Accepts GET requests ONLY!
    JSON interface: gets JSON, responds with JSON
    """
    # try:
        # Fetch the newest brevet data from the database
    brev_dist, begin_date, checkpoints = get_brevet() 
    app.logger.debug(f"BREV_DIST: {brev_dist}")   
    app.logger.debug(f"BEGIN+DATE: {begin_date}")   
    app.logger.debug(f"CHECKPOINTS: {checkpoints}")   

    return flask.jsonify(
            result={"brev_dist": brev_dist, "begin_date": begin_date, "checkpoints": checkpoints}, 
            status=1,
            message="Successfully fetched brevet data")
    # except:
    #     return flask.jsonify(
    #             result={}, 
    #             status=0,
    #             message="Cannot be fetched")


#############

if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    app.run(port=port_num, host="0.0.0.0")
