import re

# Sample output from the command
input_string = """
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


if __name__ == "__main__":
    cmd_sasi_data_list = cmd_show_application_status_ise_formatting(input_string)

    # Print the list of dictionaries
    for data in cmd_sasi_data_list:
        print(data)
