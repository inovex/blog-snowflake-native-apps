SET APP_PACKAGE = 'LUNCH_PLANNER_PACKAGE';
SET APP_DEV_ROLE = 'LUNCH_PLANNER_APP_DEVELOPER';
SET APP_PACKAGE_SCHEMA = CONCAT($APP_PACKAGE, '.PUBLIC');
SET APP_PACKAGE_STAGE = CONCAT($APP_PACKAGE_SCHEMA, '.APPLICATIONCODE');
SET APP_NAME = 'LUNCH_PLANNER_APP';
SET SOURCE_DATABASE = 'LUNCH_PLANNER_DB';
SET SOURCE_SCHEMA = CONCAT($SOURCE_DATABASE, '.TEST_SCHEMA');

USE ROLE ACCOUNTADMIN;
USE SCHEMA IDENTIFIER($APP_PACKAGE_SCHEMA);

-- Create external access to api
CREATE OR REPLACE NETWORK RULE edamam_apis_network_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('api.edamam.com');

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION edamam_external_access_integration
  ALLOWED_NETWORK_RULES = (edamam_apis_network_rule)
  ENABLED = true;

USE ROLE IDENTIFIER($APP_DEV_ROLE);
USE WAREHOUSE COMPUTE_WH;

CREATE APPLICATION IDENTIFIER($APP_NAME)
  FROM APPLICATION PACKAGE IDENTIFIER($APP_PACKAGE)
  USING '@LUNCH_PLANNER_PACKAGE.PUBLIC.APPLICATIONCODE';

USE ROLE ACCOUNTADMIN;

-- Create table used later in Snowflake Native App
CREATE OR REPLACE DATABASE IDENTIFIER($SOURCE_DATABASE);
USE IDENTIFIER($SOURCE_DATABASE);
CREATE OR REPLACE SCHEMA test_schema;
USE SCHEMA IDENTIFIER($SOURCE_SCHEMA);

CREATE TABLE IF NOT EXISTS lunch_plan (label VARCHAR, image VARCHAR, url VARCHAR, calories DOUBLE, totalTime INT);
TRUNCATE TABLE lunch_plan;
INSERT INTO lunch_plan VALUES
  ('Cauliflower soup',
  'https://images.immediate.co.uk/production/volatile/sites/30/2020/08/cauliflower_soup-877eac5.jpg?quality=90&webp=true&resize=300,272',
  'https://www.bbcgoodfood.com/recipes/cauliflower-soup',
  176.0, 40);

GRANT USAGE ON DATABASE IDENTIFIER($SOURCE_DATABASE) TO ROLE IDENTIFIER($APP_DEV_ROLE);
USE DATABASE IDENTIFIER($SOURCE_DATABASE);
GRANT USAGE ON SCHEMA IDENTIFIER($SOURCE_SCHEMA) TO ROLE IDENTIFIER($APP_DEV_ROLE);
GRANT SELECT ON ALL TABLES IN SCHEMA IDENTIFIER($SOURCE_SCHEMA) TO ROLE IDENTIFIER($APP_DEV_ROLE);
GRANT INSERT ON ALL TABLES IN SCHEMA IDENTIFIER($SOURCE_SCHEMA) TO ROLE IDENTIFIER($APP_DEV_ROLE);
GRANT UPDATE ON ALL TABLES IN SCHEMA IDENTIFIER($SOURCE_SCHEMA) TO ROLE IDENTIFIER($APP_DEV_ROLE);
GRANT DELETE ON ALL TABLES IN SCHEMA IDENTIFIER($SOURCE_SCHEMA) TO ROLE IDENTIFIER($APP_DEV_ROLE);
GRANT USAGE ON INTEGRATION edamam_external_access_integration TO ROLE IDENTIFIER($APP_DEV_ROLE);
GRANT USAGE ON INTEGRATION edamam_external_access_integration TO APPLICATION IDENTIFIER($APP_NAME);
