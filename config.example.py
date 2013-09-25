"""Configuration settings for the RedEye title generator web application
and offline / background supporting processes"""

import os

mongo = {
    "host": "127.0.0.1",
    "port": 27017,
    "database": "redeye"
}

site_title = "RedEye Title Generator"
template_dir = os.path.join(os.path.realpath(__file__), '..', 'templates')
static_dir = os.path.join(os.path.realpath(__file__), '..', 'static')
google_analytics_id = None 
google_ad_client_id = None 
google_ad_slot_id = None 
debug = False 
