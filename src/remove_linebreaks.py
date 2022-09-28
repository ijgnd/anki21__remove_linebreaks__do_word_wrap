# by ijgnd 2019- 
# based upon https://ankiweb.net/shared/info/1290231794 which has this comment on top of it
    # Based upon https://ankiweb.net/shared/info/892669336 , edited with permission
    # To make copy/pasting from PDF files less cumbersome
    # Edited version made by Remco32
    # License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


# there's also an unpublished add-on from Glutanimate at
# https://github.com/glutanimate/anki-addons-misc/blob/master/src/editor_replace_linebreaks/editor_replace_linebreaks.py
# I don't think that it gets better results.

from .anki_version_detection import anki_point_version
from .config import gc

import os

import aqt
from aqt import mw
from aqt.editor import Editor

if anki_point_version >= 50:
    from aqt.gui_hooks import (
        editor_did_init_buttons,
        editor_will_show_context_menu,
        webview_will_set_content,
    )
else:
    from anki.hooks import addHook

from aqt.qt import (
    QKeySequence,
    Qt,
)


def get_selection_function():
    if anki_point_version <= 40:
        return "window.getSelection();"
    elif anki_point_version < 50:
        return "getCurrentField().shadowRoot.getSelection();"
    else:
        return "document.activeElement.shadowRoot.getSelection();"


def get_save_function():
    if anki_point_version <= 40:
        return "saveField('key');"
    else:
        return "saveNow(true);"
    


jsfunc_remove_breaks = """
var addon_remove_linbreaks_rarestring = '⁂⸗┴▓⍗➉';
var regex_addon_remove_linbreaks_rarestring = new RegExp(addon_remove_linbreaks_rarestring, "g");
function remove_breaks() {
    let sel = %(GETSEL)s
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
                        .replace(/&#173;<br>/g, '')
                        .replace(/&#xad;<br>/g, '')
                        .replace(/&#xAD;<br>/g, '')
                        .replace(/\u00AD<br>/g,'')
                        .replace(/-<br\/>/g, '')
                        .replace(/<br>/g, ' ')
                        .replace(/<br \/>/g, ' ')
                        .replace(/<br\/>/g, ' ')
                        .replace(regex_addon_remove_linbreaks_rarestring, '<br><br>');
    document.execCommand('insertHTML', false, temp_rb_tag.innerHTML);
    %(DOSAVE)s
};
"""% { 
"GETSEL": get_selection_function(),
"DOSAVE": get_save_function(),
}


if anki_point_version <= 49:
    aqt.editor._html = f"<script>{jsfunc_remove_breaks}</script>" + aqt.editor._html


def append_js_to_Editor(web_content, context):
    if isinstance(context, Editor):
        web_content.head += f"""\n<script>\n{jsfunc_remove_breaks}\n</script>\n"""
if anki_point_version >= 50:
    webview_will_set_content.append(append_js_to_Editor)



def process_selection(editor, selection):
    editor.web.eval("remove_breaks();")


def linebreak_helper(editor):
    selection = editor.web.selectedText()
    if selection:
        process_selection(editor, selection)


def remove_linebreaks(editor):
    selection = editor.web.selectedText()
    if selection:
        process_selection(editor, selection)
    else:
        jscmd = "document.execCommand('selectAll');"
        editor.web.evalWithCallback(jscmd, lambda _, e=editor: linebreak_helper(e))


def keystr(k):
    key = QKeySequence(k)
    return key.toString(QKeySequence.SequenceFormat.NativeText)


def add_button_to_editor(buttons, editor):
    addon_path = os.path.dirname(__file__)
    icons_dir = os.path.join(addon_path, 'icons')
    cut = gc('shortcut')
    if cut:
        cutfmt = f"({keystr(cut)})"
    else:
        cutfmt = ""
    b = editor.addButton(
        icon=os.path.join(icons_dir, 'linebreak.png'),
        cmd="remove_linebreaks", 
        func=lambda e=editor: remove_linebreaks(e),
        tip=f"Remove Linebreaks {cutfmt}",
        keys=gc('shortcut')
    )
    buttons.append(b)
    return buttons
if anki_point_version <= 49:
    addHook("setupEditorButtons", add_button_to_editor)
else:
    editor_did_init_buttons.append(add_button_to_editor)


def add_to_context(view, menu):
    a = menu.addAction("Remove Linebreak")
    a.triggered.connect(lambda _,e=view.editor: remove_linebreaks(e))
if gc("show_in_context_menu", True):
    if anki_point_version <= 49:
        addHook("EditorWebView.contextMenuEvent", add_to_context)
    else:
        editor_will_show_context_menu.append(add_to_context)
