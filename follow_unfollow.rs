extern crate reqwest;
extern crate tokio;
extern crate serde_json;

use std::env;
use std::collections::HashSet;
use std::thread::sleep;
use std::time::Duration;
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

// The rest of the code remains unchanged...

#[tokio::main]
async fn main() {
    let github_token = env::var("TOKEN").expect("TOKEN environment variable not set");
    let github_username = env::var("USERNAME").expect("USERNAME environment variable not set");

    let mut headers = HeaderMap::new();
    headers.insert(AUTHORIZATION, HeaderValue::from_str(&format!("token {}", github_token)).unwrap());

    follow_all_followers(&github_username, &headers).await;
    find_and_unfollow_non_followers(&github_username, &headers).await;
}
