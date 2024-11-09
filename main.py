import pandas as pd

# Load the alliance, requirements, and names_map CSV files
try:
    df_alliance = pd.read_csv('alliance.csv')  # The main alliance data
    df_requirements = pd.read_csv('requirements.csv')  # The requirements file
    df_names_map = pd.read_csv('names_map.csv')  # The character name mapping file
except FileNotFoundError:
    print("Error: One or more CSV files were not found. Please make sure 'alliance.csv', 'requirements.csv', and 'names_map.csv' are in the same directory.")
    exit()
except pd.errors.EmptyDataError:
    print("Error: One or more CSV files are empty.")
    exit()

# Create a dictionary to map clean names to unclean character IDs
names_map = {row['clean_name'].lower(): row['character_id'].lower() for _, row in df_names_map.iterrows()}

# Convert the character_name column in df_requirements to character_id using names_map
df_requirements['character_id'] = df_requirements['character_name'].str.lower().map(names_map)

# Create a dictionary to store requirements based on day and mission
requirements = {}

# Parse the requirements CSV into a structured dictionary
for _, row in df_requirements.iterrows():
    character_id = row['character_id']
    day = row['day']
    mission = row['mission']
    star_type = row['star_type'].upper()  # R/Y/G for Red Stars, Yellow Stars, and Gear Tier
    level = row['level']

    if day not in requirements:
        requirements[day] = {}
    if mission not in requirements[day]:
        requirements[day][mission] = []

    requirements[day][mission].append({
        "character_id": character_id,
        "star_type": star_type,
        "level": level
    })

def process_assignments(day: int):
    """Prints out the weakest characters that meet requirements for assignments on a specific numeric day."""
    if day not in requirements:
        print("Invalid day provided. Please choose a valid day number (1-5).")
        return

    assignment_count = {player: 0 for player in df_alliance['Name'].unique()}

    print(f"\nAssignments for Day {day}")

    # Process all missions for the specified day
    for mission, tasks in requirements[day].items():
        print(f"\nMission {mission}:")

        for task in tasks:
            character_id = task["character_id"]
            star_type = task["star_type"]
            level = task["level"]

            # Filter characters based on star type, gear tier, and level
            if star_type == 'R':
                filtered_df = df_alliance[
                    (df_alliance['Character Id'].str.lower() == character_id) & (df_alliance['Red Stars'] >= level)]
            elif star_type == 'Y':
                filtered_df = df_alliance[
                    (df_alliance['Character Id'].str.lower() == character_id) & (df_alliance['Stars'] >= level)]
            elif star_type == 'G':
                filtered_df = df_alliance[
                    (df_alliance['Character Id'].str.lower() == character_id) & (df_alliance['Gear Tier'] >= level)]
            else:
                print(f"Unknown star type {star_type} for character {character_id}. Please check the requirements.")
                continue

            # Gather all players who meet the requirement for this character and mission
            matching_players = []
            for index, row in filtered_df.iterrows():
                # Check if the player has already assigned 10 toons
                player = row['Name']
                if assignment_count[player] < 10:
                    matching_players.append(row)
                    #assignment_count[player] += 1

            # Sort the players by their Power (ascending)
            matching_players_sorted = sorted(matching_players, key=lambda x: x['Power'])

            # Now select the weakest 5 (or fewer if we don't have 5)
            selected_players = matching_players_sorted[:5]

            # Print results for this character with clean names
            print(f"\n  {names_map.get(character_id, character_id)} ({star_type} Stars >= {level}):")
            if selected_players:
                for row in selected_players:
                    # Print the player's name, power, and the corresponding star or gear tier column
                    if star_type == 'R':
                        print(f"    {row['Name']} - Power: {row['Power']}, Red Stars: {row['Red Stars']}")
                    elif star_type == 'Y':
                        print(f"    {row['Name']} - Power: {row['Power']}, Yellow Stars: {row['Stars']}")
                    elif star_type == 'G':
                        print(f"    {row['Name']} - Power: {row['Power']}, Gear Tier: {row['Gear Tier']}")
            else:
                print("    No eligible players found for this character.")

            # Fill remaining slots with "Unable to fill" if fewer than 5 members were assigned
            if len(selected_players) < 5:
                missing_slots = 5 - len(selected_players)
                print("    " + "**Unable to fill**\n" * missing_slots)


# Ask user to specify a day
try:
    day = int(input("Enter the day number (1-5) for assignments: "))
    process_assignments(day)
except ValueError:
    print("Invalid input. Please enter a numeric day value (1-5).")
