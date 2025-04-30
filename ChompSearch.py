from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Chomp – Let's Find Your Snack!</title>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Nunito', sans-serif;
            background: #FFD6CC; /* pastel red/orange */
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
            width: 90%;
            max-width: 500px;
            text-align: center;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 20px;
        }
        form {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 20px;
        }
        input[type="text"] {
            width: 100%;
            max-width: 300px;
            padding: 12px;
            font-size: 16px;
            border: 2px solid #ccc;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        button {
            padding: 12px 20px;
            background-color: #ff6f61;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background-color: #e05a4f;
        }
        img {
            width: 200px;
            margin-top: 20px;
        }
        .info {
            text-align: left;
            margin-top: 30px;
        }
        .info h2 {
            color: #343a40;
        }
        .info h3 {
            color: #495057;
            margin-top: 20px;
        }
        ul {
            padding-left: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Chomp – Let's Find Your Snack!</h1>
        <form method="post">
            <input type="text" name="barcode" placeholder="Enter Barcode" required>
            <button type="submit">Search</button>
        </form>

        {% if product %}
            <div class="info">
    <h2>{{ product['name'] }}</h2>
    {% if product['image_url'] %}
        <img src="{{ product['image_url'] }}" alt="Product Image">
    {% endif %}
    <h3>Category: {{ product['category'] }}</h3>
    <h3>Nutrition Facts (per 100g)</h3>
    <ul>
        {% for nutrient, value in product['nutrition'].items() %}
            <li>{{ nutrient }}: {{ value }}</li>
        {% endfor %}
    </ul>
    <h3>Common Allergens</h3>
    <ul>
        {% if product['allergens'] %}
            {% for allergen in product['allergens'] %}
                <li>{{ allergen }}</li>
            {% endfor %}
        {% else %}
            <li>None</li>
        {% endif %}
    </ul>
</div>

        {% endif %}
    </div>
</body>
</html>
'''

def fetch_product_info(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()
    if data.get('status') != 1:
        return None

    product_data = data['product']
    nutriments = product_data.get('nutriments', {})
    ingredients = product_data.get('ingredients_text', '').lower()

    sugar = nutriments.get('sugars_100g', 0) or 0
    fat = nutriments.get('fat_100g', 0) or 0
    salt = nutriments.get('salt_100g', 0) or 0

    # Simple classification rules
    if sugar > 10:
        category = "Sweet"
    elif salt > 1 or "salt" in ingredients or "cheese" in ingredients or "spice" in ingredients:
        category = "Savory"
    elif sugar < 5 and fat < 5 and salt < 0.5:
        category = "Healthy"
    else:
        category = "Uncategorized"

    nutrition = {
        'Energy (kcal)': nutriments.get('energy-kcal_100g', 'N/A'),
        'Fat (g)': fat,
        'Carbohydrates (g)': nutriments.get('carbohydrates_100g', 'N/A'),
        'Sugars (g)': sugar,
        'Proteins (g)': nutriments.get('proteins_100g', 'N/A'),
        'Salt (g)': salt,
    }

    allergens = [a.split(':')[-1] for a in product_data.get('allergens_tags', [])]

    return {
        'name': product_data.get('product_name', 'Unknown Product'),
        'image_url': product_data.get('image_url', ''),
        'nutrition': nutrition,
        'allergens': allergens,
        'category': category
    }

   

@app.route('/', methods=['GET', 'POST'])
def home():
    product = None
    if request.method == 'POST':
        barcode = request.form['barcode']
        product = fetch_product_info(barcode)
    return render_template_string(TEMPLATE, product=product)

if __name__ == '__main__':
    app.run(debug=True)


