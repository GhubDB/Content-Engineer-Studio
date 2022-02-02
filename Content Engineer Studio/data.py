descriptors = [
    ['Ja, hätte besser gemacht werden können', 'Nein, hätte nicht besser gemacht werden können'],
    ['Bot hat Anliegen korrekt erkannt', 'Bot hat Anliegen nicht korrekt erkannt'],
    ['Korrektes FAQ ausgespielt/Flow gestartet', 'Ausgespieltes FAQ/Flow nicht korrekt'],
    ['Kundenanliegen gelöst', 'Kundenanliegen nicht gelöst']
    ]

# add Priorität, bereits in Arbeit?
# add faq paste function 
canned_questions = ['Gibt es Verbesserungspotenzial?', 'Hat der Bot das Anliegen korrekt erkannt?', 'Korrektes FAQ ausgespielt/Flow gestartet?', 'Kundenanliegen gelöst?', 'T2A gerechtfertigt?']
multiple_choice = ['Ja', 'Nein', 'Teilweise', 'None']

example_flows = ['Some flow', 'Some other flow', 'Example flow', 'Some FAQ']
example_actions = ['Some action', 'Some other action', 'Example action', 'Example FAQ']
example_chat = ['Lorem ipsum dolor sit amet, consectetur adipiscing elit. In porttitor ligula ac turpis eleifend blandit.', 
'Lorem ipsum dolor sit amet, consectetur adipiscing elit. In porttitor ligula ac turpis eleifend blandit. In elementum velit quis turpis lobortis finibus. Morbi ex dui, facilisis sed mattis ut, vulputate ac odio. Ut rhoncus, quam sed accumsan tempor, purus felis egestas quam, quis pulvinar libero justo at sem. Fusce ac volutpat sapien. Vestibulum pretium ullamcorper fermentum. Mauris vitae eleifend dolor. Sed vel neque et enim ornare consequat. In nec placerat metus. Duis feugiat tellus vel justo faucibus euismod. ',
 'Ut rhoncus, quam sed accumsan tempor, purus felis egestas quam, quis ', 
 'Vestibulum pretium ullamcorper fermentum. Mauris vitae eleifend dolor. Sed vel neque et enim ornare consequat. In nec placerat metus. Duis feugiat tellus vel justo faucibus euismod. ',
  'Suspendisse', 'Suspendisse suscipit, tellus ut varius aliquam, tortor enim placerat sem, sit amet porta eros tellus ultrices risus. Etiam lobortis sapien consectetur felis elementum, in commodo sem pharetra. Vivamus eget risus molestie, pulvinar orci in, viverra nunc. Quisque elit eros, suscipit sed quam sed, pretium feugiat mi.',
   'Nunc et condimentum ligula. Vivamus porta volutpat gravida. Morbi molestie arcu vel commodo tempus. Duis aliquam quis felis at posuere. Aliquam aliquet ipsum erat, eu tincidunt dolor vehicula at. Sed dolor augue, maximus ut blandit at, iaculis vitae dolor. Vestibulum quis erat egestas, fringilla tortor non, mollis libero. ',
    'Aenean massa nisi, tincidunt non lectus ac, auctor commodo turpis.']