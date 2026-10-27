# Fit Plate

A budget-based weekly diet planner built with Python, Pandas, Matplotlib and Streamlit. The user enters a weekly food budget, body details and diet type (Veg or Non-Veg). The app shows the daily calories, protein, carbohydrate and fat needed and builds a 7-day meal plan that tries to stay within the budget.

## Why this project
A healthy diet looks costly and most people do not know how much protein, carbs and fat they need. Fit Plate calculates the needs and plans a full week of meals according to the budget, so planning takes seconds instead of hours.

## Features
- Weekly diet plan (Breakfast, Lunch, Snack, Dinner for 7 days) within the budget
- Veg / Non-Veg option
- Daily calorie, protein, carbohydrate and fat needs based on age, gender, height, weight, activity and goal (lose weight, maintain, gain muscle)
- Day-wise tables with cost, calories and nutrients of every meal
- Cost per day bar graph (Monday to Sunday) with a daily budget line
- Food data kept in a spreadsheet (foods.csv) that anyone can edit
- Download the weekly plan as a CSV file

## How it works
1. **Daily calories:** BMR is calculated with the Mifflin-St Jeor formula (10 x weight + 6.25 x height - 5 x age, then +5 for male or -161 for female). It is multiplied by an activity factor (1.2 to 1.725). 400 kcal is subtracted for weight loss or added for muscle gain.
2. **Macros:** protein = body weight x 1.6 (lose), 1.2 (maintain) or 1.8 (gain) grams. Fat = 25% of calories (9 kcal per gram). Carbohydrate = the remaining calories (4 kcal per gram).
3. **Meal split:** calories and money are shared as Breakfast 25%, Lunch 35%, Snack 10% and Dinner 30%.
4. **Meal builder:** for each meal the program tries 30 random pairs of foods from foods.csv, adjusts the servings to reach the calorie target, and keeps the highest-protein pair that fits the meal's budget. If nothing fits, it picks the cheapest foods and warns that the plan is above budget.
5. **Veg / Non-Veg:** Veg keeps only rows marked Veg in the spreadsheet. Non-Veg uses all rows.

## Tech stack
- Python 3
- Pandas (reading and filtering the spreadsheet, building the plan table)
- Matplotlib (cost per day graph)
- Streamlit (web page)

## Project structure
- `app.py` - main program (classes, functions and the web page)
- `foods.csv` - food data: name, type, meal, serving, price, calories, protein, carbs, fat
- `requirements.txt` - libraries needed
- `screenshots/` - images used in this README

## How to run on your computer
1. Install Python 3.10 or newer.
2. Download or clone this repository.
3. Open a terminal in the project folder and run `pip install -r requirements.txt`
4. Run `streamlit run app.py`
5. The app opens at http://localhost:8501

## Editing the food data
Open `foods.csv` in Excel or Google Sheets, change prices or add foods (keep the same column names), save as CSV and refresh the page. Prices are approximate Indian prices in Rs per serving.

## Python concepts used
Variables and data types, if/else, loops, lists, dictionaries, functions, classes and objects (Person), inheritance (Food, VegFood, NonVegFood), Pandas DataFrame, Matplotlib graph.

## Disclaimer
Prices and nutrition values are approximate and made for a college project. This is not medical or dietary advice.

## Future scope
- Move the food data to a database (ADBMS version)
- Add more foods, regional cuisines and allergy filters
- Save user profiles and past plans

## Author
Your Name - Your Course, Your College
