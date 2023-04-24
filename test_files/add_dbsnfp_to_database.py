import psycopg2
import os
import glob
import json

# Connect to the PostgreSQL database
conn = psycopg2.connect(database="protein_variants_db", user="postgres", password="sqldatabase", host="localhost", port="5432")
cursor = conn.cursor()

# Set the directory path
directory_path = '/home2/mehmet/dbsnfp_data/checked_json_files'
table_prefix = 'dbsnfp_'

table_names = []
for filepath in glob.glob(os.path.join(directory_path, 'cheched*')):
    filename = os.path.basename(filepath)
    tablename = os.path.splitext(filename)[0].replace("cheched_","dbsnfp_").replace("-","_")
    table_names.append(tablename)
# Create the full outer join query
query = f"SELECT COALESCE({table_names[0]}.md5sum"
for table_name in table_names[1:]:
    query += f", {table_name}.md5sum"
query += f") as md5sum"

for table_name in table_names:
    query += f", to_json({table_name}.scores) as {table_name}_scores"
query += f" FROM {table_names[0]}"

for i in range(1, len(table_names)):
    query += f" FULL OUTER JOIN {table_names[i]} ON {table_names[0]}.md5sum = {table_names[i]}.md5sum"

# Create a new table name
new_table_name = 'dbsnfp'
# Drop the table if it already exists
cursor.execute("DROP TABLE IF EXISTS dbsnfp;")
# Create the table with the correct columns
columns = ', '.join([f"{table_name}_scores JSONb" for table_name in table_names] + ["md5sum VARCHAR(128) UNIQUE NOT NULL"])
create_table_query = f"CREATE TABLE IF NOT EXISTS {new_table_name} ({columns});"
cursor.execute(create_table_query)
conn.commit()
# Insert the data into the new table
cursor.execute(f"INSERT INTO {new_table_name} ({', '.join([f'{table_name}_scores' for table_name in table_names])}, md5sum) SELECT {', '.join([f'{table_name}_scores' for table_name in table_names])}, md5sum FROM ({query}) as joined_table;")

# Commit the changes
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()
