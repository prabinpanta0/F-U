import os
import requests
import json

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# Track followed and unfollowed users
followed_users = []
unfollowed_users = []
failed_follow_users = []
failed_unfollow_users = []

def _extract_username(message, prefix):
    """Extract username from a message with a given prefix"""
    return message.replace(prefix, "").replace(".", "").strip()

def send_discord_notification(message):
    """
    Track GitHub users from notification messages
    
    Args:
        message (str): The notification message that contains action and username
    """
    # Define message patterns and their corresponding lists
    message_patterns = {
        "Followed ": followed_users,
        "Unfollowed ": unfollowed_users,
        "Failed to follow ": failed_follow_users,
        "Failed to unfollow ": failed_unfollow_users
    }
    
    # Process the message based on its prefix
    for prefix, user_list in message_patterns.items():
        if message.startswith(prefix):
            username = _extract_username(message, prefix)
            user_list.append(username)
            break
            
    # Log the tracked message to console
    print(f"Tracked: {message}")

def send_message_to_user(username, subject, body):
    # Just log the message locally without sending individual Discord notifications
    message = f"Message for {username} - {subject}: {body}"
    print(message)


def _create_user_category(users, label):
    """Create a category object for the JSON report"""
    return {
        "count": len(users),
        "users": users
    }

def _create_report():
    """Create the JSON report of followed/unfollowed users"""
    return {
        "followed": _create_user_category(followed_users, "followed"),
        "unfollowed": _create_user_category(unfollowed_users, "unfollowed"),
        "failed_follows": _create_user_category(failed_follow_users, "failed_follows"),
        "failed_unfollows": _create_user_category(failed_unfollow_users, "failed_unfollows")
    }

def _create_summary():
    """Create a summary text of changes"""
    categories = [
        (followed_users, "Followed"),
        (unfollowed_users, "Unfollowed"),
        (failed_follow_users, "Failed to follow"),
        (failed_unfollow_users, "Failed to unfollow")
    ]
    
    summary = [f"{label}: {len(users)}" for users, label in categories if users]
    return ", ".join(summary)

def _post_to_discord(content, embeds=None):
    """Send a message to Discord webhook"""
    data = {"content": content}
    if embeds:
        data["embeds"] = embeds
        
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    
    if response.status_code != 204:
        print(f"Failed to send Discord report. Status code: {response.status_code}")
        return False
    else:
        print("Discord report sent successfully")
        return True

def _clear_user_lists():
    """Clear all user tracking lists"""
    followed_users.clear()
    unfollowed_users.clear()
    failed_follow_users.clear()
    failed_unfollow_users.clear()

# Function to send a consolidated JSON report to Discord
def send_follow_report():
    """Send a JSON report of follow/unfollow activity to Discord"""
    # Check if there are any changes to report
    if not any([followed_users, unfollowed_users, failed_follow_users, failed_unfollow_users]):
        _post_to_discord("No changes in followers/following today.")
        return
        
    # Create report and summary
    report = _create_report()
    summary_text = _create_summary()
    
    # Format the data for Discord
    embeds = [{
        "title": "GitHub Follow/Unfollow Report",
        "description": f"```json\n{json.dumps(report, indent=2)}\n```"
    }]
    
    # Send the notification
    if _post_to_discord(f"Github(prabinpanta0) Report: {summary_text}", embeds):
        _clear_user_lists()

# Added notifications for no one to follow/unfollow
def no_one_to_follow():
    print("No one to follow")
    # We'll include this information in the final report

def no_one_to_unfollow():
    print("No one to unfollow")
    # We'll include this information in the final report
