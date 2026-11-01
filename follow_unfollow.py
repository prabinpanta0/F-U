import time

import config
from github_api import GitHubClient
from notifications import (
    send_message_to_user,
    send_discord_notification,
    no_one_to_follow,
    no_one_to_unfollow,
    send_follow_report,
)

client = GitHubClient()


def get_following():
    """Fetch list of users the authenticated user is following"""
    return client.get_following()


def get_followers():
    """Fetch list of users following the authenticated user"""
    return client.get_followers()


def already_following(user):
    return client.is_following(config.GITHUB_USERNAME, user)


def followed_by(user):
    return client.is_follower(user, config.GITHUB_USERNAME)


def modify_follow_status(user, action="follow"):
    """Follow or unfollow a user, verifying the mutual state first."""
    if action == "follow":
        if already_following(user):
            return None
        if not followed_by(user):
            print(f"Skipping {user}: not a follower (state changed).")
            return False
        success = client.follow(user)
    else:
        if not already_following(user):
            return None
        if followed_by(user):
            print(f"Skipping {user}: now follows you back.")
            return False
        success = client.unfollow(user)

    return success


def follow_user(user):
    return modify_follow_status(user, "follow")


def unfollow_user(user):
    return modify_follow_status(user, "unfollow")


def process_user_list(users, operation_type):
    """Process a list of users, respecting dry-run and per-run limits."""
    operation_func = follow_user if operation_type == "follow" else unfollow_user
    verb = "followed" if operation_type == "follow" else "unfollowed"
    failed_verb = f"Failed to {operation_type}"

    attempted = 0
    for i, user in enumerate(users, 1):
        if config.MAX_ACTIONS_PER_RUN and attempted >= config.MAX_ACTIONS_PER_RUN:
            print(f"Reached MAX_ACTIONS_PER_RUN ({config.MAX_ACTIONS_PER_RUN}), stopping.")
            break

        if config.DRY_RUN:
            print(f"[DRY RUN] Would {operation_type} {user}.")
            continue

        result = operation_func(user)
        if result is None:
            print(f"{i}. Already in desired state, skipping {user}.")
            continue

        attempted += 1
        if result:
            print(f"{i}. {verb} {user}.")
            if operation_type == "follow":
                subject = f"Dear {user}, Thank you for following!"
                body = f"It's great to have you on board. {config.GITHUB_USERNAME} (GitHub)"
            else:
                subject = f"Dear {user}, It's sad to see you go"
                body = f"We hope to see you again! {config.GITHUB_USERNAME} (GitHub)"
            send_message_to_user(user, subject, body)
            send_discord_notification(f"{verb.capitalize()} {user}.")
        else:
            print(f"{i}. {failed_verb} {user}.")
            send_discord_notification(f"{failed_verb} {user}.")

        if config.ACTION_DELAY:
            time.sleep(config.ACTION_DELAY)


def process_follow_unfollow(operation_type):
    following = set(get_following())
    followers = set(get_followers())

    if operation_type == "follow":
        target_users = list(followers - following)
        empty_message = "No one left to follow back"
        notify_func = no_one_to_follow
        success_message = f"\n {len(target_users)} are left to followback \n"
        user_list_title = "\nList of users to follow:\n"
        finish_message = "\nFinished processing all non-following."
    else:
        target_users = list(following - followers)
        empty_message = "You don't follow anyone who doesn't follow you back."
        notify_func = no_one_to_unfollow
        success_message = f"\nYou follow {len(target_users)} people who don't follow you back."
        user_list_title = "\nList of non-followers:\n"
        finish_message = "\nFinished processing all non-followers."

    if not target_users:
        print(empty_message)
        notify_func()
        return

    print(success_message)
    print(user_list_title)

    process_user_list(target_users, operation_type)

    print(finish_message)
    send_follow_report()


def follow_all_followers():
    """Follow all users who follow you but you don't follow back"""
    process_follow_unfollow("follow")


def find_and_unfollow_non_followers():
    """Unfollow users who don't follow you back"""
    process_follow_unfollow("unfollow")


def main():
    follow_all_followers()
    find_and_unfollow_non_followers()


if __name__ == "__main__":
    main()
