import os
import json

def load_json_file(json_path):
    """Load and parse the JSON file containing word index data."""
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {json_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file {json_path} is not a valid JSON file.")
        return None

def search_word(documents_dir, json_path, output_json):
    """Search for exact word matches in the JSON file and save results to a new JSON file."""
    # Validate documents directory with fallback
    while not os.path.isdir(documents_dir):
        print(f"Error: The documents directory {documents_dir} does not exist.")
        documents_dir = input("Please enter a valid documents directory path: ").strip()
        if not documents_dir:
            print("No path provided. Exiting.")
            return

    # Load JSON data
    data = load_json_file(json_path)
    if data is None:
        return

    # Prompt user for search word
    search_word = input("Enter the word to search: ").strip()

    # Search for exact matches
    matches = [entry for entry in data if entry["word"] == search_word]

    # Save results to output JSON
    if matches:
        try:
            with open(output_json, 'w') as f:
                json.dump(matches, f, indent=2)
            print(f"\nFound {len(matches)} occurrence(s) of the word '{search_word}'.")
            print(f"Results saved to {output_json}.")
        except Exception as e:
            print(f"Error saving results to {output_json}: {str(e)}")
    else:
        print(f"\nNo matches found for the word '{search_word}'.")
        try:
            with open(output_json, 'w') as f:
                json.dump([], f, indent=2)
            print(f"Empty results saved to {output_json}.")
        except Exception as e:
            print(f"Error saving empty results to {output_json}: {str(e)}")

def main():
    """Main function to execute the search process."""
    # Prompt for paths with defaults
    documents_dir = input("Enter the do cuments directory path: ").strip() or "/home/litzchill/Boon_sai/doc_search/DATA/data"
    json_path = input("Enter the JSON file path: ").strip() or "/home/litzchill/Boon_sai/doc_search/word_index.json"
    output_json = input("Enter the output JSON file path: ").strip() or "/home/litzchill/Boon_sai/doc_search/search_results.json"

    search_word(documents_dir, json_path, output_json)

if __name__ == "__main__":
    main()