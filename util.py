# ~*~ coding: utf-8 ~*~
'''Utilities

This module provides helper functions and variables called in app.py
'''

import requests

STATES = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AS': 'American Samoa',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'GU': 'Guam',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MP': 'Northern Mariana Islands',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NA': 'National',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'PR': 'Puerto Rico',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VI': 'Virgin Islands',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}


def generate_html(message):
    '''
    Generates the HTML and CSS used for styling the letter

    I'm concatenating the message to the html (rather than using variable interpolation)
    because of the API's limit on the data object not having values greater than 500 characters.
    This seems like a safer/simpler workaround.
    '''
    # Normally I would use .format() on the string and import this giant string from 
    # another file, but the routing engine for Flask is complaining
    message = message.replace('"', "'") # Lob can't handle double quotes
    return '''<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css?family=Open+Sans" rel="stylesheet" type="text/css">
<title>Representative Letter</title>
<style>
  *, *:before, *:after {
    -webkit-box-sizing: border-box;
    -moz-box-sizing: border-box;
    box-sizing: border-box;
  }

  body {
    width: 8.5in;
    height: 11in;
    margin: 0;
    padding: 0;
    font-size: .15in;
  }

  .header {
    position: relative;
    left: .45in;
    top: 3in;
    margin-bottom: 20px;
    width: 6in;
  }

  .page {
    page-break-after: always;
  }

  .page-content {
    position: relative;
    width: 8.125in;
    height: 10.625in;
    left: 0.1875in;
    top: 0.1875in;
    border-color: gray;
    border-style: solid;
  }

  .text {
    position: relative;
    left: .45in;
    top: 3in;
    bottom: 1in;
    width: 6in;
  }

  #return-address-window {
    position: absolute;
    left: .625in;
    top: .5in;
    width: 3.25in;
    height: .875in;
    
  }

  #return-address-text {
    position: absolute;
    left: .07in;
    top: .34in;
    width: 2.05in;
    height: .44in;
    background-color: white;
    font-size: .11in;
  }

  #return-logo {
    position: absolute;
    left: .07in;
    top: .02in;
    width: 2.05in;
    height: .3in;
    background-color: white;
  }

  #recipient-address-window {
    position: absolute;
    left: .625in;
    top: 1.75in;
    width: 4in;
    height: 1in;
  }

  #recipient-address-text {
    position: absolute;
    left: .07in;
    top: .05in;
    width: 2.92in;
    height: .9in;
    background-color: white;
  }

   #signature {
    padding-top: 30px;
  }

</style>
</head>

<body>
  <div class="page">
    <div class="page-content">
      <div class="header">
        Dear Representative {{recipient_name}},
      </div>
      <div class="text">
        ''' + message + '''  
      <div id="signature">
          Sincerely,<br>
          {{sender_name}}
      </div>
      </div>
    
    </div>
    <div id="return-address-window">
      <div id="return-logo">
      </div>
      <div id="return-address-text">
      </div>
    </div>
    <div id="recipient-address-window">
      <div id="recipient-address-text">
      </div>
    </div>
  </div>
</body>

</html>'''


def get_representative(address):
    ''' 
    Use Google Civics API to find representatives given user's address
    '''
    civic_api = 'https://www.googleapis.com/civicinfo/v2/representatives'
    query = {
        'address': address,
        'key': 'GOOGLE_CIVIC_API_KEY'
    }
    resp = requests.get(civic_api, query)

    return resp


def parse_civic_error(error_reason):
    '''
    Returns a helpful message explaining the error based on the status code
    from Google's Civic Information API
    '''
    errors = {
        "parseError": "the address you entered was not completely specified.",
        "required": "you didn't specify your address.",
        "invalidValue": "we don't know anything about that election.",
        "invalidQuery": "we don't have the data for that election anymore. Sorry!",
        "limitExceeded": "you're making us look up your address too much! Read a page of <a href=\"https://en.wikipedia.org/wiki/Infinite_Jest\">Infinite Jest</a>, and we should be ready for you by then.",
        "notFound": "we couldn't find any representatives for the address you entered.\
                      \nPlease make sure you entered a US residential address.",
        "conflict": "there was conflicitng information found for this address. Please be more specific.",
        "backendError": "our magical way of finding your representative failed. We're sorry -- this is unexcusable. Please try again in a few moments."
    }
    return errors[error_reason]


def parse_lob_error(http_status):
    '''
    Returns a helpful message explaining the error based on the status code
    from Lob's API
    '''
    errors = {
        401: "this application doesn't have authorization to access the Lob API.",
        403: "this application is doing something forbidden based on their account status.",
        404: "this application is trying to access something that doesn't exist.",
        422: "the information you inputted to the form was incorrect.",
        429: "you're creating too many letters! Read a page of <a href=\"https://en.wikipedia.org/wiki/Infinite_Jest\">Infinite Jest</a>, and we should be ready for you by then.",
        500: "our magical letter-creating service failed. Please forgive us :("
    }

    return errors[http_status]
