# -*- coding: utf-8 -*-
"""
Created on Sat May 28 08:53:18 2016

@author: mtkessel
"""

import sys
from PyQt4 import QtGui


def main():
    
    app = QtGui.QApplication(sys.argv)

    w = QtGui.QWidget()
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('Simple')
    w.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    