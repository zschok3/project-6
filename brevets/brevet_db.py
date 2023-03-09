"""
Contains two database interaction functions for flask_brevets
"""
import os
from pymongo import MongoClient
import arrow
import sys
import logging

 

# def get_brevet():
#     """
#     Obtains the newest document in the "lists" collection in database "brevets".
#     Returns title (string) and items (list of dictionaries) as a tuple.
#     """

#     brevet = 

#     return brevet["distance"], brevet["begin_date"], brevet["control_times"]


# def insert_brevet(distance,begin_date,control_times):
#     """
#     Inserts a new to-do list into the database "todo", under the collection "lists".
    
#     Inputs a title (string) and items (list of dictionaries)
#     Returns the unique ID assigned to the document by mongo (primary key.)
#     """
#     output = collection.insert_one({
#         "distance": distance,
#         "begin_date": begin_date, 
#         "control_times": control_times})

#     _id = output.inserted_id # this is how you obtain the primary key (_id) mongo assigns to your inserted document.
#     return str(_id)
