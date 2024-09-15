
# F-U: GitHub Follow & Unfollow Automation

F-U is an automation tool designed to help manage your GitHub social interactions. It automatically follows users who follow you, unfollows users who stop following you, and checks for updates daily.

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Cron Job Setup](#cron-job-setup)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Automated Follow-back:** Automatically follow users who follow you on GitHub.
- **Unfollow Detection:** Detect and unfollow users who stop following you.
- **Daily Updates:** Scheduled daily checks for any changes in your followers.
- **Notifications:** Integrate with Discord for notification alerts when followers change.

## Technologies

The project is built using:

- **Python:** Core programming language.
- **GitHub API:** For interacting with GitHub followers data.
- **Selenium:** Automating browser tasks.
- **Discord API (Optional):** For sending notifications about new followers or unfollows.

## Installation

To install and set up the project on your local machine:

1. Clone the repository:

    ```bash
    git clone https://github.com/prabinpanta0/F-U.git
    ```

2. Navigate to the project directory:

    ```bash
    cd F-U
    ```

3. Install required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up your environment variables for GitHub API access:

    - Create a `.env` file in the project root directory and add the following:
    
      ```bash
      TOKEN=your_github_access_token
      USERNAME=your_github_username
      DISCORD_WEBHOOK=your_discord_webhook_url  # Optional
      ```

## Usage

Once everything is set up, you can run the script to automate your follow/unfollow tasks.

```bash
python follow_unfollow.py
```

You can also set it to check for updates daily by setting up a cron job (Linux/macOS) or Task Scheduler (Windows).

### Example Cron Job Setup (Linux/macOS)

To run the script daily at midnight:

```bash
0 0 * * * /usr/bin/python3 /path/to/F-U/follow_unfollow.py
```

## Configuration

### Environment Variables

- `TOKEN`: Your GitHub personal access token.
- `USERNAME`: Your GitHub username.
- `DISCORD_WEBHOOK`: Discord webhook URL for notifications (optional).

### Discord Notifications

If you'd like to receive alerts on Discord when a user follows or unfollows you, set up a Discord webhook and add the URL to your `.env` file as shown above.

## Cron Job Setup

To automate the script execution daily, you can set up a cron job or task scheduler depending on your operating system. For cron (Linux/macOS), use the following command to edit the crontab:

```bash
crontab -e
```

Then, add the following line to schedule the job:

```bash
0 0 * * * /usr/bin/python3 /path/to/F-U/follow_unfollow.py
```

For Windows, you can use the Task Scheduler to achieve similar automation.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit and push (`git commit -am 'Added a new feature'`).
5. Create a Pull Request.

Please ensure your code follows the project's coding style and includes relevant tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
