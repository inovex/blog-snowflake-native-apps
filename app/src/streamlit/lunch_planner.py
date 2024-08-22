# Import python packages
import streamlit as st
from snowflake.snowpark import Session
import pandas as pd
import json


def response_to_dataframe(response_txt):
    recipe_dict_list = [recipe['recipe'] for recipe in json.loads(response_txt)['hits']]
    return pd.DataFrame(recipe_dict_list)


def get_recipe_suggestions_df(exclude_str):
    api_call_stmt = "SELECT lunch_planner_app.code_schema.get_random_recipes('" + exclude_str + "') as src"
    response_df = session.sql(api_call_stmt).to_pandas()
    response_txt = response_df["SRC"].loc[0]
    recipe_suggestions_df = response_to_dataframe(response_txt)
    recipe_suggestions_df["add"] = False
    return recipe_suggestions_df


def insert_sel_recipes(sel_df):
    for _, row in sel_df.iterrows():
        session.sql("""
            INSERT INTO reference('lunch_plan_table')
            VALUES ('{}', '{}', '{}', {}, {})
        """.format(row["label"], row["image"], row["url"],
                   row["calories"], int(row["totalTime"]))).collect()


# Write directly to the app
st.title("🍅 Lunch Planner 🍅")

# Get the current credentials
session = Session.builder.getOrCreate()

# Section for Current Lunch Plan
st.markdown("## Current Lunch Plan")
st.write("You can select recipes to remove in the 'remove' column and click on the 'Remove' button to remove them.")

# Access currnet lunch plan and add 'remove' column for visualizing checkbox 
curr_luch_df = session.sql("SELECT * FROM reference('lunch_plan_table')").to_pandas()
curr_luch_df["remove"] = False

plan_data_editor = st.data_editor(
    data=curr_luch_df,
    column_config={
        "IMAGE": st.column_config.LinkColumn(
            "IMAGE", display_text="Recipe image"
        ),
        "URL": st.column_config.LinkColumn(
            "URL", display_text="Open recipe"
        ),
    },
    disabled=("LABEL", "IMAGE", "URL", "CALORIES", "TOTALTIME"),
    use_container_width=True
)

remove_lunch_df = plan_data_editor[plan_data_editor["remove"]]
label_list = remove_lunch_df['LABEL'].to_list()
quoted_list = ["'"+ label + "'" for label in label_list]
labels_str = "(" + ", ".join(quoted_list) + ")"
st.write("Label list to be removed:", labels_str)

if st.button("Remove", disabled=(len(remove_lunch_df) == 0)):
    try:
        session.sql("DELETE FROM reference('lunch_plan_table') WHERE LABEL in " + labels_str).collect()
        st.success('Deleted selected recipes from lunch plan successfully', icon="✅")
    except Exception as e:
        st.error('Error deleting from lunch plan table', icon="🚨")
        st.error(str(e), icon="🚨")

st.divider()

# Section for Recipe Suggestions
st.markdown("## Recipe Suggestions")

st.write(
   """Click on 'Exclude' checkbox to exclude ingredients from lunch planner suggestions.
      You can also add your own ingredients by adding the name of the ingredient in the 'NAME' colunmn
      and optionally an alternative name in the 'OTHER_NAMES' column
      (if your ingredient has more than 1 alternative names, separate the names by comma).
   """
)

st.write(
   "For deleting ingredients from the table, click on the left checkbox of the row and click on 'DEL' button of your keyboard."
)

# Create a dataframe for ingredients view
# Convert it into a Pandas dataframe and add an 'Exclude' column
queried_ingredients = session.sql("SELECT * FROM code_schema.ingredients_view").to_pandas()
queried_ingredients['Exclude'] = False

# Data Editor for marking exclusion and adding ingredients
edited_ingredients_df = st.data_editor(
    queried_ingredients,
    num_rows="dynamic",
    use_container_width=True
)

exclude_name_list = edited_ingredients_df[(edited_ingredients_df['Exclude']) & (edited_ingredients_df['NAME'] != '')]['NAME'].to_list()
exclude_other_list = edited_ingredients_df[edited_ingredients_df['Exclude']  & (edited_ingredients_df['OTHER_NAMES'] != '')]['OTHER_NAMES'].to_list()
exclude_list = exclude_name_list + exclude_other_list

exclude_str = ", ".join(exclude_list)
st.write("Ingredients to be excluded:", exclude_str)

if st.button("Get Recipes", disabled=(len(exclude_str) == 0)):
    st.session_state.recipe_suggestions_df = get_recipe_suggestions_df(exclude_str)
    st.session_state.show_recipe_suggestions_df = True


if st.session_state.get("show_recipe_suggestions_df", False):
    st.markdown("#### Recipe Ideas without selected ingredients")
    st.write("You can select recipes to add in the 'add' column and click on the 'Add selected recipes' button to add them.")
    
    suggestions_data_editor = st.data_editor(
            data=st.session_state.recipe_suggestions_df,
            column_config={
                "image": st.column_config.LinkColumn(
                    "image", display_text="Recipe image"
                ),
                "url": st.column_config.LinkColumn(
                    "url", display_text="Open recipe"
                ),
            },
            disabled=("label", "image", "url", "calories", "totalTime"),
            use_container_width=True
        )

    suggestions_to_add = suggestions_data_editor[suggestions_data_editor["add"]][["label", "image", "url", "calories", "totalTime"]]
    
    if st.button("Add selected recipes", disabled=(len(suggestions_to_add) == 0)):
        try:
            insert_sel_recipes(suggestions_to_add)
            st.success('Added selected recipes to lunch plan successfully', icon="✅")
        except Exception as e:
            st.error('Error inserting into lunch plan table', icon="🚨")
            st.error(str(e), icon="🚨")
