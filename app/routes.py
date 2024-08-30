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
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }
                input[type="submit"]:hover {
                    background-color: #555;
                }
            </style>
        </head>
        <body>
            <form action="/scrape" method="post">
                <label for="state">State:</label>
                <input type="text" id="state" name="state" list="states">
                <datalist id="states">
                    <option value="Alabama">
                    <option value="Alaska">
                    <option value="Arizona">
                    <option value="Arkansas">
                    <option value="California">
                    <option value="Colorado">
                    <option value="Connecticut">
                    <option value="Delaware">
                    <option value="Florida">
                    <option value="Georgia">
                    <option value="Hawaii">
                    <option value="Idaho">
                    <option value="Illinois">
                    <option value="Indiana">
                    <option value="Iowa">
                    <option value="Kansas">
                    <option value="Kentucky">
                    <option value="Louisiana">
                    <option value="Maine">
                    <option value="Maryland">
                    <option value="Massachusetts">
                    <option value="Michigan">
                    <option value="Minnesota">
                    <option value="Mississippi">
                    <option value="Missouri">
                    <option value="Montana">
                    <option value="Nebraska">
                    <option value="Nevada">
                    <option value="New Hampshire">
                    <option value="New Jersey">
                    <option value="New Mexico">
                    <option value="New York">
                    <option value="North Carolina">
                    <option value="North Dakota">
                    <option value="Ohio">
                    <option value="Oklahoma">
                    <option value="Oregon">
                    <option value="Pennsylvania">
                    <option value="Rhode Island">
                    <option value="South Carolina">
                    <option value="South Dakota">
                    <option value="Tennessee">
                    <option value="Texas">
                    <option value="Utah">
                    <option value="Vermont">
                    <option value="Virginia">
                    <option value="Washington">
                    <option value="West Virginia">
                    <option value="Wisconsin">
                    <option value="Wyoming">
                </datalist>
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
    bot.go_to('https://www.google.com/maps/search/') 
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

    # Generate CSV
    csv_data = generate_csv(unique_businesses)
    return send_file(csv_data, mimetype='text/csv', attachment_filename='businesses.csv', as_attachment=True)