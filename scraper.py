import re
from playwright.sync_api import sync_playwright

def get_team_id(team_name):
    """Helper to find team ID from a search page (simplified example)"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.flashscore.com/")
        
        # Search for team
        page.fill('input[name="q"]', team_name)
        page.keyboard.press("Enter")
        
        # Wait for results
        try:
            page.wait_for_selector('.table-container', timeout=5000)
        except:
            browser.close()
            return None
            
        # Extract first match link
        link = page.query_selector('a[href*="/team/"]').get_attribute('href')
        browser.close()
        
        if link:
            # Extract ID from URL like /team/manchester-united/abc123/
            parts = link.split('/')
            for part in parts:
                if len(part) == 6 or len(part) == 8: # Typical ID length
                    return part
        return None

def scrape_last_5_matches(team_url):
    """Scrapes the last 5 matches from a specific team's page on Flashscore"""
    matches = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Assuming team_url is something like 'manchester-united'
        url = f"https://www.flashscore.com/team/{team_url}/"
        page.goto(url)
        
        # Wait for match history to load
        try:
            page.wait_for_selector('.match-row', timeout=10000)
        except:
            browser.close()
            return []

        # Scrape last 5 matches
        rows = page.query_selector_all('.match-row')[:5]
        
        for row in rows:
            try:
                date = row.locator('.date').inner_text().strip()
                opponent = row.locator('.name').inner_text().strip()
                result = row.locator('.result').inner_text().strip()
                
                # Parse score e.g., "2:1"
                scores = re.findall(r'\d+', result)
                if len(scores) >= 2:
                    goals_scored = int(scores[0])
                    goals_conceded = int(scores[1])
                    
                    # Determine if home or away based on URL context or additional selectors
                    # Simplified: assume all scraped are relevant
                    matches.append({
                        'date': date,
                        'opponent': opponent,
                        'goals_scored': goals_scored,
                        'goals_conceded': goals_conceded,
                        'venue': 'Home' if 'home' in row.get_attribute('class') else 'Away'
                    })
            except Exception as e:
                continue
                
        browser.close()
    
    return matches

def fetch_stats_for_team(team_name):
    """Main function to get stats for a team"""
    # Step 1: Get Team ID/URL
    team_id = get_team_id(team_name)
    if not team_id:
        return None
        
    # Step 2: Scrape Matches
    matches = scrape_last_5_matches(team_id)
    
    # Step 3: Calculate Averages
    if not matches:
        return None
        
    total_scored = sum(m['goals_scored'] for m in matches)
    total_conceded = sum(m['goals_conceded'] for m in matches)
    
    avg_scored = total_scored / 5
    avg_conceded = total_conceded / 5
    
    return {
        'team': team_name,
        'matches': matches,
        'avg_goals_scored': round(avg_scored, 2),
        'avg_goals_conceded': round(avg_conceded, 2)
    }