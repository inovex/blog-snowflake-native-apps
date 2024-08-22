from snowflake.snowpark import Session


def init_app(session: Session, config: dict) -> str:
  """
    Initializes function API endpoints with access to the secret and API integration.

    Args:
      session (Session): An active session object for authentication and communication.
      config (Any): The configuration settings for the connector.

    Returns:
      str: A status message indicating the result of the provisioning process.
   """
  external_access_integration_name = config['external_access_integration_name']

  alter_function_sql = f'''
    ALTER FUNCTION code_schema.get_random_recipes(string) SET
    EXTERNAL_ACCESS_INTEGRATIONS = ({external_access_integration_name})'''
  
  session.sql(alter_function_sql).collect()

  return 'Snowflake translation app initialized'