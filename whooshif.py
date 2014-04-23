__author__ = 'CKolumbus'

import shutil
from multiprocessing import Process
import codecs

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
            #p = Process(target=self.whoosh_index, args=(it))
            #p.start()
            self.whoosh_index(it)
            pass

    def reindex(self, it):
        try:
            shutil.rmtree(self.indexDir)
        finally:
            self.open(it)
        pass

    # TODO: remove noteTree dependent interator code
    def whoosh_index(self, it):
        writer = self.ix.writer()
        for p in it:
            path = p[0]
            name = p[1]
            print(path, name)
            fileobj = codecs.open(path, 'r', "utf-8")
            content = fileobj.read()
            fileobj.close()
            writer.add_document(
                path=name, title=name, content=content)

        writer.commit()