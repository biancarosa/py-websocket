import asyncio
import socketio
import logging

from sanic import Sanic

sio = socketio.AsyncServer(async_mode='sanic')
app = Sanic()
sio.attach(app)


async def background_task():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        await sio.sleep(10)
        count += 1
        await sio.emit('my response', {'data': 'Server generated event'},
                       namespace='/test')


@app.listener('before_server_start')
def before_server_start(sanic, loop):
    sio.start_background_task(background_task)

@sio.on('my event', namespace='/test')
async def test_message(sid, message):
    await sio.emit('my response', {'data': message['data']}, room=sid,
                   namespace='/test')

@sio.on('disconnect request', namespace='/test')
async def disconnect_request(sid):
    await sio.disconnect(sid, namespace='/test')


@sio.on('connect', namespace='/test')
async def test_connect(sid, environ):
    logging.INFO("User {} logged in".format(sid))
    await sio.emit('my response', {'data': 'Connected', 'count': 0}, room=sid,
                   namespace='/test')


@sio.on('disconnect', namespace='/test')
def test_disconnect(sid):
    print('Client disconnected')

if __name__ == '__main__':
    app.run(port=8080)
