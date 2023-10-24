import random
import re
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Union

import psycopg2
from netmiko import ConnectHandler

# Database connection parameters
db_params = {
    "host": "localhost",
    "database": "mydb",
    "user": "myuser",
    "password": "mypassword",
}


def cmd_show_application_status_ise_formatting(
        command_string: str,
) -> list[dict[str, str]]:
    # Split the input into lines and skip the first two lines
    lines = command_string.strip().split("\n")[2:]

    # Define a regular expression pattern to capture the three parts
    pattern = r"(.+?)\s{2,}(running|disabled|not running|initializing)(?:\s{2,}(\d+))?"

    # Initialize empty lists to store the data
    process_names = []
    states = []
    process_ids = []

    # Iterate through the lines and extract the parts
    for line in lines:
        match = re.match(pattern, line)
        if match:
            process_name = match.group(1)
            state = match.group(2)
            process_id = match.group(3)
            process_names.append(process_name)
            states.append(state)
            process_ids.append(process_id if process_id is not None else "")

    # Create a list of dictionaries from the extracted data
    data_list = []
    for i in range(len(process_names)):
        data_list.append(
            {
                "ISE PROCESS NAME": process_names[i],
                "STATE": states[i],
                "PROCESS ID": process_ids[i],
            }
        )
    return data_list


def cmd_show_application_status_ise(ip_address: str):
    cisco = {
        "device_type": "cisco_ios",
        "host": ip_address,
        "username": "nothing",
        "password": "something",
        "port": 22,
    }

    # TODO: Enable the ConnectHandler inside Cisco VPN
    # with ConnectHandler(**cisco) as net_connect:
    #     command = "show application status ise"
    #     output = net_connect.send_command(command, read_timeout=60)

    # TODO: Comment this on real project
    output = """
ISE PROCESS NAME                       STATE            PROCESS ID
--------------------------------------------------------------------
Database Listener                      running          3688
Database Server                        running          41 PROCESSES
Application Server                     running          6041
Profiler Database                      running          4533
AD Connector                           running          6447
M&T Session Database                   running          2363
M&T Log Collector                      running          6297
M&T Log Processor                      running          6324
Certificate Authority Service          running          6263
pxGrid Infrastructure Service          disabled
pxGrid Publisher Subscriber Service    not running
pxGrid Connection Manager              disabled
pxGrid Controller                      disabled
Identity Mapping Service               disabled
        """

    cmd_sasi_data_list = cmd_show_application_status_ise_formatting(output)

    target_key = 'ISE PROCESS NAME'
    target_value = 'Application Server'

    output_cmd: dict[str, str] = {}
    for item in cmd_sasi_data_list:
        if item.get(target_key) == target_value:
            output_cmd = item
            break
    if output_cmd:
        print(f'Application Server Status for {ip_address}: {output_cmd["STATE"]}')
    else:
        print(f'Application Server not found for {ip_address}')


def cmd_reset_ise_servers(ip_address: str):
    cisco = {
        "device_type": "cisco_ios",
        "host": ip_address,
        "username": "nothing",
        "password": "something",
        "port": 22,
    }

    # TODO: Enable the ConnectHandler inside Cisco VPN
    with ConnectHandler(**cisco) as net_connect:
        print("command running now.....")
        print("time-out is about 10 mins")
        command = "application stop ise"
        print(">>> " + command)

        # NOTE: It should be triggered synchronously
        net_connect.send_command(command, read_timeout=600)  # 600 seconds

        print("command running now.....")
        print("time-out is about 20 mins")
        command = "application start ise"
        print(">>> " + command)

        # NOTE: It could be triggered asynchronously
        net_connect.send_command(command, read_timeout=1200)  # 1200 seconds

        application_still_not_up = True
        start_time = time.time()

        while application_still_not_up and time.time() - start_time < 1200:  # 1200 seconds = 20 minutes
            command = "show application status ise"
            time.sleep(30)  # Sleep for 30 seconds

            # Here, you would perform the logic to check if the application is up.

            def check_application_status() -> bool:
                # TODO: Enable the ConnectHandler inside Cisco VPN
                # with ConnectHandler(**cisco) as net_connect:
                #     command = "show application status ise"
                #     output = net_connect.send_command(command, read_timeout=60)

                # TODO: Comment this on real project
                output = """
                ISE PROCESS NAME                       STATE            PROCESS ID
                --------------------------------------------------------------------
                Database Listener                      running          3688
                Database Server                        running          41 PROCESSES
                Application Server                     running          6041
                Profiler Database                      running          4533
                AD Connector                           running          6447
                M&T Session Database                   running          2363
                M&T Log Collector                      running          6297
                M&T Log Processor                      running          6324
                Certificate Authority Service          running          6263
                pxGrid Infrastructure Service          disabled
                pxGrid Publisher Subscriber Service    not running
                pxGrid Connection Manager              disabled
                pxGrid Controller                      disabled
                Identity Mapping Service               disabled
                        """

                cmd_sasi_data_list = cmd_show_application_status_ise_formatting(output)

                target_key = 'ISE PROCESS NAME'
                target_value = 'Application Server'

                application_still_not_up = False
                for item in cmd_sasi_data_list:
                    if item.get(target_key) == target_value:
                        application_still_not_up = True
                        break
                return application_still_not_up

            # If it's up, set application_still_not_up = False
            # For now, let's assume you have a function to check it called check_application_status()
            application_still_not_up = check_application_status()

        if not application_still_not_up:
            print("Application is up.")
        else:
            print("Timeout: Application is still not up after 20 minutes.")


def cmd_reload_from_ssh(ip_address: str):
    pass


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

        select_string = f"""
        Choose an option from below:
            1. Show application status ise
            2. Reset ise services
            3. Reload from SSH

        Enter an option:
        """

        select_option = int(input(select_string))

        if select_option == 1:
            cmd_show_application_status_ise(interested_ip_address[0])
        elif select_option == 2:
            cmd_reset_ise_servers(interested_ip_address[0])
        elif select_option == 3:
            cmd_reload_from_ssh(interested_ip_address[0])
        else:
            print("Error: Selected incorrect option")

    except (Exception, psycopg2.Error) as error:
        print("Error:", error)

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        print("code executed successfully!")
