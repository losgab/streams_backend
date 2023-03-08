ITERATION 1:

channel_messages_v1
- if a channel has zero messages, and channel_messages_v1 is called with start 0, it will not cause an error but output an empty messages list
- if start is a negative integer, it will raise an InputError

auth_register and channel_create
- All IDs start from the 0th index and not from the first, and increment by 1 for each user

ITERATION 2:

session tokens
- If a user has been removed then also all of their session tokens are removed and they are logged out automatically

message/remove/v1
- if you try to remove an already-removed message, it will raise an InputError

ITERATION 3:

channel/messages/v1 + dm/messages/v1
- Hardcoded the output of the reacts output, as react_id = 1 is only available on the frontend
    (can be adjusted later if we want to implement more react_id's)
    e.g.
    'reacts': [
        {
            'react_id': 1,
            'u_ids': message['reacts'],
            'is_this_user_reacted': True if auth_user_id in message['reacts'] else False
        }
    ],
