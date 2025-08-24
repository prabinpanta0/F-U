
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

## 📊 Notifications

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
