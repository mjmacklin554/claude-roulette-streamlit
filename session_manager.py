"""
Session management functions for Michael's Roulette System
Handles saving, loading, and managing session history
"""

import streamlit as st
import json
import os
from datetime import datetime

HISTORY_FOLDER = "session_history"


def ensure_history_folder():
    """Create history folder if it doesn't exist"""
    if not os.path.exists(HISTORY_FOLDER):
        os.makedirs(HISTORY_FOLDER)


def save_session(session_data):
    """Save session to JSON file"""
    ensure_history_folder()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"session_{timestamp}.json"
    filepath = os.path.join(HISTORY_FOLDER, filename)

    with open(filepath, 'w') as f:
        json.dump(session_data, f, indent=2)

    return filename


@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_all_sessions():
    """Load all session files and return as list"""
    ensure_history_folder()
    sessions = []

    if not os.path.exists(HISTORY_FOLDER):
        return sessions

    files = [f for f in os.listdir(HISTORY_FOLDER) if f.endswith('.json')]

    for filename in sorted(files, reverse=True):  # Most recent first
        filepath = os.path.join(HISTORY_FOLDER, filename)
        try:
            with open(filepath, 'r') as f:
                session = json.load(f)
                session['filename'] = filename
                sessions.append(session)
        except Exception as e:
            st.warning(f"Error loading {filename}: {str(e)}")

    return sessions


def delete_session(filename):
    """Delete a session file"""
    filepath = os.path.join(HISTORY_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_available_files(numbers_folder):
    """Get list of available outcome files from numbers folder"""
    available_files = []
    if os.path.exists(numbers_folder):
        files = [f for f in os.listdir(numbers_folder) if f.endswith(('.xls', '.xlsx', '.csv', '.txt'))]
        # Sort files by date (format: YYYY-MM-DD_nnn)
        # Extract date portion before underscore for sorting
        available_files = sorted(files, key=lambda x: x.split('_')[0] if '_' in x else x)
    return available_files
