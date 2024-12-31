import requests
import json
import os

def fetch_instagram_posts(username, after_cursor=None, post_count=50):
    """
    Fetches Instagram posts for a given username, using a known GraphQL endpoint and doc_id.
    
    :param username: The Instagram username to fetch posts for.
    :param after_cursor: A string representing the pagination cursor to continue from. 
        If None, the function starts from the most recent post.
    :param post_count: The number of posts to fetch per request (batch size).
    :return: A dictionary representing the parsed JSON response if successful, or None if failed.
    
    Detailed Explanation:
    ---------------------
    1. base_url: The GraphQL query endpoint for Instagram. Typically, it’s a static string 
       like "https://www.instagram.com/graphql/query/", but this may change in official 
       Instagram updates or if they release new endpoints.
       
    2. doc_id: This is a GraphQL-specific identifier that points to a particular query 
       or 'document' on the Instagram backend. In official usage, doc_id might change, 
       so you should verify it or extract it from the web app if your requests fail.
       
    3. variables: A dictionary that includes parameters required by Instagram’s GraphQL query. 
       These can vary over time, but the essential ones are:
         - username: The profile we want to query.
         - data, __relay_internal__..., etc.: Additional flags that might be needed for the 
           GraphQL query to work properly. 
         - first: The batch size for pagination, how many items (posts) to fetch at a time.
         - after: The pagination cursor (if continuing from a previous request).

    4. params: Query parameters that get appended to the URL, including the serialized 
       'variables' dictionary and doc_id.

    5. headers: Some requests to Instagram’s endpoints may require an Authorization header 
       (if you have a user session token or a Bearer token). If you’re scraping, 
       this can be tricky since scraping might violate Instagram’s ToS. You might 
       also need a User-Agent header so the requests aren’t flagged as bots.

    6. The function sends a GET request. If the status code is 200 (OK), it returns 
       the JSON data as a Python dictionary. Otherwise, it prints an error message and returns None.
    """
    
    base_url = "https://www.instagram.com/graphql/query/"
    doc_id = "789826179xxxxxxxx"  # Example doc_id, may vary
    
    # The variable structure can differ based on the internal schema Instagram is using.
    variables = {
        "username": username,
        "data": {
            "count": post_count,
            "include_relationship_info": True,
            "latest_besties_reel_media": True,
            "latest_reel_media": True,
        },
        "__relay_internal__pv__PolarisFeedShareMenurelayprovider": False,
        "first": post_count,
    }

    # Only add the cursor if provided.
    if after_cursor:
        variables["after"] = after_cursor

    # Convert variables to JSON before passing to the params
    params = {
        "variables": json.dumps(variables),
        "doc_id": doc_id,
        "server_timestamps": True,
    }

    # Customize your headers as needed
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Authorization": "Bearer YOUR_ACCESS_TOKEN",  # Replace with your token if needed
    }

    response = requests.get(base_url, params=params, headers=headers)
    
    # Check the status code to see if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch posts: {response.status_code}")
        return None


def load_resume_state(resume_file):
    """
    Loads the pagination state from a JSON file if it exists.
    
    :param resume_file: The file path where the pagination state is stored.
    :return: A tuple (after_cursor, post_count). If not found, returns (None, 0).
    
    Detailed Explanation:
    ---------------------
    1. This function attempts to open 'resume_file', which should contain a JSON object 
       with at least two keys: 'after_cursor' (the string used for continuing pagination)
       and 'post_count' (an integer indicating how many posts have been fetched so far).
    2. If the file doesn't exist, it returns (None, 0), implying no saved state is found.
    3. If it does exist, it loads the data as a Python dictionary and retrieves the 
       'after_cursor' and 'post_count' keys. 
    4. This makes it possible to continue fetching posts from where we left off, 
       instead of re-fetching everything from scratch.
    """
    
    if os.path.exists(resume_file):
        with open(resume_file, "r", encoding="utf-8") as f:
            state = json.load(f)
            return state.get("after_cursor"), state.get("post_count", 0)
    return None, 0


def save_resume_state(resume_file, after_cursor, post_count):
    """
    Saves the current pagination state to a JSON file.
    
    :param resume_file: The file path to which the state should be saved.
    :param after_cursor: The current 'end_cursor' from Instagram's GraphQL response.
    :param post_count: The total number of posts fetched so far.
    
    Detailed Explanation:
    ---------------------
    1. Creates a dictionary called 'state' containing 'after_cursor' and 'post_count'.
    2. Saves it in JSON format to the specified file. 
    3. The 'indent=4' parameter makes the JSON more readable, but it’s optional.
    4. Saving the state after each batch ensures we can resume if the process is 
       interrupted for any reason (e.g., network error, script crash, etc.).
    """
    
    state = {
        "after_cursor": after_cursor,
        "post_count": post_count
    }
    with open(resume_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)


def load_existing_posts(output_file):
    """
    Loads previously downloaded posts from a JSON file if we want to append 
    new posts to the existing dataset.
    
    :param output_file: The file path containing the previously saved posts.
    :return: A list of post objects if successful, or an empty list if the file 
             does not exist or can't be loaded as valid JSON.
    
    Detailed Explanation:
    ---------------------
    1. This function checks if 'output_file' exists. If it doesn't, return an empty list.
    2. If it does exist, open it and attempt to parse it as JSON.
    3. If JSON decoding fails (e.g., file is corrupt or in invalid format), 
       return an empty list to avoid crashing.
    4. The function expects the file to contain a list of posts. If the file 
       exists but is not a valid list, or is malformed, the function still 
       tries to handle it gracefully by returning an empty list.
    """
    
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def iterate_and_save_posts(username, output_file, resume_file, batch_size=50):
    """
    Iterates through the pages of Instagram posts for a given user,
    saving the results to a JSON file. Also manages a 'resume file' 
    to keep track of the pagination state.
    
    :param username: The Instagram username to fetch posts from.
    :param output_file: The file to which fetched posts will be saved/updated.
    :param resume_file: The file that stores pagination state (cursor, total count).
    :param batch_size: The number of posts to fetch per request (default = 50).
    
    Detailed Explanation:
    ---------------------
    1. load_existing_posts: 
       - Reads previously saved posts so that we can append to them 
         rather than overwriting them.
    2. load_resume_state: 
       - Loads the 'after_cursor' and 'downloaded_count' (how many posts 
         are already fetched) so we know where to continue from.
    3. While True loop: 
       - We keep requesting posts in batches until:
         a) No more posts are returned, or
         b) We reach a situation where the server doesn't respond 
            (response is None).
    4. fetch_instagram_posts: 
       - Retrieves the next batch of posts. We pass 'after_cursor' if available.
    5. We look at 'edges' in the returned JSON. Each edge contains a 'node' 
       that represents a single post. We append each post to 'all_posts'.
    6. After adding each batch of posts, we overwrite 'output_file' with 
       the new combined list. 
    7. We also check 'page_info' for 'has_next_page'. If True, we save 
       the 'end_cursor' and increment the post count. If False, 
       we've reached the last page.
    8. The function prints messages indicating the progress to provide 
       clear feedback on how many posts have been saved and whether 
       there are more to fetch.
    """
    
    # Load existing posts to continue appending
    all_posts = load_existing_posts(output_file)
    
    # Load resume state (after_cursor and how many posts we have so far)
    after_cursor, downloaded_count = load_resume_state(resume_file)

    while True:
        print(f"Fetching next {batch_size} posts. Current count: {downloaded_count}")
        
        # Call the function that fetches Instagram posts
        response = fetch_instagram_posts(username, after_cursor, post_count=batch_size)
        
        # If the response is None, it could be due to rate-limiting or an error.
        # Break to avoid an infinite loop; you can retry later.
        if not response:
            print("No response received, stopping.")
            break

        # Dig into the JSON structure to find the post 'edges'
        edges = (response.get("data", {})
                        .get("xdt_api__v1__feed__user_timeline_graphql_connection", {})
                        .get("edges", []))
        
        # If no edges, we've likely fetched all posts or there's an issue.
        if not edges:
            print("No more posts found, finishing.")
            break

        # Append new posts to our master list
        for edge in edges:
            post_node = edge.get("node", {})
            all_posts.append(post_node)
            downloaded_count += 1

        # Save all posts to the JSON file after each batch
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_posts, f, ensure_ascii=False, indent=4)
        print(f"Saved {len(all_posts)} posts to {output_file}")

        # Check pagination info to see if there's another page
        page_info = (response.get("data", {})
                            .get("xdt_api__v1__feed__user_timeline_graphql_connection", {})
                            .get("page_info", {}))
        
        # If there's a next page, update 'after_cursor' and save state
        if page_info.get("has_next_page"):
            after_cursor = page_info.get("end_cursor")
            save_resume_state(resume_file, after_cursor, downloaded_count)
        else:
            print("Reached the end of available pages.")
            break


def load_json_file(file_path):
    """
    Attempts to load a JSON file from the specified path. Handles various 
    exceptions such as file not found, invalid JSON format, or encoding issues.
    
    :param file_path: The path to the JSON file to be loaded.
    :return: The JSON data if it’s a list, otherwise None (and prints diagnostic info).
    
    Detailed Explanation:
    ---------------------
    1. Tries to open 'file_path' with UTF-8 encoding:
       - If successful, loads it as JSON.
       - Checks if the data is a list. If it is, returns it.
         Otherwise, prints the data type for debugging.
    2. If FileNotFoundError is raised, prints an error message. 
       This usually means the path is incorrect or the file doesn't exist.
    3. If json.JSONDecodeError is raised, prints that the file is not valid JSON.
    4. If UnicodeDecodeError is raised (e.g., because the file is not 
       in UTF-8 encoding), tries again with Latin-1 encoding. If that 
       also fails, prints an error message.
    5. Any other exception is caught and printed.
    """
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, list):
                print("The JSON file contains a list:")
                return data
            else:
                print("The JSON file does not contain a list.")
                print(f"Type of data: {type(data)}")
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")
    except UnicodeDecodeError as e:
        print(f"Error decoding file with UTF-8: {e}")
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                data = json.load(file)
                print("The JSON file was loaded using latin-1 encoding.")
                if isinstance(data, list):
                    print("The JSON file contains a list:")
                    return data
                else:
                    print("The JSON file does not contain a list.")
                    print(f"Type of data: {type(data)}")
        except UnicodeDecodeError as e2:
            print(f"Error decoding file with latin-1: {e2}")
            print(f"Could not decode the file. Please check the file encoding.")
        except Exception as e3:
            print(f"An unexpected error occurred while trying latin-1: {e3}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    

# --------------------------------------------------------------------------
# Below is an example usage block that demonstrates how you might use these functions.
# --------------------------------------------------------------------------

if __name__ == "__main__":
    version = '01'
    username = "natgeo"
    output_file = f"instagram_posts_{username}_{version}.json"
    resume_file = f"resume_state_{username}_{version}.json"
    
    # Calls our main function to iterate through available pages and save fetched posts
    iterate_and_save_posts(username, output_file, resume_file, batch_size=50)

    # Example of how to load the JSON file after it's saved:
    # loaded_data = load_json_file(output_file)
    # if loaded_data:
    #     print(f"Loaded {len(loaded_data)} posts from {output_file}")
