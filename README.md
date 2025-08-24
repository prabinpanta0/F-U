
<div align="center">

```
46 6f 6c 6c 6f 77 20 79 6f 75            
```
</div>

# F-U: GitHub Follow & Unfollow Automation 🚀

> Automate your GitHub social network with this elegant tool!

## ✨ Features

<div align="center">

```
┌──────────────────────────────────────────────┐
│ ✅ Auto-follow your followers                │
│ ✅ Auto-unfollow those who don't follow back │
│ ✅ Discord notifications with JSON reports   │
│ ✅ Scheduled daily checks                    │
│ ✅ Network visualization of your followers   │
└──────────────────────────────────────────────┘
```
</div>

## 🔧 Setup

### Prerequisites

- Python 3.6+
- GitHub Account
- Discord Webhook (optional)

### Quick Start

1️⃣ **Clone the repo**
```bash
git clone https://github.com/prabinpanta0/F-U.git && cd F-U
```

2️⃣ **Install dependencies**
```bash
pip install -r requirements.txt
# For network visualization you'll need these additional packages:
pip install matplotlib networkx pandas pillow plotly
```

3️⃣ **Configure environment**
```bash
# Create .env file with your credentials
echo "TOKEN=your_github_access_token
USERNAME=your_github_username
DISCORD_WEBHOOK_URL=your_discord_webhook_url" > .env
```

4️⃣ **Run it!**
```bash
python follow_unfollow.py
```

## 🔄 Automation

### Set up daily checks with cron (Linux/macOS)

```bash
# Open crontab editor
crontab -e

# Add this line to run daily at midnight
0 0 * * * /usr/bin/python3 /path/to/F-U/follow_unfollow.py
```

### GitHub Actions Workflow

The repository includes a GitHub Actions workflow that automatically:
- Runs on a daily schedule
- Generates network visualizations of your GitHub connections
- Follows/unfollows users based on your settings
- Saves visualization history in the repository

To use this feature:
1. Fork this repository
2. Set up repository secrets (`TOKEN`, `USERNAME`, `DISCORD_WEBHOOK_URL`)
3. Enable GitHub Actions on your fork
4. The workflow will create visualizations in the `visualizations/` directory

## 📊 Network Visualization

The tool generates interactive and static visualizations of your GitHub network:

- **Summary Image**: Key metrics about your follower network
- **Interactive HTML Graph**: Explore connections with hover effects
- **Static Network Graph**: Visual representation of your network
- **CSV Data**: Historical data of your network growth

Images and data are stored in the `visualizations/` and `network_data/` directories.

## 📢 Notifications

Discord notifications include a neat JSON report:
```json
{
  "followed": {
    "count": 5,
    "users": ["user1", "user2", "user3", "user4", "user5"]
  },
  "unfollowed": {
    "count": 2,
    "users": ["user6", "user7"]
  }
}
```

## 📜 License

[MIT ©](LICENSE) [prabinpanta0](https://github.com/prabinpanta0)

---
```
    Keep your GitHub social network healthy! 

by >> 70 72 61 62 69 6e 70 61 6e 74 61 30
```
