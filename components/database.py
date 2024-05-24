import os
from supabase import create_client, Client
from dotenv import load_dotenv
import requests
from datetime import datetime
import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash


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
    # Retrieve all usernames and their availability
    response = supabase.table('participants').select('username', 'username_availability').execute()
    
    if not response.data:
        return []

    # Extract usernames and availability
    usernames = [(record['username'], record['username_availability']) for record in response.data]

    # Calculate Levenshtein distance and partial match
    similar_usernames = []
    for name, availability in usernames:
        distance = levenshtein_distance(username.lower(), name.lower())
        if username.lower() in name.lower() or distance <= threshold:
            similar_usernames.append((name, availability, distance))
    
    # Sort by similarity (lower distance is more similar)
    similar_usernames.sort(key=lambda x: x[2])
    
    # Return the list of tuples containing username and availability
    return [(name, availability) for name, availability, distance in similar_usernames]


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
    stats = {"all_records": {}}
    
    for category in categories:
        bestScore = getBestScoreUsername(username, category)
        first_place = getFirstPlace(category)
        total_drivers = getTotalDrivers(category)
        
        # get total drivers for the category from supabase

        
        
        records = []
        
        for record in bestScore:
            date = record['date']
            formatted_date = date.split("T")[0]
            date_object = datetime.strptime(formatted_date, '%Y-%m-%d')
            day_of_week = date_object.strftime('%A')
            
            player_top_percentage = (record['position'] / total_drivers) * 100
            percentage_to_beat_first = ((record['score'] - first_place['score']) / first_place['score']) * 100
            seconds_to_beat_first = record['score'] - first_place['score']

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

            records.append({
                "label": label,
                "seconds_to_beat_first": f"{abs(seconds_to_beat_first):.3f}",
                "player_top_percentage": f"{player_top_percentage:.2f}",
                "position": record['position'],
                "date": formatted_date,
                "score": record['score'],
                "participant": username,
                "percentage_to_beat_first": f"{percentage_to_beat_first:.2f}",
                "day_of_week": day_of_week,
                "total_drivers": total_drivers,
            })
        
        stats["all_records"][category] = records
    
    return stats



def get_top_20_best_all_categories():
    # get the top 20 best scores for all categories and return the position, participant, score and calculate the gaps between the scores
    categories = ['kids', 'normal', 'adults']
    top_20 = []
    
    for category in categories:
        response = supabase.table('records').select('participant_id', 'score').eq('category', category).order('score').limit(20).execute()
        category_data = {
            'category': category,
            'data': response.data
        }
        top_20.append(category_data)
        
    for category_data in top_20:
        category_data['data'].sort(key=lambda x: x['score'])
        for i, record in enumerate(category_data['data']):
            if i == 0:
                record['gap'] = 0
                continue
            record['gap'] = record['score'] - category_data['data'][i - 1]['score']
        
    # Convert participant_id to username
    participant_ids = [record['participant_id'] for category_data in top_20 for record in category_data['data']]
    response = supabase.table('participants').select('id', 'username').in_('id', participant_ids).execute()
    participant_map = {participant['id']: participant['username'] for participant in response.data}
    
    for category_data in top_20:
        for record in category_data['data']:
            participant_id = record['participant_id']
            if participant_id in participant_map:
                record['participant'] = participant_map[participant_id]
    return top_20




# get the total number of drivers for each category, and then a total number of drivers for all categories together. And then the total number of records for all categories together.
def get_total_drivers_and_records():
    categories = ['kids', 'normal', 'adults']
    total_drivers = 0
    total_records = 0
    
    for category in categories:
        response = supabase.table('records').select('participant_id').eq('category', category).execute()
        total_drivers += len(set(record['participant_id'] for record in response.data))
        total_records += len(response.data)
    
    return total_drivers, total_records




class Users:
    def __init__(self):
        pass
    
    def get_user_by_id(self, user_id):
        response = supabase.table('users').select('id', 'email', 'username', 'username_easykart').eq('id', user_id).execute()
        return response.data[0] if response.data else None
    
    def get_user_by_email(self, email):
        response = supabase.table('users').select('id', 'email', 'username', 'username_easykart').eq('email', email).execute()
        return response.data[0] if response.data else None
    
    def get_user_by_username(self, username):
        response = supabase.table('users').select('id', 'email', 'username', 'username_easykart').eq('username', username).execute()
        return response.data[0] if response.data else None
    
    def authenticate_user(self, email, password):
        # get the hashed password using email from supabase
        response = supabase.table('users').select('password').eq('email', email).execute()
        if not response.data:
            return False
        
        hashed_password = response.data[0]['password']
        
        # compare the hashed password with the password provided
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    

    
    def create_user(self, email, password, username, easykart_username):

        user = self.get_user_by_email(email)
        if user:
            return None
        
        # check if the username is taken
        user = self.get_user_by_username(username)
        if user:
            return { "error": "Username is already taken" }
        
        # check if username is available from participants
        response = supabase.table('participants').select('username_availability').eq('username', easykart_username).execute()
        if not response.data:
            return { "error": "Username is not available" }
        
        # check if email is taken
        user = self.get_user_by_email(email)
        if user:
            return { "error": "Email is already taken" }
        
        
        # hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # create user
        response = supabase.table('users').insert({
            "email": email,
            "password": hashed_password.decode('utf-8'),
            "username": username,
            "username_easykart": easykart_username
        }).execute()
        
        # mark the username as unavailable
        response = supabase.table('participants').update({
            "username_availability": False
        }).eq('username', easykart_username).execute()
        
        
        return response.data[0] if response.data else None
    
    def update_easykart_username(self, user_id, username_easykart):
        response = supabase.table('users').update({
            "username_easykart": username_easykart
        }).eq('id', user_id).execute()
        return response.data[0] if response.data else None
    
    
    def get_easykart_username(self, user_id):
        response = supabase.table('users').select('username_easykart').eq('id', user_id).execute()
        return response.data[0] if response.data else None
    
    def connect_easykart(self, user_id, username_easykart):
        response = supabase.table('users').update({
            "username_easykart": username_easykart
        }).eq('id', user_id).execute()
        return response.data[0] if response.data else None
    
    
    def search_all_available_similar_usernames(self, username, threshold=2):
        # Retrieve all usernames
        response = supabase.table('participants').select('username').eq('username_availability', True).execute()
        
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
        
    
    def get_all_easykart_users(self, username):
        # use the search function to get all similar usernames
        similar_usernames = self.search_all_available_similar_usernames(username)
        
        return similar_usernames