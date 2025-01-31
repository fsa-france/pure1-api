#!/usr/bin/env python3
"""
Retrieve and display information about Pure1 arrays fleet, such as total capacity,
data reduction, load and system space. 
Connection to Pure1 REST API is done using 2 parameters:
    - path to private key
    - application ID.

Usage:
    usage: get_pure1_fleet_infos.py [-h] [-p PASSWORD] pure1_api_id pure1_pk_file

Example:
   % python3 get_pure1_fleet_infos.py  pure1:apikey:DSIxxxxxx2FGCADN /Users/user1/.ssh/my_ssh_private_key.pem
"""

import argparse
import datetime
import logging

# The Pure Storage python module for Pure1, Flasharray and Flashblade
from pypureclient import pure1

# Constants
METRIC_RESOLUTION_DAY = 86_400_000  # 24 hours in milliseconds
REPORTING_INTERVAL_DAYS = 7
BYTES_IN_A_TERABYTE = 1_099_511_627_776
BYTES_IN_A_GIGABYTE = 1_073_741_824

# Lower the logger level for the pypureclient logger
logging.getLogger("pypureclient").setLevel(logging.ERROR)

def get_pure1_fleet_information(pure1_api_id, pure1_pk_file, pure1_pk_pwd):
    """
    Retrieve system space and other metrics for all Pure1 arrays associated with
    the specified API ID and private key.

    :param pure1_api_id: (str) The Pure1 API Client Application ID.
    :param pure1_pk_file: (str) Path to the Pure1 API Client Private Key file.
    :param pure1_pk_pwd: (str) Password for the private key file (if encrypted).
    """
    
    # Create a Pure1 Client instance
    pure1_client = pure1.Client(
        private_key_file=pure1_pk_file,
        private_key_password=pure1_pk_pwd,
        app_id=pure1_api_id,
        timeout=15  # Should be an integer
    )

    # Retrieve the list of fleet arrays (FlashArray and Flashblade)
    response = pure1_client.get_arrays()
    arrays = list(response.items) if response and response.items else []

    print("List of Pure1 fleet arrays")
    print("==========================")
    for array in arrays:
        name = array.name
        os_version = array.version
        model = array.model

        # Define metrics to retrieve
        metrics_names = [
            'array_total_capacity',
            'array_effective_used_space',
            'array_data_reduction',
            'array_shared_space',
            'array_system_space',
            'array_total_load'
        ]

        # Calculate the time range for the metrics
        end_time = int(datetime.datetime.now().timestamp())
        start_time = int((datetime.datetime.now() - datetime.timedelta(days=REPORTING_INTERVAL_DAYS)).timestamp())

        # Get metrics history for each array
        metrics_response = pure1_client.get_metrics_history(
            aggregation='avg',
            names=metrics_names,
            resource_ids=array.id,
            resolution=METRIC_RESOLUTION_DAY * REPORTING_INTERVAL_DAYS,
            start_time=start_time,
            end_time=end_time
        )

        # Initialize default values for metrics
        total_capacity_tb = 0
        effective_used_space_gb = 0
        data_reduction = 0
        shared_space_gb = 0
        system_space_gb = 0
        array_load = 0

        # Process the metrics (if present)
        if hasattr(metrics_response, 'items'):
            for metric_item in metrics_response.items:
                metric_name = metric_item.name

                # Check if we have data points for the current metric
                if metric_item.data:
                    # We only need the latest metric data point in this scenario
                    # metric_data is a list of [timestamp, value]
                    _, value = metric_item.data[-1]  # Take the last data point

                    if metric_name == 'array_total_capacity':
                        total_capacity_tb = value / BYTES_IN_A_TERABYTE
                    elif metric_name == 'array_effective_used_space':
                        effective_used_space_gb = value / BYTES_IN_A_GIGABYTE
                    elif metric_name == 'array_data_reduction':
                        data_reduction = value
                    elif metric_name == 'array_shared_space':
                        shared_space_gb = value / BYTES_IN_A_GIGABYTE
                    elif metric_name == 'array_system_space':
                        system_space_gb = value / BYTES_IN_A_GIGABYTE
                    elif metric_name == 'array_total_load':
                        array_load = value

        # Print out the information about this array
        print(f"Array Name: {name}")
        print(f"\tModel: {model}")
        print(f"\tPurity Version: {os_version}")
        print(f"\tTotal Capacity (TB): {total_capacity_tb:.2f}")
        print(f"\tEffective Used Space (GB): {effective_used_space_gb:.2f}")
        print(f"\tData Reduction: {data_reduction:.2f}")
        print(f"\tSystem Space (GB): {system_space_gb:.2f}")
        print(f"\tArray Load (avg): {array_load:.2f}")

def main():
    """
    Main entry point. Parses command-line arguments, then retrieves
    and displays information on all Pure1 arrays.
    """
    parser = argparse.ArgumentParser(description="Pure1 Reporting integration parameters.")
    parser.add_argument("pure1_api_id", type=str, help="Pure1 API Client App ID.")
    parser.add_argument("pure1_pk_file", type=str, help="Path to the Pure1 API Client Private Key File.")
    parser.add_argument(
        "-p",
        "--password",
        type=str,
        help="Use if private key is encrypted (or leave empty if not needed)."
    )
    args = parser.parse_args()

    print("Retrieving array information and system space from Pure1...")
    get_pure1_fleet_information(args.pure1_api_id, args.pure1_pk_file, args.password)

if __name__ == "__main__":
    main()
