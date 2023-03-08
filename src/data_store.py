'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

## YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    # these are lists within lists
    'users': [],
    'channels': [],
    'dms' : [],
}
## YOU SHOULD MODIFY THIS OBJECT ABOVE

# # DATA STRUCTURE VISUALISATION
'''
Values are data types for the particular key
initial_object = {
    'users': [ # structure of each element: id, email, password, name_first, name_last, handle, permission_id
        # 2 Users registed Data Setup Example
        { 
            'u_id': integer1,
            'email': string, 
            'password': string,
            'name_first': string, 
            'name_last': string,
            'handle_str': string,
            'permission_id': integer,
            'notifications': [],
            'tagged_messages_notified': [],
            'channels_joined': [],
            'dms_joined': [],
            'messages_sent': [],
            'involvement_rate': float,
            'profile_img_url': string,
            'removed': boolean,
        }, 
        {
            'u_id': integer2,
            'email': string, 
            'password': string,
            'name_first': string, 
            'name_last': string,
            'handle_str': string,
            'permission_id': integer,
            'notifications': [],
            'tagged_messages_notified': [],
            'channels_joined': [],
            'dms_joined': [],
            'messages_sent': [],
            'involvement_rate': float,
            'profile_img_url': string,
            'removed': boolean,
        }
    ],

    'channels': [ # structure of each element: id, owners, name, is_public, members, messages
        # 2 Channel Data Setup Example 
        # Channel 1 - Only id1 has access
        # Channel 2 - Both id1 and id2 have access
        {
            'channel_id': integer1,
            'owners': [auth_user_id1], 
            'name': string, 
            'is_public': boolean,
            'members': [auth_user_id1],
            'messages': [
                {
                    'message_id': integer,
                    'u_id': integer,
                    'message': string,
                    'time_sent': integer
                    'reacts': [auth_user_id1],
                    'is_pinned': boolean
                },
                {
                    'message_id': integer,
                    'u_id': integer,
                    'message': string,
                    'time_sent': integer
                    'reacts': [auth_user_id1],
                    'is_pinned': boolean
                }
            ]
        }, 
        {
            'channel_id': integer2,
            'owners': [auth_user_id1], 
            'name': string, 
            'is_public': boolean,
            'members': [auth_user_id1, auth_user_id2],
            'messages': [
                {
                    'message_id': integer,
                    'u_id': integer,
                    'message': string,
                    'time_sent': integer
                },
                {
                    'message_id': integer,
                    'u_id': integer,
                    'message': string,
                    'time_sent': integer
                }
            ]
        }
    ],
    'dms': [
        {
            'dm_id': integer,
            'owner': auth_id,
            'name': string,
            'members': [list of u_ids],
            'messages': [list of dictionary messages]
            'removed': boolean
        }
    ]
}
'''
# END DATA STRUCTURE VISUALISATION

## YOU ARE ALLOWED TO CHANGE THE BELOW IF YOU WISH
class Datastore:
    def __init__(self):
        self.__store = initial_object

    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store

print('Loading Datastore...')

global data_store
data_store = Datastore()
