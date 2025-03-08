import sqlite3
import time

def fetch_instagram_following(username):
    # Simulate scraping (Replace this with real Selenium or Playwright logic)
    return [f"{username}_friend1", f"{username}_friend2"]

def scrape_following():
    conn = sqlite3.connect("ig_tracker.db")
    cursor = conn.cursor()

    # Get all tracked usernames
    cursor.execute("SELECT DISTINCT username FROM following")
    users = cursor.fetchall()

    for user in users:
        username = user[0]
        following_list = fetch_instagram_following(username)
        
        for follow in following_list:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO following VALUES (?, ?)", (follow, timestamp))
            conn.commit()

    conn.close()

# Run scraper every hour (replace with cron job in production)
if __name__ == "__main__":
    while True:
        scrape_following()
        time.sleep(3600)  # Run every hour
