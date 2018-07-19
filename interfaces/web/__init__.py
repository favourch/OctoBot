import copy
import logging
import time

import dash
import flask
import numpy

from config.cst import PriceIndexes
from interfaces.web.advanced_controllers import get_advanced_blueprint
from interfaces.web.api import get_api_blueprint

server_instance = flask.Flask(__name__)

server_instance.register_blueprint(get_advanced_blueprint())
server_instance.register_blueprint(get_api_blueprint())

# dash
app_instance = dash.Dash(__name__, sharing=True, server=server_instance, url_base_pathname='/dashboard')
app_instance.config['suppress_callback_exceptions'] = True

# disable Flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

notifications = []

matrix_history = []
symbol_data_history = {}
portfolio_value_history = {
    "real_value": [],
    "simulated_value": [],
    "timestamp": []
}

TIME_AXIS_TITLE = "Time"


def add_to_matrix_history(matrix):
    matrix_history.append({
        "matrix": copy.deepcopy(matrix.get_matrix()),
        "timestamp": time.time()
    })


def add_to_portfolio_value_history(real_value, simulated_value):
    portfolio_value_history["real_value"].append(real_value)
    portfolio_value_history["simulated_value"].append(simulated_value)
    portfolio_value_history["timestamp"].append(time.time())


def add_to_symbol_data_history(symbol, data, time_frame, force_data_reset=False):
    if symbol not in symbol_data_history:
        symbol_data_history[symbol] = {}

    if force_data_reset or time_frame not in symbol_data_history[symbol]:
        symbol_data_history[symbol][time_frame] = data
    else:
        # merge new data into current data
        # find index from where data is new
        new_data_index = 0
        for i in range(1, len(data)):
            if data[-i][PriceIndexes.IND_PRICE_TIME.value] > \
                    symbol_data_history[symbol][time_frame][-1][PriceIndexes.IND_PRICE_TIME.value]:
                new_data_index = i
            else:
                break
        if new_data_index > 0:
            data_list = [None] * len(PriceIndexes)
            for i in range(len(data)):
                data_list[i] = data[i][-new_data_index:]
            new_data = numpy.array(data_list)
            symbol_data_history[symbol][time_frame] = numpy.concatenate((symbol_data_history[symbol][time_frame],
                                                                         new_data), axis=1)


def add_notification(level, title, message):
    notifications.append({
        "Level": level.value,
        "Title": title,
        "Message": message
    })


def flush_notifications():
    notifications.clear()


def get_matrix_history():
    return matrix_history


def get_portfolio_value_history():
    return portfolio_value_history


def get_symbol_data_history(symbol, time_frame):
    return symbol_data_history[symbol][time_frame]


def get_notifications():
    return notifications


def load_callbacks():
    from interfaces.web.controllers.dash import update_values, \
        update_strategy_values, \
        update_time_frame_dropdown_options, \
        update_symbol_dropdown_options, \
        update_symbol_dropdown_value, \
        update_evaluator_dropdown_options, \
        update_evaluator_dropdown_values, \
        update_currencies_amounts, \
        update_portfolio_value


def load_routes():
    from .controllers.trading import portfolio
    from .controllers.trading import orders
    from .controllers.tentacles import tentacles
    from .controllers.tentacles import tentacle_manager
    from .controllers.backtesting import backtesting
    from .controllers.backtesting import data_collector
    from .controllers.commands import commands
    from .controllers.commands import update
    from .controllers.configuration import config
    from .controllers.dashboard import dash
    from .controllers.home import home


def load_advanced_routes():
    from interfaces.web.advanced_controllers.home import home


def load_api_routes():
    from interfaces.web.api.trading import orders
