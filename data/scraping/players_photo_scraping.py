import pandas as pd
import random
import csv
import time
import queue
import logging
import argparse
import threading
import urllib.error
import os.path
import sys
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from googlesearch import search

# Set up logging with proper encoding handling
file_handler = logging.FileHandler("scraping.log", encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Configure console handler with error handling for Unicode characters
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Configure root logger
logger = logging.getLogger('player_scraper')
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Helper function to sanitize strings for console output
def safe_log(msg, level='info'):
    """Log messages safely, handling Unicode characters"""
    try:
        if level == 'debug':
            logger.debug(msg)
        elif level == 'warning':
            logger.warning(msg)
        elif level == 'error':
            logger.error(msg)
        else:
            logger.info(msg)
    except UnicodeEncodeError:
        # If encoding fails, try to replace problematic characters
        msg_safe = msg.encode('cp1252', errors='replace').decode('cp1252')
        if level == 'debug':
            logger.debug(msg_safe)
        elif level == 'warning':
            logger.warning(msg_safe)
        elif level == 'error':
            logger.error(msg_safe)
        else:
            logger.info(msg_safe)

# Queue for failed requests
retry_queue = queue.Queue()

def get_player_photo_url_by_profile_page(url):
    """
    Given a player profile page URL of zerozero.pt, return the URL of the player's photo.
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    ]
    headers = {'User-Agent': random.choice(user_agents)}
    req = Request(url, headers=headers)
    
    try:
        response = urlopen(req).read()
        soup = BeautifulSoup(response, 'html.parser')
        
        div_image = soup.find('div', class_='profile_picture')
        div_logo = div_image.find('div', class_='logo')
        a = div_logo.find('a')
        img = a.find('img')
        img_url = img['src']
        
        safe_log(f"Successfully fetched photo URL: {img_url}", 'debug')
        return img_url
    except urllib.error.HTTPError as e:
        if e.code == 429:
            safe_log(f"HTTP 429 error (Too Many Requests) for URL: {url}", 'warning')
            return None
        else:
            safe_log(f"HTTP error {e.code} for URL: {url}", 'error')
            return None
    except Exception as e:
        safe_log(f"Error fetching photo URL: {str(e)}", 'error')
        return None

def find_zerozero_url(name, club):
    """Find a zerozero.pt URL for a player, trying multiple search approaches"""
    # First try: standard search
    to_search = f"{name} {club} zerozero"
    safe_log(f"Searching: {to_search}", 'debug')
    
    try:
        # Try to get multiple results to increase chances of finding zerozero URL
        search_results = list(search(to_search, num_results=3))
        
        # First check if any of the results are from zerozero
        for url in search_results:
            if "zerozero.pt" in url:
                safe_log(f"Found zerozero URL on first attempt: {url}")
                return url
        
        # Second try: more specific search with site:
        to_search = f"{name} {club} site:zerozero.pt"
        safe_log(f"No zerozero URL found, trying more specific search: {to_search}")
        
        search_results = list(search(to_search, num_results=3))
        for url in search_results:
            if "zerozero.pt" in url:
                safe_log(f"Found zerozero URL on second attempt: {url}")
                return url
        
        # Third try: just name with site:
        to_search = f"{name} site:zerozero.pt"
        safe_log(f"Still no zerozero URL, trying simplified search: {to_search}")
        
        search_results = list(search(to_search, num_results=3))
        for url in search_results:
            if "zerozero.pt" in url:
                safe_log(f"Found zerozero URL on third attempt: {url}")
                return url
                
        # If we got here, no zerozero URL found
        safe_log(f"Failed to find zerozero.pt URL for {name} from {club} after multiple attempts", 'warning')
        if search_results:
            return search_results[0]  # Return the first result even if not zerozero
        return None
    except Exception as e:
        safe_log(f"Error during search: {str(e)}", 'error')
        return None

def process_player(rk, name, club, writer, file):
    """Process a single player, fetch data and write to file"""
    safe_log(f"Processing player: {name} (Rank: {rk}) from {club}")
    
    try:
        zerozero_url = find_zerozero_url(name, club)
        if not zerozero_url:
            safe_log(f"No URL found for {name} (Rank: {rk})", 'error')
            writer.writerow([rk, name, "", ""])
            file.flush()
            return False
            
        safe_log(f"Found URL: {zerozero_url}")
        
        if "zerozero.pt" in zerozero_url:
            photo_url = get_player_photo_url_by_profile_page(zerozero_url)
            if photo_url is None:
                # If we got a 429 error, add to retry queue
                safe_log(f"Adding player {name} to retry queue")
                retry_queue.put((rk, name, club, zerozero_url))
                return False
        else:
            photo_url = None
            safe_log(f"Non-zerozero URL found for {name}: {zerozero_url}", 'warning')
            # Still save non-zerozero URLs, but mark for retry later
            retry_queue.put((rk, name, club, ""))  # Empty URL to trigger new search during retry
        
        writer.writerow([rk, name, zerozero_url, photo_url])
        file.flush()
        safe_log(f"Data written for {name}")
        return True
        
    except Exception as e:
        safe_log(f"Error processing player {name}: {str(e)}", 'error')
        return False

def process_retry_queue(output_file):
    """Process items in the retry queue"""
    safe_log(f"Processing retry queue with {retry_queue.qsize()} items")
    
    with open(output_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Process at most all current items in the queue
        current_size = retry_queue.qsize()
        for _ in range(current_size):
            if retry_queue.empty():
                break
                
            rk, name, club, zerozero_url = retry_queue.get()
            safe_log(f"Retrying player: {name}")
            
            try:
                # If URL is empty, try to find a zerozero URL first
                if not zerozero_url or "zerozero.pt" not in zerozero_url:
                    zerozero_url = find_zerozero_url(name, club)
                    if not zerozero_url or "zerozero.pt" not in zerozero_url:
                        safe_log(f"Still can't find zerozero URL for {name}, skipping", 'warning')
                        # Re-queue for future attempts
                        retry_queue.put((rk, name, club, ""))
                        time.sleep(5)
                        continue
                
                # Now we have a zerozero URL, get the photo
                photo_url = get_player_photo_url_by_profile_page(zerozero_url)
                if photo_url is None:
                    # Put back in the queue if still failing
                    safe_log(f"Still failing for {name}, re-queueing", 'warning')
                    retry_queue.put((rk, name, club, zerozero_url))
                else:
                    writer.writerow([rk, name, zerozero_url, photo_url])
                    file.flush()
                    safe_log(f"Successfully processed queued player {name}")
                
                # Wait between requests to avoid rate limiting
                time.sleep(5)
            except Exception as e:
                safe_log(f"Error processing queued player {name}: {str(e)}", 'error')
                retry_queue.put((rk, name, club, zerozero_url))

def setup_retry_scheduler(output_file, interval=300):
    """Set up a scheduler to process the retry queue periodically"""
    def scheduler_job():
        while True:
            if not retry_queue.empty():
                safe_log("Scheduler: processing retry queue")
                process_retry_queue(output_file)
            time.sleep(interval)
    
    thread = threading.Thread(target=scheduler_job, daemon=True)
    thread.start()
    return thread

def load_existing_entries(output_file):
    """
    Load already processed entries from the output file.
    Returns two sets:
    - complete_entries: entries with photo URLs
    - incomplete_entries: entries without photo URLs that need retrying
    """
    complete_entries = set()
    incomplete_entries = []
    
    # Special ranks to diagnose
    special_ranks = {8, 25, 57}
    
    if not os.path.exists(output_file):
        safe_log(f"Output file {output_file} does not exist yet, starting fresh")
        return complete_entries, incomplete_entries
    
    try:
        with open(output_file, 'r', newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and len(row) >= 4 and row[0].isdigit():  # Check if it's a valid data row with enough columns
                    rk = int(row[0])
                    name = row[1]
                    website_url = row[2]
                    photo_url = row[3] if len(row) > 3 else None
                    
                    # Diagnostic for special ranks
                    if rk in special_ranks:
                        safe_log(f"DIAGNOSTIC - Player rank {rk}: Name={name}, URL={website_url}, Photo={photo_url}")
                    
                    # More stringent check for valid photo URLs
                    if (photo_url and isinstance(photo_url, str) and 
                        len(photo_url.strip()) >= 5 and 
                        photo_url.strip().startswith(('http://', 'https://'))):
                        complete_entries.add(rk)
                    else:  # No photo URL or invalid URL, add to retry list
                        safe_log(f"Found entry with missing/invalid photo URL: {name} (Rank: {rk})")
                        incomplete_entries.append((rk, name, website_url))
        
        safe_log(f"Loaded {len(complete_entries)} complete entries and found {len(incomplete_entries)} entries without valid photos")
        return complete_entries, incomplete_entries
    except Exception as e:
        safe_log(f"Error loading existing entries: {str(e)}", 'error')
        return complete_entries, incomplete_entries

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Scrape player photos from zerozero.pt')
    parser.add_argument('--start', type=int, default=0, help='Starting rank')
    parser.add_argument('--end', type=int, default=None, help='Ending rank')
    parser.add_argument('--input', type=str, default='players_data_light-2024_2025.csv', help='Input CSV file')
    parser.add_argument('--output', type=str, default='players.csv', help='Output CSV file')
    parser.add_argument('--delay', type=int, default=10, help='Delay between requests in seconds')
    parser.add_argument('--skip-existing', action='store_true', help='Skip entries that already exist in the output file')
    parser.add_argument('--diagnose', nargs='+', type=int, help='Specific ranks to diagnose')
    
    args = parser.parse_args()
    
    # Special diagnostic for specific ranks
    if args.diagnose:
        safe_log(f"Running diagnostic for ranks: {args.diagnose}")
        df_main = pd.read_csv(args.input)
        for rank in args.diagnose:
            try:
                player = df_main[df_main['Rk'] == rank].iloc[0]
                safe_log(f"DIAGNOSTIC - Rank {rank}: {player['Player']} from {player['Squad']}")
                
                # Check if this entry is in the output file
                if os.path.exists(args.output):
                    with open(args.output, 'r', newline='', encoding='utf-8') as file:
                        reader = csv.reader(file)
                        for row in reader:
                            if row and len(row) > 0 and row[0].isdigit() and int(row[0]) == rank:
                                safe_log(f"  Found in output file: {row}")
                                break
                        else:
                            safe_log(f"  Not found in output file")
                
                # Try the search with our improved function
                safe_log(f"  Testing search for this player...")
                url = find_zerozero_url(player['Player'], player['Squad'])
                safe_log(f"  Search result: {url}")
                
                if url and "zerozero.pt" in url:
                    safe_log(f"  Testing photo URL extraction...")
                    photo_url = get_player_photo_url_by_profile_page(url)
                    safe_log(f"  Photo URL: {photo_url}")
            except Exception as e:
                safe_log(f"  Error during diagnosis: {str(e)}", 'error')
    
    df_main = pd.read_csv(args.input)
    output_file = args.output
    
    # Load existing entries to avoid duplication
    complete_entries = set()
    incomplete_entries = []
    if args.skip_existing:
        complete_entries, incomplete_entries = load_existing_entries(output_file)
        
        # Queue ALL incomplete entries for retrying, regardless of URL type
        for rk, name, website_url in incomplete_entries:
            safe_log(f"Queueing existing entry with missing photo: {name} (Rank: {rk})")
            
            # Get club from dataframe for consistency
            try:
                club = df_main.loc[df_main['Rk'] == rk, 'Squad'].iloc[0]
            except (IndexError, KeyError):
                club = ""  # Default if not found in dataframe
                
            # If URL is not from zerozero, pass empty URL to force new search
            if not website_url or "zerozero.pt" not in website_url:
                safe_log(f"Entry has non-zerozero URL or missing URL, will search for new URL: {name}")
                retry_queue.put((rk, name, club, ""))  # Empty URL to trigger new search
            else:
                # Use existing zerozero URL
                retry_queue.put((rk, name, club, website_url))
    
    safe_log(f"Starting scraping from rank {args.start}" + 
             (f" to {args.end}" if args.end else " to end") +
             (f" (skipping {len(complete_entries)} complete entries, retrying {len(incomplete_entries)} incomplete entries)" if args.skip_existing else ""))
    
    # Start the retry scheduler
    scheduler_thread = setup_retry_scheduler(output_file)
    
    with open(output_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Uncomment if you need to write headers
        # writer.writerow(["Rk", "Player", "UrlWebsite", "UrlPhoto"])

        for index, row in df_main.iterrows():
            rk = row['Rk']
            
            # Skip if not in range
            if rk < args.start:
                continue
            if args.end and rk >= args.end:
                break
            
            # Only skip if the entry is complete (has valid photo URL)
            # Don't skip entries that need retrying
            if args.skip_existing and rk in complete_entries:
                safe_log(f"Skipping rank {rk} as it already has a complete entry")
                continue
                
            name = row['Player']
            club = row['Squad']
            
            # Check if this entry is already in the retry queue
            retry_items = list(retry_queue.queue)
            is_queued = any(item[0] == rk for item in retry_items)
            
            if is_queued:
                safe_log(f"Skipping rank {rk} as it's already in the retry queue")
                continue
                
            success = process_player(rk, name, club, writer, file)
            
            # Only delay if the request was successful
            if success:
                # Add to complete entries set to track what we've processed
                complete_entries.add(rk)
                safe_log(f"Sleeping for {args.delay} seconds", 'debug')
                time.sleep(args.delay)
    
    # Process any remaining items in retry queue
    if not retry_queue.empty():
        safe_log("Final processing of retry queue")
        process_retry_queue(output_file)
    
    safe_log("Scraping completed")

if __name__ == "__main__":
    main()