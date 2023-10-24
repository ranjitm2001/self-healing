import random
import uuid
from datetime import datetime, timedelta

import psycopg2

# Database connection parameters
db_params = {
    "host": "localhost",
    "database": "mydb",
    "user": "myuser",
    "password": "mypassword",
}

if __name__ == "__main__":
    try:
        # Establish a connection to the PostgreSQL database
        connection = psycopg2.connect(**db_params)

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Execute a SELECT query
        # TODO: Don't have to fetch DISTINCT elements, ip_address are always distinct
        cursor.execute(
            "SELECT DISTINCT ip_address, maintenance_mode FROM  server_modes"
        )
        server_modes_results = cursor.fetchall()

        # Make key-value pair between ip and mmode
        server_modes_dict = {
            ip: maintenance_mode for ip, maintenance_mode in server_modes_results
        }

        # Get current timestamp
        current_timestamp = datetime.now()

        # Print the retrieved data
        for server_modes_result in server_modes_results:
            id_value = str(uuid.uuid4())

            # If server is in maintenance_mode, skip the iteration
            maintenance_mode_true = server_modes_dict[server_modes_result[0]]
            if maintenance_mode_true:
                continue

            # TODO: It shall be replace by cli.authenticate()
            failure_status = random.randint(0, 1)

            # Insert the data into the server_status table
            insert_query = """
                        INSERT INTO server_status (id, ip_address, failure_status, created_at)
                        VALUES (%s, %s, %s, %s)
                    """
            data_to_insert = (
                id_value,
                server_modes_result[0],
                bool(failure_status),
                current_timestamp,
            )
            cursor.execute(insert_query, data_to_insert)

        # Commit changes (if necessary)
        connection.commit()

        # Calculate the timestamp
        # TODO: Store this timestamp in DB as a global constant
        time_range = datetime.now() - timedelta(minutes=60)

        # SQL query to retrieve recent failures
        query = """
                    SELECT ip_address, count(*)
                    FROM server_status
                    WHERE failure_status = TRUE
                      AND created_at >= %s
                      AND created_at <= %s
                    GROUP BY ip_address
                """

        # Execute the query with the calculated timestamps
        cursor.execute(query, (time_range, datetime.now()))

        # Fetch all rows
        current_failed_servers = cursor.fetchall()
        print("current_failed_servers")
        print(current_failed_servers)

        # If threshold >= 3, then
        # show them all the self-healing options available for that particular ip_address
        interested_ip_address = input(
            "Enter the server which needs to be checked: "
        ).split(" ")

        print("interested_ip_address")
        print(interested_ip_address)

    except (Exception, psycopg2.Error) as error:
        print("Error:", error)

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        print("code executed successfully!")
