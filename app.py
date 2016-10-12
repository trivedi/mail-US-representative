# ~*~ coding: utf-8 ~*~
'''Main App

This module contains the logic for rendering pages of the webapp via Flask's routing engine
'''

import lob
import util
from flask import Flask, render_template, request

app = Flask(__name__)
lob.api_key = 'LOB_API_KEY'
lob.api_version = 'LOB_API_VERSION'

@app.route('/')
def index():
    '''
    Renders the home page
    '''
    return render_template('index.html', states=sorted(util.STATES))


@app.route('/build_letter', methods=['POST'])
def build_letter():
    '''
    This is the page that gets rendered when user submits information for creating a letter
    '''
    resp = util.get_representative(request.form['address1'])

    # Handle Civic API errors
    if resp.status_code != 200:
        # Something went wrong with the Google Civics query, render error page
        return render_error_page(resp.json(), 'civic')

    # Get the recipient's information
    rep = find_house_member(resp)

    # JSON response of letter via Lob
    letter = create_letter(request.form, rep)

    # Handle Lob Letter API errors
    if not isinstance(letter, lob.Letter):
        return render_error_page(letter.http_status, 'lob')

    # Variable interpolations for the letter
    letter_file = letter['url']
    state = '+'.join(util.STATES[request.form['state']].split()) # Ensure that the get query encodes two-word states correctly

    return render_template('build_letter.html', user_data=request.form, resp_data=resp.json(),
                           letter_file=letter_file, state=state)


def render_error_page(error, api):
    '''
    Renders an error page that upon a faulty response (JSON) from an API query
    '''
    if api == 'civic':
        error_code = error['error']['code']
        error_msg = util.parse_civic_error(
            error['error']['errors'][0]['reason'])
        return render_template('error.html', code=error_code, msg=error_msg)
    else:
        error_msg = util.parse_lob_error(error)
        return render_template('error.html', code=error, msg=error_msg)


def find_house_member(civics_data):
    '''
    Given the response from the Civics query, return a member of the House of Representatives
    '''
    # I'm positive there's not a simple way to query by official rank :(
    for official in civics_data.json().get('officials'):
        if 'urls' in official:
            for url in official['urls']:
                if '.house.gov' in url:
                    return official


def create_letter(sender, recipient):
    '''
    Create letter using Lob's API given sender and recipient data
    '''
    letter = None

    try:
        letter = lob.Letter.create(
            description='Letter to ' + sender['name'] + '\'s Representative',
            from_address={
                'name': sender['name'],
                'address_line1': sender['address1'],
                'address_line2': sender['address2'],
                'address_city': sender['city'],
                'address_state': sender['state'],
                'address_zip': sender['zip'],
                'address_country': 'US'
            },
            to_address={
                'name': recipient['name'],
                'address_line1': recipient['address'][0]['line1'],
                'address_city': recipient['address'][0]['city'],
                'address_state': recipient['address'][0]['state'],
                'address_zip': recipient['address'][0]['zip'],
                'address_country': 'US'
            },

            data={
                'sender_name': sender['name'],
                'recipient_name': recipient['name'].split()[1]
            },
            file=util.generate_html(sender['message'].replace('\n', '<br>')), # textarea adds newlines
            color=True
        )
        return letter
    except Exception as ex:
        return ex


if __name__ == '__main__':
    app.run(debug=True)
