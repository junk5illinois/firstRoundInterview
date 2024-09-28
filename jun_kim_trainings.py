"""
Author: Jun Kim
"""
import json
from collections import defaultdict
from datetime import datetime, timedelta

INPUT_FILE_PATH = 'trainings.txt'

def get_training_count(data, output_file_path):
    """
    Count the number of completions for each unique training in the dataset and save the result to a JSON file.

    Args:
        data (list): List of dictionaries containing people and their training completions.
        output_file_path (str): Path to save the output JSON file.
    """
    # Dictionary to store the count of each training
    training_count = defaultdict(int)

    # Iterate through each person's completions and count each training
    for person in data:
        completions = person.get('completions', [])
        for completion in completions:
            training_name = completion.get('name')
            if training_name:
                training_count[training_name] += 1

    # Write the training count result to a JSON file
    with open(output_file_path, 'w') as output_file:
        json.dump(training_count, output_file, indent=4)


def get_completed_trainings(data, trainings, fiscal_year, output_file_path):
    """
    List all people who completed the specified trainings in the given fiscal year.

    Args:
        data (list): List of dictionaries containing people and their training completions.
        trainings (list): List of trainings to check for completions.
        fiscal_year (int): The fiscal year for filtering completions.
        output_file_path (str): Path to save the output JSON file.
    """
    # Dictionary to store all people who completed a certain training
    training_results = {training: [] for training in trainings}
    
    fiscal_start = datetime(fiscal_year - 1, 7, 1)
    fiscal_end = datetime(fiscal_year, 6, 30)

    # Check if each person's completions fall within the fiscal year for the specified trainings
    for person in data:
        for completion in person.get('completions', []):
            training_name = completion.get('name')
            timestamp = completion.get('timestamp')
            
            if training_name in training_results and timestamp:
                date = datetime.strptime(timestamp, "%m/%d/%Y")
                if fiscal_start <= date <= fiscal_end:
                    training_results[training_name].append(person['name'])

    # Write the training results to a JSON file
    with open(output_file_path, 'w') as output_file:
        json.dump(training_results, output_file, indent=4)


def get_most_recent_completions(completions):
    """
    Get the most recent completion date for each unique training.

    Args:
        completions (list): List of training completions with name, timestamp, and expiration.

    Returns:
        dict: A dictionary mapping training names to the most recent expiration dates.
    """
    most_recent = {}

    # Find the most recent completion for each unique training
    for completion in completions:
        training_name = completion.get('name')
        timestamp = completion.get('timestamp')
        expiry = completion.get('expires')
        
        if training_name and timestamp:
            completion_date = datetime.strptime(timestamp, "%m/%d/%Y")
            
            # Update if this completion is more recent than any previous one
            if (training_name not in most_recent) or (completion_date > most_recent[training_name]['timestamp']):
                most_recent[training_name] = {
                    'timestamp': completion_date,
                    'expires': expiry
                }

    # Return the most recent completions
    return most_recent


def get_expired_or_expiring_trainings(data, reference_date, output_file_path):
    """
    Find people who have trainings that have expired or will expire soon (within 30 days).

    Args:
        data (list): List of dictionaries containing people and their training completions.
        reference_date (datetime): The date to use as the reference for checking expiry.
        output_file_path (str): Path to save the output JSON file.
    """
    results = []

    # Get only the most recent training completions for each person
    for person in data:
        most_recent_trainings = get_most_recent_completions(person.get('completions', []))
        expired_or_expiring_trainings = []
        
        # Get the expiration date for each training
        for training_name, details in most_recent_trainings.items():
            expiry_str = details['expires']
            if expiry_str:
                expiry_date = datetime.strptime(expiry_str, "%m/%d/%Y")
                status = None

                # Determine if the training is expired or will expire within 30 days
                if reference_date > expiry_date:
                    status = 'expired'
                elif expiry_date <= reference_date + timedelta(days=30):
                    status = 'expires soon'
                
                if status:
                    expired_or_expiring_trainings.append({
                        'training': training_name,
                        'status': status,
                        # 'expiration_date': expiry_str
                    })

        # Add the person to the results if any trainings are expired or expiring soon
        if expired_or_expiring_trainings:
            results.append({
                'name': person['name'],
                'trainings': expired_or_expiring_trainings
            })

    # Write the results to a JSON file
    with open(output_file_path, 'w') as output_file:
        json.dump(results, output_file, indent=4)


if __name__ == '__main__':
    # Load input data from file
    with open(INPUT_FILE_PATH, 'r') as file:
        data = json.load(file)
    
    # Task 1: Get the count of people who completed each training
    get_training_count(data, 'task_1_training_count.json')

    # Task 2: List all people who completed specific trainings in the given fiscal year
    trainings = ["Electrical Safety for Labs", "X-Ray Safety", "Laboratory Safety Training"]
    fiscal_year = 2024
    get_completed_trainings(data, trainings, fiscal_year, 'task_2_completed_trainings.json')

    # Task 3: Find people with expired or expiring trainings as of the reference date
    reference_date = datetime.strptime('10/1/2023', '%m/%d/%Y')
    get_expired_or_expiring_trainings(data, reference_date, 'task_3_expired_or_expiring_trainings.json')