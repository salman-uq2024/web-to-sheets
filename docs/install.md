# Installation Guide

This guide provides step-by-step instructions to set up `web-to-sheets` on your local machine. It assumes you have Python 3.10 or higher installed. The process includes creating a virtual environment, installing dependencies, and configuring environment variables for Google Sheets integration.

## Prerequisites

- Python 3.10+ (download from [python.org](https://www.python.org/downloads/))
- Git (for cloning the repository)
- A Google account for Sheets API setup (optional for demo mode)

## Step 1: Clone the Repository

Clone the project to your local machine:

```bash
git clone https://github.com/yourusername/web-to-sheets.git  # Replace with actual repo URL
cd web-to-sheets
```

## Step 2: Set Up Virtual Environment

Use the provided bootstrap script for an automated setup, which creates a virtual environment and installs dependencies:

```bash
./scripts/bootstrap.sh
```

This script:
- Creates a `venv` directory with a virtual environment.
- Upgrades `pip`.
- Installs the project in editable mode (`-e .[dev]`) including development tools like `pytest`.

Alternatively, for manual setup:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e .[dev]
```

## Step 3: Verify Installation

Activate the virtual environment (if not already) and check the CLI:

```bash
source venv/bin/activate
ws --help
```

You should see the usage information for the `ws` command.

## Step 4: Configure Environment Variables (for Google Sheets)

To enable Google Sheets export, set up authentication using a service account:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Enable the Google Sheets API:
   - Navigate to "APIs & Services" > "Library".
   - Search for "Google Sheets API" and enable it.
4. Create a service account:
   - Go to "APIs & Services" > "Credentials".
   - Click "Create Credentials" > "Service Account".
   - Fill in the details and create the account.
   - Grant the service account "Editor" role for Google Sheets.
5. Download the service account JSON key:
   - From the service account details, create a key (JSON format) and download it.
6. Share your Google Sheet:
   - Create a new Google Sheet or use an existing one.
   - Note the Sheet ID from the URL (e.g., `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit`).
   - Share the sheet with the service account email (found in the JSON key) with "Editor" access.

Copy `.env.example` to `.env` and update it:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```
# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_PATH=path/to/your_service_account.json
GOOGLE_SHEETS_ID=your_google_sheet_id

# Logging (optional)
LOG_LEVEL=INFO

# Optional: Slack Notifications (for alerts on failures)
SLACK_WEBHOOK_URL=YOUR_SLACK_WEBHOOK_URL_HERE
```

- Replace `path/to/your_service_account.json` with the full path to your downloaded JSON file.
- Replace `your_google_sheet_id` with the actual Sheet ID.
- Add other optional vars as needed (e.g., for basic auth in site configs).

**Note:** Never commit `.env` to version control; it's gitignored. For demo mode, Google Sheets setup is optional as exports are skipped.

## Step 5: Run Tests

Verify everything works by running the test suite:

```bash
pytest
```

This runs unit and integration tests, including the demo mode, without requiring network access.

## Troubleshooting

- **Command not found (`ws`)**: Ensure the virtual environment is activated and `pip install -e .` was run.
- **Python version issues**: Check with `python --version`. Upgrade if below 3.10.
- **Google Sheets auth errors**: Verify the service account has access to the sheet and the JSON path is correct.
- **Dependency conflicts**: Use a fresh virtual environment.

For more details on running the demo or operations, see [docs/demo.md](demo.md) and [docs/ops.md](ops.md).

---

*Last updated: October 2024*