# by ijgnd 2019- 
# based upon https://ankiweb.net/shared/info/1290231794 which has this comment on top of it
    # Based upon https://ankiweb.net/shared/info/892669336 , edited with permission
    # To make copy/pasting from PDF files less cumbersome
    # Edited version made by Remco32
    # License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


# there's also an unpublished add-on from Glutanimate at
# https://github.com/glutanimate/anki-addons-misc/blob/master/src/editor_replace_linebreaks/editor_replace_linebreaks.py
# I don't think that it gets better results.

# TODO: add: spellchecking/autocorrect


import json
import os
import re

from bs4 import BeautifulSoup

from anki.hooks import addHook, wrap

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


def get_anki_version():
    try:
        # 2.1.50+ because of bdd5b27715bb11e4169becee661af2cb3d91a443, https://github.com/ankitects/anki/pull/1451
        from anki.utils import point_version
    except:
        try:
            # introduced with 66714260a3c91c9d955affdc86f10910d330b9dd in 2020-01-19, should be in 2.1.20+
            from anki.utils import pointVersion
        except:
            # <= 2.1.19
            from anki import version as anki_version
            return int(anki_version.split(".")[-1]) 
        else:
            return pointVersion()
    else:
        return point_version()
anki_21_version = get_anki_version()


rarestring = '⁂⸗┴▓⍗➉'


def get_selection_function():
    if anki_21_version <= 40:
        return "window.getSelection();"
    elif anki_21_version < 50:
        return "getCurrentField().shadowRoot.getSelection();",
    else:
        return ""


def get_save_function():
    if anki_21_version <= 40:
        return "saveField('key');"
    # elif anki_21_version < :
    #     return ""
    else:
        return "saveNow(true);"


jsfunc_remove_breaks = """

function getSelectionText() {
var text = "";
if (window.getSelection) {
    text = window.getSelection().toString();
} else if (document.selection && document.selection.type != "Control") { text = document.selection.createRange().text; }
return text;
}


var addon_remove_linbreaks_rarestring = '⁂⸗┴▓⍗➉';
var regex_addon_remove_linbreaks_rarestring = new RegExp(addon_remove_linbreaks_rarestring, "g");
function remove_breaks() {
    var sel2 = getSelectionText()
    console.log(sel2);
    console.log('äääääääääääääääääää');
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
                        .replace(/&shy;<br>/g, '')
                        .replace(/-<br\/>/g, '')
                        .replace(/<br>/g, ' ')
                        .replace(/<br \/>/g, ' ')
                        .replace(/<br\/>/g, ' ')
                        .replace(regex_addon_remove_linbreaks_rarestring, '<br><br>');
    document.execCommand('insertHTML', false, temp_rb_tag.innerHTML);
    %(DOSAVE)s;
}

""" % { 
"GETSEL": get_selection_function(),
"DOSAVE": get_save_function(),
}
if anki_21_version < 49:
    aqt.editor._html = f"<script>{jsfunc_remove_breaks}</script>" + aqt.editor._html
else:
    from aqt import gui_hooks
    def js_inserter(self):
        self.web.eval(jsfunc_remove_breaks)
    gui_hooks.editor_did_init.append(js_inserter)


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
    return key.toString(QKeySequence.SequenceFormat.NativeText)


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
