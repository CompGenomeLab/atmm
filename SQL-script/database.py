from sqlalchemy.orm import sessionmaker
import json
from sqlalchemy.sql import text


class Database:
    def __init__(self, engine):
        self.engine = engine
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def get_tables(self):
        result = self.session.execute("""SELECT table_name FROM information_schema.tables
                                   WHERE table_schema = 'public'""")
        tables = [table[0] for table in result.fetchall()]
        print(f"Found {len(tables)} tables in the database.")
        return tables

    def execute_query(self, query):
        try:
            result = self.session.execute(query)
            self.session.commit()
            print("Query is executed.")
            return result
        except Exception as error:
            print("Error while executing query:", error)

    def copy_from_file(self, file_path, table_name):
        try:
            sql_copy = rf'''COPY {table_name} FROM '{file_path}' USING DELIMITERS E'\t' WITH NULL AS '\null' CSV HEADER;'''
            self.session.execute(sql_copy)

            print(f"Data from {file_path} has been copied to {table_name} table.")
        except Exception as e:
            print(f"Error encountered while copying data from {file_path} to {table_name} table:")
            print(str(e))
            if hasattr(e, 'diag'):
                print(f"Problematic line: {file_path}:{e.diag.row_number}: {e.diag.column_name}")
            else:
                print("Cannot determine the problematic line.")

    def copy_from_file_json(self, file_path, table_name, header=True, delimiter='\t', null='\\N'):
        with open(file_path, 'r') as file:
            # Skip the header line if the header is set to True
            if header:
                next(file)

            # Keep track of the md5sum values that have already been seen
            md5sums = set()

            # Iterate through each line of the file and insert the data into the main table
            for line in file:
                columns = line.strip().split(delimiter)
                md5sum = columns[0]
                json_data = columns[1]

                # Skip rows with duplicate md5sum values
                if md5sum in md5sums:
                    print(f"Skipping row with duplicate md5sum value: {md5sum}")
                    continue
                else:
                    md5sums.add(md5sum)

                # Parse the JSON data using Python's json module
                parsed_json = json.loads(json_data)

                # Convert the dictionary back into a JSON-formatted string
                json_string = json.dumps(parsed_json)

                # Insert the row into the main table, ignoring duplicates
                insert_query = text(
                    f"INSERT INTO {table_name} (md5sum, scores) VALUES (:md5sum, :scores) ON CONFLICT DO NOTHING")
                self.session.execute(insert_query, {"md5sum": md5sum, "scores": json_string})

            self.session.commit()

            print(f"Data from {file_path} has been copied to {table_name} table.")

    def close(self):
        self.session.close()
        print("PostgreSQL connection is closed.")

    class TableAlreadyExists(Exception):
        def __init__(self, message='The table you want to create already exists'):
            self.message = message

        def __str__(self):
            return self.message

    class TableNotFound(Exception):
        def __init__(self, message='The table you want to update cannot be found'):
            self.message = message

        def __str__(self):
            return self.message
