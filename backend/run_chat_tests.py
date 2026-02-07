from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def run():
    print('Running quick WebSocket chat tests...')
    try:
        with client.websocket_connect('/ws/chat') as ws:
            ws.send_json({'type':'init'})
            msg = ws.receive_json()
            print('INIT response:', msg)
            session_id = msg['session_id']

            ws.send_json({'type':'user','session_id':session_id,'text':'Hello there'})
            full = ''
            while True:
                chunk = ws.receive_json()
                print('CHUNK:', chunk)
                full += ' ' + chunk['text']
                if not chunk.get('partial', False):
                    break
            print('FINAL:', full)

        with client.websocket_connect('/ws/chat') as ws:
            ws.send_json({'type':'init','context':{'transliteration':{'explanation':'Because of fidelity to original orthography.'}}})
            msg = ws.receive_json()
            print('INIT w/context response:', msg)
            session_id = msg['session_id']
            ws.send_json({'type':'user','session_id':session_id,'text':'Please explain transliteration.'})
            full = ''
            while True:
                chunk = ws.receive_json()
                print('CHUNK:', chunk)
                full += ' ' + chunk['text']
                if not chunk.get('partial', False):
                    break
            print('FINAL context reply:', full)
    except Exception as e:
        print('Test failed:', e)


if __name__ == '__main__':
    run()
