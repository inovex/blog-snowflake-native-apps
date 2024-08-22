import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import snowflake.connector
from dotenv import load_dotenv, find_dotenv
from gitignore_parser import parse_gitignore

# Use .env from current workdir
load_dotenv(find_dotenv('.env.template'))

# Snowflake connection parameters
# NOTE: Set session parameter ABORT_DETACHED_QUERY=FALSE --> Default for us
conn_params = {
    "account": os.environ.get("SNOWFLAKE_ACCOUNT"),
    "user": os.environ.get("SNOWFLAKE_USER"),
    "password": os.environ.get("SNOWFLAKE_PASSWORD"),
    "warehouse": os.environ.get("COMPUTE_WH"),
    "database": os.environ.get("SNOWFLAKE_DATABASE"),
    "schema": os.environ.get("SNOWFLAKE_SCHEMA"),
    "role": os.environ.get("SNOWFLAKE_ROLE"),
}


def upload_file(
    local_dir: Path, local_file_path: Path, stage_name: str, conn_params: dict[str, str]
):
    with snowflake.connector.connect(**conn_params) as conn:
        relative_local_file_path = local_file_path.absolute().relative_to(Path.cwd())
        remote_file_path = local_file_path.relative_to(local_dir).parent
        remote_file_path = "/".join(p for p in remote_file_path.parts if p != ".")
        snowflake_full_path = (
            f"@{conn.database}.{conn.schema}.{stage_name}/{remote_file_path}"
        )
        print(f"Uploading {relative_local_file_path} to {snowflake_full_path}")
        conn.cursor().execute(
            f"PUT file://{local_file_path} {snowflake_full_path} AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
        )


def upload_files(
    local_dir: Path, stage_name: str, gitignore: Path = Path(".gitignore")
):
    # Used to match gitignore files, so that exlcuded files will not be uploaded
    matches = parse_gitignore(gitignore)

    # For async upload to safe some time
    with ThreadPoolExecutor() as ex:
        futures = [
            ex.submit(
                upload_file,
                local_dir,
                file,
                stage_name,
                conn_params,
            )
            for file in local_dir.rglob("*")
            if not matches(file) and file.is_file()
        ]
        [future.result() for future in as_completed(futures)]
        print((os.get_terminal_size().columns - 1) * "=")
        print("All files uploaded")


if __name__ == "__main__":
    upload_files(local_dir=Path("app/"), stage_name="APPLICATIONCODE")
