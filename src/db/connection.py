import pymssql
import logging
from config import DB_SERVER,DB_USER,DB_PASSWORD,DB_NAME
# Configuración del logging
logger = logging.getLogger(__name__)

class MSSQLConnectionManager:
    _connection = None
 
    @staticmethod
    def get_connection():
        if MSSQLConnectionManager._connection is None :
           try:
              MSSQLConnectionManager._connection = pymssql.connect(
                server=DB_SERVER,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                as_dict=True
                )
           except pymssql.DatabaseError as e:
              MSSQLConnectionManager._connection = None
              print(f"Error connecting to database: {e}")
        return MSSQLConnectionManager._connection
            
    @staticmethod
    def close_connection():
        """
        Cierra la conexión activa a la base de datos si existe.
        """
        if MSSQLConnectionManager._connection:
            try:
                MSSQLConnectionManager._connection.close()
                MSSQLConnectionManager._connection = None
            except pymssql.DatabaseError as e:
                print(f"Error closing database connection: {e}")
    
       
def execute_query(query, params=None,fetch=True): 
    conn = MSSQLConnectionManager.get_connection()
    if conn:
        try:
            with conn.cursor(as_dict=True) as cur:
                if params:
                    cur.execute(query, params)
                else:
                    cur.execute(query)
                if fetch:
                    return cur.fetchall()  
                else: 
                    conn.commit()  
                    return None  
        except pymssql.DatabaseError as e:
            print(f"Error executing query: {e}")
            return None
        except Exception as e:
            # Capturar cualquier otro error
            print(f"Otro error ha ocurrido: {e}")
            return None
    else:
        print("Failed to establish database connection.")
        return None