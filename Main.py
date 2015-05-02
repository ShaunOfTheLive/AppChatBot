from AppChatBot import AppChatBot

def main():
    desired_username = 'chatbot'

    appchatbot = AppChatBot('config.json')

    if appchatbot.is_registered():
        appchatbot.sign_in()
    else:
        appchatbot.register()
        appchatbot.change_username(desired_username)
        # TODO: handle error if username is taken

    rooms = appchatbot.get_rooms()
    if(len(rooms) == 0 or 
       rooms[0].get('packageName') != 'com.android.calculator2'):
        rooms = [{"name":"Calculator","packageName":"com.android.calculator2"}]
        appchatbot.join_rooms(rooms)

    appchatbot.post_message('com.android.calculator2', 'BOT TEST')

if __name__ == "__main__":
    main()
