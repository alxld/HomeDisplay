import gpsoauth

email = 'aarondeno11@gmail.com'
android_id = '0123456789abcdef'
token = 'oauth2_4/0AanRRrt6YOau779X1JLLtDu3IvSpIjhRzuTK5IEBDAvbl-hYxnNEE9l9PWB1graXr6yi7w'

master_response = gpsoauth.exchange_token(email, token, android_id)
master_token = master_response['Token']  # if there's no token check the response for more details

auth_response = gpsoauth.perform_oauth(
    email, master_token, android_id,
    service='sj', app='com.google.android.music',
    client_sig='...')
token = auth_response['Auth']
print(token)