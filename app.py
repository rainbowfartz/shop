
from flask import Flask, render_template, session, redirect, url_for, flash
from datetime import datetime, timedelta
import random
import shelve

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this to a more secure key

# Shelve file for data storage
SHELVE_FILE = 'claw_machine_data.shelve'

class ClawMachine:
    def __init__(self):
        self.last_play_key = 'last_play'
        self.play_frequency = timedelta(hours=24)
        self.max_daily_plays = 3  # Maximum allowed plays per day
    
    def can_play(self):
        if self.last_play_key in session:
            plays_today = session.get('plays_today', 0)
            if plays_today >= self.max_daily_plays:
                raise PermissionError('You have reached the maximum number of plays for today!')
            
            # Increment the plays_today counter
            session['plays_today'] = plays_today + 1

            if datetime.now() - session[self.last_play_key] < self.play_frequency:
                raise PermissionError('You can only play once every 24 hours!')
        else:
            # First play of the day, reset the plays_today counter
            session['plays_today'] = 1

        return True

    def play(self):
        if self.can_play():
            # Simulate the claw machine game
            user_wins = random.choice([True, False])
            
            # Save the user's result to the database
            user_data = shelve.open(SHELVE_FILE)
            try:
                if 'user_wins' not in user_data:
                    user_data['user_wins'] = {}

                play_number = session['plays_today']
                user_data['user_wins'][f'Try {play_number}'] = 'Win' if user_wins else 'Lose'

            finally:
                user_data.close()

            # Update the last play time
            session[self.last_play_key] = datetime.now()
            return user_wins

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play')
def play_game():
    claw_machine = ClawMachine()

    try:
        if claw_machine.play():
            flash('Congratulations! You won a prize!', 'success')
        else:
            flash('Sorry, you didn\'t win this time. Try again tomorrow!', 'info')
    except PermissionError as e:
        flash(str(e), 'danger')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)