import mmh3


class Hash:
    def hash_list(self, messages: list):
        if not messages or not isinstance(messages, list):
            return False

        messages = [mmh3.hash(x) for x in messages]

        return messages


# with open(file="csv/selected_messages.xlsx")  as f:
