#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command-line currency converter. Using openexchangerate.com. Restricted to 1000 requests per month.
"""

import argparse
import json
from urllib import request

__author__ = "Matej Vanek"
__email__ = "vanekmatej@gmail.com"


def parse():
    """
    Parses arguments from command line.
    :return: dict; dictionary of <argument: value> pairs
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--amount', type=float, default=1.0,
                        help="amount of an input currency to convert; if not present, 1 is used")
    parser.add_argument('-i', '--input_currency', type=str, required=True,
                        help="""3 letters name or symbol of a source currency;
                             available symbols: $ (USD), € (EUR), £ (GBP), ¥ (CNY)""")
    parser.add_argument('-o', '--output_currency', type=str, default='###',
                        help="""3 letters name or symbol of a target currency;
                             available symbols: $ (USD), € (EUR), £ (GBP), ¥ (CNY);
                             if not present, all currencies are used""")
    args = vars(parser.parse_args())
    return args


def process(args):
    """
    Downloads exchange rates and processes conversion.
    :param args: {argument: value} dictionary
    :raises ValueError, ConnectionError
    :return: json conversion output
    """
    # name standardization to the ISO 4217 codes
    # symbols restricted to the 4 most used ones
    symbols = {'$': 'USD', '€': 'EUR', '£': 'GBP', '¥': 'CNY'}
    for item in ['input_currency', 'output_currency']:
        args[item] = str.upper(args[item])
        if args[item] in symbols:
            args[item] = symbols[args[item]]

    # currencies and rates request
    try:
        result = request.urlopen(
            "https://openexchangerates.org/api/latest.json?app_id=9ed25edf0bed4020ac6291cc6134ce85").read()
    except Exception as e:
        raise ConnectionError("Server communication error", e)
    result = str(result)[2:-1].replace('\\n', "")
    rates = json.loads(result)['rates']

    # input data validation
    if len(args['input_currency']) != 3 or args['input_currency'] not in rates:
        raise ValueError("Unsupported input currency code or symbol.", args['input_currency'])
    if (len(args['output_currency']) != 3 or args['output_currency'] not in rates)\
       and args['output_currency'] != '###':
        raise ValueError("Unsupported output currency code or symbol.", args['output_currency'])

    # currency conversion
    if args['output_currency'] == '###':
        output = json.dumps({'input': {'amount': args['amount'], 'currency': args['input_currency']},
                             'output': {currency: convert(args['amount'], args['input_currency'], currency, rates)
                                        for currency in rates}},
                            sort_keys=True, indent=4)
    else:
        output = json.dumps({'input': {'amount': args['amount'], 'currency': args['input_currency']},
                             'output': {args['output_currency']:
                                        convert(args['amount'], args['input_currency'],
                                                args['output_currency'], rates)}},
                            sort_keys=True, indent=4)
    print(output)
    return output


def convert(amount, input_currency, output_currency, rates):
    """
    Converts the amount of money from one currency to another.
    :param amount: float; amount of the source currency to convert
    :param input_currency: string; ISO4 217 code of the source currency
    :param output_currency: strung; ISO 4217 code of the target currency
    :param rates: dict; dictionary of <ISO4217_currency: USD_to_ISO4217_currency_rate> pairs
    :return: amount of the target currency (rounded to 2 decimal places)
    """
    if rates[input_currency] > 0:
        rate = rates[output_currency] / rates[input_currency]
        return round(amount * rate, 2)
    else:
        return 0.

if __name__ == '__main__':
    args = parse()
    process(args)
