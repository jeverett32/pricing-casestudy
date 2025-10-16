import streamlit as st
import pandas as pd
import pickle
import numpy as np

# # --- Password Protection ---
# def check_password():
#     """Returns `True` if the user had the correct password."""
#     def password_entered():
#         if st.session_state["password"] == st.secrets["passwords"]["user1"]:
#             st.session_state["password_correct"] = True
#             del st.session_state["password"]  # Don't store password.
#         else:
#             st.session_state["password_correct"] = False

#     if "password_correct" not in st.session_state:
#         st.text_input("Password", type="password", on_change=password_entered, key="password")
#         return False
#     elif not st.session_state["password_correct"]:
#         st.text_input("Password", type="password", on_change=password_entered, key="password")
#         st.error("😕 Password incorrect")
#         return False
#     else:
#         return True

# if not check_password():
#     st.stop()  # Do not render the rest of the app if password is wrong

# --- Page Configuration ---
st.set_page_config(
    page_title="Sunoco Pricing Simulator",
    page_icon="⛽",
    layout="centered"
)

# --- Caching the Models for Performance ---
# This function loads all models and caches them so the app is fast.
@st.cache_data
def load_all_models():
    with open('volume_models.pkl', 'rb') as f:
        linear_models = pickle.load(f)
    with open('volume_models_polynomial.pkl', 'rb') as f:
        poly_models = pickle.load(f)
    with open('volume_models_randomforest.pkl', 'rb') as f:
        rf_models = pickle.load(f)
    
    return {
        "Linear Regression": linear_models,
        "Polynomial Regression": poly_models,
        "Random Forest": rf_models
    }

# Load the models using the cached function
all_models = load_all_models()

# --- App Title and Description ---
st.title("⛽ Sunoco Fuel Pricing Simulator")
st.markdown(
    "Use this tool to compare predictive models and see how your pricing strategy "
    "impacts fuel volume and total profit."
)

# --- User Inputs in the Sidebar ---
st.sidebar.header("Simulation Inputs")

# 1. Model Selection Toggle
model_selection = st.sidebar.radio(
    "Select a Prediction Model:",
    options=list(all_models.keys())
)

# 2. Site Selection
site_id = st.sidebar.selectbox(
    "Select a Site ID:",
    options=list(all_models[model_selection].keys())
)

# 3. Price Delta Slider
price_delta = st.sidebar.slider(
    "Price Delta to Competitor ($)",
    min_value=-0.25,
    max_value=0.25,
    value=0.00,  # Default to an even price
    step=0.01
)

# --- Dynamic Model Prediction ---
# Get the correct dictionary of models based on the radio button selection
model_dict = all_models[model_selection]
# Get the specific model for the selected site
model = model_dict[site_id]

# The model expects a 2D array, so we create a DataFrame
prediction_data = pd.DataFrame([[price_delta]], columns=['Price_Delta_To_Competitor'])
predicted_volume = model.predict(prediction_data)[0]

# --- Calculate Profit ---
cents_per_gallon = 0.15 - price_delta
total_profit = predicted_volume * cents_per_gallon

# --- Display The Results ---
st.subheader(f"Predictions for Site {site_id} (using {model_selection})")

col1, col2 = st.columns(2)
with col1:
    st.metric(
        label="Predicted Volume Sold (Gallons)",
        value=f"{predicted_volume:,.0f}"
    )
with col2:
    st.metric(
        label="Predicted Total Profit ($)",
        value=f"${total_profit:,.2f}"
    )

# --- Display the relationship for context ---
st.markdown("---")
st.write(f"### Profit vs. Price Delta Curve ({model_selection})")

# Create a chart showing how profit changes across the delta range
delta_range = np.arange(-0.25, 0.26, 0.01)
profit_curve_data = pd.DataFrame([[d] for d in delta_range], columns=['Price_Delta_To_Competitor'])

predicted_volumes = model.predict(profit_curve_data)
cpgs = 0.15 - delta_range
total_profits = predicted_volumes * cpgs

chart_data = pd.DataFrame({
    'Price Delta': delta_range,
    'Total Profit': total_profits
}).set_index('Price Delta')


st.line_chart(chart_data)
