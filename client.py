import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import firebase_admin
from firebase_admin import db, credentials

from firebase_client.firebase_navigation import FirebaseClient as FCL


TOKEN = 'TOKEN'
bot = telebot.TeleBot(TOKEN)

# ----------------------------------------------------------------------------------------------------

cred = credentials.Certificate("firebase_client/credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://journalbot-d5d2b-default-rtdb.europe-west1.firebasedatabase.app/'
})

class Interface:
    def __init__(self) -> None:
        self.bot_cmd = {
            'start': {
                'response': "Welcome! First, select a language\n\nПривет, для начала выбери язык",
                'en': {
                    'description': 'Onboarding and initial bot configuration',
                    'response': "Hey, let's begin our setup"
                },
                'ru': {
                    'description': 'Знакомство и первоначальная конфигурация бота',
                    'response': 'Привет, давай начнем настройку!'
                }
            },
            'create': {
                'en': {
                    'description': 'Create a new journal',
                    'response': 'What is the name for your journal?'
                },
                'ru': {
                    'description': 'Создать новый журнал',
                    'response': 'Придумай название для журнала'
                }
            },
            'report': {
                'en': {
                    'description': 'Report a bug or suggest a feature',
                    'response': 'What do you wish to tell us?'
                },
                'ru': {
                    'description': 'Сообщить об ошибке или порекомендовать фичу',
                    'response': 'Что ты хочешь нам рассказать?'
                }
            }
        }
        self.journal_cmd = {
            'add': {
                'en': {
                    'description': 'Add a new record',
                    'response': ''
                },
                'ru': {
                    'description': 'Добавить новую запись',
                    'response': ''
                }
            },
            'edit': {
                'en': {
                    'description': 'Edit the jounal',
                    'response': ''
                },
                'ru': {
                    'description': 'Редактировать запсь',
                    'response': ''
                }
            },
            'createsub': {
                'en': {
                    'description': 'Create a new nested journal',
                    'response': 'What is the name for your journal?'
                },
                'ru': {
                    'description': 'Создать новый вложенный журнал',
                    'response': 'Придумай название для журнала'
                }
            }
        }
        self.record_cmd = {
            'edit': {
                'en': {
                    'description': 'Edit the jounal',
                    'response': ''
                },
                'ru': {
                    'description': 'Редактировать запсь',
                    'response': ''
                }
            }
        }
        self.preferences_markup = {
            'lang': [
                {
                    'button': 'English',
                    'callback': 'en'
                },
                {
                    'button': 'Русский',
                    'callback': 'ru'
                }
            ],
            'default': {
                'en': {
                    'caption': "Your default journal will be used to store any message you send " +
                            "without selecting any other journal or any other action\n\nBy default it's set to 'Ideas'",
                    'response': 'Enter the name for your default journal',
                    'response_on_completion': 'All set! You can start exploring what I can do by typing /help or selecting it from the menu',
                    'button': 'Edit default journal',
                    'callback': 'edj'
                },
                'ru': {
                    'caption': "Журнал по умолчанию используется для хранения любых сообщений, " +
                            "для которых ты не выбрал журнал или любое другое действие\n\nПо умолчанию он называется 'Идеи' ",
                    'response': 'Придумайте имя для журнала по умолчанию',
                    'response_on_completion': 'Настройка завершена, ты можешь узнать все возможности бота с напечатав команду /help или выбрав её в меню',
                    'button': 'Изменить журнал по умолчанию',
                    'callback': 'edj'
                }
            }
        }
        self.bot_init_markup = {
            'create': {
                'en': {
                    'button': 'Create a new journal',
                    'callback': 'crj',
                    'response': 'What is the name for your journal?'
                },
                'ru': {
                    'button': 'Создать новый журнал',
                    'callback': 'crj',
                    'response': 'Придумай название для журнала'
                }
            }
        }
        self.call_interpretation = {
            'cb_en': {
                'response': 'Your language is set to',
                'interpretation': 'English'
            },
            'cb_ru': {
                'response': 'Ваш язык изменен на',
                'interpretation': 'Русский'
            }
        }
        self.sessions = {
            'default_journal_setup': False,
            'open_message': True,  # Any message while this session is active directs to the default journal
            'onboarding': True
        }
        self.bot_lang = ''
        self.firebase_client =  FCL()
    
    def get_user_preferences(self, route):
        if route == 'lang':
            if not self.bot_lang:
                return db.reference(f'/{self.user_id}/preferences/{route}').get()
            else:
                return self.bot_lang
    
    def global_cmd(self):
        bot.delete_my_commands()
        bot.set_my_commands(
            commands=[
                *[telebot.types.BotCommand(cmd, descr) for cmd, descr in
                    zip([cmd for cmd in self.bot_cmd.keys()], [descr['description'] for descr in [val[self.get_user_preferences('lang')] for val in self.bot_cmd.values()]])
                ]
            ]
        )
    
    def update_markup(self, markup_source, type):
        if type == 'lang':
            self.lang_markup = InlineKeyboardMarkup()
            self.lang_markup.row_width = len(markup_source)
            self.lang_markup.add(
                *[InlineKeyboardButton(markup['button'], callback_data=f'cb_{markup['callback']}') for markup in markup_source]
            )

        elif type == 'default' or type=='init':
            self.setup_markup = InlineKeyboardMarkup()
            self.setup_markup.row_width = len(markup_source)
            markup = markup_source[self.get_user_preferences('lang')]
            self.setup_markup.add(
                InlineKeyboardButton(markup['button'], callback_data=f'cb_{markup['callback']}')
            )

    def start(self, message):
        self.firebase_client.start_fcl(message)
        self.user_id = message.from_user.id
        self.update_markup(self.preferences_markup['lang'], 'lang')
        bot.send_message(message.chat.id, self.bot_cmd['start']['response'], reply_markup=self.lang_markup)
    
    def create(self, call):
        bot.edit_message_text(call.id, self.bot_cmd['create'][self.get_user_preferences('lang')]['response'])
    
    def changeLangEdit(self, call):  # Just for cosmetic options
        bot.edit_message_text(chat_id=call.message.chat.id, text=f'{self.call_interpretation[call.data]['response']} {self.call_interpretation[call.data]['interpretation']}', 
                              message_id=call.message.message_id, reply_markup=self.lang_markup)
    
    def changeLangDelete(self, call):  # Just for cosmetic options
        self.bot_lang = self.firebase_client.lang_fcl(call)
        self.global_cmd()
        bot.answer_callback_query(call.id, f'{self.call_interpretation[call.data]['response']} {self.call_interpretation[call.data]['interpretation']}')
        # Bot sends message ... now let's continue the setup: default ideas folder, etc.
        self.update_markup(self.preferences_markup['default'], 'default')
        bot.send_message(chat_id=call.message.chat.id, 
                         text=self.preferences_markup['default'][self.get_user_preferences('lang')]['caption'],
                         reply_markup=self.setup_markup)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    
    def editDefaultJournal(self, call):
        self.sessions['default_journal_setup'] = True
        self.default_setup_call_copy, self.default_setup_message_copy = call, call.message
        bot.send_message(chat_id=call.message.chat.id, text=self.preferences_markup['default'][self.get_user_preferences('lang')]['response'])
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    
    def handleAnyMessage(self, message):
        if self.sessions['default_journal_setup'] and self.sessions['onboarding']:
            print(message.text, self.sessions['onboarding'])  # Refactor all this mess, add first time check (onboarding), etc.
            # Default journal is "Ideas" by default, so if user decides not to change it 
            #       and sends open message right off the bat update self.sessions['default_journal_setup']
            if len(message.text) < 15 and message.text != str(message.from_user.id):
                self.firebase_client.default_fcl(message, 'setup')
                self.sessions['default_journal_setup'] = False
            # Maybe instead of deleting the message change it to some stiker (make custom stickers for the bot in Midjourney)
            bot.delete_message(chat_id=message.chat.id, message_id=self.default_setup_message_copy.message_id + 1)
            bot.answer_callback_query(self.default_setup_call_copy.id, f'Default folder set to {message.text}')
            self.update_markup(self.bot_init_markup['create'], 'init')
            bot.send_message(chat_id=message.chat.id,
                             text=self.preferences_markup['default'][self.get_user_preferences('lang')]['response_on_completion'],
                             reply_markup=self.setup_markup)

        elif self.sessions['open_message'] and not self.sessions['default_journal_setup']:  # To "Ideas"
            # Slay queen
            self.firebase_client.default_fcl(message, 'open')
            self.firebase_client.push_fcl(message, 'open_message')
            self.sessions['default_journal_setup'] = True

        elif self.sessions['open_message'] and self.sessions['default_journal_setup']:  # To custom default journal
            self.firebase_client.push_fcl(message, 'open_message')
        
        self.sessions['onboarding'] = False

# -------------------------------------------------------------------------------------------------

interface = Interface()

@bot.message_handler(commands=['start'])
def start(message) -> None:
    interface.start(message)

@bot.callback_query_handler(func=lambda call: True)
def preferences(call):
    if call.data == 'cb_back':
        pass
    elif call.data == 'cb_en' or call.data == 'cb_ru':
        interface.changeLangDelete(call)
    elif call.data == 'cb_edj':
        interface.editDefaultJournal(call)

@bot.message_handler(content_types=['text'])
def open_message(message):
    interface.handleAnyMessage(message)


if __name__ == '__main__':
    bot.infinity_polling()
