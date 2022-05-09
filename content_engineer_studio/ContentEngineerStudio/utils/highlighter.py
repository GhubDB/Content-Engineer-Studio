import re

from PyQt5.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat


class Highlighter(QSyntaxHighlighter):
    """
    Highlights predefined regular expressions in the chat log
    """

    def __init__(self, document, name, parent=None):
        super().__init__(parent)
        self._mapping = {}
        self.name = name
        self.container = parent

        # Email addresses
        class_format = QTextCharFormat()
        class_format.setBackground(QColor(68, 126, 237))
        pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"  # Working changes
        # pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)" # Original
        self.add_mapping(pattern, class_format)

        # Phone numbers
        class_format = QTextCharFormat()
        class_format.setBackground(QColor(68, 126, 237))
        pattern = r"(\b(0041|0)|\B\+41)(\s?\(0\))?([\s\-./,'])?[1-9]{2}([\s\-./,'])?[0-9]{3}([\s\-./,'])?[0-9]{2}([\s\-./,'])?[0-9]{2}\b"
        # class_format.setTextColor(QColor(120, 135, 171))
        self.add_mapping(pattern, class_format)

        self.setDocument(document)

    def add_mapping(self, pattern, pattern_format):
        self._mapping[pattern] = pattern_format

    def highlightBlock(self, text_block):
        """
        Reimplemented highlighting function
        """
        for pattern, fmt in self._mapping.items():
            for match in re.finditer(pattern, text_block):
                start, end = match.span()
                self.container.auto_anonymized.append([self.name, start, end])
                # self.setFormat(start, end-start, fmt) # Original implementation
