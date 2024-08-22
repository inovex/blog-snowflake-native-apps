# Upgrading Native App

See [here](https://docs.snowflake.com/en/developer-guide/native-apps/versioning) for reference and more detail.

## Short version

- **Versions** and **patches** are used to destinguish between states of the code
- Provider can create the app from any specified version
- **Default release directive** allows the provider to specify which version and patch is installed when any customer installs the app from the marketplace
- **Custom release directive** allows provider to set a custom version for a *specific* customer (Snowflake account for that matter)
- A release directive is required to publish the app
- Native App Framework support **automatic** and **manual upgrades**
- `OWNERSHIP` or `MANAGE VERSIONS` privilige on the `APPLICATION PACKAGE` is required to specify version or patch

## Workflow

1. Adjust your application code (e.g. locally)
2. Upload your code to a new subfolder for the version in `applicationcode` stage (e.g. `applicationcode/v2_0/` for version 2.0)

3a. Add a new version (object in Snowflake, not to be confused with your actual code or the subfolder in the stage) for the `APPLICATION PACKAGE`

```sql
ALTER APPLICATION PACKAGE <packagename>
    ADD VERSION v2_0
    USING '@<packagename>.public.applicationcode/v2_0'
    LABEL = '<Appname> Version 2.0';
```

3b. Same thing for patches if you want to release that (note: is no patch number is provided it will just increment)

```sql
ALTER APPLICATION PACKAGE <packagename>
    ADD PATCH FOR VERSION v2_0
    USING '@<packagename>.public.applicationcode/v2_0_p1'
```

4a. Set release directive for consumers to use

```sql
ALTER APPLICATION PACKAGE <packagename>
  SET DEFAULT RELEASE DIRECTIVE
  VERSION = v2_0
  PATCH = 1;
```

4b. Similarly for custom directives:

```sql
ALTER APPLICATION PACKAGE <packagename>
  SET RELEASE DIRECTIVE
  ACCOUNTS = (<consumerorg>.<consumeraccount>)
  VERSION = v1_0
  PATCH = 0;
```
