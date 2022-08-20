- [About](#about)
- [Demo](#demo)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [More Info](#more-info)

## About

Content Engineer Studio is is a tool for analyzing chat-logs, handling live chats and optimizing your workflow.

## Demo

[![Content Engineer Studio Demo](https://i.imgur.com/p9Ap0UD.jpg)](https://www.youtube.com/watch?v=DKgMpt6OwGM "Content Engineer Studio Demo")

[Content Engineer Studio Demo](https://www.youtube.com/watch?v=DKgMpt6OwGM)

## Installation

Clone this repo and install the Content Engineer Studio Package:

```shell
pip install content_engineer_studio
```

Download ChromeDriver and add it to your Program Files folder:
https://chromedriver.chromium.org/downloads

## Usage

- Import a CSV or XLSX file via the menu or via drag & drop.
- Drag the imported file onto the testing or analysis area.
- Set roles ( link / bot messages / user messages / comments / multiple choice ) for each column.
- Start a new live chat session in testing mode or import a chat-log in analysis mode.
- Save messages to the DataFrame and add annotations.
- Export the file.

## Features

- Start live chat sessions (currently configured for cleverbot), select messages and save them to the DataFrame
- Load and analyze chat-logs, save selected messages to the DataFrame
- Edit messages
- Automatically recognize and anonymize personal information such as phone numbers and email addresses
- Add multiple choice selection fields to the DataFrame
- Search and select content sent by the bot (FAQs). Currently populated by sample data.
- View and edit DataFrames
- Add/remove rows and columns
- Reorder columns
- Import XLSX and CSV files with drag & drop
- Search toolbar

## Current status

This project is still in version 0.x.y and subject to breaking changes. The latest changes will be on the `development` branch, and will be occasionally merged to `master`.

## What I learned on this project

- Working with an existing codbase and adding to it.
- Gained more in depth knowledge about the model view pattern.
- Learned more about separating applications into components and reducing coupling.
- Gained experience working with the Qt framework.
- Learned more about UI and UX design.
- Improved my webscraping and automation skills.