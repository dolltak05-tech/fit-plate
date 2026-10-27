# Fit Plate - budget based weekly diet planner
# Run with:  streamlit run app.py

import random
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ---------------------------------------------------------------
# 1. Basic data (lists and dictionaries)
# ---------------------------------------------------------------
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
        'Friday', 'Saturday', 'Sunday']

# How the day's calories and money are shared between meals
MEAL_SHARE = {'Breakfast': 0.25, 'Lunch': 0.35, 'Snack': 0.10, 'Dinner': 0.30}

# Activity level -> multiplier
ACTIVITY = {
    'Sedentary (little exercise)': 1.2,
    'Light (1-3 days/week)': 1.375,
    'Moderate (3-5 days/week)': 1.55,
    'Very active (6-7 days/week)': 1.725,
}

# Goal -> (calories to add/remove, protein grams per kg body weight)
GOALS = {
    'Lose weight': (-400, 1.6),
    'Maintain weight': (0, 1.2),
    'Gain muscle': (400, 1.8),
}


# ---------------------------------------------------------------
# 2. Classes
# ---------------------------------------------------------------
class Person:
    # Stores user details and calculates daily needs

    def __init__(self, age, gender, height, weight, activity, goal):
        self.age = age
        self.gender = gender
        self.height = height      # cm
        self.weight = weight      # kg
        self.activity = activity
        self.goal = goal

    def daily_calories(self):
        # Mifflin-St Jeor formula for BMR
        bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age
        if self.gender == 'Male':
            bmr += 5
        else:
            bmr -= 161
        calorie_change, _ = GOALS[self.goal]
        return round(bmr * ACTIVITY[self.activity] + calorie_change)

    def daily_macros(self):
        calories = self.daily_calories()
        _, protein_per_kg = GOALS[self.goal]
        protein = self.weight * protein_per_kg           # grams
        fat = calories * 0.25 / 9                        # 25% of calories, 1 g fat = 9 kcal
        carbs = (calories - protein * 4 - fat * 9) / 4   # rest of calories, 1 g = 4 kcal
        return round(protein), round(carbs), round(fat)


class Food:
    # Base class for any food item
    tag = ''

    def __init__(self, row):
        self.name = row['food']
        self.serving = row['serving']

    def label(self, servings):
        return f'{self.name} ({servings} x {self.serving}) [{self.tag}]'


class VegFood(Food):          # inheritance
    tag = 'Veg'


class NonVegFood(Food):       # inheritance
    tag = 'Non-Veg'


def make_food(row):
    if row['type'] == 'Veg':
        return VegFood(row)
    return NonVegFood(row)


# ---------------------------------------------------------------
# 3. Functions
# ---------------------------------------------------------------
@st.cache_data
def load_foods(diet):
    # Read the spreadsheet and keep only the foods the user can eat
    foods = pd.read_csv('foods.csv')
    if diet == 'Veg':
        foods = foods[foods['type'] == 'Veg']
    return foods


def make_result(picks, servings):
    # Turn the chosen foods into one row of the plan
    items = [make_food(row).label(servings) for _, row in picks.iterrows()]
    return {
        'Items': ', '.join(items),
        'Cost (Rs)': round(picks['price'].sum() * servings, 1),
        'Calories': round(picks['calories'].sum() * servings),
        'Protein (g)': round(picks['protein'].sum() * servings, 1),
        'Carbs (g)': round(picks['carbs'].sum() * servings, 1),
        'Fat (g)': round(picks['fat'].sum() * servings, 1),
    }


def build_meal(foods, meal, calorie_target, money_target):
    # Try 30 random combinations, keep the highest-protein one within budget
    options = foods[foods['meal'] == meal]
    best = None

    for _ in range(30):
        picks = options.sample(n=min(2, len(options)),
                               random_state=random.randint(0, 100000))
        # servings needed to reach the calorie target (steps of 0.5)
        servings = round(calorie_target / picks['calories'].sum() * 2) / 2
        servings = max(0.5, min(servings, 3))

        cost = picks['price'].sum() * servings
        protein = picks['protein'].sum() * servings

        if cost <= money_target:
            if best is None or protein > best['Protein (g)']:
                best = make_result(picks, servings)

    if best is None:   # nothing fits the budget -> take the cheapest foods
        picks = options.nsmallest(2, 'price')
        best = make_result(picks, 1)
    return best


def build_week(foods, person, weekly_budget):
    # Build the 7-day plan as a table
    calorie_target = person.daily_calories()
    daily_budget = weekly_budget / 7
    rows = []
    for day in DAYS:
        for meal, share in MEAL_SHARE.items():
            result = build_meal(foods, meal,
                                calorie_target * share,
                                daily_budget * share)
            rows.append({'Day': day, 'Meal': meal, **result})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------
# 4. Web page (Streamlit)
# ---------------------------------------------------------------
st.set_page_config(page_title='Fit Plate',
                   menu_items={'Get help': None, 'Report a bug': None, 'About': None})

# Hide Streamlit's own menu, footer, heading links and table/chart toolbars
st.markdown('''
<style>
#MainMenu, footer, [data-testid='stToolbar'], [data-testid='stDecoration'] {display: none !important;}
[data-testid='stHeaderActionElements'] {display: none !important;}
[data-testid='stElementToolbar'] {display: none !important;}
button[title='View fullscreen'] {display: none !important;}
</style>
''', unsafe_allow_html=True)

# Starting values for every input (used at first load and by Clear_data)
DEFAULTS = {
    'budget': 2000, 'diet': 'Veg', 'gender': 'Male', 'age': 20,
    'height': 170, 'weight': 65,
    'activity': list(ACTIVITY)[0], 'goal': list(GOALS)[0],
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def clear_data():
    st.cache_data.clear()                  # forget the loaded spreadsheet data
    for key, value in DEFAULTS.items():    # put every input back to its start value
        st.session_state[key] = value


# Title on the left, Clear_data button on the right
title_col, button_col = st.columns([4, 1])
with title_col:
    st.title('Fit Plate', anchor=False)
    st.caption('A weekly diet plan that fits your budget')
with button_col:
    st.button('Clear_data', on_click=clear_data)

with st.sidebar:
    st.header('Your details')
    budget = st.number_input('Weekly food budget (Rs)', min_value=300, step=100, key='budget')
    diet = st.radio('Diet type', ['Veg', 'Non-Veg'], horizontal=True, key='diet')
    gender = st.selectbox('Gender', ['Male', 'Female'], key='gender')
    age = st.number_input('Age', min_value=15, max_value=80, key='age')
    height = st.number_input('Height (cm)', min_value=120, max_value=220, key='height')
    weight = st.number_input('Weight (kg)', min_value=30, max_value=150, key='weight')
    activity = st.selectbox('Activity level', list(ACTIVITY), key='activity')
    goal = st.selectbox('Goal', list(GOALS), key='goal')

# Daily needs
person = Person(age, gender, height, weight, activity, goal)
protein, carbs, fat = person.daily_macros()

st.subheader('Your daily needs', anchor=False)
c1, c2, c3, c4 = st.columns(4)
c1.metric('Calories', f'{person.daily_calories()} kcal')
c2.metric('Protein', f'{protein} g')
c3.metric('Carbs', f'{carbs} g')
c4.metric('Fat', f'{fat} g')

# Weekly plan
foods = load_foods(diet)
random.seed(1)          # same inputs always give the same plan
plan = build_week(foods, person, budget)
total_cost = plan['Cost (Rs)'].sum()

st.subheader('Your weekly plan', anchor=False)
if total_cost <= budget:
    st.success(f'Total cost Rs {total_cost:.0f} is within your budget of Rs {budget}.')
else:
    st.warning(f'Total cost Rs {total_cost:.0f} is above your budget of Rs {budget}. '
               'Try a higher budget or choose Veg.')

tabs = st.tabs(DAYS)
for tab, day in zip(tabs, DAYS):
    with tab:
        day_plan = plan[plan['Day'] == day].drop(columns='Day')
        st.table(day_plan.set_index('Meal'))      # plain table, no toolbar
        day_cost = day_plan['Cost (Rs)'].sum()
        day_cal = day_plan['Calories'].sum()
        day_protein = day_plan['Protein (g)'].sum()
        st.write(f'Day total: Rs {day_cost:.0f} | {day_cal} kcal | Protein {day_protein:.0f} g')

# Cost per day bar chart (days kept in Monday to Sunday order)
st.subheader('Cost per day', anchor=False)
daily_cost = plan.groupby('Day')['Cost (Rs)'].sum().reindex(DAYS)

fig, ax = plt.subplots(figsize=(8, 3.5))
ax.bar(DAYS, daily_cost.values, color='#2e8b57')
ax.axhline(budget / 7, color='gray', linestyle='--', label='Daily budget')
ax.set_xlabel('Day')
ax.set_ylabel('Cost (Rs)')
ax.legend()
plt.xticks(rotation=30)
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)

st.download_button('Download plan as CSV',
                   plan.to_csv(index=False),
                   file_name='fitplate_weekly_plan.csv')

st.caption('Values are approximate and for learning purposes. '
           'This is not medical advice.')