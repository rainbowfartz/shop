# from flask import Flask, render_template, session, redirect, url_for, flash
# from datetime import datetime, timedelta
# import random
# import shelve

# app = Flask(__name__)
# app.secret_key = 'supersecretkey'  # Change this to a more secure key

# # Shelve file for data storage
# SHELVE_FILE = 'claw_machine_data.shelve'

# class ClawMachine:
#     def __init__(self):
#         self.last_play_key = 'last_play'
#         self.play_frequency = timedelta(hours=24)

#     def can_play(self):
#         if self.last_play_key in session and datetime.now() - session[self.last_play_key] < self.play_frequency:
#             raise PermissionError('You can only play once every 24 hours!')
#         return True

#     def play(self):
#         if self.can_play():
#             # Simulate the claw machine game
#             user_wins = random.choice([True, False])
#             # Update the last play time
#             session[self.last_play_key] = datetime.now()
#             return user_wins

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/play')
# def play_game():
#     claw_machine = ClawMachine()

#     try:
#         if claw_machine.play():
#             flash('Congratulations! You won a prize!', 'success')
#         else:
#             flash('Sorry, you didn\'t win this time. Try again tomorrow!', 'info')
#     except PermissionError as e:
#         flash(str(e), 'danger')

#     return redirect(url_for('home'))

# @app.route('/claw_machine')
# def claw_machine():
#     return render_template('claw_machine.html')

# if __name__ == '__main__':
#     app.run(debug=True)