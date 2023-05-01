from sqlalchemy.orm import sessionmaker

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

    def copy_from_file(self, file_path, table_name, header=True, delimiter='\t', null='\\N'):
        with open(file_path, 'r') as file:
            # Skip the header line if the header is set to True
            if header:
                next(file)

            sql_copy = f"COPY {table_name} FROM {file_path} WITH (FORMAT CSV, DELIMITER '{delimiter}', NULL '{null}')"
            self.session.execute(sql_copy)

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
