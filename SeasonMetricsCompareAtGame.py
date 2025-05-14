import os
import time
import yaml
import fcntl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from pybaseball import cache, schedule_and_record
from atproto import Client

# Global constants
TOTAL_GAMES_MODERN = 162  # Total number of games in a modern season
TOTAL_GAMES_OLDEN = 154   # Total number of games in an olden season
OAK_2023_DIFF = -339      # Run differential for the 2023 OAK season
BOS_1932_DIFF = -349      # Run differential for the 1932 BOS season

# Replace YAML file paths with environment variable lookups
LOCK_FILE = "process.lock"
CONFIG_FILE = os.getenv("CONFIG_FILE_PATH", "config.yaml")
SECRETS_FILE = os.getenv("SECRETS_FILE_PATH", "secrets.yaml")

def acquire_lock():
    """Acquire a lock to prevent concurrent execution."""
    lock = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("Another instance is running. Exiting.")
        exit(1)
    return lock

def release_lock(lock):
    """Release the lock."""
    fcntl.flock(lock, fcntl.LOCK_UN)
    lock.close()

def load_yaml(file_path):
    """Load a YAML file."""
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

def save_yaml(data, file_path):
    """Save data to a YAML file."""
    with open(file_path, "w") as file:
        yaml.safe_dump(data, file)

def get_wins(record):
    """Extract the number of wins from a baseball record string."""
    return int(record.split('-')[0])

def get_wins_after_games(team_season_data, games_played):
    """Calculate the number of wins after a specified number of games."""
    if games_played < 1 or games_played > 162:
        return 0
    record = team_season_data.loc[games_played, 'W-L']
    return get_wins(record)

def get_season_games_played(team_season_data):
    """Get the number of games played in a season."""
    return len([record for record in team_season_data['W-L'] if record != None])

def generate_plot(teamA, yearA, teamB, yearB, games_played, the_last, this_time, colorA='red', colorB='blue'):
    """Generate a step line plot comparing two seasons."""
    x = np.arange(1, games_played + 1)
    y1 = [get_wins_after_games(the_last, i) for i in x]
    y2 = [get_wins_after_games(this_time, i) for i in x]

    plt.figure(figsize=(8, 8))
    plt.step(x, y1, label=f"{teamA} {yearA} Season", where='mid', color=colorA)
    plt.step(x, y2, label=f"{teamB} {yearB} Season", where='mid', color=colorB)
    plt.xlabel('Games Played')
    plt.xlim(1, games_played)
    plt.ylabel('Wins')
    plt.ylim(0, max(max(y1), max(y2)) + 1)
    plt.title(f"Wins Comparison: {teamA} {yearA} vs {teamB} {yearB} Seasons")
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.gca().set_aspect('equal', adjustable='box')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    raw_image_data = buffer.getvalue()
    buffer.close()
    plt.close()

    return raw_image_data, y1[-1], y2[-1]

def generate_chart(year, team, diff_data, games_played):
    """
    Generate a chart image showing a table of calculated metrics for a given team's season data.

    Args:
        diff_data (DataFrame): The DataFrame containing the team's season data.
        games_played (int): The number of games played so far.

    Returns:
        bytes: The chart image data as raw bytes.
    """
    # Calculate metrics
    run_diff = diff_data.loc[games_played, 'R'] - diff_data.loc[games_played, 'RA']
    run_diff_per_game = run_diff / games_played
    games_remaining_modern = TOTAL_GAMES_MODERN - games_played
    games_remaining_olden = TOTAL_GAMES_OLDEN - games_played
    run_diff_per_game_modern_record = (OAK_2023_DIFF - run_diff) / games_remaining_modern
    run_diff_per_game_olden_record = (BOS_1932_DIFF - run_diff) / games_remaining_olden
    run_diff_per_game_olden_record_modern_games = (BOS_1932_DIFF - run_diff) / games_remaining_modern
    current_wins = get_wins_after_games(diff_data, games_played)
    current_win_percentage = current_wins / games_played
    pythagorean_win_percentage = (diff_data.loc[games_played, 'R'] ** 2) / ((diff_data.loc[games_played, 'R'] ** 2 + diff_data.loc[games_played, 'RA'] ** 2))
    pythagorean_wins = pythagorean_win_percentage * games_played
    pythagorean_win_percentage_br = (diff_data.loc[games_played, 'R'] ** 1.83) / ((diff_data.loc[games_played, 'R'] ** 1.83) + (diff_data.loc[games_played, 'RA'] ** 1.83))
    pythagorean_wins_br = pythagorean_win_percentage_br * games_played

    # Create a DataFrame to organize the data
    data = {
        "Metric": [
            "RD/G",
            "RD/G, match 2023OAK",
            "RD/G, match 1932BOS",
            "(154) RD/G, match 1932BOS",
            "G Remaining 162",
            "G Remaining 154",
            "",
            "Actual W%",
            "Actual W",
            "Pythag W%",
            "Pythag W",
            "Pythag W% (BR)",
            "Pythag W (BR)"
        ],
        "Value": [
            round(run_diff_per_game, 4),
            round(run_diff_per_game_modern_record, 4),
            round(run_diff_per_game_olden_record, 4),
            round(run_diff_per_game_olden_record_modern_games, 4),
            f"{int(games_remaining_modern)}",
            int(games_remaining_olden),
            "",
            round(current_win_percentage, 4),
            int(current_wins),
            round(pythagorean_win_percentage, 4),
            round(pythagorean_wins, 4),
            round(pythagorean_win_percentage_br, 4),
            round(pythagorean_wins_br, 4)
        ],
        "Total": [
            f"{int(run_diff)}",
            OAK_2023_DIFF,
            BOS_1932_DIFF,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]
    }
    df = pd.DataFrame(data)

    # Dynamically adjust the figure size based on the number of rows
    num_rows = len(df)
    fig_width = max(8, num_rows * 0.5)  # Minimum width of 8, expand by 0.5 per row
    fig, ax = plt.subplots(figsize=(fig_width, 8))  # Adjust figure size for better canvas fit

    ax.axis('tight')
    ax.axis('off')
    ax.set_title(f"{year} {team} RunDiff Metrics", fontsize=20)
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center', bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(16)
    table.auto_set_column_width(col=list(range(len(df.columns))))

    # Right-align the first column
    for (row, col), cell in table.get_celld().items():
        if col == 0:  # First column
            cell.set_text_props(ha='right')  # Set horizontal alignment to 'right'

    # Save the table as an image in a BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    raw_image_data = buffer.getvalue()
    buffer.close()
    plt.close()

    return raw_image_data, run_diff, current_win_percentage, pythagorean_win_percentage, pythagorean_win_percentage_br

def post_plot_to_bluesky(client, teamA, yearA, teamB, yearB, games_played, y1_last, y2_last, raw_image_data, colorA='red', colorB='blue'):
    """Post the comparison plot to Bluesky."""
    if y1_last > y2_last:
        # It's worse. Shit.
        bluesky_post = (
            f"With {games_played} game(s) in the books, the {teamB} {yearB} season is somehow worse at {y2_last} wins,"
            f"behind the {teamA} {yearA} season by {y1_last - y2_last} win(s)."
            "\n\n"
            "No 'could always be' worse here. It *is* worse at this point."
        )
    elif y1_last < y2_last:
        # It's better. For now.
        bluesky_post = (
            f"Through {games_played} game(s) played, the {teamB} {yearB} season is ahead with {y2_last} wins, "
            f"above the {teamA} {yearA} season by {y2_last - y1_last} win(s)."
            "\n\n"
            "The grass, for now, is greener here. It could always be worse."
        )
    else:
        # It's not worse, but it's not better
        bluesky_post = (
            f"After {games_played} game(s), the {teamB} {yearB} season isn't better than the {teamA} {yearA} season at {y1_last} win(s) each."
            "\n\n"
            "But it also isn't worse."
        )

    image_alt_text = (
        f"A step line plot comparing the wins of the {teamA} {yearA} season and the {teamB} {yearB} season. "
        f"The x-axis represents the number of games played (1 to {games_played}), and the y-axis represents the number of wins. "
        f"The {teamA} {yearA} season is shown in {colorA}, and the {teamB} {yearB} season is shown in {colorB}. "
        f"After {games_played} games, the {teamA} {yearA} season has {y1_last} wins, while the {teamB} {yearB} season has {y2_last} wins."
    )
    client.send_image(text=bluesky_post, image=raw_image_data, image_alt=image_alt_text)

def post_chart_to_bluesky(client, team, year, games_played, raw_image_data, run_diff, current_win_percentage, pythagorean_win_percentage, pythagorean_win_percentage_br):
    """Post the run differential chart to Bluesky."""
    bluesky_post = (
        f"After {int(games_played)} game(s), the {team} {year} season has a run differential of {int(run_diff)}."
        "\n\n"
        f"The current W% is {current_win_percentage:.4f},\n"
        f"Pythagorean W% is {pythagorean_win_percentage:.4f}, and\n"
        f"Pythagorean W% (BRef) is {pythagorean_win_percentage_br:.4f}."
    )
    image_alt_text = (
        f"A table showing various metrics for the {team} {year} season. "
        f"The table includes run differential, games remaining, and Pythagorean win percentage"
        f"using regular (2) & baseball-reference.com's (1.83) exponent values)."
    )
    client.send_image(text=bluesky_post, image=raw_image_data, image_alt=image_alt_text)

def main():
    # Acquire lock
    lock = acquire_lock()
    # We're in. Enable cache
    cache.enable()
    
    try:
        # Load configuration and secrets
        config = load_yaml(CONFIG_FILE)
        secrets = load_yaml(SECRETS_FILE)

        # Initialize Bluesky client
        client = Client()
        client.login(secrets['bluesky']['username'], secrets['bluesky']['password'])

        # Process each team-year pair
        for pair in config['pairs']:
            teamA = pair['teamA']
            yearA = pair['yearA']
            colorA = pair['colorA']
            teamB = pair['teamB']
            yearB = pair['yearB']
            colorB = pair['colorB']
            games_played = pair['games_played']

            # Fetch data
            the_last = schedule_and_record(yearA, teamA)
            this_time = schedule_and_record(yearB, teamB)

            # Increment for a new games_played
            games_played += 1

            # Check if games_played is within each data's range
            if games_played < 1 or games_played > get_season_games_played(the_last) or games_played > get_season_games_played(this_time):
                print(f"Pairs: Games played {games_played} is out of range for {teamA} {yearA} or {teamB} {yearB}.")
                continue

            # Generate plot
            raw_image_data, y1_last, y2_last = generate_plot(teamA, yearA, teamB, yearB, games_played, the_last, this_time, colorA, colorB)

            # Post to Bluesky
            post_plot_to_bluesky(client, teamA, yearA, teamB, yearB, games_played, y1_last, y2_last, raw_image_data, colorA, colorB)

            # Sleep for 10 seconds to avoid rate limits
            time.sleep(10)

            # Increment games played
            pair['games_played'] += 1

        # Process each run differential team
        for diff in config['diffs']:
            team = diff['team']
            year = diff['year']
            games_played = diff['games_played']

            # Fetch data
            diff_data = schedule_and_record(year, team)

            # Increment for a new games_played
            games_played += 1

            # Check if games_played is within the data's range
            if games_played < 1 or games_played > get_season_games_played(diff_data):
                print(f"Diffs: Games played {games_played} is out of range for {team} {year}.")
                continue

            # Generate chart
            raw_image_data, run_diff, current_win_percentage, pythagorean_win_percentage, pythagorean_win_percentage_br = generate_chart(year, team, diff_data, games_played)

            # Pass the calculated metrics to the function
            post_chart_to_bluesky(
                client,
                team,
                year,
                games_played,
                raw_image_data,
                run_diff,
                current_win_percentage,
                pythagorean_win_percentage,
                pythagorean_win_percentage_br
            )
            
            # Sleep for 10 seconds to avoid rate limits
            time.sleep(10)

            # Increment games played
            diff['games_played'] += 1

        # Save updated configuration
        save_yaml(config, CONFIG_FILE)

    finally:
        # Release lock
        release_lock(lock)

if __name__ == "__main__":
    main()