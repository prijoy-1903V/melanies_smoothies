# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col
from snowflake.snowpark.context import get_active_session

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# App UI
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie")

name_on_order = st.text_input("Name on Smoothie")
st.write('The Name on Your Smoothie will be:', name_on_order)

# Get data from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'), col('SEARCH_ON')
)

# Convert Snowpark DF to Pandas
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)

# Multiselect fruits from the list
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Get API search value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        # API call
        response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        
        if response.ok:
            st.dataframe(response.json(), use_container_width=True)
        else:
            st.error(f"Error fetching data for {fruit_chosen}")

    # Insert order SQL
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """
    
    st.write(my_insert_stmt)
    
    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
