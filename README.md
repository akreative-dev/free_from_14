# FreeFrom14

**Allergen-aware recipe search using Python, Flask and PostgreSQL**

FreeFrom14 is an MSc Computer Science research project exploring whether
ethical use of web-based recipe data and faceted search can improve the
experience of finding recipes suitable for people managing food allergens.

The application allows users to search recipes and filter results against
the 14 major allergen categories used in UK/EU food-labelling guidance.

## The Problem

Finding recipes that avoid specific allergens can require users to read
long ingredient lists and manually check for relevant ingredients.

FreeFrom14 explores whether structured allergen filtering can make this
process faster and easier while keeping the limitations of automated
ingredient analysis visible to the user.

## Key Features

- Searchable recipe database containing approximately 50,000 recipes
- Filtering across 14 allergen categories
- Ingredient-level allergen analysis
- Recipe detail pages with allergen warnings
- Automated ingredient substitution suggestions
- Responsive interface for desktop and mobile
- Original recipe attribution and source links
- Guidance-only safety messaging

## The 14 Allergen Categories

The application tracks:

- Cereals containing gluten
- Crustaceans
- Eggs
- Fish
- Lupin
- Milk
- Molluscs
- Mustard
- Peanuts
- Sesame
- Soybeans
- Sulphur dioxide / sulphites
- Tree nuts
- Celery

## Technical Architecture

```text
Recipe Data Sources
        ↓
Data Cleaning & Normalisation
        ↓
Allergen Processing
        ↓
Supabase PostgreSQL
        ↓
Flask Application
        ↓
Search & Allergen Filtering
        ↓
Recipe Detail & Warnings

## Technology

Python
Flask
Supabase / PostgreSQL
HTML5
CSS3
JavaScript
spaCy
Word2Vec
Python-Dotenv

## Allergen Detection

The deployed application uses a custom rule-based Regex system to analyse
recipe titles and ingredient text.

The processing pipeline includes rules designed to reduce false positives
where words can have different culinary meanings. Examples investigated
during development include:

Eggplant
Buckwheat
Gluten-free
Coconut
Nutmeg
Butternut squash
Water chestnuts
Soy lecithin

The database stores boolean contains_[allergen] fields for the 14
tracked allergen categories.

BOTANICAL EXCLUSIONS (False Positive Mitigation)
------------------------------------------------------------
This database employs a "Botanical vs. Culinary" exclusion layer 
as a rule designed to reduce false positives. The following 
common "False Positives" are explicitly flagged as FALSE:

CATEGORY          | EXCLUDED KEYWORDS (Triggered but ignored)
------------------------------------------------------------
Tree Nuts         | Coconut, Nutmeg, Butternut Squash, 
                  | Water Chestnuts, Shea Butter, 
                  | Nutritional Yeast, Pine Nuts, Chestnuts.
------------------------------------------------------------
Gluten            | Buckwheat, Glutinous Rice, Gluten-Free.
------------------------------------------------------------
Eggs              | Eggplant.
------------------------------------------------------------
Soy               | Soy Lecithin (Refined fat, low protein).
------------------------------------------------------------

*Note on Pine Nuts/Chestnuts: These are botanically distinct 
from common tree nut allergies (Cashew/Almond) and are 
excluded to focus on primary culinary allergens.

## NLP Research

Several NLP approaches were investigated during development, including
spaCy Named Entity Recognition and Word2Vec.

The NLP work formed part of the wider research and experimentation around
allergen identification and ingredient substitutions.

Word2Vec was used to explore semantically related ingredients and generate
potential substitution suggestions.

## Data Engineering

The project involved processing recipe data from multiple sources before
loading the final dataset into Supabase PostgreSQL.

The data pipeline included:

Data normalisation
Schema standardisation
Deduplication using recipe URLs
Allergen classification
Boolean data validation
Source attribution
Data quality checks

The final database structure includes recipe metadata, ingredient text,
source information and allergen flags.




## User Experience

The interface was designed around faceted search, allowing users to apply
multiple allergen filters while searching for recipes.

The visual design uses a deliberately distinctive Vintage Ledger /
Neo-Brutalist aesthetic, with strong typography, asymmetrical layouts
and high-contrast interface elements.

The interface also provides explicit guidance that automated allergen
analysis should not replace checking the original ingredient information.

## Research & Evaluation

FreeFrom14 was evaluated using a mixed approach combining system testing
with user feedback.

User testing investigated:

- Recipe search and filtering
- Speed of locating recipes
- Visibility of allergen information
- Understanding of warning labels
- Comparison between ingredient lists and warnings
- Mobile usability
- Understanding of the application's limitations

The evaluation formed part of the wider MSc Computer Science research
project.

## Safety & Limitations

FreeFrom14 is an information and research tool. It is not medical
advice and should not be treated as a guarantee that a recipe is safe
for a particular allergy.

Automated ingredient analysis can produce incorrect classifications.

Users with serious or life-threatening allergies should always verify
the original ingredient list and relevant product information themselves.

The application also does not currently model every possible source of
cross-contamination or "may contain" information.

## Ethical Data Use

The project considered ethical and legal issues surrounding recipe data
collection and processing.

The wider research process considered:

- Respecting website terms and robots.txt restrictions
- Using publicly available recipe information
- Source attribution
- Deduplication
- Avoiding unnecessary personal data
- Transparency about automated analysis
- Providing links back to original recipe sources

## Installation

1. Clone the repository and create a Python environment.

2. Install the dependencies:

pip install -r requirements.txt

3. Create a .env file in the root directory and include:

FLASK_SECRET_KEY=
SUPABASE_URL=
SUPABASE_KEY=

Populate these variables with your own credentials.

4. Start the application:

python app.py

The application runs locally on:

http://localhost:5000


## Environment Variables

The repository includes .env.example as a template.

Never commit your real .env file or API credentials.

## Future Development

Potential future improvements identified during the project include:

- "May contain" and cross-contamination information
- User verification of automated allergen classifications
- Authenticated recipe/pantry features
- Support for additional food intolerances

## Project Context

FreeFrom14 was developed as an MSc Computer Science research project.

The project brought together software engineering, data processing,
natural language processing, database design, user-centred design and
research evaluation.


## Database Structure

The Supabase PostgreSQL database stores recipe metadata alongside
allergen-processing results.

Key fields include:

- `id` — unique recipe identifier
- `external_id` — source API identifier
- `title` — recipe title
- `ingredients` — ingredient text used for analysis
- `recipe_url` — original recipe URL and deduplication key
- `api_source` — source attribution
- `attribution_required` — source attribution flag
- `contains_[allergen]` — boolean allergen classifications

