
* index on save: overwrite SaveFileMain from ReWiki.window.ReTextWindow
* view attachments :either
    * list whole tree and jump to sub-dir if window changes
    * or recreate mikidown behavior (just list page associated attach dir)

* Drag-n-Drop of local files and insert as links (NEED to work for md & rst!!!)<br>
  from mikiedit (overwrite QTextEdit)

<pre>
       def insertFromMimeData(self, source):
            """ Intended behavior
            If copy/drag something that hasUrls, then check the extension name:
                if image then apply image pattern ![Alt text](/path/to/img.jpg)
                         else apply link  pattern [text](http://example.net)
            If copy/drag something that hasImage, then ask for file name
            If copy/drag something that hasHtml, then html2text
            Else use the default insertFromMimeData implementation
            """
</pre>