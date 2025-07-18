import subprocess
import os
import time
import json

# CONFIG
NUM_BATCHES = 10
GAMES_PER_BATCH = 8
REPLAYS_DIR = "replays"

def run_game_and_wait():
    """
    Starts main.py and waits until 8 replays are created.
    Assumes replay saving is turned on by default in your project.
    """
    process = subprocess.Popen(["python", "main.py"])

    while True:
        # Wait a bit before checking
        time.sleep(5)
        replay_files = [f for f in os.listdir(REPLAYS_DIR) if f.endswith(".json")]
        if len(replay_files) >= GAMES_PER_BATCH:
            break

    # Kill the game process
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()

def count_wins_and_clean():
    """
    Reads replay files, counts wins, deletes files.
    Returns (x_wins, o_wins)
    """
    x_wins = 0
    o_wins = 0
    replay_files = [f for f in os.listdir(REPLAYS_DIR) if f.endswith(".json")]

    for filename in replay_files:
        filepath = os.path.join(REPLAYS_DIR, filename)
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                winner = data.get("metadata", {}).get("winner")
                if winner == "X":
                    x_wins += 1
                elif winner == "O":
                    o_wins += 1
        except Exception as e:
            print(f"Error reading {filename}: {e}")

        # Delete the file
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"Error deleting {filename}: {e}")

    return x_wins, o_wins

def main():
    total_x_wins = 0
    total_o_wins = 0

    for batch in range(NUM_BATCHES):
        print(f"\n🕹️ Starting batch {batch+1}/{NUM_BATCHES}...")

        run_game_and_wait()

        x_wins, o_wins = count_wins_and_clean()
        total_x_wins += x_wins
        total_o_wins += o_wins

        print(f"Batch {batch+1} results: X won {x_wins} times, O won {o_wins} times.")

    print("\n✅ FINAL RESULTS after 80 games:")
    print(f"X won: {total_x_wins} times")
    print(f"O won: {total_o_wins} times")

if __name__ == "__main__":
    main()
