# This file just contains a blocklist of the JWT tokens. 
# It will be imported by app and the logout resource so that tokens
# can be added to the blocklist when the user logs out.
#
# probably should use a database here, such as reddis (for max performance)
# the reason why if you restart the app this blocklist now is empty

BLOCKLIST = set()