# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col
# from snowflake.snowpark.context import get_active_session

cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom smoothie
  """
)
name_on_order = st.text_input("Name on Smoothie")
st.write('The Name on Your Smoothie will be:', name_on_order)

my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'), col('SEARCH_ON'))

pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),  # FIXED: Provide a list of strings for selection
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    for fruits_chosen in ingredients_list:
        ingredients_string += fruits_chosen + ' '
        
        # FIXED: Use the correct variable and prevent crash if not found
        match = pd_df.loc[pd_df['FRUIT_NAME'] == fruits_chosen, 'SEARCH_ON']
        if not match.empty:
            search_on = match.iloc[0]
        else:
            search_on = fruits_chosen  # fallback

        st.subheader(fruits_chosen + ' Nutrition Information ')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string.strip() + """','""" + name_on_order + """')"""
    
    st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')    

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
