__author__ = 'CKolumbus'

from multiprocessing import Process

from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser, RegexPlugin

from PyQt4.QtCore import (QDir)

class Whoosh():
    def __init__(self, indexDir, schema):
        self.indexDir = indexDir
        self.schema   = schema
        self.ix = None

    def open(self, it):
        try:
            self.ix = open_dir(self.indexDir)
        except:
            QDir().mkpath(self.indexDir)
            self.ix = create_in(self.indexDir, self.schema)
            # Fork a process to update index, which benefit responsiveness.
            p = Process(target=self.whoosh_index, args=())
            p.start()
            pass

    def reindex(self):
        pass

    # TODO: remove noteTree dependent interator code
    def whoosh_index(self):
        it = QTreeWidgetItemIterator(
            self.notesTree, QTreeWidgetItemIterator.All)
        writer = self.ix.writer()
        while it.value():
            treeItem = it.value()
            name = self.notesTree.itemToPage(treeItem)
            path = os.path.join(self.notesTree.pageToFile(name))
            print(path)
            fileobj = open(path, 'r')
            content = fileobj.read()
            fileobj.close()
            writer.add_document(
                path=name, title=parseTitle(content, name), content=content)
            it += 1
        writer.commit()