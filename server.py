import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import random

with open('dataset.json', 'r') as dataset_file:
    DATA = json.load(dataset_file)
    

class RestaurantHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        if path == '/listMeals':
            self.handle_list_meals(query_params)
        elif path == '/getMeal':
            self.handle_get_meal(query_params)
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode('utf-8'))

    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = parse_qs(post_data.decode('utf-8'))

        if path == '/quality':
            self.handle_quality_calculation(data)
        elif path == '/price':
            self.handle_price_calculation(data)
        elif path == '/random':
            self.handle_random_selection(data)
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode('utf-8'))


    def meets_dietary_preference(self, ingredients, is_vegetarian, is_vegan):
        for ingredient_name in ingredients:
            ingredient_detail = next((ing for ing in DATA['ingredients'] if ing['name'].lower() == ingredient_name.lower()), None)
            if not ingredient_detail:
                continue
            
            groups = ingredient_detail.get('groups', [])
            
            if is_vegan and 'vegan' not in groups:
                return False
            
            if is_vegetarian and 'vegetarian' not in groups:
                return False
        
        return True

    def handle_list_meals(self, query_params):
        is_vegetarian = query_params.get('is_vegetarian', [False])[0] == 'true'
        is_vegan = query_params.get('is_vegan', [False])[0] == 'true'
        sort_by = query_params.get('name', [None])[0]

        filtered_meals = []
        for meal in DATA['meals']:
            ingredients = [ing['name'] for ing in meal['ingredients']]
            if self.meets_dietary_preference(ingredients, is_vegetarian, is_vegan):
                filtered_meals.append({'id': meal['id'], 'name': meal['name'], 'ingredients': ingredients})

        if sort_by == 'name':
            filtered_meals.sort(key=lambda x: x['name'])

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(filtered_meals).encode('utf-8'))
        
    def handle_get_meal(self, query_params):
        try:
            meal_id = int(query_params['id'][0])
        except (KeyError, ValueError):
            self.send_error(400, 'Invalid or missing "id" parameter')
            return

        meal = next((meal for meal in DATA['meals'] if meal['id'] == meal_id), None)
        if meal:
            ingredients = []
            for ingredient in meal['ingredients']:
                detailed_ingredient = next((ing for ing in DATA['ingredients'] if ing['name'] == ingredient['name']), None)
                if detailed_ingredient:
                    ingredients.append({
                        'name': detailed_ingredient['name'],
                        'groups': detailed_ingredient['groups'],
                        'options': detailed_ingredient['options']
                    })
            response = {'id': meal['id'], 'name': meal['name'], 'ingredients': ingredients}
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_error(404, 'Meal not found')

    def handle_quality_calculation(self, data):
        try:
            meal_id = int(data['meal_id'][0])
        except (KeyError, ValueError):
            self.send_error(400, 'Invalid or missing "meal_id" parameter')
            return

        def calculate_quality(meal, data):
            quality_scores = {'high': 30, 'medium': 20, 'low': 10}
            total_quality = 0
            for ingredient in meal['ingredients']:
                ingredient_name = ingredient['name'].lower()
                if ingredient_name in data:
                    quality = data[ingredient_name][0]
                else:
                    quality = 'high'
                    
                total_quality += quality_scores[quality]

            return total_quality // len(meal['ingredients'])

        meal = next((meal for meal in DATA['meals'] if meal['id'] == meal_id), None)
        if not meal:
            self.send_error(404, 'Meal not found')
            return

        total_quality = calculate_quality(meal, data)
        response = {'quality': total_quality}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def handle_price_calculation(self, data):
        try:
            meal_id = int(data['meal_id'][0])
        except (KeyError, ValueError):
            self.send_error(400, 'Invalid or missing "meal_id" parameter')
            return
        
        def calculate_price(meal, data):
            price_per_quality = {'high': 0.00, 'medium': 0.05, 'low': 0.10}
            price = 0

            for ingredient in meal['ingredients']:
                ingredient_name = ingredient['name'].lower()  

                lowercase_data = {key.lower(): value for key, value in data.items()}
                
                quality = lowercase_data.get(ingredient_name, ['high'])[0]
                
                ingredient_detail = next((ing for ing in DATA['ingredients'] if ing['name'].lower() == ingredient_name), None)
                
                if ingredient_detail:
                    option = next((opt for opt in ingredient_detail['options'] if opt['quality'] == quality), None)
                    if option:
                        price += (ingredient['quantity'] / 1000) * option['price'] + price_per_quality[quality]
            return price

        meal = next((meal for meal in DATA['meals'] if meal['id'] == meal_id), None)
        if not meal:
            self.send_error(404, 'Meal not found')

        total_price = calculate_price(meal, data)
        response = {'price': round(total_price, 2)}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def handle_random_selection(self, data):
        budget = float(data.get('budget', [float('inf')])[0])

        possible_meals = []
        def random_quality_selection(meal):
            quality_scores = {'high': 30, 'medium': 20, 'low': 10}
            price_per_quality = {'high': 0.00, 'medium': 0.05, 'low': 0.10}

            quality_score = 0
            price = 0
            for ingredient in meal['ingredients']:
                random_quality = random.choice(['high', 'medium', 'low'])
                ingredient_detail = next((ing for ing in DATA['ingredients'] if ing['name'] == ingredient['name']), None)
                if ingredient_detail:
                    option = next((opt for opt in ingredient_detail['options'] if opt['quality'] == random_quality), None)
                    if option:
                        price += (ingredient['quantity'] / 1000) * option['price'] + price_per_quality[random_quality]
                        quality_score += quality_scores[random_quality]
            return quality_score // len(meal['ingredients']), price

        def meal_quality_details(meal):
            details = []
            for ingredient in meal['ingredients']:
                random_quality = random.choice(['high', 'medium', 'low'])
                details.append({'name': ingredient['name'], 'quality': random_quality})
            return details

        for meal in DATA['meals']:
            meal_quality, meal_price = random_quality_selection(meal)
            if meal_price <= budget:
                possible_meals.append({
                    'id': meal['id'],
                    'name': meal['name'],
                    'price': round(meal_price, 2),
                    'quality_score': meal_quality,
                    'ingredients': meal_quality_details(meal)
                })

        if possible_meals:
            response = random.choice(possible_meals)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_error(404, 'No meal found within budget')


def run_server(server_class=HTTPServer, handler_class=RestaurantHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
