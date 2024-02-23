import firebase_admin
from firebase_admin import db, credentials


class FirebaseClient:
    def __init__(self) -> None:
        db.reference('/').delete()
        self.sessions = {
            'default_journal': False
        }

    def start_fcl(self, message):
        self.user_id = message.from_user.id
        if not db.reference(f'/{self.user_id}').get():
            db.reference('/').update({
                self.user_id: {}
            })

        if not db.reference(f'/{self.user_id}/credentials').get():
            db.reference(f'/{self.user_id}').update({
                'credentials': {
                    'chat_id': message.chat.id
                }
            })
    
    def lang_fcl(self, call):
        db.reference(f'/{self.user_id}/preferences').update({
            'lang': call.data[3:]
        })
    
    def default_fcl(self, call, type):
        self.lang = db.reference(f'/{self.user_id}/preferences/lang').get()
        if type=='setup':
            db.reference(f'/{self.user_id}/preferences').update({
                'default_journal': call.text
            })
            self.sessions['default_journal'] = True

        elif type=='open' and not self.sessions['default_journal']:
            db.reference(f'/{self.user_id}/preferences').update({
                'default_journal': 'Ideas' if self.lang == 'en' else 'Идеи'
            })
            self.sessions['default_journal'] = True

        self.default_journal = db.reference(f'/{self.user_id}/preferences/default_journal').get()
    
    def push_fcl(self, call, type):
        if type=='open_message':
            # Initializing default journal
            db.reference(f'/{self.user_id}/data/journals/{self.default_journal}').update({
                call.date: call.text
            })