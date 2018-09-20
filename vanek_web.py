#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web API currency converter. Using openexchangerate.com. Restricted to 1000 requests per month.
"""

import flask
import warnings

__author__ = "Matej Vanek"
__email__ = "vanekmatej@gmail.com"

app = flask.Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    """
    Basic information. GET
    """
    return """
    <h1>Web API currency converter</h1>
    Using openexchangerate.com. Restricted to 1000 requests per month.</br>
    Created by Matej Vanek, 2018
    """


@app.route('/currency_converter', methods=['GET'])
def convert_currencies():
    """
    Currency conversion based on request parameters, processed by CLI application. GET
    """
    from vanek_cli import process

    args = dict(flask.request.args)

    for key in args:
        args[key] = args[key][0]
    if 'amount' in args:
        try:
            args['amount'] = float(args['amount'])
        except ValueError:
            warnings.warn("Amount argument '{}' cannot convert to float. Amount set to 1.".format(str(args['amount'])))
            args['amount'] = 1.
    else:
        args['amount'] = 1.

    if 'output_currency' not in args:
        args['output_currency'] = '###'  # abbreviation '###' means all currencies

    return process(args)


app.run()
