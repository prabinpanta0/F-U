require 'net/http'
require 'json'
require 'time'

GITHUB_TOKEN = ENV['TOKEN']
GITHUB_USERNAME = ENV['USERNAME']

HEADERS = { 'Authorization' => "token #{GITHUB_TOKEN}" }

def get_following
  following = []
  page = 1
  loop do
    url = URI("https://api.github.com/users/#{GITHUB_USERNAME}/following?per_page=100&page=#{page}")
    response = Net::HTTP.get(url)
    data = JSON.parse(response)
    break if data.empty?

    following.concat(data.map { |user| user['login'] })
    page += 1
  end
  following
end

def get_followers
  followers = []
  page = 1
  loop do
    url = URI("https://api.github.com/users/#{GITHUB_USERNAME}/followers?per_page=100&page=#{page}")
    response = Net::HTTP.get(url)
    data = JSON.parse(response)
    break if data.empty?

    followers.concat(data.map { |user| user['login'] })
    page += 1
  end
  followers
end

def follow_user(user, retries = 3)
  follow_url = URI("https://api.github.com/user/following/#{user}")
  retries.times do
    request = Net::HTTP::Put.new(follow_url, HEADERS)
    response = Net::HTTP.start(follow_url.hostname, follow_url.port, use_ssl: true) { |http| http.request(request) }
    return true if response.code.to_i == 204
    if response.code.to_i == 403
      puts 'Rate limit hit. Waiting before retrying...'
      sleep(60)
    else
      sleep(2)
    end
  end
  false
end

def follow_all_followers
  following = get_following.to_set
  followers = get_followers.to_set
  non_following = followers - following
  if non_following.empty?
    puts 'No one Left to follow back'
    return
  end

  puts "\n #{non_following.size} are left to follow back \n"
  puts '\nList of non-followers:\n'
  non_following.each_with_index do |user, index|
    if follow_user(user)
      puts "#{index + 1}. Followed #{user}."
    else
      puts "#{index + 1}. Failed to follow #{user}."
    end
    sleep(2)
  end
  puts '\nFinished processing all non-following.'
end

def unfollow_user(user, retries = 3)
  unfollow_url = URI("https://api.github.com/user/following/#{user}")
  retries.times do
    request = Net::HTTP::Delete.new(unfollow_url, HEADERS)
    response = Net::HTTP.start(unfollow_url.hostname, unfollow_url.port, use_ssl: true) { |http| http.request(request) }
    return true if response.code.to_i == 204
    if response.code.to_i == 403
      puts 'Rate limit hit. Waiting before retrying...'
      sleep(60)
    else
      sleep(2)
    end
  end
  false
end

def find_and_unfollow_non_followers
  following = get_following.to_set
  followers = get_followers.to_set
  non_followers = following - followers
  if non_followers.empty?
    puts "You don't follow anyone who doesn't follow you back."
    return
  end

  puts "\nYou follow #{non_followers.size} people who don't follow you back."
  puts '\nList of non-followers:\n'
  non_followers.each_with_index do |user, index|
    if unfollow_user(user)
      puts "#{index + 1}. Unfollowed #{user}."
    else
      puts "#{index + 1}. Failed to unfollow #{user}."
    end
    sleep(2)
  end
  puts '\nFinished processing all non-followers.'
end

follow_all_followers
find_and_unfollow_non_followers
