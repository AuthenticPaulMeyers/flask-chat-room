from flask import Flask, render_template, session, redirect, request, url_for
from flask_socketio import SocketIO, join_room, leave_room, send
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
            return render_template('home.html', error='Chat does not exist!', name=name, code=code)
        

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
    
    return render_template('room.html', room=room, title="Chat Room")

# connect to the socket function for the user to join the room
@socketio.on('connect')
def connect(auth):
    name = session.get('name')
    room = session.get('room')

    if not room or not room:
        return 
    
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "joined the chat!"}, to=room)
    rooms[room]['members'] += 1

# disconnect to the socket function for the user to leave the room
@socketio.on('disconnect')
def disconnect():
    name = session.get('name')
    room = session.get('room')

    leave_room(room)

    if room in rooms:
        rooms[room]['members'] -= 1
        if rooms[room]['members'] <= 0:
            del rooms[room]    

    send({"name": name, "message": "left the chat!"}, to=room)

# socket allow the sending and receiving of messages
@socketio.on('message')
def message(data):
    name = session.get('name')
    room = session.get('room')

    if room not in rooms: 
        return
    
    # save the messages in the dctionary

    content = {
        'name': name,
        'message': data['data']
    }

    send(content, to=room)
    rooms[room]['messages'].append(content)

if __name__=="__main__":
    socketio.run(app, debug=True)