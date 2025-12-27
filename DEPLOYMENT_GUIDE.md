# Deployment Guide: OpenRouter Key Manager on Railway

This guide will help you deploy the OpenRouter Key Manager as a daily cron job on Railway with persistent storage for your usage history.

## Prerequisites

1.  A **Railway account**.
2.  An **OpenRouter Provisioning API Key** (Get it from [openrouter.ai/settings/provisioning-keys](https://openrouter.ai/settings/provisioning-keys)).
3.  The codebase pushed to a **GitHub repository**.

## Deployment Steps

### 1. Create a New Project on Railway
- Go to [Railway](https://railway.app/) and click **"New Project"**.
- Select **"Deploy from GitHub repo"** and choose your repository.

### 2. Configure a Persistent Volume
The SQLite database stores your 7-day usage history. To prevent data loss when the cron job container shuts down, you **must** attach a volume:
1.  In your Railway project, click **"Add Service"** (or select your existing service).
2.  Go to the **"Settings"** tab.
3.  Scroll down to the **"Volumes"** section and click **"Add Volume"**.
4.  Set the **Mount Path** to `/data`.
5.  Click **"Save"**.

### 3. Set Environment Variables
Go to the **"Variables"** tab of your service and add the following:

| Variable | Value | Description |
| :--- | :--- | :--- |
| `PROVISIONING_API_KEY` | `sk-or-v1-...` | Your OpenRouter Provisioning key. |
| `DB_PATH` | `/data/usage.db` | Path to the database on the mounted volume. |

### 4. Verify Cron Configuration
The project is pre-configured via `railway.json` to run every day at 11:55 PM UTC (just before the midnight reset):
- **Schedule**: `55 23 * * *`
- **Restart Policy**: `NEVER` (This ensures it runs once and stops).

### 5. Deployment
Railway should automatically detect the `Dockerfile` and `railway.json` and start the deployment. 

## Monitoring & Logs

- You can view the execution logs in the **"Deployments"** or **"Logs"** tab of your Railway service.
- The logs will show:
    - Number of keys found.
    - Usage recorded for each key.
    - Calculated 7-day average (excluding outliers).
    - Success/Failure of the limit updates.

## Local Testing

If you want to run the script locally before deploying:
1.  Install dependencies: `pip install -r requirements.txt`
2.  Create a `.env` file with your `PROVISIONING_API_KEY`.
3.  Run: `python main.py`

---
*Note: The first 7 days of runs will use simple averages until enough data is collected for the IQR outlier detection logic to become fully effective.*

