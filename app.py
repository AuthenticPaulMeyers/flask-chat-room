from flask import Flask, render_template, session, redirect, request, url_for
from flask_socketio import SocketIO, join_room, leave_room
import random
from string import ascii_uppercase


app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecretkey'
socketio=SocketIO(app)

# global dictionary to store the rooms
rooms = {}

# generate a four digital code
def generate_random_code(length):
    while True:

        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break
    return code



# default home route
@app.route("/", methods=['GET', 'POST'])
def home():
    session.clear()
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        join = request.form.get('join', False)
        create = request.form.get('create', False)

        if name == "":
            return render_template('home.html', error='Name field cannot be empty!', name=name, code=code)
        
        if join != False and not code:
            return render_template('home.html', error='Enter room code to join chat!', name=name, code=code)
        
        room = code
        if create != False:
            room = generate_random_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template('home.html', error='Room does not exist!', name=name, code=code)
        

        session['name'] = name
        session['room'] = room 
        return redirect(url_for('room'))
        
    return render_template('home.html', title='Home')

# the chat room route 
@app.route('/room')
def room():
    # Check if the user is logged in to access this route
    room = session.get('room')
    name = session.get('name')

    if name is None or room is None or room not in rooms:
        return redirect(url_for('home'))
    
    return render_template('room.html')

if __name__=="__main__":
    socketio.run(app, debug=True)