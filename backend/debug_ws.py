from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
with client.websocket_connect('/ws/chat') as ws:
    ws.send_json({'type':'init'})
    init = ws.receive_json()
    print('INIT', init)
    sid = init.get('session_id')
    ws.send_json({'type':'user','session_id':sid,'text':'Hello there'})
    for i in range(10):
        try:
            msg = ws.receive_json()
            print('MSG', i, msg)
        except Exception as e:
            print('RECV ERROR', e)
            break
