from flask import Flask, render_template, request, url_for, session
import os
import re  
from dotenv import load_dotenv
from supabase import create_client

# 1. SETUP & CONFIGURATION
load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# 2. DATABASE CONNECTION
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
if not url or not key:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set.")
supabase = create_client(url, key)

# 2. HELPER FUNCTIONS
def get_dynamic_substitutions(recipe_ingredients):
    # Expanded database of culinary swaps
    swap_master_map = {
        # DAIRY ALERTS
        'milk': {'sub': 'Oat or Almond Milk', 'type': 'Dairy'},
        'butter': {'sub': 'Vegan Butter or Coconut Oil', 'type': 'Dairy'},
        'cheese': {'sub': 'Nutritional Yeast or Vegan Cheese', 'type': 'Dairy'},
        'cream': {'sub': 'Coconut Cream', 'type': 'Dairy'},
        'yogurt': {'sub': 'Coconut Yogurt', 'type': 'Dairy'},
        
        # EGG ALERTS
        'egg': {'sub': 'Flax-egg (1tbsp ground flax + 3tbsp water)', 'type': 'Egg'},
        'mayonnaise': {'sub': 'Vegan Mayo (Aquafaba based)', 'type': 'Egg'},
        
        # GLUTEN ALERTS
        'flour': {'sub': 'GF All-purpose Blend', 'type': 'Gluten'},
        'soy sauce': {'sub': 'Tamari (Gluten-Free)', 'type': 'Gluten'},
        'breadcrumbs': {'sub': 'Crushed GF Crackers or Panko', 'type': 'Gluten'},
        'pasta': {'sub': 'Chickpea or Brown Rice Pasta', 'type': 'Gluten'},

        # NUT ALERTS
        'peanut': {'sub': 'Roasted Sunflower Seeds', 'type': 'Nuts'},
        'almond': {'sub': 'Pumpkin Seeds (Pepitas)', 'type': 'Nuts'},
        'cashew': {'sub': 'Sunflower Seed Butter', 'type': 'Nuts'},
        
        # VEGAN/LIFESTYLE
        'honey': {'sub': 'Agave or Maple Syrup', 'type': 'Vegan'},
        'gelatine': {'sub': 'Agar Agar', 'type': 'Vegan'}
    }

    active_subs = []
    ingredients_lower = recipe_ingredients.lower()

    # Search for keys in the ingredients text
    for key, data in swap_master_map.items():
        if key in ingredients_lower:
            active_subs.append({
                'original_ingredient': key.title(),
                'substitute': data['sub'],
                'allergen_type': data['type']
            })
            
    return active_subs

# ROUTE 1: THE SEARCH PAGE
@app.route("/", methods=["GET"])
def index():
    # 1. IDENTIFY THE ACTION
    # We look for the 'action' parameter we added to our submit buttons
    action = request.args.get("action") 
    
    # 2. LOGIC HANDLING
    if action == "update":
        # Handle Pantry Logic
        selected_excludes = request.args.getlist('exclude')
        # You might want to save these to a session so they persist
        session['selected_excludes'] = selected_excludes
    elif action == "search":
        # Handle Search Logic
        search_query = request.args.get("search", "").strip()
        session['search_query'] = search_query
    else:
        # Default load: fetch from session if available
        selected_excludes = session.get('selected_excludes', [])
        search_query = session.get('search_query', "")

    # ... continue with the rest of your existing database query logic ...
    # INPUT SANITISATION
    raw_query = request.args.get("search", "").strip()
    # Keep only alphanumeric characters and spaces (removes scripts/injection attempts)
    search_query = re.sub(r'[^\w\s-]', '', raw_query)[:100]

    excludes_desktop = request.args.getlist('exclude')
    excludes_mobile = request.args.getlist('exclude_mob')
    selected_excludes = list(set(excludes_desktop + excludes_mobile))

    # STATE PERSISTENCE
    if search_query or selected_excludes:
        session['last_search'] = request.full_path
        session.modified = True

    # DATABASE QUERY
    db_query = supabase.table("recipes").select("*, allergen_warnings")

    if search_query:
        db_query = db_query.ilike("title", f"%{search_query}%")
    
    # Mapping (Matches 14-allergen Expert Logic)
    mapping = {
        "celery": "celery", "gluten": "gluten", "crustaceans": "crustaceans",
        "eggs": "eggs", "fish": "fish", "lupin": "lupin", "milk": "dairy",
        "dairy": "dairy", "molluscs": "molluscs", "mustard": "mustard",
        "nuts": "tree_nuts", "peanuts": "peanuts", "sesame": "sesame",
        "soya": "soy", "sulphites": "sulphites"
    }

    for allergen in selected_excludes:
        # Avoid Paradox: don't exclude the term the user is actually searching for
        if search_query and (search_query.lower() in allergen.lower()):
            continue
        suffix = mapping.get(allergen.lower())
        if suffix:
            db_query = db_query.eq(f"contains_{suffix}", False)

    try:
        results = db_query.order("title").limit(24).execute()
        recipes_to_show = results.data
        for recipe in recipes_to_show:
            # Check the ingredients text and attach matching swaps
            recipe['substitutions'] = get_dynamic_substitutions(recipe.get('ingredients', ''))

    except Exception as e:
        print(f"Database Error: {e}")
        recipes_to_show = []
 
    return render_template(
        "index.html", 
        recipes=recipes_to_show, 
        query=search_query, 
        selected_excludes=selected_excludes 
    )

# ROUTE 2: THE RECIPE DETAIL PAGE
@app.route("/recipe/<int:recipe_id>")
def recipe_detail(recipe_id):
    # Back button logic
    session_url = session.get('last_search')
    referrer_url = request.referrer if request.referrer and "recipe" not in request.referrer else None
    back_url = session_url or referrer_url or url_for('index')

    try:
        # 1. Fetch the recipe
        recipe_res = supabase.table("recipes").select("*").eq("id", recipe_id).single().execute()
        recipe = recipe_res.data
        
        if not recipe:
            return "Recipe not found", 404

        # 2. GENERATE DYNAMIC SWAPS
        # Pass the ingredients string to function
        dynamic_substitutions = get_dynamic_substitutions(recipe.get('ingredients', ''))

        # 3. Render the page
        return render_template(
            "detail.html", 
            recipe=recipe, 
            substitutions=dynamic_substitutions, # This now uses the function results!
            back_url=back_url
        )
        
    except Exception as e:
        print(f"Error: {e}")
        return "Internal Server Error", 500

@app.after_request
def add_security_headers(response):
    # This policy allows:
    # 1. Scripts/Styles from your own site ('self')
    # 2. Google Analytics (googletagmanager.com and google-analytics.com)
    # 3. Inline styles (unsafe-inline) - often needed for simple CSS
    csp = (
    "default-src 'self'; "
    "script-src 'self' https://cdn.jsdelivr.net https://www.googletagmanager.com; " # Added Bootstrap JS
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; " # Added Bootstrap CSS
    "font-src 'self' https://fonts.gstatic.com; " 
    "img-src 'self' data: https://www.google-analytics.com; "
    "connect-src 'self' https://*.supabase.co https://cdn.jsdelivr.net;"
)
    response.headers['Content-Security-Policy'] = csp
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

if __name__ == "__main__":
    app.run(
    host='0.0.0.0',
    port=5000,
    debug=os.getenv('FLASK_DEBUG', '0') == '1'
)