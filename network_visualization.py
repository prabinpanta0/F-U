#!/usr/bin/env python3
"""
Network Visualization Generator for F-U: GitHub Follow & Unfollow Automation

This script generates a visual representation of a user's GitHub follower network,
showing relationships between followers and following. It saves both the raw data
and generated visualizations.

The script does not require a database, instead it:
1. Fetches current follower/following data from GitHub API
2. Saves raw data as CSV for historical comparison
3. Creates a network graph visualization
4. Saves both static images and interactive HTML versions
"""

import os
import json
import requests
import csv
import time
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
from PIL import Image, ImageDraw, ImageFont

# Get environment variables
GITHUB_TOKEN = os.getenv('TOKEN')
GITHUB_USERNAME = os.getenv('USERNAME')

headers = {'Authorization': f'token {GITHUB_TOKEN}'}

def get_github_user_list(endpoint, per_page=100):
    """
    Fetch user lists from GitHub API with pagination
    
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

def fetch_user_data(username):
    """Fetch basic profile data for a GitHub user"""
    url = f'https://api.github.com/users/{username}'
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                'login': data.get('login'),
                'name': data.get('name', ''),
                'public_repos': data.get('public_repos', 0),
                'followers': data.get('followers', 0),
                'following': data.get('following', 0),
                'created_at': data.get('created_at', ''),
                'bio': data.get('bio', '')[:100] if data.get('bio') else ''  # Truncate bio to avoid very long text
            }
    except Exception as e:
        print(f"Error fetching data for {username}: {e}")
    
    # Return minimal data if API call fails
    return {'login': username, 'name': '', 'public_repos': 0, 'followers': 0, 'following': 0, 'created_at': '', 'bio': ''}

def save_data_to_csv(followers, following):
    """Save current follower/following data as CSV"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Create followers CSV
    with open(f'network_data/followers_{today}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['username'])
        for user in followers:
            writer.writerow([user])
    
    # Create following CSV
    with open(f'network_data/following_{today}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['username'])
        for user in following:
            writer.writerow([user])
    
    # Create relationship CSV
    with open(f'network_data/network_{today}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['source', 'target', 'relationship'])
        
        # You follow these users
        for user in following:
            writer.writerow([GITHUB_USERNAME, user, 'following'])
        
        # These users follow you
        for user in followers:
            writer.writerow([user, GITHUB_USERNAME, 'following'])
    
    print(f"Data saved to CSV files with date {today}")

def generate_network_graph(followers, following):
    """Generate a NetworkX graph of follower/following relationships"""
    G = nx.DiGraph()
    
    # Add the main user
    G.add_node(GITHUB_USERNAME, type='main')
    
    # Add followers and following
    mutual = set(followers) & set(following)
    followers_only = set(followers) - mutual
    following_only = set(following) - mutual
    
    # Add different types of users
    for user in mutual:
        G.add_node(user, type='mutual')
    
    for user in followers_only:
        G.add_node(user, type='follower')
    
    for user in following_only:
        G.add_node(user, type='following')
    
    # Add edges
    for user in followers:
        G.add_edge(user, GITHUB_USERNAME)
    
    for user in following:
        G.add_edge(GITHUB_USERNAME, user)
    
    return G

def create_matplotlib_visualization(G):
    """Create a static visualization using matplotlib"""
    plt.figure(figsize=(14, 10))
    
    # Define positions
    pos = nx.spring_layout(G, k=0.3, iterations=50)
    
    # Define node colors based on type
    color_map = []
    for node in G:
        if node == GITHUB_USERNAME:
            color_map.append('red')
        elif G.nodes[node]['type'] == 'mutual':
            color_map.append('purple')
        elif G.nodes[node]['type'] == 'follower':
            color_map.append('green')
        else:  # following
            color_map.append('blue')
    
    # Draw the graph
    nx.draw(G, pos, with_labels=True, node_color=color_map, 
            node_size=500, arrows=True, connectionstyle='arc3,rad=0.1',
            font_size=8, font_weight='bold')
    
    # Add a legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', label=f'You ({GITHUB_USERNAME})',
                  markerfacecolor='red', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='Mutual Followers',
                  markerfacecolor='purple', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='Followers Only',
                  markerfacecolor='green', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='Following Only',
                  markerfacecolor='blue', markersize=10)
    ]
    plt.legend(handles=legend_elements, loc='upper left')
    
    # Add title and other details
    today = datetime.now().strftime('%Y-%m-%d')
    plt.title(f"GitHub Network for {GITHUB_USERNAME} - {today}")
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(f'visualizations/network_graph_{today}.png', dpi=300)
    print(f"Static visualization saved as network_graph_{today}.png")

def create_plotly_visualization(G, followers, following):
    """Create an interactive visualization using plotly"""
    # Create edge traces
    edge_x = []
    edge_y = []
    
    pos = nx.spring_layout(G, k=0.3, iterations=50)
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    # Create node traces for different types
    main_trace = go.Scatter(
        x=[], y=[],
        mode='markers+text',
        name=GITHUB_USERNAME,
        marker=dict(
            color='red',
            size=20,
            line=dict(width=2, color='DarkSlateGrey')
        ),
        text=[],
        textposition="bottom center",
        hoverinfo='text'
    )
    
    mutual_trace = go.Scatter(
        x=[], y=[],
        mode='markers+text',
        name='Mutual Followers',
        marker=dict(
            color='purple',
            size=15,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        text=[],
        textposition="bottom center",
        hoverinfo='text'
    )
    
    follower_trace = go.Scatter(
        x=[], y=[],
        mode='markers+text',
        name='Followers Only',
        marker=dict(
            color='green',
            size=10,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        text=[],
        textposition="bottom center",
        hoverinfo='text'
    )
    
    following_trace = go.Scatter(
        x=[], y=[],
        mode='markers+text',
        name='Following Only',
        marker=dict(
            color='blue',
            size=10,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        text=[],
        textposition="bottom center",
        hoverinfo='text'
    )
    
    # Add nodes to traces
    mutual_set = set(followers) & set(following)
    
    for node in G.nodes():
        x, y = pos[node]
        hover_text = f"User: {node}"
        
        if node == GITHUB_USERNAME:
            main_trace['x'] += tuple([x])
            main_trace['y'] += tuple([y])
            main_trace['text'] += tuple([node])
            main_trace['hovertext'] = hover_text
        elif node in mutual_set:
            mutual_trace['x'] += tuple([x])
            mutual_trace['y'] += tuple([y])
            mutual_trace['text'] += tuple([node])
            mutual_trace['hovertext'] = hover_text
        elif node in followers:
            follower_trace['x'] += tuple([x])
            follower_trace['y'] += tuple([y])
            follower_trace['text'] += tuple([node])
            follower_trace['hovertext'] = hover_text
        else:
            following_trace['x'] += tuple([x])
            following_trace['y'] += tuple([y])
            following_trace['text'] += tuple([node])
            following_trace['hovertext'] = hover_text
    
    # Create figure
    fig = go.Figure(data=[edge_trace, main_trace, mutual_trace, follower_trace, following_trace],
                 layout=go.Layout(
                    title=f'GitHub Network for {GITHUB_USERNAME}',
                    titlefont=dict(size=16),
                    showlegend=True,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                ))
    
    today = datetime.now().strftime('%Y-%m-%d')
    fig.write_html(f'visualizations/interactive_network_{today}.html')
    print(f"Interactive visualization saved as interactive_network_{today}.html")

def create_summary_image():
    """Create a summary image with key metrics"""
    today = datetime.now().strftime('%Y-%m-%d')
    followers = get_github_user_list('followers')
    following = get_github_user_list('following')
    
    mutual = set(followers) & set(following)
    followers_only = set(followers) - mutual
    following_only = set(following) - mutual
    
    # Create a summary image
    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Try to load a font, fall back to default if not available
    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_heading = ImageFont.truetype("arial.ttf", 24)
        font_text = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font_title = ImageFont.load_default()
        font_heading = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # Add title
    d.text((50, 50), f"GitHub Network Summary for {GITHUB_USERNAME}", fill=(0, 0, 0), font=font_title)
    d.text((50, 100), f"Generated on {today}", fill=(100, 100, 100), font=font_heading)
    
    # Add metrics
    d.text((50, 150), f"Total Followers: {len(followers)}", fill=(0, 100, 0), font=font_text)
    d.text((50, 190), f"Total Following: {len(following)}", fill=(0, 0, 200), font=font_text)
    d.text((50, 230), f"Mutual Connections: {len(mutual)}", fill=(128, 0, 128), font=font_text)
    d.text((50, 270), f"Followers Only: {len(followers_only)}", fill=(0, 150, 0), font=font_text)
    d.text((50, 310), f"Following Only: {len(following_only)}", fill=(0, 0, 150), font=font_text)
    
    # Add follow ratio
    if len(following) > 0:
        ratio = len(followers) / len(following)
        ratio_text = f"Follower/Following Ratio: {ratio:.2f}"
        d.text((50, 350), ratio_text, fill=(200, 0, 0), font=font_text)
    
    # Add legend
    d.text((50, 410), "Legend:", fill=(0, 0, 0), font=font_heading)
    
    # Draw colored squares for the legend
    d.rectangle([(50, 450), (70, 470)], fill=(255, 0, 0))
    d.text((80, 450), f"You ({GITHUB_USERNAME})", fill=(0, 0, 0), font=font_text)
    
    d.rectangle([(50, 480), (70, 500)], fill=(128, 0, 128))
    d.text((80, 480), "Mutual Followers", fill=(0, 0, 0), font=font_text)
    
    d.rectangle([(300, 450), (320, 470)], fill=(0, 200, 0))
    d.text((330, 450), "Followers Only", fill=(0, 0, 0), font=font_text)
    
    d.rectangle([(300, 480), (320, 500)], fill=(0, 0, 255))
    d.text((330, 480), "Following Only", fill=(0, 0, 0), font=font_text)
    
    # Save the image
    img.save(f'visualizations/summary_{today}.png')
    print(f"Summary image saved as summary_{today}.png")

def main():
    """Main function to generate all visualizations"""
    print(f"Generating network visualization for {GITHUB_USERNAME}")
    
    # Make sure directories exist
    os.makedirs('network_data', exist_ok=True)
    os.makedirs('visualizations', exist_ok=True)
    
    # Get followers and following
    followers = get_github_user_list('followers')
    following = get_github_user_list('following')
    
    print(f"Found {len(followers)} followers and {len(following)} following")
    
    # Save raw data
    save_data_to_csv(followers, following)
    
    # Generate graph
    G = generate_network_graph(followers, following)
    
    # Create visualizations
    create_matplotlib_visualization(G)
    create_plotly_visualization(G, followers, following)
    create_summary_image()
    
    # Create a metadata file with info about the graph
    metadata = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'username': GITHUB_USERNAME,
        'followers_count': len(followers),
        'following_count': len(following),
        'mutual_count': len(set(followers) & set(following)),
        'followers_only_count': len(set(followers) - set(following)),
        'following_only_count': len(set(following) - set(followers)),
    }
    
    with open(f'network_data/metadata_{datetime.now().strftime("%Y-%m-%d")}.json', 'w') as f:
        json.dump(metadata, f, indent=2)

if __name__ == "__main__":
    main()