import os
import requests
import time
from notifications import send_message_to_user, send_discord_notification, no_one_to_follow, no_one_to_unfollow, send_follow_report

# Get environment variables
GITHUB_TOKEN = os.getenv('TOKEN')
GITHUB_USERNAME = os.getenv('USERNAME')

headers = {'Authorization': f'token {GITHUB_TOKEN}'}

def get_github_user_list(endpoint, per_page=100):
    """
    Generic function to fetch user lists from GitHub API with pagination
    
    Args:
        endpoint (str): API endpoint ('following' or 'followers')
        per_page (int): Number of results per page
        
    Returns:
        list: List of GitHub usernames
    """
    users = []
    page = 1
    while True:
        url = f'https://api.github.com/users/{GITHUB_USERNAME}/{endpoint}?per_page={per_page}&page={page}'
        response = requests.get(url, headers=headers)
        data = response.json()
        if not data:
            break
        users.extend([user['login'] for user in data])
        page += 1
    return users

def get_following():
    """Fetch list of users the authenticated user is following"""
    return get_github_user_list('following')

def get_followers():
    """Fetch list of users following the authenticated user"""
    return get_github_user_list('followers', per_page=110)

def modify_follow_status(user, action="follow", retries=3):
    """
    Generic function to follow or unfollow a user
    
    Args:
        user (str): GitHub username to follow/unfollow
        action (str): 'follow' or 'unfollow'
        retries (int): Number of retries in case of failure
        
    Returns:
        bool: True if successful, False otherwise
    """
    url = f'https://api.github.com/user/following/{user}'
    method = requests.put if action == "follow" else requests.delete
    
    for i in range(retries):
        response = method(url, headers=headers)
        if response.status_code == 204:
            return True
        elif response.status_code == 403:
            print(f'Rate limit hit. Waiting before retry {i+1}/{retries}...')
            time.sleep(60)
        else:
            print(f'Request failed. Attempt {i+1}/{retries}. Waiting before retry...')
            time.sleep(2)
    return False

def follow_user(user, retries=3):
    """Follow a GitHub user"""
    return modify_follow_status(user, "follow", retries)

def unfollow_user(user, retries=3):
    """Unfollow a GitHub user"""
    return modify_follow_status(user, "unfollow", retries)

def process_user_list(users, operation_type):
    """
    Process a list of users to follow or unfollow them
    
    Args:
        users (list): List of usernames to process
        operation_type (str): "follow" or "unfollow"
    """
    operation_func = follow_user if operation_type == "follow" else unfollow_user
    verb = "followed" if operation_type == "follow" else "unfollowed"
    failed_verb = f"Failed to {operation_type}"
    
    for i, user in enumerate(users, 1):
        if operation_func(user):
            print(f'{i}. {verb} {user}.')
            
            # Different messages for follow vs unfollow
            if operation_type == "follow":
                message_subject = f"Dear {user}, Thank you for following!"
                message_body = f"It's great to have you on board. {GITHUB_USERNAME} (GitHub)"
            else:
                message_subject = f"Dear {user}, It's sad to see you go"
                message_body = f"We hope to see you again! {GITHUB_USERNAME} (GitHub)"
                
            send_message_to_user(user, message_subject, message_body)
            send_discord_notification(f"{verb.capitalize()} {user}.")
        else:
            print(f'{i}. {failed_verb} {user}.')
            send_discord_notification(f"{failed_verb} {user}.")
        time.sleep(2)

def process_follow_unfollow(operation_type):
    """
    Common function to handle follow/unfollow operations
    
    Args:
        operation_type (str): "follow" or "unfollow"
    """
    following = set(get_following())
    followers = set(get_followers())
    
    if operation_type == "follow":
        target_users = list(followers - following)  # Users to follow
        empty_message = 'No one left to follow back'
        notify_func = no_one_to_follow
        success_message = f'\n {len(target_users)} are left to followback \n'
        user_list_title = '\nList of users to follow:\n'
        finish_message = '\nFinished processing all non-following.'
    else:  # unfollow
        target_users = list(following - followers)  # Users to unfollow
        empty_message = 'You don\'t follow anyone who doesn\'t follow you back.'
        notify_func = no_one_to_unfollow
        success_message = f'\nYou follow {len(target_users)} people who don\'t follow you back.'
        user_list_title = '\nList of non-followers:\n'
        finish_message = '\nFinished processing all non-followers.'
        
    if not target_users:
        print(empty_message)
        notify_func()
        return
        
    print(success_message)
    print(user_list_title)
    
    # Process the list of users
    process_user_list(target_users, operation_type)
    
    print(finish_message)
    # Send combined report after processing is complete
    send_follow_report()

def follow_all_followers():
    """Follow all users who follow you but you don't follow back"""
    process_follow_unfollow("follow")

# Execute the follow operation
follow_all_followers()

def find_and_unfollow_non_followers():
    """Unfollow users who don't follow you back"""
    process_follow_unfollow("unfollow")

# Execute the unfollow operation
find_and_unfollow_non_followers()
