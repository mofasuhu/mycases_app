import json
import os
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CASE_IDS_FILE = os.path.join(DATA_DIR, "case_ids.json")

def sanitize_filename(name):
    """Sanitizes a string to be used as a filename by removing or replacing invalid characters."""
    name = re.sub(r'[^\w\s-]', '', name).strip()
    name = re.sub(r'[-\s]+', '_', name)
    return name

def get_next_case_id():
    """Gets the next available unique case ID.
    
    Reads from a JSON file that tracks all used IDs, finds the next available ID,
    updates the tracking file, and returns the new ID.
    
    Returns:
        int: The next available unique case ID.
    """
    # Ensure data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Initialize case IDs tracking structure
    case_ids = {"next_id": "1", "used_ids": []}
    
    # Load existing case IDs if available
    if os.path.exists(CASE_IDS_FILE):
        try:
            with open(CASE_IDS_FILE, 'r', encoding='utf-8') as f:
                case_ids = json.load(f)
        except Exception as e:
            print(f"Error loading case IDs file: {str(e)}. Starting with new tracking.")
    
    # Get the next available ID
    next_id = case_ids["next_id"]
    
    # Update the tracking information
    case_ids["next_id"] = str(int(next_id) + 1)
    if next_id not in case_ids["used_ids"]:
        case_ids["used_ids"].append(next_id)
    
    # Save the updated tracking information
    try:
        with open(CASE_IDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(case_ids, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving case IDs file: {str(e)}")
    
    return next_id

def find_existing_case_folder(case_id):
    if not case_id:
        return None
    existing_folders = get_all_case_folders()
    for folder in existing_folders:
        folder_data = load_case_data_from_json(folder)
        if folder_data and folder_data.get("case_id") == case_id:
            return folder
    return None

def save_case_data_to_json(case_data):
    """Saves the case data to a JSON file in the appropriate child's folder."""
    if not isinstance(case_data, dict):
        return False, "تنسيق بيانات الحالة غير صالح."

    child_name = case_data.get("child_name")
    case_id = case_data.get("case_id")

    if not child_name or not case_id:
        return False, "يجب إدخال اسم الطفل ومعرف الحالة لحفظ الحالة."

    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        # If we have a case_id, try to find the existing folder
        if case_id:
            existing_case_folder_name = find_existing_case_folder(case_id)
            
            # If we found the folder, we'll update the existing case
            if existing_case_folder_name:
                print(f"Updating existing case with ID {case_id}")
            else:
                print(f"Could not find folder for case ID {case_id}. A new folder will be created.")
        
        child_data_path = os.path.join(DATA_DIR, case_id)
        if not os.path.exists(child_data_path):
            os.makedirs(child_data_path)
        
        surveys_path = os.path.join(child_data_path, "surveys")
        if not os.path.exists(surveys_path):
            os.makedirs(surveys_path)

        case_file_path = os.path.join(child_data_path, "case.json")
        with open(case_file_path, 'w', encoding='utf-8') as f:
            json.dump(case_data, f, ensure_ascii=False, indent=4)
        
        return True, f"تم حفظ بيانات الحالة بنجاح"
    except Exception as e:
        return False, f"فشل حفظ بيانات الحالة\n{str(e)}"

def load_case_data_from_json(case_folder_name):
    """Loads case data from a JSON file within the specified child's folder."""
    case_file_path = os.path.join(DATA_DIR, case_folder_name, "case.json")
    if not os.path.exists(case_file_path):
        return None
    try:
        with open(case_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading case data from {case_file_path}: {str(e)}")
        return None

def get_all_case_folders():
    """Scans the data directory and returns a list of all valid case folder names."""
    if not os.path.exists(DATA_DIR):
        return []
    return [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d)) and os.path.exists(os.path.join(DATA_DIR, d, "case.json"))]

# --- Survey File Management ---

def save_survey_data_to_json(case_folder_name, survey_data):
    if not isinstance(survey_data, dict):
        return False, "Invalid survey data format (must be a dictionary)."

    survey_type_str = survey_data.get("survey_type")
    if not survey_type_str:
        return False, "Survey Type is required to save the survey."

    try:
        surveys_dir_path = os.path.join(DATA_DIR, case_folder_name, "surveys")
        if not os.path.exists(surveys_dir_path):
            os.makedirs(surveys_dir_path) 

        survey_filename = survey_type_str + ".json"
        survey_file_path = os.path.join(surveys_dir_path, survey_filename)

        with open(survey_file_path, 'w', encoding='utf-8') as f:
            json.dump(survey_data, f, ensure_ascii=False, indent=4)
        
        print(f"Survey data saved successfully to: {survey_file_path}")
        return True, survey_filename
    except Exception as e:
        error_msg = str(e)
        print(error_msg)
        return False, error_msg

def load_surveys_for_case(case_folder_name):
    """Loads all survey JSON files for a given case folder.
    Args:
        case_folder_name (str): The folder name of the case.
    Returns:
        list: A list of dictionaries, where each dictionary is a loaded survey. Returns empty list on error or if no surveys.
    """
    surveys_dir_path = os.path.join(DATA_DIR, case_folder_name, "surveys")
    loaded_surveys = []

    if not os.path.exists(surveys_dir_path) or not os.path.isdir(surveys_dir_path):
        return loaded_surveys # No surveys directory, so no surveys

    for filename in sorted(os.listdir(surveys_dir_path), reverse=True): # Sort by name (often date-based)
        if filename.endswith(".json"):
            file_path = os.path.join(surveys_dir_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    survey_content = json.load(f)
                    # Add filename to the content for reference if needed in UI
                    survey_content['_filename'] = filename.replace(".json","") 
                    loaded_surveys.append(survey_content)
            except Exception as e:
                print(f"Error loading survey file {file_path}: {str(e)}")
                # Optionally, append a placeholder or error object
    return loaded_surveys

def load_single_survey(case_folder_name, survey_filename):
    """Loads a single survey JSON file.
    Args:
        case_folder_name (str): The folder name of the case.
        survey_filename (str): The filename of the survey.
    Returns:
        dict or None: Loaded survey data or None if error.
    """
    survey_file_path = os.path.join(DATA_DIR, case_folder_name, "surveys", survey_filename)
    if not os.path.exists(survey_file_path):
        print(f"Survey file not found: {survey_file_path}")
        return None
    try:
        with open(survey_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading survey {survey_file_path}: {e}")
        return None
