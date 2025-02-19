from datetime import datetime

history = []

def add_to_history(url):
    analysis_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    history.append({'url': url, 'time': analysis_time})

def get_history():
    return history

def clear_history():
    global history
    history = []
