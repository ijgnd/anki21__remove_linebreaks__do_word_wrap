# by ijgnd 2019- 
# based upon https://ankiweb.net/shared/info/1290231794 which has this comment on top of it
    # Based upon https://ankiweb.net/shared/info/892669336 , edited with permission
    # To make copy/pasting from PDF files less cumbersome
    # Edited version made by Remco32
    # License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
    # Version: 1.0, 2016/03/13


import os, re
from bs4 import BeautifulSoup


from anki.hooks import addHook, wrap
from anki.utils import json
from anki.lang import _
from aqt.editor import Editor
from aqt import mw
# from aqt.utils import showInfo
# from aqt.browser import Browser
from aqt.qt import *


def gc(arg, fail=False):
    conf = mw.addonManager.getConfig(__name__)
    if conf:
        return conf.get(arg, fail)
    return fail


rarestring = '⁂⸗┴▓⍗➉'
def removeLinebreaks(text):
    # soup = BeautifulSoup(str,"html.parser")
    # for e in soup.findAll('br'):
    #     e.extract()
    # return soup.prettify()

    #text = re.sub(r'<div>\s.*?<br>','<br><br>', text)
    text = re.sub(r'<div><br>','<br><br>', text)
    text = text.replace('<br><br>',rarestring)       
    text = text.replace('<div>', '')
    text = text.replace('</div>', ' ')
    if gc('try_to_remove_-_from_line_ending'):
        text = text.replace('-<br>', '')
        text = text.replace('-<br />', '')
        text = text.replace('-<br/>', '')
    text = text.replace('<br>', ' ')
    text = text.replace('<br />', ' ')
    text = text.replace('<br/>', ' ')
    text = text.replace(rarestring, '<br><br>')
    return text


def cleanLinebreaksField(editor, field):
    text = editor.note.fields[field]
    editor._myfieldUndo = (field, text)
    fmt = removeLinebreaks(text)
    editor.note.fields[field] = fmt 
    editor.saveTags()
    editor.note.flush()
    editor.loadNote(focusTo=field)


def myOnFieldUndo(editor):
    if not hasattr(editor, "_myfieldUndo") or not editor._myfieldUndo:
        return
    n, html = editor._myfieldUndo
    editor.note.fields[n] = html
    editor.loadNote()
    editor.web.setFocus()
    editor.loadNote(focusTo=n)


def cleanLinebreaks(editor):
    modifiers = editor.mw.app.queryKeyboardModifiers()
    shift_and_click = modifiers == Qt.ShiftModifier
    if shift_and_click:
        myOnFieldUndo(editor)
        return
    selection = editor.web.selectedText()
    if selection:
        #selection = selection.replace('\n',rarestring).replace('\r',rarestring)  # doesn't work
        selection = selection.replace('-\n','').replace('-\n','')
        fmt = removeLinebreaks(selection)
        editor.web.eval("document.execCommand('inserthtml', false, %s);" % json.dumps(fmt))   
    else:
        field = editor.currentField
        editor.saveNow(lambda e=editor, f=field: cleanLinebreaksField(e, f))
Editor.cleanLinebreaks = cleanLinebreaks


def keystr(k):
    key = QKeySequence(k)
    return key.toString(QKeySequence.NativeText)

def setupEditorButtonsFilter(buttons, editor):
    addon_path = os.path.dirname(__file__)
    icons_dir = os.path.join(addon_path, 'icons')
    b = editor.addButton(
        icon=os.path.join(icons_dir, 'linebreak.png'),
        cmd="lb", 
        func=cleanLinebreaks,
        tip="Remove Linebreaks ({})".format(keystr(gc('shortcut'))),
        keys=gc('shortcut')
    )
    buttons.append(b)
    return buttons
addHook("setupEditorButtons", setupEditorButtonsFilter)


def add_to_context(view, menu):
    a = menu.addAction(_("Remove Linebreak"))
    a.triggered.connect(lambda _,e=view.editor: cleanLinebreaks(e))


if gc("show_in_context_menu", True):
    addHook("EditorWebView.contextMenuEvent", add_to_context)
