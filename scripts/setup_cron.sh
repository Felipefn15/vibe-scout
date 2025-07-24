#!/bin/bash

# Setup script for Vibe Scout Daily Campaign
# This script sets up the cron job to run the daily campaign at 8 AM

echo "=== Vibe Scout Daily Campaign Setup ==="

# Get the current directory (project root)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "Project directory: $PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "❌ Virtual environment not found. Please run 'python3 -m venv venv' first."
    exit 1
fi

# Create the cron job command
PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
SCRIPT_PATH="$PROJECT_DIR/scheduler/daily_campaign.py"
LOG_PATH="$PROJECT_DIR/logs/cron.log"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

# Create the cron job entry (runs at 8 AM daily)
CRON_JOB="0 8 * * * cd $PROJECT_DIR && $PYTHON_PATH $SCRIPT_PATH --run-now >> $LOG_PATH 2>&1"

echo "Cron job to be created:"
echo "$CRON_JOB"
echo ""

# Ask for confirmation
read -p "Do you want to add this cron job? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Add the cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    
    if [ $? -eq 0 ]; then
        echo "✅ Cron job added successfully!"
        echo "📅 The daily campaign will run at 8:00 AM every day"
        echo "📝 Logs will be saved to: $LOG_PATH"
        echo ""
        echo "To view current cron jobs:"
        echo "crontab -l"
        echo ""
        echo "To remove the cron job:"
        echo "crontab -e"
        echo "Then delete the line with the Vibe Scout job"
    else
        echo "❌ Failed to add cron job"
        exit 1
    fi
else
    echo "❌ Cron job not added"
    exit 1
fi

echo ""
echo "=== Setup Complete ==="
echo "The daily campaign will now run automatically at 8:00 AM"
echo "You can also run it manually with:"
echo "cd $PROJECT_DIR && source venv/bin/activate && python scheduler/daily_campaign.py --run-now" 