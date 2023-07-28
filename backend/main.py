from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/greet', methods=['GET'])
def greet():
    name = request.args.get('name')
    if name:
        message = f'Hello, {name}!'
    else:
        message = 'Please provide a name parameter.'
    return jsonify({'message': message})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=6000)

