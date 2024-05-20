import os
from supabase import create_client, Client
from dotenv import load_dotenv
import requests
from datetime import datetime

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)


def convert_score_to_seconds(score):
    try:
        minutes, seconds = score.split(":")
        total_seconds = int(minutes) * 60 + float(seconds)
        return total_seconds
    except ValueError:
        return float(score)


def fetch_data(api_url):
    response = requests.get(api_url)
    response.raise_for_status()
    return response.json()['records']

def add_participants(records):
    participants = set(record['participant'] for record in records)
    for participant in participants:
        response = supabase.table('participants').select('id', 'username').eq('username', participant).execute()
        if response.data:
            print(f"Participant already exists: {participant}")
            continue
        response = supabase.table('participants').insert({"username": participant}).execute()
        print(f"Added participant: {participant}, Response: {response}")

def insert_records(records, category):
    participant_response = supabase.table('participants').select('id', 'username').execute()
    participant_map = {participant['username']: participant['id'] for participant in participant_response.data}
    print(f"Participant map: {participant_map}")

    for record in records:
        participant_name = record['participant']
        if participant_name not in participant_map:
            print(f"Participant not found in map: {participant_name}")
            continue
        participant_id = participant_map[participant_name]
        score_in_seconds = convert_score_to_seconds(record['score'])
        
        # Check for existing record with the same date and category
        existing_record_response = supabase.table('records').select('score').eq('participant_id', participant_id).eq('date', record['date']).eq('category', category).execute()
        if existing_record_response.data:
            existing_score = existing_record_response.data[0]['score']
            if existing_score == score_in_seconds:
                print(f"Record already exists with the same score for participant {participant_name} on date {record['date']}")
                continue

        response = supabase.table('records').insert({
            "participant_id": participant_id,
            "position": record['position'],
            "date": record['date'],
            "score": score_in_seconds,
            "category": category
        }).execute()
        print(f"Inserted record for participant {participant_name}, Response: {response}")


def get_all_stats_username(username):
    response = supabase.table('participants').select('id').eq('username', username).execute()
    if not response.data:
        return None
    participant_id = response.data[0]['id']
    response = supabase.table('records').select('position', 'date', 'score', 'category').eq('participant_id', participant_id).execute()
    return response.data



def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def search_all_similar_usernames(username, threshold=2):
    # Retrieve all usernames
    response = supabase.table('participants').select('username').execute()
    
    if not response.data:
        return []

    usernames = [record['username'] for record in response.data]

    # Calculate Levenshtein distance and partial match
    similar_usernames = []
    for name in usernames:
        distance = levenshtein_distance(username.lower(), name.lower())
        if username.lower() in name.lower() or distance <= threshold:
            similar_usernames.append((name, distance))
    
    # Sort by similarity (lower distance is more similar)
    similar_usernames.sort(key=lambda x: x[1])
    
    # Return only the usernames
    return [name for name, distance in similar_usernames]


def getBestScoreUsername(username, category):
    response = supabase.table('participants').select('id').eq('username', username).execute()
    if not response.data:
        return None
    participant_id = response.data[0]['id']
    response = supabase.table('records').select('position', 'date', 'score', 'category').eq('participant_id', participant_id).eq('category', category).execute()
    return response.data


def getTotalDrivers(category):
    response = supabase.table('records').select('participant_id').eq('category', category).execute()
    return len(response.data)

def getFirstPlace(category):
    response = supabase.table('records').select('score').eq('category', category).order('score').execute()
    return response.data[0]

def getLastPlace(category):
    response = supabase.table('records').select('score').eq('category', category).order('score', ascending=False).execute()
    return response.data[0]


def detailedUserStats(username):
    categories = ['kids', 'normal', 'adults']
    stats = {
        "all_records": []
    }
    
    for category in categories:
        
        bestScore = getBestScoreUsername(username, category)
        
        print(bestScore)
        
        record_count = 0
        records = []
        
        for record in bestScore:
            date = float(record['score'])

            date = record['date']
            formatted_date = date.split("T")[0]
            date_object = datetime.strptime(formatted_date, '%Y-%m-%d')
            day_of_week = date_object.strftime('%A')
            
            print(getTotalDrivers(category))

            player_top_percentage = getTotalDrivers(category) / record['position'] * 100

            percentage_to_beat_first = (record['score'] - getFirstPlace(category)['score']) / getFirstPlace(category)['score'] * 100

            seconds_to_beat_first = record['score'] - getFirstPlace(category)['score']

            label = ""
            if player_top_percentage >= 80:
                label = "Newbie"
            elif player_top_percentage >= 60:
                label = "Beginner"
            elif player_top_percentage >= 40:
                label = "Amateur"
            elif player_top_percentage >= 20:
                label = "Pro"
            elif player_top_percentage >= 10:
                label = "Epic"
            elif player_top_percentage >= 1:
                label = "Legendary"
            else:
                label = "Track Owner"

            seconds_to_beat_first = f"{abs(seconds_to_beat_first):.3f}"
            player_top_percentage = f"{player_top_percentage:.2f}"
            position = record['position']
            formatted_date = formatted_date
            score = record['score']
            participant = username
            percentage_to_beat_first = f"{percentage_to_beat_first:.2f}"

            records.append({
                "label": label,
                "seconds_to_beat_first": seconds_to_beat_first,
                "player_top_percentage": player_top_percentage,
                "position": position,
                "date": formatted_date,
                "score": score,
                "participant": participant,
                "percentage_to_beat_first": percentage_to_beat_first,
                "day_of_week": day_of_week
            })
            
            record_count += 1
        
        stats["all_records"].append({
            category: records
        })
        
    return stats
