class DelegateRichTextEditor(QtWidgets.QTextEdit):
    commit = QtCore.pyqtSignal(QtWidgets.QWidget)
    sizeHintChanged = QtCore.pyqtSignal()
    storedSize = None

    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShape(0)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.contentTimer = QtCore.QTimer(self, 
            timeout=self.contentsChange, interval=0)
        self.document().setDocumentMargin(0)
        self.document().contentsChange.connect(self.contentTimer.start)

    @QtCore.pyqtProperty(str, user=True)
    def content(self):
        text = self.toHtml()
        # find the end of the <body> tag and remove the new line character
        bodyTag = text.find('>', text.find('<body')) + 1
        if text[bodyTag] == '\n':
            text = text[:bodyTag] + text[bodyTag + 1:]
        return text

    @content.setter
    def content(self, text):
        self.setHtml(text)

    def contentsChange(self):
        newSize = self.document().size()
        if self.storedSize != newSize:
            self.storedSize = newSize
            self.sizeHintChanged.emit()

    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier:
            if event.key() in (QtCore.Qt.Key_Return, ):
                self.commit.emit(self)
                return
            elif event.key() == QtCore.Qt.Key_B:
                if self.fontWeight() == QtGui.QFont.Bold:
                    self.setFontWeight(QtGui.QFont.Normal)
                else:
                    self.setFontWeight(QtGui.QFont.Bold)
            elif event.key() == QtCore.Qt.Key_I:
                self.setFontItalic(not self.fontItalic())
            elif event.key() == QtCore.Qt.Key_U:
                self.setFontUnderline(not self.fontUnderline())
        super().keyPressEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        cursor = self.textCursor()
        cursor.movePosition(cursor.End)
        self.setTextCursor(cursor)


class SegmentsTableViewDelegate(QtWidgets.QStyledItemDelegate):
    rowSizeHintChanged = QtCore.pyqtSignal(int)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.editors = {}

    def createEditor(self, parent, option, index):
        pIndex = QtCore.QPersistentModelIndex(index)
        editor = self.editors.get(pIndex)
        if not editor:
            editor = DelegateRichTextEditor(parent)
            editor.sizeHintChanged.connect(
                lambda: self.rowSizeHintChanged.emit(pIndex.row()))
            self.editors[pIndex] = editor
        return editor

    def eventFilter(self, editor, event):
        if (event.type() == event.KeyPress and 
            event.modifiers() == QtCore.Qt.ControlModifier and 
            event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return)):
                self.commitData.emit(editor)
                self.closeEditor.emit(editor)
                return True
        return super().eventFilter(editor, event)

    def destroyEditor(self, editor, index):
        # remove the editor from the dict so that it gets properly destroyed;
        # this avoids any "wrapped C++ object destroyed" exception
        self.editors.pop(QtCore.QPersistentModelIndex(index))
        super().destroyEditor(editor, index)
        # emit the signal again: if the data has been rejected, we need to
        # restore the correct hint
        self.rowSizeHintChanged.emit(index.row())


    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        painter.save()
        doc = QtGui.QTextDocument()
        doc.setDocumentMargin(0)
        doc.setTextWidth(option.rect.width())
        doc.setHtml(option.text)
        option.text = ""
        option.widget.style().drawControl(
            QtWidgets.QStyle.CE_ItemViewItem, option, painter)
        painter.translate(option.rect.left(), option.rect.top())
        doc.drawContents(painter)
        painter.restore()

    def sizeHint(self, option, index):
        self.initStyleOption(option, index)
        editor = self.editors.get(QtCore.QPersistentModelIndex(index))
        if editor:
            doc = QtGui.QTextDocument.clone(editor.document())
        else:
            doc = QtGui.QTextDocument()
            doc.setDocumentMargin(0)
            doc.setHtml(option.text)
            doc.setTextWidth(option.rect.width())
        doc_height_int = int(doc.size().height())
        return QtCore.QSize(int(doc.idealWidth()), doc_height_int)


class SegmentsTableView(QtWidgets.QTableView):
    def __init__(self, parent):
        super().__init__(parent)
        delegate = SegmentsTableViewDelegate(self)
        self.setItemDelegate(delegate)
        delegate.rowSizeHintChanged.connect(self.resizeRowToContents)
        # ...
