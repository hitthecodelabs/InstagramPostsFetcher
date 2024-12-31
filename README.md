
# Instagram Posts Fetcher

A Python script that fetches Instagram posts from a specified account using a GraphQL endpoint. It supports batching, pagination, and resumable downloads, saving your results into JSON format. It also handles encoding issues for robust JSON loading.

## Features

1. **Batch Fetching**: Pull a specified number of Instagram posts in batches.  
2. **Pagination**: Uses `after_cursor` to fetch subsequent pages automatically.  
3. **Resumable**: Keeps track of the last fetched cursor in a state file (`resume_file`) so you can resume fetching later.  
4. **Flexible Encoding**: Includes error-handling for different text encodings (`utf-8`, `latin-1`, etc.).  

## Requirements

- Python 3.7 or later  
- [Requests](https://pypi.org/project/requests/) library  
  ```bash
  pip install requests
  ```

- A valid Instagram GraphQL `doc_id` or endpoint (the example uses `doc_id="7898261xxxxxxxxxxx"`, but this can change).

## Installation

1. Clone the repository (or download the script files):
   ```bash
   git clone https://github.com/hitthecodelabs/InstagramPostsFetcher.git
   ```

2. Install Dependencies:
   ```bash
   cd InstagramPostsFetcher
   pip install -r requirements.txt
   ```

3. If you don't have a requirements file, just ensure `requests` is installed:
   ```bash
   pip install requests
   ```

## Usage

1. Update the Code:
   - Replace `YOUR_ACCESS_TOKEN` with your token if needed (or remove the Authorization header if you’re not using it).
   - Make sure your `doc_id` is correct or aligned with the currently valid Instagram GraphQL endpoints.

2. Run the Script:
   ```bash
   python ig_posts_fecther.py
   ```

   By default, it will:
   - Fetch posts from the specified username (`username`).
   - Save them to a JSON file (`output_file`, e.g., `instagram_posts_<username>.json`).
   - Keep track of pagination state in a resume file (`resume_file`, e.g., `resume_state_<username>.json`).

3. Check the Output:
   - After running, open or parse the JSON file to verify the fetched posts.
   - If you stop the script or if it stops due to an error, just run it again to resume where it left off.

## Script Explanation

- `fetch_instagram_posts(username, after_cursor, post_count)`  
  Makes a GET request to the Instagram GraphQL endpoint to fetch a specific batch of posts.

- `load_resume_state(resume_file)`  
  Loads the last pagination state from a JSON file so you can resume from the last cursor.

- `save_resume_state(resume_file, after_cursor, post_count)`  
  Saves the pagination state after each successful fetch.

- `load_existing_posts(output_file)`  
  Loads previously saved posts so you can append newly fetched data.

- `iterate_and_save_posts(username, output_file, resume_file, batch_size)`  
  Orchestrates fetching in batches until there are no more posts or an error occurs.

- `load_json_file(file_path)`  
  Demonstrates safe reading of JSON files with fallback encodings.

## Troubleshooting

- If Invalid Token errors occur, check your token or authorization method.
- If the `doc_id` is invalid or outdated, you may see errors from Instagram's GraphQL endpoint. Make sure to update to a valid endpoint or `doc_id`.

## Contributing

1. Fork the project.  
2. Create your feature branch (`git checkout -b feature/NewFeature`).  
3. Commit your changes (`git commit -m 'Add a new feature'`).  
4. Push to the branch (`git push origin feature/NewFeature`).  
5. Open a Pull Request.  

## License

This project is licensed under the MIT License. You are free to modify and use the code. Refer to the license file for details.
