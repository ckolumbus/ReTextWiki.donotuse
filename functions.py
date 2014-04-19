__author__ = 'CKolumbus'

import logging

from PyQt4.QtCore import (QDir)
from PyQt4.QtGui import (QTreeWidgetItem)

#from autologging import logged, traced, TracedMethods

_logger = logging.getLogger(__name__)

def initTree(notePath, parent):
    ''' When there exist foo.md, foo.mkd, foo.markdown,
        only one item will be shown in notesTree.
    '''
    if not QDir(notePath).exists():
        return
    notebook_dir = QDir(notePath)
    notes_list = notebook_dir.entryInfoList(['*.md', '*.mkd', '*.markdown', '*.rst'],
                                           QDir.NoFilter,
                                           QDir.Name|QDir.IgnoreCase)
    nl = [note.completeBaseName() for note in notes_list]
    no_duplicate = list(set(nl))
    for name in no_duplicate:
        item = QTreeWidgetItem(parent, [name])
        path = notePath + '/' + name
        initTree(path, item)

