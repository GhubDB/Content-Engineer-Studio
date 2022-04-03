from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

class SubWidget( QWidget ) :
    def __init__ ( self, parent = None ) :
        super( SubWidget, self ).__init__( parent )
        button = QPushButton( 'toggle' )
        checkbox = QCheckBox( 'check' )
        button.clicked.connect( checkbox.toggle )
        hLayout = QHBoxLayout( self )
        hLayout.addWidget( button )
        hLayout.addWidget( checkbox )
        self.setLayout( hLayout )

class Window( QMainWindow ) :
    def __init__ ( self, parent = None ) :
        super( Window, self ).__init__( parent )
        # loadUi( 'main-something.ui', self )
        button = QPushButton( 'add' )
        button.clicked.connect( self.add )
        self.vLayout = QVBoxLayout( self )
        self.vLayout.addWidget( button )
        centralWidget = QWidget()
        centralWidget.setLayout( self.vLayout )
        self.setCentralWidget( centralWidget )

    def add ( self ) :
        self.vLayout.addWidget( SubWidget( self ) )
        # self.vLayout.addWidget( loadUi( 'sub-something.ui', self ) )

if __name__ == "__main__" :
    app = QApplication( [] )
    w = Window()
    w.show()
    app.exec_()