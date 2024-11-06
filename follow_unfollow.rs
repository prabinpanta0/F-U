extern crate reqwest;
extern crate tokio;
extern crate serde_json;

use std::env;
use std::collections::HashSet;
use reqwest::header::{HeaderMap, HeaderValue, AUTHORIZATION};
use serde_json::Value;

async fn get_following(github_username: &str) -> HashSet<String> {
    let mut following = HashSet::new();
    let mut page = 1;

    loop {
        let url = format!("https://api.github.com/users/{}/following?per_page=100&page={}", github_username, page);
        let response = match reqwest::get(&url).await {
            Ok(resp) => resp,
            Err(_) => {
                println!("Failed to fetch following list for user: {}", github_username);
                break;
            }
        };
        let json: Value = match response.json().await {
            Ok(json) => json,
            Err(_) => {
                println!("Failed to decode following list for user: {}", github_username);
                break;
            }
        };

        if json.as_array().unwrap().is_empty() {
            break;
        }

        for user in json.as_array().unwrap() {
            following.insert(user["login"].as_str().unwrap().to_string());
        }

        page += 1;
    }

    following
}

async fn get_followers(github_username: &str) -> HashSet<String> {
    let mut followers = HashSet::new();
    let mut page = 1;

    loop {
        let url = format!("https://api.github.com/users/{}/followers?per_page=100&page={}", github_username, page);
        let response = match reqwest::get(&url).await {
            Ok(resp) => resp,
            Err(_) => {
                println!("Failed to fetch followers list for user: {}", github_username);
                break;
            }
        };
        let json: Value = match response.json().await {
            Ok(json) => json,
            Err(_) => {
                println!("Failed to decode followers list for user: {}", github_username);
                break;
            }
        };

        if json.as_array().unwrap().is_empty() {
            break;
        }

        for user in json.as_array().unwrap() {
            followers.insert(user["login"].as_str().unwrap().to_string());
        }

        page += 1;
    }

    followers
}

async fn follow_user(user: &str, headers: &HeaderMap<HeaderValue>, retries: u8) -> bool {
    let follow_url = format!("https://api.github.com/user/following/{}", user);

    for _ in 0..retries {
        let client = reqwest::Client::new();
        let response = client.put(&follow_url).headers(headers.clone()).send().await.unwrap();

        if response.status().is_success() {
            return true;
        } else if response.status().as_u16() == 403 {
            println!("Rate limit hit. Waiting before retrying...");
            tokio::time::sleep(tokio::time::Duration::from_secs(60)).await;
        } else {
            tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
        }
    }

    false
}

async fn follow_all_followers(github_username: &str, headers: &HeaderMap<HeaderValue>) {
    let following = get_following(github_username).await;
    let followers = get_followers(github_username).await;
    let non_following: HashSet<_> = followers.difference(&following).collect();

    if non_following.is_empty() {
        println!("No one Left to follow back");
        return;
    }

    println!("\n{} are left to follow back\n", non_following.len());
    println!("\nList of non-followers:\n");

    for (i, user) in non_following.iter().enumerate() {
        if follow_user(user, headers, 3).await {
            println!("{}. Followed {}.", i + 1, user);
        } else {
            println!("{}. Failed to follow {}.", i + 1, user);
        }
        tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
    }

    println!("\nFinished processing all non-following.");
}

async fn unfollow_user(user: &str, headers: &HeaderMap<HeaderValue>, retries: u8) -> bool {
    let unfollow_url = format!("https://api.github.com/user/following/{}", user);

    for _ in 0..retries {
        let client = reqwest::Client::new();
        let response = client.delete(&unfollow_url).headers(headers.clone()).send().await.unwrap();

        if response.status().is_success() {
            return true;
        } else if response.status().as_u16() == 403 {
            println!("Rate limit hit. Waiting before retrying...");
            tokio::time::sleep(tokio::time::Duration::from_secs(60)).await;
        } else {
            tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
        }
    }

    false
}

async fn find_and_unfollow_non_followers(github_username: &str, headers: &HeaderMap<HeaderValue>) {
    let following = get_following(github_username).await;
    let followers = get_followers(github_username).await;
    let non_followers: HashSet<_> = following.difference(&followers).collect();

    if non_followers.is_empty() {
        println!("You don't follow anyone who doesn't follow you back.");
        return;
    }

    println!("\nYou follow {} people who don't follow you back.", non_followers.len());
    println!("\nList of non-followers:\n");

    for (i, user) in non_followers.iter().enumerate() {
        if unfollow_user(user, headers, 3).await {
            println!("{}. Unfollowed {}.", i + 1, user);
        } else {
            println!("{}. Failed to unfollow {}.", i + 1, user);
        }
        tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
    }

    println!("\nFinished processing all non-followers.");
}

#[tokio::main]
async fn main() {
    let github_token = env::var("TOKEN").expect("TOKEN environment variable not set");
    let github_username = env::var("USERNAME").expect("USERNAME environment variable not set");

    let mut headers = HeaderMap::new();
    headers.insert(AUTHORIZATION, HeaderValue::from_str(&format!("token {}", github_token)).unwrap());

    follow_all_followers(&github_username, &headers).await;
    find_and_unfollow_non_followers(&github_username, &headers).await;
}
