# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col
#from snowflake.snowpark.context import get_active_session

cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom smoothie
  """
)
name_on_order = st.text_input("Name on Smoothie")
st.write('The Name on Your Smoothie will be:',name_on_order)
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
    
)
if ingredients_list:
    ingredients_string = ''
    for fruits_chosen in ingredients_list:
        ingredients_string += fruits_chosen + ' '
        st.subheader(fruits_chosen + ' Nutrition Information ')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruits_chosen)
        sf_df = st.dataframe(data = smoothiefroot_response.json(), use_container_width = True)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','"""+name_on_order+"""')"""
    
    st.write(my_insert_stmt)
    #st.write(ingredients_string)
    time_to_insert = st.button('Submit Order')    

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
      


