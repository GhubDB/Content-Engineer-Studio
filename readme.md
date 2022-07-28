- [About](#about)
- [Demo](#demo)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [More Info](#more-info)

## About

Content Engineer Studio is is a chat-log analyzation and workflow optimization tool.

## Demo

[![Content Engineer Studio Demo](https://imgur.com/a/t93fITR.jpg)](https://www.youtube.com/watch?v=DKgMpt6OwGM "Content Engineer Studio Demo")

## Installation

Clone this repo and install the Content Engineer Studio Package:

```shell
pip install content_engineer_studio
```

Download ChromeDriver and add it to your Program Files folder:
https://chromedriver.chromium.org/downloads

## Usage

- Import a CSV or XLSX file for testing/analysis.
- Drag the imported DataFrame onto the testing or the analysis area.
- Start a new live chat session.
- Save messages to the DataFrame and add annotations.
- Export the file.

## Features

- Start live chat sessions (currently configured for cleverbot), select messages and save them to the DataFrame
- Load and analyze chat-logs and save selected messages to the DataFrame
- Edit messages
- Automatically recognize and anonymize personal information such as phone numbers and email addresses
- Add multiple choice selection fields to the DataFrame
- Search and select content sent by the bot (FAQs), currently populated by sample data.
- View and edit DataFrames
- Add/remove rows and columns
- Reorder columns
- Data editing and copy / paste
- Import CSV files with drag & drop
- Search toolbar

## Current status

This project is still in version 0.x.y and subject to breaking changes. The latest changes will be on the `development` branch, and will be occasionally merged to `master`.

## What I learned on this project

- Working with an existing codbase and adding to it.
- Gained more in depth knowledge about the model view pattern
- Learned more about separating applications into components and reducing coupling
- Gained experience working with the Qt framework
- Learned more about UI and UX design