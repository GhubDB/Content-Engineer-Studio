elegantdark = '''
/*
ElegantDark Style Sheet for QT Applications
Author: Jaime A. Quiroga P.
Company: GTRONICK
Last updated: 17/04/2018
Available at: https://github.com/GTRONICK/QSS/blob/master/ElegantDark.qss
*/
QMainWindow {
	background-color: rgb(70, 70, 70);
}
QTableView {
    background-color:rgb(50, 50, 50);
    color: rgb(230, 230, 230);
    
    selection-color: rgb(255, 255, 255);
    
    selection-background-color: rgb(55, 92, 123);
  
}
/*
#actions {
    selection-background-color: rgb(170, 132, 57);
}
#flows {
    selection-background-color: rgb(170, 158, 57);
}
*/
QTextEdit {
	background-color:rgb(60, 60, 60);
	color: rgb(230, 230, 230);
}
#analysis {
	background-color:rgb(50, 50, 50);
	color: rgb(230, 230, 230);
    font-size: 11pt;
}
#analysis_2 {
	background-color:rgb(50, 50, 50);
	color: rgb(230, 230, 230);
    font-size: 11pt;
}
/*
#chat_bubble_customer {
    font-size: 10pt;
    border-style: outset;
    border-left-width: 5px;
    border-left-color: rgb(83, 43, 114);
    padding-left: 4px;
    background-color: rgb(90, 90, 90);
}
#chat_bubble_bot {
    font-size: 10pt;
    text-align: right;
    border-style: outset;
    border-right-width: 5px;
    border-right-color: rgb(45, 136, 45);
    padding-right: 4px;
    
    read-only
    margin-right: 4px;
    text-decoration: line-through;
}
*/
#canned::item {
    /*
    border: 0px;
    padding-right: 5px;
    */
}
QComboBox {
	border-style: outset;
	border-width: 2px;
	border-top-color: qlineargradient(spread:pad, x1:0.5, y1:0.6, x2:0.5, y2:0.4, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-right-color: qlineargradient(spread:pad, x1:0.4, y1:0.5, x2:0.6, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-left-color: qlineargradient(spread:pad, x1:0.6, y1:0.5, x2:0.4, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-bottom-color: rgb(58, 58, 58);
	border-bottom-width: 1px;
	border-style: solid;
	color: rgb(255, 255, 255);
	padding: 2px;
	background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(77, 77, 77, 255), stop:1 rgba(97, 97, 97, 255));
}
QComboBox::drop-down  {
	border-style: outset;
	border-width: 2px;
	border-top-color: qlineargradient(spread:pad, x1:0.5, y1:0.6, x2:0.5, y2:0.4, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-right-color: qlineargradient(spread:pad, x1:0.4, y1:0.5, x2:0.6, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-left-color: qlineargradient(spread:pad, x1:0.6, y1:0.5, x2:0.4, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-bottom-color: rgb(58, 58, 58);
	border-bottom-width: 1px;
	border-style: solid;
}
QComboBox::down-arrow   {
	border-style: outset;
	border-width: 2px;
	border-top-color: qlineargradient(spread:pad, x1:0.5, y1:0.6, x2:0.5, y2:0.4, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-right-color: qlineargradient(spread:pad, x1:0.4, y1:0.5, x2:0.6, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-left-color: qlineargradient(spread:pad, x1:0.6, y1:0.5, x2:0.4, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-bottom-color: rgb(58, 58, 58);
	border-bottom-width: 1px;
	border-style: solid;

}
QComboBox:hover{
	border-style: outset;
	border-width: 2px;
	border-top-color: qlineargradient(spread:pad, x1:0.5, y1:0.6, x2:0.5, y2:0.4, stop:0 rgba(180, 180, 180, 255), stop:1 rgba(110, 110, 110, 255));
	border-right-color: qlineargradient(spread:pad, x1:0.4, y1:0.5, x2:0.6, y2:0.5, stop:0 rgba(180, 180, 180, 255), stop:1 rgba(110, 110, 110, 255));
	border-left-color: qlineargradient(spread:pad, x1:0.6, y1:0.5, x2:0.4, y2:0.5, stop:0 rgba(180, 180, 180, 255), stop:1 rgba(110, 110, 110, 255));
	border-bottom-color: rgb(115, 115, 115);
	border-bottom-width: 1px;
	border-style: solid;
	color: rgb(255, 255, 255);
	padding: 2px;
	background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(107, 107, 107, 255), stop:1 rgba(157, 157, 157, 255));
}
QComboBox:pressed{
	border-style: outset;
	border-width: 2px;
	border-top-color: qlineargradient(spread:pad, x1:0.5, y1:0.6, x2:0.5, y2:0.4, stop:0 rgba(62, 62, 62, 255), stop:1 rgba(22, 22, 22, 255));
	border-right-color: qlineargradient(spread:pad, x1:0.4, y1:0.5, x2:0.6, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-left-color: qlineargradient(spread:pad, x1:0.6, y1:0.5, x2:0.4, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-bottom-color: rgb(58, 58, 58);
	border-bottom-width: 1px;
	border-style: solid;
	color: rgb(255, 255, 255);
	padding: 2px;
	background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(77, 77, 77, 255), stop:1 rgba(97, 97, 97, 255));
}
QPushButton{
	border-style: outset;
	border-width: 2px;
	border-top-color: qlineargradient(spread:pad, x1:0.5, y1:0.6, x2:0.5, y2:0.4, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-right-color: qlineargradient(spread:pad, x1:0.4, y1:0.5, x2:0.6, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-left-color: qlineargradient(spread:pad, x1:0.6, y1:0.5, x2:0.4, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-bottom-color: rgb(58, 58, 58);
	border-bottom-width: 1px;
	border-style: solid;
	color: rgb(255, 255, 255);
	padding: 2px;
	background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(77, 77, 77, 255), stop:1 rgba(97, 97, 97, 255));
}
QPushButton:hover{
	border-style: outset;
	border-width: 2px;
	border-top-color: qlineargradient(spread:pad, x1:0.5, y1:0.6, x2:0.5, y2:0.4, stop:0 rgba(180, 180, 180, 255), stop:1 rgba(110, 110, 110, 255));
	border-right-color: qlineargradient(spread:pad, x1:0.4, y1:0.5, x2:0.6, y2:0.5, stop:0 rgba(180, 180, 180, 255), stop:1 rgba(110, 110, 110, 255));
	border-left-color: qlineargradient(spread:pad, x1:0.6, y1:0.5, x2:0.4, y2:0.5, stop:0 rgba(180, 180, 180, 255), stop:1 rgba(110, 110, 110, 255));
	border-bottom-color: rgb(115, 115, 115);
	border-bottom-width: 1px;
	border-style: solid;
	color: rgb(255, 255, 255);
	padding: 2px;
	background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(107, 107, 107, 255), stop:1 rgba(157, 157, 157, 255));
}
QPushButton:pressed{
	border-style: outset;
	border-width: 2px;
	border-top-color: qlineargradient(spread:pad, x1:0.5, y1:0.6, x2:0.5, y2:0.4, stop:0 rgba(62, 62, 62, 255), stop:1 rgba(22, 22, 22, 255));
	border-right-color: qlineargradient(spread:pad, x1:0.4, y1:0.5, x2:0.6, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-left-color: qlineargradient(spread:pad, x1:0.6, y1:0.5, x2:0.4, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-bottom-color: rgb(58, 58, 58);
	border-bottom-width: 1px;
	border-style: solid;
	color: rgb(255, 255, 255);
	padding: 2px;
	background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(77, 77, 77, 255), stop:1 rgba(97, 97, 97, 255));
}
QPushButton:disabled{
	border-style: outset;
	border-width: 2px;
	border-top-color: qlineargradient(spread:pad, x1:0.5, y1:0.6, x2:0.5, y2:0.4, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-right-color: qlineargradient(spread:pad, x1:0.4, y1:0.5, x2:0.6, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-left-color: qlineargradient(spread:pad, x1:0.6, y1:0.5, x2:0.4, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-bottom-color: rgb(58, 58, 58);
	border-bottom-width: 1px;
	border-style: solid;
	color: rgb(0, 0, 0);
	padding: 2px;
	background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(57, 57, 57, 255), stop:1 rgba(77, 77, 77, 255));
}
QLineEdit {
	border-width: 1px; border-radius: 4px;
	border-color: rgb(58, 58, 58);
	border-style: inset;
	padding: 0 8px;
	color: rgb(255, 255, 255);
	background:rgb(100, 100, 100);
	selection-background-color: rgb(187, 187, 187);
	selection-color: rgb(60, 63, 65);
}
QLineEdit:focus {
    border: 2px solid #007ce5;
}
QLabel {
	color:rgb(255,255,255);	
}
QRadioButton {
    color: rgb(230, 230, 230);
    selection-background-color: rgb(55, 92, 123);
}
QRadioButton::indicator {
    color: rgb(230, 230, 230);
    selection-background-color: rgb(55, 92, 123);
    selection-color: rgb(55, 92, 123);
}
QRadioButton::indicator::checked {
    color: rgb(230, 230, 230);
    selection-background-color: rgb(55, 92, 123);
    selection-color: rgb(55, 92, 123);
}
QProgressBar {
	text-align: center;
	color: rgb(240, 240, 240);
	border-width: 1px; 
	border-radius: 10px;
	border-color: rgb(58, 58, 58);
	border-style: inset;
	background-color:rgb(77,77,77);
}
QProgressBar::chunk {
	background-color: qlineargradient(spread:pad, x1:0.5, y1:0.7, x2:0.5, y2:0.3, stop:0 rgba(87, 97, 106, 255), stop:1 rgba(93, 103, 113, 255));
	border-radius: 5px;
}
QMenuBar {
	background:rgb(70, 70, 70);
}
QMenuBar::item {
	color:rgb(223,219,210);
	spacing: 3px;
	padding: 1px 4px;
	background: transparent;
}

QMenuBar::item:selected {
	background:rgb(115, 115, 115);
}
QMenu::item:selected {
	color:rgb(255,255,255);
	border-width:2px;
	border-style:solid;
	padding-left:18px;
	padding-right:8px;
	padding-top:2px;
	padding-bottom:3px;
	background:qlineargradient(spread:pad, x1:0.5, y1:0.7, x2:0.5, y2:0.3, stop:0 rgba(87, 97, 106, 255), stop:1 rgba(93, 103, 113, 255));
	border-top-color: qlineargradient(spread:pad, x1:0.5, y1:0.6, x2:0.5, y2:0.4, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-right-color: qlineargradient(spread:pad, x1:0.4, y1:0.5, x2:0.6, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-left-color: qlineargradient(spread:pad, x1:0.6, y1:0.5, x2:0.4, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
	border-bottom-color: rgb(58, 58, 58);
	border-bottom-width: 1px;
}
QMenu::item {
	color:rgb(223,219,210);
	background-color:rgb(78,78,78);
	padding-left:20px;
	padding-top:4px;
	padding-bottom:4px;
	padding-right:10px;
}
QMenu{
	background-color:rgb(78,78,78);
}
QTabWidget {
	color:rgb(0,0,0);
	background-color:rgb(247,246,246);
}
QTabWidget::pane {
		border-color: rgb(77,77,77);
		background-color:rgb(101,101,101);
		border-style: solid;
		border-width: 1px;
    	border-radius: 6px;
}
QTabBar::tab {
	padding:2px;
	color:rgb(250,250,250);
  	background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(77, 77, 77, 255), stop:1 rgba(97, 97, 97, 255));
	border-style: solid;
	border-width: 2px;
  	border-top-right-radius:4px;
   border-top-left-radius:4px;
	border-top-color: qlineargradient(spread:pad, x1:0.5, y1:0.6, x2:0.5, y2:0.4, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(95, 92, 93, 255));
	border-right-color: qlineargradient(spread:pad, x1:0.4, y1:0.5, x2:0.6, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(95, 92, 93, 255));
	border-left-color: qlineargradient(spread:pad, x1:0.6, y1:0.5, x2:0.4, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(95, 92, 93, 255));
	border-bottom-color: rgb(101,101,101);
}
QTabBar::tab:selected, QTabBar::tab:last:selected, QTabBar::tab:hover {
  	background-color:rgb(101,101,101);
  	margin-left: 0px;
  	margin-right: 1px;
}
QTabBar::tab:!selected {
    	margin-top: 1px;
		margin-right: 1px;
}
QCheckBox {
	color:rgb(223,219,210);
	padding: 2px;
}
QCheckBox:hover {
	border-radius:4px;
	border-style:solid;
	padding-left: 1px;
	padding-right: 1px;
	padding-bottom: 1px;
	padding-top: 1px;
	border-width:1px;
	border-color: rgb(87, 97, 106);
	background-color:qlineargradient(spread:pad, x1:0.5, y1:0.7, x2:0.5, y2:0.3, stop:0 rgba(87, 97, 106, 150), stop:1 rgba(93, 103, 113, 150));
}
QCheckBox::indicator:checked {
	border-radius:4px;
	border-style:solid;
	border-width:1px;
	border-color: rgb(180,180,180);
	background-color: #2d6594;
}
QCheckBox::indicator:unchecked {
	border-radius:4px;
	border-style:solid;
	border-width:1px;
	border-color: rgb(87, 97, 106);
	background-color:qlineargradient(spread:pad, x1:0.5, y1:0.7, x2:0.5, y2:0.3, stop:0 rgba(87, 97, 106, 255), stop:1 rgba(93, 103, 113, 255));
}
QStatusBar {
	color:rgb(240,240,240);
}
'''


deepbox = '''
/*Copyright (c) DevSec Studio. All rights reserved.

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

/*-----QWidget-----*/
QWidget
{
	background-color: #141414;
	color: #000000;

}


/*-----QLabel-----*/
QLabel
{
	background-color: #141414;
	color: #ffffff;

}


/*-----QPushButton-----*/
QPushButton
{
	background-color: #141414;
	color: #bfbfbf;
	border: none;
	padding: 5px;

}


QPushButton::hover
{
	background-color: #141414;
	color: #bfbfbf;
	border-bottom-style: solid;
	border-bottom-color: #bfbfbf;
	border-bottom-width: 3px;
	

}


QPushButton::pressed
{
	background-color: #141414;
	color: #bfbfbf;
	border: none;

}


/*-----QLineEdit-----*/
QLineEdit
{
	background-color: #bfbfbf;
	color: #000000;
	border-style: solid;
	border-width: 1px;
	border-color: #141414;

}


/*-----QListView-----*/
QListView{
	background-color: #141414;
	font-size: 12pt;
	border: none;
	color: #fff;
	show-decoration-selected: 0;
	padding-left: px;

}


QListView::item:selected{
   color: #000;
   background-color: lightgray;
   border: none;
   border-radius: 0px;

}


QListView::item:!selected{
   color: #fff;
   background-color: transparent;
   border: none;
   border-radius: 0px;

}


QListView::item:!selected:hover{
   color: #fff;
   background-color: #3e3e3e;
   border: none;
   border-radius: 0px;

}


/*-----QScrollBar-----*/
QScrollBar:vertical 
{
   border: none;
   width: 12px;

}


QScrollBar::handle:vertical 
{
   border: none;
   border-radius : 0px;
   background-color: #7a7a7a;
   min-height: 80px;
   width : 12px;

}


QScrollBar::handle:vertical:pressed
{
   background-color: #5d5f60; 

}


QScrollBar::add-line:vertical
{
   border: none;
   background: transparent;
   height: 0px;
   subcontrol-position: bottom;
   subcontrol-origin: margin;

}


QScrollBar::add-line:vertical:hover 
{
   background-color: transparent;

}


QScrollBar::add-line:vertical:pressed 
{
   background-color: #3f3f3f;

}


QScrollBar::sub-line:vertical
{
   border: none;
   background: transparent;
   height: 0px;

}


QScrollBar::sub-line:vertical:hover 
{
   background-color: transparent;

}


QScrollBar::sub-line:vertical:pressed 
{
   background-color: #3f3f3f;

}


QScrollBar::up-arrow:vertical
{
   width: 0px;
   height: 0px;
   background: transparent;

}


QScrollBar::down-arrow:vertical 
{
   width: 0px;
   height: 0px;
   background: transparent;

}


QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical
{
   background-color: #222222;
	
}'''