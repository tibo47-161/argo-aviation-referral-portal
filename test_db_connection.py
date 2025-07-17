import pyodbc
import os
from dotenv import load_dotenv

load_dotenv() # Lade Umgebungsvariablen aus der .env-Datei
db_url_from_env = os.getenv("DATABASE_URL")

if not db_url_from_env:
    print("Fehler: DATABASE_URL wurde nicht aus der .env-Datei geladen.")
    exit()

print(f"Versuche, mich mit dieser URL zu verbinden: {db_url_from_env}")

try:
    # Für DSN-Verbindungen muss der "mssql+pyodbc:///?odbc_connect=" Teil entfernt werden
    # pyodbc.connect erwartet die DSN-Zeichenkette direkt
    odbc_connection_string = db_url_from_env.replace("mssql+pyodbc:///?odbc_connect=", "")
    print(f"Versuche, mich mit dieser pyodbc-Verbindungszeichenkette zu verbinden: {odbc_connection_string}")

    cnxn = pyodbc.connect(odbc_connection_string)
    cursor = cnxn.cursor()
    cursor.execute("SELECT 1")
    print("Verbindung erfolgreich hergestellt und eine einfache Abfrage ausgeführt!")
    cursor.close()
    cnxn.close()

except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    print(f"\n🚫 FEHLER BEIM VERBINDEN MIT PYODBC:")
    print(f"SQLSTATE: {sqlstate}")
    print(f"Nachricht: {ex.args[1]}")
except Exception as e:
    print(f"\n🚫 Ein unerwarteter Fehler ist aufgetreten: {e}")