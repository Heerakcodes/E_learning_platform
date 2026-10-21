"""
create_db.py -- Auto-creates the MySQL database if it doesn't exist.

HOW TO RUN:
    python create_db.py

This script connects to MySQL WITHOUT specifying a database (just host/user/password),
then runs: CREATE DATABASE IF NOT EXISTS elearn_db

Run this ONCE before running: python manage.py migrate
"""

import sys

# -- Step 1: Try to import mysqlclient
try:
    import MySQLdb
except ImportError:
    print("ERROR: mysqlclient is not installed.")
    print("Run: pip install mysqlclient")
    sys.exit(1)


# -- Step 2: Database connection settings
# These must match what's in settings.py
HOST     = 'localhost'
PORT     = 3306
USER     = 'root'
PASSWORD = 'heerak@4017'   # Your MySQL root password
DB_NAME  = 'elearn_db'


# -- Step 3: Connect WITHOUT a database and create it
print("Connecting to MySQL at {}:{} as '{}'...".format(HOST, PORT, USER))

try:
    # Connect without specifying a database (that's the key!)
    connection = MySQLdb.connect(
        host=HOST,
        port=PORT,
        user=USER,
        passwd=PASSWORD,
    )
    cursor = connection.cursor()

    # Create the database if it doesn't already exist
    cursor.execute(
        "CREATE DATABASE IF NOT EXISTS `{}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;".format(DB_NAME)
    )
    connection.commit()

    print("[OK] Database '{}' created/verified successfully!".format(DB_NAME))
    print("")
    print("Next steps:")
    print("  1. python manage.py migrate")
    print("  2. python seed_data.py")
    print("  3. python manage.py runserver")

    cursor.close()
    connection.close()

except MySQLdb.OperationalError as e:
    error_code = e.args[0]
    error_msg  = e.args[1]

    print("")
    print("[FAILED] MySQL Connection Error!")
    print("   Error {}: {}".format(error_code, error_msg))
    print("")

    if error_code == 1045:
        print("CAUSE:   Wrong username or password.")
        print("FIX:     Open create_db.py and update the PASSWORD variable.")
    elif error_code == 2003:
        print("CAUSE:   Can't connect to MySQL server.")
        print("FIX:     Make sure MySQL is running (check MySQL Workbench or Services).")
    elif error_code == 2005:
        print("CAUSE:   Unknown host.")
        print("FIX:     Make sure HOST is correct (usually 'localhost').")
    else:
        print("FIX:     Check your MySQL installation and credentials.")

    sys.exit(1)
