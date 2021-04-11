# by ijgnd 2019- 
# based upon https://ankiweb.net/shared/info/1290231794 which has this comment on top of it
    # Based upon https://ankiweb.net/shared/info/892669336 , edited with permission
    # To make copy/pasting from PDF files less cumbersome
    # Edited version made by Remco32
    # License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


# TODO incorporate https://github.com/glutanimate/anki-addons-misc/blob/master/src/editor_replace_linebreaks/editor_replace_linebreaks.py

import json
import os
import re

from bs4 import BeautifulSoup

from anki.hooks import addHook, wrap
from anki.utils import pointVersion

import aqt
from aqt import mw
from aqt.editor import Editor
# from aqt.utils import showInfo
# from aqt.browser import Browser
from aqt.qt import (
    QKeySequence,
    Qt,
)


def gc(arg, fail=False):
    conf = mw.addonManager.getConfig(__name__)
    if conf:
        return conf.get(arg, fail)
    return fail


rarestring = '⁂⸗┴▓⍗➉'
oldanki = pointVersion() <= 40

jsfunc_remove_breaks = """
<script>
var addon_remove_linbreaks_rarestring = '⁂⸗┴▓⍗➉';
var regex_addon_remove_linbreaks_rarestring = new RegExp(addon_remove_linbreaks_rarestring, "g");
function remove_breaks() {
    var sel = %(GETSEL)s
    var r = sel.getRangeAt(0);
    var content = r.cloneContents();
    var temp_rb_tag = document.createElement("span");
    temp_rb_tag.appendChild(content);
    temp_rb_tag.innerHTML = temp_rb_tag.innerHTML
                        .replace(/<div><br>/g, '<br><br>')
                        .replace(/<br><br>/g, addon_remove_linbreaks_rarestring)
                        .replace(/<div>/g, '<span>')
                        .replace(/<\/div>/g, '</span>')
                        .replace(/-<br>/g, '')
                        .replace(/-<br \/>/g, '')
                        .replace(/-<br\/>/g, '')
                        .replace(/<br>/g, ' ')
                        .replace(/<br \/>/g, ' ')
                        .replace(/<br\/>/g, ' ')
                        .replace(regex_addon_remove_linbreaks_rarestring, '<br><br>');
    document.execCommand('insertHTML', false, temp_rb_tag.innerHTML);
    %(DOSAVE)s;
}
</script>
""" % { 
"GETSEL": "window.getSelection();" if oldanki else "getCurrentField().shadowRoot.getSelection();",
"DOSAVE": "saveField('key');" if oldanki else "saveNow(true);"
}
aqt.editor._html = jsfunc_remove_breaks + aqt.editor._html


def process_selection(editor, selection):
    editor.web.eval("remove_breaks();")


def linebreakhelper(editor):
    selection = editor.web.selectedText()
    if selection:
        process_selection(editor, selection)


def cleanLinebreaks(editor):
    selection = editor.web.selectedText()
    if selection:
        process_selection(editor, selection)
    else:
        jscmd = "document.execCommand('selectAll');"
        editor.web.evalWithCallback(jscmd, lambda _, e=editor: linebreakhelper(e))


def keystr(k):
    key = QKeySequence(k)
    return key.toString(QKeySequence.NativeText)


def setupEditorButtonsFilter(buttons, editor):
    addon_path = os.path.dirname(__file__)
    icons_dir = os.path.join(addon_path, 'icons')
    cut = gc('shortcut')
    if cut:
        cutfmt = f"({keystr(cut)})"
    else:
        cutfmt = ""
    b = editor.addButton(
        icon=os.path.join(icons_dir, 'linebreak.png'),
        cmd="lb", 
        func=lambda e=editor: cleanLinebreaks(e),
        tip=f"Remove Linebreaks {cutfmt}",
        keys=gc('shortcut')
    )
    buttons.append(b)
    return buttons
addHook("setupEditorButtons", setupEditorButtonsFilter)


def add_to_context(view, menu):
    a = menu.addAction("Remove Linebreak")
    a.triggered.connect(lambda _,e=view.editor: cleanLinebreaks(e))


if gc("show_in_context_menu", True):
    addHook("EditorWebView.contextMenuEvent", add_to_context)
