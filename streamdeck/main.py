from frctools.streamdeck import StreamDeckBoard
from frctools.streamdeck.keys import StreamDeckKeyBool

from frc_streamdeck import ReefSelector

import ntcore


# Initialize the network table
nt = ntcore.NetworkTableInstance.getDefault()
nt.startClient4('streamdeck')
nt.setServer('localhost', ntcore.NetworkTableInstance.kDefaultPort4)

# Initialize the board
board = StreamDeckBoard()

# Add the is connected key to the top right
board.set_key((7, 3), StreamDeckKeyBool(label='Is Connected', true_img='green', false_img='red').bind_nt_connected())

# Add the reef selector to the left
reef = ReefSelector(board)

# Start the stream deck
board.start()
board.wait_forever()
