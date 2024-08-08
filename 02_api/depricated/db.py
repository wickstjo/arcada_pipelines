import psycopg2

class create_client:
    def __init__(self):
        self.client = psycopg2.connect(
            database="database",
            host='postgres_db',
            # host='localhost',
            user="username",
            password="password",
            port="5432"
        )

    # QUERY WRAPPER
    def pg_query(self, query_string, query_values=[]):
        cursor = self.client.cursor()
        cursor.execute(query_string, query_values)
        self.client.commit()

        return cursor

    def exercise_schema(self, input_tuple):
        return {
            'id': input_tuple[0],
            'name': input_tuple[1],
            'description': input_tuple[2],
        }
    
    def submission_schema(self, input_tuple):
        return {
            'id': input_tuple[0],
            'user_session': input_tuple[1],
            'exercise_id': input_tuple[2],
            'correct': input_tuple[3],
        }

    # READ QUERY
    def read(self, query: str, schema=False):
        cursor = self.pg_query(query)
        result = cursor.fetchall()

        if schema:
            return [schema(x) for x in result]
        
        return result

    # WRITE QUERY
    def write(self, query: str, values: tuple):

        # query = 'INSERT INTO temp_tbl (full_url, shortcut) VALUES (%s, %s)'
        # values = (url, item_id)

        # PERFORM QUERY
        self.pg_query(query, values)