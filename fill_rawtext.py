from pathlib import Path
import argparse
import shutil
import sys


# list[list[str]]
# A list of documents, each as a list of lines
Documents = dict[str, list[str]]


status_stack: list[str] = []
last_sitrep_len: int = 0


def sitrep():
    global last_sitrep_len
    cur_print_len = 0
    print('\r'+(' '*last_sitrep_len), end='\r')
    for item in status_stack:
        print(item, end=' ')
        cur_print_len += len(item)+1
    last_sitrep_len = cur_print_len
    sys.stdout.flush()


def loadds(filename: Path):  # -> Documents:
    with open(filename) as fdataset:
        # documents: list[list[str]] = []
        documents: dict[str, list[str]] = {}
        sentences: list[str] = []
        old_docid = ''
        while True:
            line = fdataset.readline()
            if line == '':  # encountered EOF
                if len(sentences) > 0:
                    # documents.append(sentences)
                    documents[old_docid] = sentences
                return documents
            elif line.strip() == '':
                continue
            else:
                assert line[-1] == '\n'
                line = line.strip()
                # fetch docid to detect change
                lineid = line.split('/')[0]
                docid = lineid[:lineid.rfind('-')]
                if docid != old_docid:
                    if len(sentences) > 0:
                        # documents.append(sentences)
                        documents[old_docid] = sentences
                        sentences = []
                    old_docid = docid
                sentences.append(line[len(lineid)+4:])


def split_tokens(sentence: str) -> list:
    if '[' not in sentence:
        return sentence.split('  ')
    # Otherwise, there're quoted NERs in the sentence

    # Find the span of first NER
    ner_start_pos = 0
    while ner_start_pos < len(sentence):
        if sentence[ner_start_pos] == '[':
            break
        ner_start_pos += 1
    ner_end_pos = ner_start_pos+1
    bracket_lvl = 1
    while ner_end_pos < len(sentence):
        if sentence[ner_end_pos] == '[':
            bracket_lvl += 1
        if sentence[ner_end_pos] == ']':
            bracket_lvl -= 1
            if bracket_lvl == 0:
                break
        ner_end_pos += 1
    if ner_end_pos >= len(sentence):
        print('Warning: NE bracket not closed: '+sentence)

    # Before first NER (we can safely split)
    before_content = sentence[:ner_start_pos].strip()
    before = before_content.split('  ') if before_content != '' else []
    # The NER part (there might be nested NERs)
    ner_part = split_tokens(sentence[ner_start_pos+1: ner_end_pos])
    # Type label of the NER part and following tokens
    after_content = sentence[ner_end_pos+1:]
    if '  ' in after_content:
        ner_lbl = after_content[:after_content.find('  ')]
        after = split_tokens(after_content[after_content.find('  ')+2:])
    else:
        ner_lbl = after_content
        after = []

    return before+[(ner_part, ner_lbl)]+after


def cvt_text(tokens: list[str | tuple]) -> str:
    text = ''
    for tok in tokens:
        if isinstance(tok, tuple):
            text += cvt_text(tok[0])  # corrsp. to NEs
        else:
            if '{' in tok:
                tok_text = tok[:tok.find('{')]
            else:
                tok_text = tok[:tok.find('/')]
            if tok_text not in ['〓']:
                text += tok_text
    return text


def main(rawfile: Path, anno_root: Path, out_root: Path):
    if not rawfile.exists():
        print('Fatal: Rawtext file does not exist')
        exit(-1)
    if not (anno_root.exists() and anno_root.is_dir()):
        print('Fatal: Annotation directory does not exist, or is not a directory')
        exit(-1)

    print('Reading and converting rawtext file...')
    docname2rawtext: dict[str, list[str]] = {}
    raw_docs = loadds(rawfile)
    for docid in raw_docs:
        texts = []
        for sentence in raw_docs[docid]:
            texts.append(cvt_text(split_tokens(sentence)))
        docname2rawtext[docid] = texts

    print('Saving converted corpus...')
    for docd in anno_root.iterdir():
        docname = docd.name
        if docname not in docname2rawtext:
            print(
                f'Warning: document {docname} is not found in PKU PD corpus, ignoring this document')
            continue
        out_docd = out_root/docname
        out_docd.mkdir(parents=True, exist_ok=True)
        for f_anno in docd.glob(docname+'*.xml'):
            try:
                shutil.copy(str(f_anno), str(out_docd))
            except shutil.SameFileError:
                pass  # occurs when converting in-place
        # write down rawtext file
        if (out_docd/docname).exists():
            print(
                f'Warning: raw text of document {docname} is already in place, ignoring')
        else:
            with (out_docd/docname).open('w', encoding='utf-8', newline='\r\n') as fdoc:
                for line in docname2rawtext[docname]:
                    assert line[-1] != '\n'
                    fdoc.write(line+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Use PKU-released People\'s Daily corpus to fill rawtext of Chinese-TimeNorm dataset')
    parser.add_argument(
        '-r', '--raw', help='Filename of PKU released People\'s Daily corpus')
    parser.add_argument('-x', '--xml', default='RMRB-sample',
                        help='Root directory of CTN annotation files')
    parser.add_argument('-d', '--dst', default='-',
        help='New root directory of generated complete corpus. If not specified, modification will be done in-place')
    arguments = parser.parse_args()
    rawtext = arguments.raw
    annotation_root = arguments.xml
    dst_root = arguments.dst
    if dst_root == '-':
        dst_root = annotation_root
    main(Path(rawtext), Path(annotation_root), Path(dst_root))
