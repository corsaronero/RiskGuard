'''from PyQt5.QtCore import QThread, pyqtSignal
import psycopg2
from psycopg2 import sql
from qgis.core import QgsApplication, QgsDataSourceUri, QgsSettings, QgsProject

class DBWorker(QThread):
    finished = pyqtSignal(str)  # Signal to notify when the task is complete

    def __init__(self, db_params):
        super().__init__()
        self.db_params = db_params

    def run(self):

        try:
            host, port, user, password, db_name = self.db_params
            # Connect to the PostgreSQL server
            conn = psycopg2.connect(
                dbname="postgres",
                user=user,
                password=password,
                host=host,
                port=port
            )
            conn.autocommit = True
            cursor = conn.cursor()

            # Check if the database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
            if cursor.fetchone():
                result = f"Database '{db_name}' already exists."
            else:
                # Create the database
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
                result = f"Database '{db_name}' created successfully."

            cursor.close()
            conn.close()

            # Connect to the new database and load it into QGIS
            #uri = QgsDataSourceUri()
            #uri.setConnection(host, port, db_name, user, password)

            self.add_postgres_connection_to_browser(
                name="testdb",
                host=host,
                port=port,
                dbname=db_name,
                user=user,
                password=password
            )

            #print("Database URI:", uri.uri())
            print("Database connection complete.")

            self.finished.emit(result)
        except Exception as e:
            self.finished.emit(f"Error: {e}")


    @staticmethod
    def add_postgres_connection_to_browser(name, host, port, dbname, user, password):
        
        settings = QgsSettings()
        connections_path = "PostgreSQL/connections/"
        connection_name = connections_path + name
        print("sono qui", connection_name)
        settings.setValue(connection_name + "/host", host)
        settings.setValue(connection_name + "/port", port)
        settings.setValue(connection_name + "/database", dbname)
        settings.setValue(connection_name + "/username", user)
        settings.setValue(connection_name + "/password", password)  # Stores password in QGIS settings
        settings.setValue(connection_name + "/savePassword", True)  # Save password for re-use
        settings.setValue(connection_name + "/service", "")
        settings.setValue(connection_name + "/sslmode", "disable")
        settings.setValue(connection_name + "/estimatedMetadata", False)
        settings.setValue(connection_name + "/geometryColumnsOnly", False)

        print(f"Connection '{name}' added to QGIS PostgreSQL browser.")'''