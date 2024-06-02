from flask import Flask, request, jsonify
from telethon import TelegramClient, events
import re

access_token = "FEhHn8cxXW2ZKWyV5i3cPkFAR6U7II"
telegram_api_id = 26808455
telegram_api_hash = "784b6198c9cc5c8218b5642cfa8540df"
account_phone_number = '+14708002362'
encryption_key = "scrapperbot77"
chat_id = -4237312374

app = Flask(__name__)
return_data = {}


#check bank identity number
@app.route('/api/chkbin', methods=['POST'])
async def check_bin():
    data = request.get_json()
    if(data.get('access_token') != access_token):
        return jsonify({'error':'Token is invalid'}), 400
    else:
        message = '/bin ' + data.get('bin')
        # message = '<bold>BIN Lookup Result </bold>'
        async with TelegramClient('anon', telegram_api_id, telegram_api_hash) as tg:
            message = await tg.send_message(-4237312374, message, parse_mode='html')
            reply_msg_id = 0
            @tg.on(events.NewMessage)
            async def new_message_handler(event):
                if event.message.reply_to_msg_id == message.id:
                    # Get the replied message
                    
                    global reply_msg_id
                    reply_msg_id = event.message.id
                    
                    
            @tg.on(events.MessageEdited)
            async def edit_message_handler(event):
                global reply_msg_id
                
                if event.message.id == reply_msg_id:
                    response_message = event.message
                    pattern = r"🔍"
                    error_pattern = r"🚫"
                    if re.search(pattern=pattern, string = response_message.message):
                        api_response = response_message.message
                        api_response_str = str(api_response)
                        lines = api_response_str.split('\n')

                        # Extract the values
                        bin_number = lines[2].split('⇾')[1].strip()
                        card_type = lines[4].split('⇾')[1].strip()
                        issuer = lines[5].split('⇾')[1].strip()
                        country = lines[6].split('⇾')[1].strip()

                        # Assemble the result as a list
                        global return_data
                        return_data = {
                            'bin_num': bin_number,
                            'card_type': card_type,
                            'issuer': issuer,
                            'country': country,
                            'error':''
                        }
                        
                        await tg.disconnect()
                        
                    if re.search(pattern=error_pattern, string = response_message.message):
                        error_msg = response_message.message.split('🚫')[1]
                        return_data = {
                            'error': error_msg
                        }
                        
                        await tg.disconnect()
                    
            tg.add_event_handler(new_message_handler, events.NewMessage)
            tg.add_event_handler(edit_message_handler, events.MessageEdited)
            
            await tg.run_until_disconnected()

        return jsonify(return_data), 201

#get creditcard numbers with bin
@app.route('/api/getCardNums', methods=['POST'])
async def get_card_nums():
    data = request.get_json()
    print('card generate request:', data)
    if(data.get('access_token') != access_token):
        return jsonify({'message':'Token is invalid'}), 400
    else:
        message = '/gen ' + data.get('bin')
        
        async with TelegramClient('anon', telegram_api_id, telegram_api_hash) as tg:
            message = await tg.send_message(-4237312374, message )
            reply_msg_id = 0
            @tg.on(events.NewMessage)
            async def new_message_handler(event):
                if event.message.reply_to_msg_id == message.id:
                    # Get the replied message
                    global reply_msg_id
                    reply_msg_id = event.message.id
                    
                    
            @tg.on(events.MessageEdited)
            async def edit_message_handler(event):
                global reply_msg_id
                if event.message.id == reply_msg_id:
                    response_message = event.message
                    pattern = r"𝗕𝗜𝗡"
                    error_pattern = r"🚫"
                    if re.search(pattern=pattern, string = response_message.message):
                        card_num_list = []
                        api_response = response_message.message
                        api_response_str = str(api_response)
                        lines = api_response_str.split('\n')
                        for i in range(3, 13):
                            card_num_list.append(lines[i].split('|')[0])
                        
                        global return_data
                        return_data = { 
                            'card_nums' : card_num_list,
                            'error': ''
                        }
                        await tg.disconnect()
                        
                    if re.search(pattern=error_pattern, string = response_message.message):
                        error_msg = response_message.message.split('🚫')[1]
                        return_data = {
                            'card_nums' : [],
                            'error': error_msg
                        }
                        await tg.disconnect()
                    
            tg.add_event_handler(new_message_handler, events.NewMessage)
            tg.add_event_handler(edit_message_handler, events.MessageEdited)
            
            await tg.run_until_disconnected()

        return jsonify(return_data), 201

if __name__ == '__main__':
    app.run(debug=True, port = 8010)
