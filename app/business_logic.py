import logging
from io import StringIO
import csv

def construct_search_query(state, city, industry):
    query = f"{industry} in {city}, {state}"
    logging.debug(f"Constructed search query: {query}")
    return query

def extract_business_data(driver):
    title = driver.get_text('h1')  # Extract business name
    rating = driver.get_text("div.F7nice > span")  # Extract rating
    reviews = driver.get_text("div.F7nice > span:last-child")  # Extract reviews count
    phone_element = driver.get_element_or_none("//button[starts-with(@data-item-id,'phone')]")
    phone = phone_element.get_attribute("data-item-id").replace("phone:tel:", "") if phone_element else None
    website = driver.get_link("a[data-item-id='authority']")  # Extract website link

    logging.debug(f"Extracted business data: title={title}, rating={rating}, reviews={reviews}, phone={phone}, website={website}")

    return {
        "title": title,
        "rating": rating,
        "reviews": reviews,
        "phone": phone,
        "website": website
    }

def deduplicate_businesses(businesses):
    unique_businesses = []
    place_ids = set()
    for business in businesses:
        if business['place_id'] not in place_ids:
            place_ids.add(business['place_id'])
            unique_businesses.append(business)
    logging.debug(f"Deduplicated businesses: {unique_businesses}")
    return unique_businesses

import csv
import io

def generate_csv(data):
    if not data:
        raise ValueError("No data available to generate CSV")

    keys = data[0].keys()
    output = io.StringIO()
    dict_writer = csv.DictWriter(output, fieldnames=keys)
    dict_writer.writeheader()
    dict_writer.writerows(data)
    return output.getvalue()

from flask import Blueprint, request, send_file, render_template_string
from app.business_logic import construct_search_query, extract_business_data, deduplicate_businesses, generate_csv
import logging
from app.botasaurus_local import Botasaurus  # Updated import statement

main = Blueprint('main', __name__)

@main.route('/')
def index():
    logging.debug("Rendering index page")
    return render_template_string('''
        <html>
        <head>
            <style>
                body {
                    background-color: #121212; /* Very dark grey */
                    color: white; /* Set text color to white for better contrast */
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                form {
                    background-color: #1e1e1e; /* Slightly lighter dark grey for form background */
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
                }
                label, input {
                    display: block;
                    margin: 10px 0;
                }
                input[type="submit"] {
                    margin-top: 20px;
                    padding: 10px;
                    background-color: #333;
                }
            </style>
        </head>
        <body>
            <form action="/scrape" method="post">
                <label for="state">State:</label>
                <input type="text" id="state" name="state">
                <label for="city">City:</label>
                <input type="text" id="city" name="city">
                <label for="industry">Industry:</label>
                <input type="text" id="industry" name="industry">
                <input type="submit" value="Scrape">
            </form>
        </body>
        </html>
    ''')

@main.route('/scrape', methods=['POST'])
def scrape():
    state = request.form['state']
    city = request.form['city']
    industry = request.form['industry']
    logging.debug(f"Received form data: state={state}, city={city}, industry={industry}")

    # Construct search query
    query = construct_search_query(state, city, industry)

    # Initialize Botasaurus
    bot = Botasaurus()

    # Perform scraping
    bot.start()
    bot.go_to('https://example.com/search')
    bot.fill('input[name="state"]', state)
    bot.fill('input[name="city"]', city)
    bot.fill('input[name="industry"]', industry)
    bot.click('button[type="submit"]')
    bot.wait_for('.results')

    # Extract business data
    business_data = bot.extract('.results .business', {
        'name': '.name',
        'address': '.address',
        'phone': '.phone'
    })

    bot.stop()

    # Deduplicate businesses
    unique_businesses = deduplicate_businesses(business_data)
    logging.debug(f"Deduplicated businesses: {unique_businesses}")

    try:
        # Generate CSV
        csv_data = generate_csv(unique_businesses)
    except ValueError as e:
        logging.error(f"Error generating CSV: {e}")
        return str(e), 400

    return send_file(io.BytesIO(csv_data.encode()), mimetype='text/csv', as_attachment=True, attachment_filename='businesses.csv')