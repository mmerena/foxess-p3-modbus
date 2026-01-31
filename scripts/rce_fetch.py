import subprocess
import sys
import logging

# Konfiguracja logowania (do pliku + konsola)
LOG_FILE = "/config/scripts/rce_fetch.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def install(package):
    """Instaluje pakiet pip w bieżącym środowisku"""
    logger.info(f"Pakiet {package} nie jest zainstalowany, instaluję...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", package])
    logger.info(f"Pakiet {package} został zainstalowany.")

# Lista wymaganych pakietów
required_packages = ["requests", "PyMySQL"]

for pkg in required_packages:
    try:
        __import__(pkg.lower())
        logger.info(f"Pakiet {pkg} jest już zainstalowany.")
    except ModuleNotFoundError:
        install(pkg)

# Po instalacji importujemy ponownie
import requests
import pymysql
import sys
import signal
import os
from datetime import date, timedelta, datetime
from pymysql.err import OperationalError, ProgrammingError

logger.info("Wszystkie pakiety załadowane poprawnie!")

# Konfiguracja bazy danych
DB_HOST = 'core-mariadb'
DB_USER = 'homeassistant'
DB_PASSWORD = '****************'
DB_NAME = 'homeassistant'
TABLE_NAME = 'rce_prices'

# Konfiguracja API
API_BASE_URL = 'https://api.raporty.pse.pl/api/rce-pln'
START_DATE_IF_NEW = '2024-06-14' # business_date

def signal_handler(sig, frame):
    logger.warning("Otrzymano SIGTERM (prawdopodobnie timeout HA 60s) – zapisuję co się udało i kończę")
    if 'connection' in globals() and connection:
        try:
            connection.commit()
            logger.info("Ostatni commit wykonany przed przerwaniem")
        except Exception as commit_err:
            logger.error(f"Błąd przy ostatnim commicie: {commit_err}")
    sys.exit(0)

def connect_to_db():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, charset='utf8mb4')

def table_exists(cursor):
    try:
        cursor.execute(f"SHOW TABLES LIKE '{TABLE_NAME}'")
        return cursor.fetchone() is not None
    except ProgrammingError:
        return False

# {"dtime":"2024-06-15 00:45:00","period":"00:30 - 00:45","rce_pln":548.73000,"dtime_utc":"2024-06-14 22:45:00","period_utc":"22:30 - 22:45","business_date":"2024-06-15","publication_ts":"2024-06-14 14:24:05.631","publication_ts_utc":"2024-06-14 12:24:05.631000"}
def create_table(cursor):
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            dtime_utc DATETIME PRIMARY KEY,
            period_utc VARCHAR(20),
            dtime DATETIME,
            period VARCHAR(20),
            rce_pln FLOAT,
            business_date DATE,
            publication_ts_utc DATETIME,
            publication_ts DATETIME
        )
    """)
    logger.info(f"Tabela {TABLE_NAME} utworzona.")

def fetch_rce_data(date_str):
    # https://api.raporty.pse.pl/api/rce-pln?%24filter=business_date%20eq%20%272024-06-14%27
    url = f"{API_BASE_URL}?%24filter=business_date%20eq%20%27{date_str}%27"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get('value', [])
        logger.info(f"Pobrano {len(data)} rekordów dla daty {date_str}.")
        return data
    except requests.RequestException as e:
        logger.error(f"Błąd pobierania dla {date_str}: {e}")
        return []

def insert_data(cursor, connection, data):
    inserted = 0
    for item in data:
        try:
            cursor.execute(f"""
                INSERT IGNORE INTO {TABLE_NAME} (dtime_utc, period_utc, dtime, period, rce_pln, business_date, publication_ts_utc, publication_ts)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                item['dtime_utc'],
                item['period_utc'],
                item['dtime'],
                item['period'],
                item['rce_pln'],
                item['business_date'],
                item['publication_ts_utc'],
                item['publication_ts']
            ))
            inserted += cursor.rowcount
        except KeyError as e:
            logger.error(f"Błąd rekordu (brak klucza {e}): {item}")
        except Exception as e:
            logger.error(f"Błąd podczas zapisu rekordu: {e}")
            continue
    connection.commit()
    logger.info(f"Zapisano {inserted} nowych rekordów dla tego dnia.")

def get_dates_to_fetch(start_date_str, end_date_str):
    dates = []
    current = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    while current <= end:
        dates.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    return dates

def main():
    # Rejestrujemy handler na SIGTERM
    signal.signal(signal.SIGTERM, signal_handler)

    tomorrow = date.today() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')

    connection = None
    cursor = None

    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        is_new_table = not table_exists(cursor)
        if is_new_table:
            create_table(cursor)
            connection.commit()  # Commit po utworzeniu tabeli
            start_date = datetime.strptime(START_DATE_IF_NEW, '%Y-%m-%d').date()
            start_date_str = START_DATE_IF_NEW
            logger.info(f"Tabela nowa - pobieram od {start_date_str} do {tomorrow_str}.")
        else:
            cursor.execute(f"SELECT MAX(business_date) FROM {TABLE_NAME}")
            max_bd = cursor.fetchone()[0]
            if max_bd is None:
                start_date = datetime.strptime(START_DATE_IF_NEW, '%Y-%m-%d').date()
                start_date_str = START_DATE_IF_NEW
                logger.info(f"Tabela pusta - pobieram od {start_date_str} do {tomorrow_str}.")
            else:
                start_date = datetime.strptime(str(max_bd), '%Y-%m-%d').date() - timedelta(days=3)
                start_date_str = start_date.strftime('%Y-%m-%d')
                logger.info(f"Tabela istnieje - pobieram dane od {start_date_str} do {tomorrow_str}.")

        dates = get_dates_to_fetch(start_date_str, tomorrow_str)

        for i, date_str in enumerate(dates, 1):
            logger.info(f"[{i}/{len(dates)}] Pobieram dane dla: {date_str}")
            data = fetch_rce_data(date_str)
            if data:
                insert_data(cursor, connection, data)
            else:
                logger.info(f"Brak danych dla {date_str} – pomijam.")

            # Opcjonalna przerwa między requestami (włącz jeśli API blokuje za szybkie zapytania)
            # import time
            # time.sleep(0.5)  # 0.5 sekundy

        logger.info("Pobieranie zakończone sukcesem.")

    except Exception as e:
        logger.error(f"Błąd krytyczny: {type(e).__name__}: {e}")
        if connection:
            try:
                connection.rollback()
            except:
                pass

    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if connection:
            try:
                connection.close()
            except:
                pass
        logger.info("Skrypt zakończył działanie (normalnie lub przez timeout).")

if __name__ == "__main__":
    main()
