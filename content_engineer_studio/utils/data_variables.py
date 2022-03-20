import pandas as pd
from dataclasses import dataclass
from enum import Enum, auto


class Data(Enum):

    # Sets the number of prebuffered windows for auto mode
    BUFFER = 2

    LIVECHAT_URL = "https://www.cleverbot.com/"

    DUMMY_DF = pd.DataFrame([0, 0])

    ROLES = [
        "None",
        "Bot",
        "Customer",
        "Multi-Choice",
        "Editable",
        "Correct FAQ",
        "Link",
    ]

    MULTIPLE_CHOICE = ["", "Ja", "Nein", "Teilweise"]

    EXAMPLE_FLOWS = ["Some flow", "Some other flow", "Example flow", "Some FAQ"]

    EXAMPLE_ACTIONS = [
        "Some action",
        "Some other action",
        "Example action",
        "Example FAQ",
    ]

    EXAMPLE_CHAT = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In porttitor ligula ac turpis eleifend blandit.",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In porttitor ligula ac turpis eleifend blandit. In elementum velit quis turpis lobortis finibus. Morbi ex dui, facilisis sed mattis ut, vulputate ac odio. Ut rhoncus, quam sed accumsan tempor, purus felis egestas quam, quis pulvinar libero justo at sem. Fusce ac volutpat sapien. Vestibulum pretium ullamcorper fermentum. Mauris vitae eleifend dolor. Sed vel neque et enim ornare consequat. In nec placerat metus. Duis feugiat tellus vel justo faucibus euismod. ",
        "Ut rhoncus, quam sed accumsan tempor, purus felis egestas quam, quis ",
        "Vestibulum pretium ullamcorper fermentum. Mauris vitae eleifend dolor. Sed vel neque et enim ornare consequat. In nec placerat metus. Duis feugiat tellus vel justo faucibus euismod. ",
        "Suspendisse",
        "Suspendisse suscipit, tellus ut varius aliquam, tortor enim placerat sem, sit amet porta eros tellus ultrices risus. Etiam lobortis sapien consectetur felis elementum, in commodo sem pharetra. Vivamus eget risus molestie, pulvinar orci in, viverra nunc. Quisque elit eros, suscipit sed quam sed, pretium feugiat mi.",
        "Nunc et condimentum ligula. Vivamus porta volutpat gravida. Morbi molestie arcu vel commodo tempus. Duis aliquam quis felis at posuere. Aliquam aliquet ipsum erat, eu tincidunt dolor vehicula at. Sed dolor augue, maximus ut blandit at, iaculis vitae dolor. Vestibulum quis erat egestas, fringilla tortor non, mollis libero. ",
        "Aenean massa nisi, tincidunt non lectus ac, auctor commodo turpis.",
    ]
