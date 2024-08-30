/**
 * @typedef {import('../../frontend/node_modules/botasaurus-controls/dist/index').Controls} Controls
 */

const CountryOptions = [{ "value": "US", "label": "United States (2829 Cities)" }];

function fixupdatebugs(controls) {
    if (typeof controls.numberGreaterThanOrEqualToOne === 'function') {
        controls.greaterThanOrEqualToOne = controls.numberGreaterThanOrEqualToOne
        controls.greaterThanOrEqualToZero = controls.numberGreaterThanOrEqualToZero
        
    } else {
        controls.numberGreaterThanOrEqualToOne = controls.greaterThanOrEqualToOne
        controls.numberGreaterThanOrEqualToZero = controls.greaterThanOrEqualToZero 
    }
}
/**
 * @param {Controls} controls
 */
function getInput(controls) {
    const hasCountry = (data) => data['country']
    controls
        .listOfTexts('queries', {
            isDisabled: hasCountry,
            defaultValue: ["Real Estate Agents in Miami"],
            placeholder: "Real Estate Agents in Miami",
            label: 'Search Queries', 
            isRequired: true
        })
        .section("Extract Cities By Country", (section) => {
            fixupdatebugs(section)
            section
                .select('country', {
                    options: CountryOptions,
                })
                .text('business_type', {
                    placeholder: "Real Estate Agents",
                    isRequired: hasCountry
                }
                )
                .greaterThanOrEqualToOne('max_cities', {
                    placeholder: 100,
                    label: 'Maximum Cities to Extract (Leave empty to extract all cities in a country)'
                }).switch('randomize_cities'  , {
                    defaultValue:true, 
                    label:"Randomize Cities (Recommended)",
                    helpText:"When multiple users are targeting the same places in the same cities, it reduces the opportunity for each individual user to make a sale. By randomizing cities, it spreads the places across different locations, giving each user a better chance to make a sale."
                })
        })
        .section("Email and Social Links Extraction", (section) => {
            section.text('api_key', {
                placeholder: "2e5d346ap4db8mce4fj7fc112s9h26s61e1192b6a526af51n9",
                label: 'Email and Social Links Extraction API Key',
                helpText: 'Enter your API key to extract email addresses and social media links.',
            })
        })
        .section("Reviews Extraction", (section) => {

            fixupdatebugs(section)

            section
                .switch('enable_reviews_extraction', {
                    label: "Enable Reviews Extraction"
                })
                .numberGreaterThanOrEqualToZero('max_reviews', {
                    label: 'Max Reviews per Place (Leave empty to extract all reviews)',
                    placeholder: 30,
                     isShown: (data) => data['enable_reviews_extraction'], defaultValue: 20,
                })
                .choose('reviews_sort', {
                    label: "Sort Reviews By",
                    isRequired: true, isShown: (data) => data['enable_reviews_extraction'], defaultValue: 'newest', options: [{ value: 'newest', label: 'Newest' }, { value: 'most_relevant', label: 'Most Relevant' }, { value: 'highest_rating', label: 'Highest Rating' }, { value: 'lowest_rating', label: 'Lowest Rating' }]
                })
        })
        .section("Language and Max Results", (section) => {

            fixupdatebugs(section)

            section
                .addLangSelect()
                .numberGreaterThanOrEqualToOne('max_results', {
                    placeholder: 100,
                    label: 'Max Results per Search Query (Leave empty to extract all places)'
                })
        })
        .section("Geo Location", (section) => {

            fixupdatebugs(section)

            section
                .text('coordinates', {
                    placeholder: '12.900490, 77.571466'
                })
                .numberGreaterThanOrEqualToOne('zoom_level', {
                    label: 'Zoom Level (1-21)',
                    defaultValue: 14,
                    placeholder: 14
                })
        })
}

