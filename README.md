Welcome to ReText and ReTextWiki
================================

## from the original ReText project

ReText is a simple but powerful editor for Markdown and reStructuredText markup
languages. ReText is written in Python language and works on Linux and other
POSIX-compatible platforms. To install ReText, use `setup.py install` command.

You can read more about ReText on [our website](http://retext.sourceforge.net/)
or in the [wiki](http://sourceforge.net/p/retext/wiki/).

ReText requires the following packages to run:

* [python](http://python.org/) — we recommend using version 3.2 or higher
* [python-qt4](http://www.riverbankcomputing.co.uk/software/pyqt/intro)
* [python-markups](http://pypi.python.org/pypi/Markups)

We also recommend having these packages installed:

* [python-markdown](http://packages.python.org/Markdown/) — for Markdown
  language support
* [python-docutils](http://docutils.sourceforge.net/) — for reStructuredText
  language support
* [python-enchant](http://pypi.python.org/pypi/pyenchant) — for spell checking
  support

Translation files are already compiled for release tarballs and will be
automatically loaded. For development snapshots, compile translations using
`lrelease locale/*.ts` command. Translation files can also be loaded from
`/usr/share/retext/` directory.

If you want to translate ReText into your language, follow the instructions in
ReText wiki.

## ReTextWiki 

ReTextWiki integrates the wiki managment portion of 
[mikidown](http://rnons.github.io/mikidown/) with the mature ReText editor.
This  requires (currently) in addition

* [mikidown](http://rnons.github.io/mikidown/) - for wiki management, the
  md/rst file and attachment handling


## License

This project is licensed under GNU GPL (v2+) license, the current version is
available in `LICENSE_GPL` file.

## Copyright

ReTextWiki is Copyright 2014 by [CKolumbus](https://github.com/ckolumbus), alias Chris Drexler

Mikidown is written by [rnons](https://github.com/rnons)
and is licensed according to `LICENSE_Mikidown`.

ReText is Copyright 2011–2012 [Dmitry Shachnev](https://launchpad.net/~mitya57)
and is licensed under GNU GPL (v2+) license, the current version is available in
`LICENSE_GPL` file.

ReText icon is based on `accessories-text-editor` icon from the Faenza theme.
