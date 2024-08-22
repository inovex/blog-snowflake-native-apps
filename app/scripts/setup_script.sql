-- Setup script for the lunch planner app.
CREATE APPLICATION ROLE IF NOT EXISTS app_public;

-- Add a view to access data content
CREATE OR ALTER VERSIONED SCHEMA code_schema;
GRANT USAGE ON SCHEMA code_schema TO APPLICATION ROLE app_public;

CREATE VIEW IF NOT EXISTS code_schema.ingredients_view
  AS SELECT NAME, OTHER_NAMES
  FROM shared_data.ingredients;
GRANT SELECT ON VIEW code_schema.ingredients_view TO APPLICATION ROLE app_public;

-- Procedure for inializing external API call function
CREATE OR REPLACE PROCEDURE code_schema.init_app(config variant)
  RETURNS string
  LANGUAGE python
  runtime_version = '3.10'
  packages = ('snowflake-snowpark-python', 'requests', 'simplejson')
  imports = ('/src/libraries/init.py')
  handler = 'init.init_app';

GRANT USAGE ON PROCEDURE code_schema.init_app(variant) TO APPLICATION ROLE app_public;

-- Add function for external API call
CREATE or REPLACE FUNCTION code_schema.get_random_recipes(excluded STRING)
  RETURNS STRING
  LANGUAGE PYTHON
  RUNTIME_VERSION=3.10
  PACKAGES = ('requests')
  IMPORTS = ('/src/libraries/external_api.py')
  HANDLER='external_api.get_random_recipes';

GRANT USAGE ON FUNCTION code_schema.get_random_recipes(STRING) TO APPLICATION ROLE app_public;

-- Procedure for updating reference (e.g. to bind customer account data with reference)
CREATE OR REPLACE PROCEDURE code_schema.update_reference(ref_name string, operation string, ref_or_alias string)
RETURNS STRING
LANGUAGE SQL
AS $$
BEGIN
  CASE (operation)
    WHEN 'ADD' THEN
       SELECT SYSTEM$SET_REFERENCE(:ref_name, :ref_or_alias);
    WHEN 'REMOVE' THEN
       SELECT SYSTEM$REMOVE_REFERENCE(:ref_name, :ref_or_alias);
    WHEN 'CLEAR' THEN
       SELECT SYSTEM$REMOVE_ALL_REFERENCES();
    ELSE
       RETURN 'Unknown operation: ' || operation;
  END CASE;
  RETURN 'Success';
END;
$$;

GRANT USAGE ON PROCEDURE code_schema.update_reference(string, string, string) TO APPLICATION ROLE app_public;

-- Add the streamlit object to the setup script
CREATE STREAMLIT IF NOT EXISTS code_schema.lunch_planner_streamlit
  FROM '/src/streamlit'
  MAIN_FILE = '/lunch_planner.py'
;

GRANT USAGE ON STREAMLIT code_schema.lunch_planner_streamlit TO APPLICATION ROLE app_public;
