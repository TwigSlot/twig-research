import sys
import os
import pickle
from extract_textblock import extract
import fitz

if(len(sys.argv) < 2):
    print("usage: python labeller.py <pdf_filename>")
    exit()
path = sys.argv[1]
if(path[-4:] != '.pdf'):
    print("usage: python labeller.py <pdf_filename>")
    print("<pdf_filename> must end in .pdf")
    exit()

pickle_filename = path.replace(".pdf","_labels.pickle")
doc = None
if(os.path.exists(pickle_filename)):
    print(f"Found save file {pickle_filename}. Loading from it...")
    print(f"If you do not wish to load an existing save file, rename or delete {pickle_filename}")
    with open(pickle_filename, 'rb') as f:
        doc = pickle.load(f)
if(doc is None):
    with open(path, 'rb') as f:
        print("extracting pdf contents...")
        doc = extract(f)
        fitz_doc = fitz.open(f)
        for i in doc:
            i.drawRect(fitz_doc)
        fitz_doc.save(path.replace('.pdf', '_annotated.pdf'))
        print("saved annotated pdf")
    with open(pickle_filename, 'wb') as f:
        pickle.dump(doc, f)

input("press enter > ")
tb_idx = 0
search_phrase = ""
while True:
    print("\n"*100) # clear screen
    for i in range(max(0,tb_idx-10), min(tb_idx+10, len(doc)-1)):
        if(i == tb_idx):
            print("{:<5} {:<8} {:<40} {:>10} {:>12}".format("idx", "rel idx", "textblock", "is_header", "header_level"))
        print("{:<5} {:<8} {:<40} {:>10} {:>12}".format(i, (i-tb_idx if i != tb_idx else ">>>>>"), doc[i].text[:40], 
            str(doc[i].isHeader) if doc[i].isHeader is not None else "", 
            str(doc[i].headerLevel) if doc[i].headerLevel is not None else ""))
    cmd = input("labeller > ")
    if(cmd.strip() == ""): cmd='s'
    if(cmd == "help"):
        print("""
        commands available:
        j/s/<enter>: down
        j 10: down x10
        k/w: up
        k 10: up x10
        /<phrase>: search for phrase
        n: next occurrence
        save: save progress
        q: quit
        z: jump to latest
        e: expand text
        r: relabel
        exec rel: calculate all relative properties
        """)
        input("press enter > ")
        continue
    if(cmd[:4] == "exec"):
        fn = cmd.replace("exec", "").strip()
        print('executing',fn)
        if(fn == "rel"):
            for i in range(len(doc)-1):
                doc[i+1].compare_prev(doc[i])
            input("press enter > ")
            continue
        elif(fn == "fix"):
            for i in doc:
                if(isinstance(i.font_size, tuple)):
                    i.fix_font()
            input("press enter > ")
            continue
        elif(fn == "dbg"):
            print('debug')
            print(doc[tb_idx].font_size)
            input("press enter > ")
            continue
    if(cmd == "tree"):
        for i in range(len(doc)):
            if(doc[i].isHeader and doc[i].headerLevel != -1):
                print("--" * doc[i].headerLevel + doc[i].text[:40])
        input("press enter > ")
        continue
    if(cmd == "save"):
        with open(pickle_filename, 'wb') as f:
            pickle.dump(doc, f)
        print(f"saved to {pickle_filename}")
        input("press enter > ")
        continue
    if(cmd[0] == 'e'):
        print(doc[tb_idx].text)
        input("press enter > ")
        continue
    if(cmd[0] == 'j'):
        cmd = 's'+cmd[1:]
    elif(cmd[0] == 'k'):
        cmd = 'w'+cmd[1:]
    if(cmd[0] == 's'):
        mv = 1
        try:
            mv = int(cmd[1:])
        except:
            print("usage: s <number>")
        tb_idx += mv
        tb_idx = min(tb_idx, len(doc)-1)
    elif(cmd[0] == 'w'):
        mv = 1
        try:
            mv = int(cmd[1:])
        except:
            print("usage: w <number>")
        tb_idx -= mv
        tb_idx = max(0, tb_idx)
    elif(cmd[0] == 'n'):
        for j in range(tb_idx+1, len(doc)):
            if(search_phrase in doc[j].text[:40].lower()):
                tb_idx = j
                break
    elif(cmd[0] == '/'):
        search_phrase = cmd.split('/')[1].lower()
        for j in range(tb_idx+1, len(doc)):
            if(search_phrase in doc[j].text[:40].lower()):
                tb_idx = j
                break
    elif(cmd[0] == 'z'):
        for j in range(tb_idx, len(doc)):
            if(doc[j].isHeader is not None):
                tb_idx = j
    elif(cmd[0] == 'r'):
        doc[tb_idx].isHeader = True if doc[tb_idx].isHeader is None else not doc[tb_idx].isHeader
        if(doc[tb_idx].isHeader):
            try:
                if(cmd[1:] == ''):
                    doc[tb_idx].headerLevel = int(input('header level? [-1] '))
                else:
                    try:
                        doc[tb_idx].headerLevel = int(cmd[1:])
                    except:
                        print("invalid header level, must be int!")
            except:
                doc[tb_idx].headerLevel = -1
        tb_idx += 1
    elif(cmd[0] == 'q'):
        if(input("confirm quit? did you save? [y/N] ").lower() == "y"):
            break