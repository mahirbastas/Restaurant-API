
# Restaurant API

This Python project contains a simple API that serves a restaurant's menu. The API supports functionalities like listing meals, fetching a specific meal, calculating meal quality, calculating meal price, and selecting a random meal within budget.

## Getting Started

These instructions will help you to run or develop the project on your local machine.

### Prerequisites

To run this project, you will need Python 3 and the following Python libraries:

- `json`
- `http.server`
- `urllib.parse`
- `random`

### Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/mahirbastas/mahir-bastas-otsimo-internship-task-2024.git
   ```
2. Navigate to the project directory:

   ```bash
   cd mahir-bastas-otsimo-internship-task-2024
   ```
3. Start the server by running the following command:

   ```bash
   python3 server.py
   ```
4. You can now use the API. Sample requests:

   - To list all meals:

     ```bash
     curl http://localhost:8000/listMeals
     ```
   - To fetch a specific meal:

     ```bash
     curl http://localhost:8000/getMeal?id=1
     ```
   - To calculate meal quality:

     ```bash
     curl -X POST -d "meal_id=1&<ingredient1>=high&<ingredient2>=medium" http://localhost:8000/quality
     ```
   - To calculate meal price:

     ```bash
     curl -X POST -d "meal_id=1&<ingredient1>=high&<ingredient2>=medium" http://localhost:8000/price
     ```
   - To select a random meal within budget:

     ```bash
     curl -X POST -d "budget=10" http://localhost:8000/random
     ```

## Features

- **Listing Meals**: Endpoint to list all available meals.
- **Fetching a Specific Meal**: Endpoint to fetch details of a specific meal by its ID.
- **Calculating Meal Quality**: Endpoint to calculate the quality of a meal based on its ingredients.
- **Calculating Meal Price**: Endpoint to calculate the price of a meal based on its ingredients.
- **Selecting a Random Meal**: Endpoint to select a random meal within a specified budget.
