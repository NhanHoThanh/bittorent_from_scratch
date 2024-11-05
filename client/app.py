import streamlit as st
from api import signup, login, announce

st.title('Torrent Tracker Interface')

# Registration
st.header('Register')
username = st.text_input('Username', key='register_username')
password = st.text_input('Password', type='password', key='register_password')
if st.button('Register'):
    response = signup(username, password)
    st.write(response)

# Login
st.header('Login')
login_username = st.text_input('Username', key='login_username')
login_password = st.text_input(
    'Password', type='password', key='login_password')
if st.button('Login'):
    response = login(login_username, login_password)
    st.write(response)
    if 'access' in response:
        st.session_state.access_token = response['access']
        st.write("Login successful. Access token saved.")

# Announce a File
st.header('Announce a File')
info_hash = st.text_input('Info Hash', key='announce_info_hash')
peer_id = st.text_input('Peer ID', key='announce_peer_id')
port = st.number_input('Port', min_value=1, max_value=65535,
                       value=6663, key='announce_port')
uploaded = st.number_input('Uploaded', min_value=0,
                           value=0, key='announce_uploaded')
downloaded = st.number_input(
    'Downloaded', min_value=0, value=0, key='announce_downloaded')
left = st.number_input('Left', min_value=0, value=0, key='announce_left')
event = st.selectbox(
    'Event', ['started', 'completed', 'stopped'], key='announce_event')
compact = st.selectbox('Compact', [0, 1], key='announce_compact')
ip_address = st.text_input('IP Address (optional)', key='announce_ip_address')
if st.button('Announce'):
    if 'access_token' in st.session_state:
        access_token = st.session_state.access_token
        response = announce(access_token, info_hash, peer_id, port, uploaded,
                            downloaded, left, event, compact, ip_address)
        st.write(response)
    else:
        st.write("Please log in first to get an access token.")

# # Get Magnet Link
# st.header('Get Magnet Link')
# magnet_info_hash = st.text_input('Info Hash', key='magnet_info_hash')
# if st.button('Get Magnet Link'):
#     response = get_file(magnet_info_hash)
#     st.write(response)
