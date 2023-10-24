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

        servers_mmode_true = input(
            "Enter the servers whose maintenance needs to be started: "
        ).split(" ")
        servers_mmode_false = input(
            "Enter the servers whose maintenance is completed: "
        ).split(" ")

        # Check if the input is empty and set the lists accordingly
        if servers_mmode_true == ['']:
            servers_mmode_true = []
        if servers_mmode_false == ['']:
            servers_mmode_false = []

        print(servers_mmode_true)
        print(servers_mmode_false)

        for server in servers_mmode_true:
            # Check if the server is existing
            server_exists_query = (
                "SELECT COUNT(*) ip_address FROM server_modes WHERE ip_address = %s"
            )
            cursor.execute(server_exists_query, (server,))

            server_count = cursor.fetchone()[0]
            if server_count != 1:
                raise ValueError("Entered server doesn't exist")

            # Update the maintenance_mode for the specified IP address
            update_query = """
                   UPDATE server_modes
                   SET maintenance_mode = TRUE
                   WHERE ip_address = %s
               """
            cursor.execute(update_query, (server,))

            delete_query = """
                   DELETE FROM server_status
                   WHERE ip_address = %s
            """
            cursor.execute(delete_query, (server,))

            # Commit the transaction
            connection.commit()

        for server in servers_mmode_false:
            # Check if the server is existing
            server_exists_query = (
                "SELECT COUNT(*) ip_address FROM server_modes WHERE ip_address = %s"
            )
            cursor.execute(server_exists_query, (server,))

            server_count = cursor.fetchone()[0]
            if server_count != 1:
                raise ValueError("Entered server doesn't exist")

            # Update the maintenance_mode for the specified IP address
            update_query = """
                   UPDATE server_modes
                   SET maintenance_mode = FALSE
                   WHERE ip_address = %s
               """
            cursor.execute(update_query, (server,))

            # Commit the transaction
            connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error:", error)

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        print("code executed successfully!")
