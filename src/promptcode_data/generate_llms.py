import os
import time
import argparse
import requests # Import requests
from urllib.parse import urlparse
# No datetime needed for this version
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

def crawl_and_save_markdown(api_key: str, url: str, output_path: str | None = None, crawl_limit: int = 10, poll_interval: int = 5):
    """
    Crawls using Firecrawl's async crawl, polls status via direct HTTP requests
    to potentially get real-time page updates, extracts markdown, and saves it.
    Args:
        api_key: Firecrawl API key.
        url: Target URL.
        output_path: Output file path. Defaults to content/raw/google_adk/full_llms.txt.
        crawl_limit: Max pages (default: 10).
        poll_interval: Polling interval (seconds, default: 5).
    """
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable not set.")

    # Determine and create output path
    if not output_path:
        output_dir = "content/raw/google_adk"
        output_filename = "full_llms.txt"
        output_path = os.path.join(output_dir, output_filename)
    else:
        output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = "."

    print(f"Initializing FirecrawlApp...")
    firecrawl = FirecrawlApp(api_key=api_key)

    crawl_params = {
        'limit': crawl_limit,
        'scrapeOptions': {
            'formats': ['markdown']
        }
    }

    print(f"Starting crawl job for: {url} (limit: {crawl_limit}, format: markdown)...")
    job_id = None
    try:
        start_response = firecrawl.async_crawl_url(url=url, params=crawl_params)
        if not start_response or not start_response.get('success') or not start_response.get('id'):
            print(f"Failed to start crawl job. Response: {start_response}")
            return
        job_id = start_response['id']
        print(f"Crawl job started successfully. Job ID: {job_id}")
    except Exception as e:
        print(f"Error starting crawl job: {e}")
        return

    print(f"Polling job status every {poll_interval} seconds...")
    last_reported_completed = -1
    printed_urls = set() # Keep track of URLs printed in real-time
    final_data = [] # Store final data list on completion

    status_url = f'{firecrawl.api_url}/v1/crawl/{job_id}'
    headers = firecrawl._prepare_headers() # Get headers from the app instance

    while True:
        try:
            # Direct HTTP GET request to the status endpoint
            response = requests.get(status_url, headers=headers, timeout=30)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            status_result = response.json()

            if not status_result:
                print("Warning: Received empty status JSON. Retrying...")
                time.sleep(poll_interval)
                continue

            current_status = status_result.get('status', 'unknown')
            completed_count = status_result.get('completed')
            total_count = status_result.get('total')

            # Print overall progress
            should_print_status = (completed_count is not None and completed_count != last_reported_completed) or \
                                  current_status in ['completed', 'failed', 'cancelled', 'error']
            if should_print_status:
                status_parts = [f"Status: {current_status}"]
                if completed_count is not None:
                    progress = f"Pages completed: {completed_count}"
                    if total_count is not None:
                        progress += f" / {total_count}"
                    status_parts.append(progress)
                    last_reported_completed = completed_count
                print(", ".join(status_parts))

            # --- Real-time URL printing (if data is present) ---
            intermediate_data = status_result.get('data')
            if isinstance(intermediate_data, list):
                new_urls_found = False
                for item in intermediate_data:
                    metadata = item.get('metadata', {})
                    source_url = metadata.get('sourceURL')
                    if source_url and source_url not in printed_urls:
                        if not new_urls_found:
                             print("  Real-time discovered pages:")
                             new_urls_found = True
                        printed_urls.add(source_url)
                        print(f"    - {source_url}")
            # --- End of Real-time URL printing ---

            # Handle final states
            if current_status == 'completed':
                print("\nCrawl completed.")
                # Re-fetch final status to ensure pagination is handled if necessary
                # (The SDK's check_crawl_status handles pagination, so let's use it here)
                try:
                    final_status_result = firecrawl.check_crawl_status(job_id)
                    if final_status_result.get('success') and 'data' in final_status_result:
                        final_data = final_status_result['data']
                    else:
                        print("Warning: Could not retrieve final paginated data using SDK's check_crawl_status.")
                        print(f"Using data from last poll: {status_result.get('data')}")
                        final_data = status_result.get('data', []) # Fallback to last polled data
                except Exception as check_e:
                     print(f"Error during final status check with SDK: {check_e}")
                     print(f"Using data from last poll: {status_result.get('data')}")
                     final_data = status_result.get('data', []) # Fallback

                if final_data:
                    all_markdown = []
                    successful_pages = 0
                    final_crawled_urls = []

                    print("\nProcessing final crawled pages:")
                    for item in final_data:
                        markdown = item.get('markdown')
                        metadata = item.get('metadata', {})
                        source_url = metadata.get('sourceURL', 'Unknown URL')
                        if markdown:
                            final_crawled_urls.append(source_url)
                            all_markdown.append(f"# Source URL: {source_url}\n\n{markdown}\n\n---\n\n")
                            successful_pages += 1
                        # No need to print warnings again, printed during polling

                    if not all_markdown:
                        print("Error: Final data processed, but no markdown content was extracted.")
                        break

                    print(f"\nFinal list of pages with extracted markdown ({successful_pages} total):")
                    for i, success_url in enumerate(final_crawled_urls):
                        print(f"  {i+1}. {success_url}")

                    print(f"\nSaving combined markdown content to: {output_path}")
                    try:
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write("".join(all_markdown))
                        print("File saved successfully.")
                    except IOError as e:
                        print(f"Error writing file {output_path}: {e}")
                else:
                    print("Crawl job reported completed, but no final data could be retrieved or processed.")
                break # Exit loop on completion

            elif current_status in ['failed', 'cancelled', 'error']:
                print(f"\nCrawl job ended with status: {current_status}")
                print(f"Error details: {status_result.get('error', 'No details provided')}")
                break

            elif current_status in ['active', 'paused', 'pending', 'queued', 'waiting', 'scraping']:
                pass # Continue polling
            else:
                print(f"\nUnknown status received: {current_status}. Stopping.")
                break

        except requests.exceptions.RequestException as http_err:
            print(f"\nHTTP Error during status check: {http_err}")
            print("Retrying after delay...")
        except KeyboardInterrupt:
            print("\nPolling interrupted by user.")
            raise
        except Exception as e:
            print(f"\nError during status check/processing: {e}")
            print("Retrying after delay...")

        time.sleep(poll_interval)

# --- Main Execution Block --- #
if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Crawl using Firecrawl polling (direct HTTP), save markdown.")
    parser.add_argument("url", help="Starting URL.")
    parser.add_argument("-o", "--output", help="Output file path.", default=None)
    parser.add_argument("--max-pages", type=int, help="Max pages to crawl.", default=10)
    parser.add_argument("--poll-interval", type=int, help="Polling interval (seconds).", default=5)
    args = parser.parse_args()

    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        print("Error: FIRECRAWL_API_KEY needed.")
        exit(1)

    try:
        crawl_and_save_markdown(
            api_key=api_key,
            url=args.url,
            output_path=args.output,
            crawl_limit=args.max_pages,
            poll_interval=args.poll_interval
        )
    except KeyboardInterrupt:
         print("\nOperation cancelled by user.")
         exit(130)
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)