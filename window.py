# vim: noexpandtab:ts=4:sw=4
# This file is part of ReTextWiki
# Copyright: CKolumbus (Chris Drexler) 2014
# License: GNU GPL v2 or higher

import os
import markups
from subprocess import Popen, PIPE
from ReText import QtCore, QtPrintSupport, QtGui, QtWidgets, QtWebKitWidgets, \
    icon_path, DOCTYPE_MARKDOWN, DOCTYPE_REST, app_name, app_version, globalSettings, \
    settings, readListFromSettings, writeListToSettings, writeToSettings, \
    datadirs, enchant, enchant_available
from ReText.webpages import wpInit, wpUpdateAll
from ReText.dialogs import HtmlDialog, LocaleDialog
from ReText.config import ConfigDialog
from ReText.highlighter import ReTextHighlighter
from ReText.editor import ReTextEdit

from mikidown.config import Setting
from mikidown.mikibook import Mikibook

from mikidown.config import __appname__, __version__
from mikidown.mikibook import NotebookListDialog
from mikidown.mikitree import MikiTree, TocTree
from mikidown.mikisearch import MikiSearch
from mikidown.attachment import AttachmentView
from mikidown.highlighter import MikiHighlighter
from mikidown.utils import LineEditDialog, ViewedNoteIcon, parseHeaders, parseTitle

from .functions import initTree
from .whooshif import Whoosh
from whoosh.qparser import QueryParser, RegexPlugin

from ReText.window import ReTextWindow

(Qt, QSize) = (QtCore.Qt, QtCore.QSize)
(QLineEdit, QSplitter, QMainWindow, QTabWidget, QTreeWidgetItemIterator) = (
    QtWidgets.QLineEdit, QtWidgets.QSplitter, QtWidgets.QMainWindow, QtWidgets.QTabWidget,
    QtWidgets.QTreeWidgetItemIterator)
(QWidget, QDockWidget, QVBoxLayout, QKeySequence) = (
    QtGui.QTableWidget, QtGui.QDockWidget, QtGui.QVBoxLayout, QtGui.QKeySequence)


class ReTextWikiWindow(ReTextWindow):
    def __init__(self, parent=None):
        ReTextWindow.__init__(self, parent)

        # Read notebookList, open the first notebook.
        notebooks = Mikibook.read()
        if len(notebooks) == 0:
            Mikibook.create()
            notebooks = Mikibook.read()

        if len(notebooks) != 0:
            settings = Setting(notebooks)
            # Initialize application and main window.

        self.settings = settings
        self.notePath = settings.notePath

        ################ Setup core components ################
        self.notesTree = MikiTree(self)
        self.notesTree.setObjectName("notesTree")
        initTree(self.notePath, self.notesTree)
        self.notesTree.sortItems(0, Qt.AscendingOrder)

        #self.viewedList = QToolBar(self.tr('Recently Viewed'), self)
        #self.viewedList.setIconSize(QSize(16, 16))
        #self.viewedList.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        #self.viewedListActions = []
        self.noteSplitter = QSplitter(Qt.Horizontal)

        self.dockIndex = QDockWidget("Index")
        self.dockSearch = QDockWidget("Search")
        self.searchEdit = QLineEdit()
        self.searchView = MikiSearch(self)
        self.searchTab = QWidget()
        self.dockToc = QDockWidget("TOC")
        self.tocTree = TocTree()
        self.dockAttachment = QDockWidget("Attachment")
        self.attachmentView = AttachmentView(self)

        #<-- wiki init done

        ################ Setup search engine   ################
        self.whoosh = Whoosh(self.settings.indexdir, self.settings.schema)
        self.whoosh.reindex(wikiPageIterator(self.notesTree))

        self.actions = dict()
        self.setupActions()

        self.setupMainWindow()

    def setupMainWindow(self):
        #--> setup Wiki Window

        searchLayout = QVBoxLayout()
        searchLayout.addWidget(self.searchEdit)
        searchLayout.addWidget(self.searchView)
        self.searchTab.setLayout(searchLayout)
        self.tocTree.header().close()

        self.dockIndex.setObjectName("Index")
        self.dockIndex.setWidget(self.notesTree)
        self.dockSearch.setObjectName("Search")
        self.dockSearch.setWidget(self.searchTab)
        self.dockToc.setObjectName("TOC")
        self.dockToc.setWidget(self.tocTree)
        self.dockAttachment.setObjectName("Attachment")
        self.dockAttachment.setWidget(self.attachmentView)

        self.setDockOptions(QMainWindow.VerticalTabs)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockIndex)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockSearch)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockToc)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockAttachment)
        self.tabifyDockWidget(self.dockIndex, self.dockSearch)
        self.tabifyDockWidget(self.dockSearch, self.dockToc)
        self.tabifyDockWidget(self.dockToc, self.dockAttachment)
        self.setTabPosition(Qt.LeftDockWidgetArea, QTabWidget.North)
        self.dockIndex.raise_()  # Put dockIndex on top of the tab stack

        self.notesTree.currentItemChanged.connect(
            self.currentItemChangedWrapperWiki)
        self.notesTree.itemDoubleClicked.connect(
            self.loadItemWiki)

        self.tabWidget.currentChanged.connect(self.changeIndexWiki)
        self.tabWidget.tabCloseRequested.connect(self.closeTabWiki)

        menubar = self.menuBar()
        menuWiki = menubar.addMenu(self.tr('Wiki'))

        menuWiki.addAction(self.actions['newPage'])
        menuWiki.addAction(self.actions['newSubpage'])
        menuWiki.addAction(self.actions['importPage'])
        menuWiki.addAction(self.actions['openNotebook'])
        menuWiki.addAction(self.actions['reIndex'])
        menuWiki.addSeparator()
        menuWiki.addAction(self.actions['renamePage'])
        menuWiki.addAction(self.actions['delPage'])
        menuWiki.addSeparator()
        menuWiki.addAction(self.actions['insertImage'])


    def setupActions(self):

        # Global Actions
        actTabIndex = self.act(self.tr('Switch to Index Tab'),
                               trig=lambda: self.raiseDock(self.dockIndex), shct='Ctrl+Shift+I')
        actTabSearch = self.act(self.tr('Switch to Search Tab'),
                                trig=lambda: self.raiseDock(self.dockSearch), shct='Ctrl+Shift+F')
        self.addAction(actTabIndex)
        self.addAction(actTabSearch)

        self.searchEdit.returnPressed.connect(self.searchNote)

        ################ Menu Actions ################
        # actions in menuFile
        actionNewPage = self.act(self.tr('&New Page...'),
                                 trig=self.notesTree.newPage, shct=QKeySequence.New)
        self.actions.update(newPage=actionNewPage)

        actionNewSubpage = self.act(self.tr('New Sub&page...'),
                                    trig=self.notesTree.newSubpage, shct='Ctrl+Shift+N')
        self.actions.update(newSubpage=actionNewSubpage)

        actionImportPage = self.act(self.tr('&Import Page...'), trig=self.importPage)
        self.actions.update(importPage=actionImportPage)

        actionOpenNotebook = self.act(self.tr('&Open Notebook...'),
                                      trig=self.openNotebook)
        self.actions.update(openNotebook=actionOpenNotebook)

        actionReIndex = self.act(self.tr('Re-index'), trig=self.reIndex)
        self.actions.update(reIndex=actionReIndex)

        actionRenamePage = self.act(self.tr('&Rename Page...'),
                                    trig=self.notesTree.renamePage, shct='F2')
        self.actions.update(renamePage=actionRenamePage)

        actionDelPage = self.act(self.tr('&Delete Page'),
                                 trig=self.notesTree.delPageWrapper)  #, QKeySequence.Delete)
        self.actions.update(delPage=actionDelPage)

        actionInsertImage = self.act(self.tr('&Insert Attachment'),
                                     trig=self.insertAttachment, shct='Ctrl+I')
        actionInsertImage.setEnabled(False)
        self.actions.update(insertImage=actionInsertImage)

    def searchNote(self):
        """ Sorting criteria: "title > path > content"
            Search matches are organized into html source.
        """

        pattern = self.searchEdit.text()
        if not pattern:
            return
        results = []

        with self.whoosh.ix.searcher() as searcher:
            matches = []
            for f in ["title", "path", "content"]:
                queryp = QueryParser(f, self.whoosh.ix.schema)
                queryp.add_plugin(RegexPlugin())
                # r"pattern" is the desired regex term format
                query = queryp.parse('r"' + pattern + '"')
                ms = searcher.search(query, limit=None) # default limit is 10!
                for m in ms:
                    if not m in matches:
                        matches.append(m)

            for r in matches:
                title = r['title']
                path = r['path']
                term = r.highlights("content")
                results.append([title, path, term])

            html = """
                    <style>
                        body { font-size: 14px; }
                        .path { font-size: 12px; color: #009933; }
                    </style>
                   """
            for title, path, hi in results:
                html += ("<p><a href='" + path + "'>" + title +
                         "</a><br/><span class='path'>" +
                         path + "</span><br/>" + hi + "</p>")
            self.searchView.setHtml(html)


    def changeIndexWiki(self):
        pass

    def closeTabWiki(self):
        pass

    def saveFileMain(self, dlg):
        ReTextWindow.saveFileMain(self, dlg)
        # TODO: add indexing code

    def currentItemChangedWrapperWiki(self, current, previous):
        if current is None:
            return
        #if previous != None and self.notesTree.pageExists(previous):
        prev = self.notesTree.itemToPage(previous)
        if self.notesTree.pageExists(prev):
            #self.saveNote(previous)
            pass
        self.loadItemWiki(current)

    def loadItemWiki(self, item):
        currentFile = self.notesTree.itemToFile(item)
        self.openFileWrapper(currentFile)

        # Update attachmentView to show corresponding attachments.
        attachmentdir = self.notesTree.itemToAttachmentDir(item)
        self.attachmentView.model.setRootPath(attachmentdir)
        #self.__logger.debug("currentItemChangedWrapper: %s", attachmentdir)
        index = self.attachmentView.model.index(attachmentdir)
        if index.row() == -1:
            index = self.attachmentView.model.index(self.settings.attachmentPath)
            #self.attachmentView.model.setFilter(QDir.Files)
            #self.attachmentView.setModel(self.attachmentView.model)
        self.attachmentView.setRootIndex(index)

    def importPage(self):
        pass

    def openNotebook(self):
        pass

    def reIndex(self):
        pass

    def insertAttachment(self):
        pass

    def updateAttachmentView(self):
        pass


class wikiPageIterator():
    def __init__(self, mikitree):
        self.mikiTree = mikitree
        self.it = QTreeWidgetItemIterator(
            self.mikiTree, QTreeWidgetItemIterator.All)

    def __iter__(self):
        return self

    # python3 compatibility
    def __next__(self):
        return self.next()

    def next(self):
        while self.it.value():
            treeItem = self.it.value()
            name = self.mikiTree.itemToPage(treeItem)
            path = os.path.join(self.mikiTree.pageToFile(name))
            x = (path, name)
            self.it += 1
            return(x)

        raise StopIteration