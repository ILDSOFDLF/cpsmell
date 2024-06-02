import ast
import re
import sys
import codecs
import json

from json import JSONEncoder

is_python3 = hasattr(sys.version_info, 'major') and (sys.version_info.major == 3)

class AstEncoder(JSONEncoder):
    def default(self, o):
        if hasattr(o, '__dict__'):
            d = o.__dict__
            # workaround: decode strings if it's not Python3 code
            if not is_python3:
                for k in d:
                    if isinstance(d[k], str):
                        if k == 's':
                          d[k] = lines[d['start']:d['end']]
                        else:
                          d[k] = d[k].decode(enc)
            d['type'] = o.__class__.__name__
            return d
        else:
            return str(o)


enc = 'latin1'
lines = ''

def parse_dump(filename):
      if is_python3:
          encoder = AstEncoder()
      else:
          encoder = AstEncoder(encoding=enc)

      tree = parse_file(filename)
      encoded = encoder.encode(tree)
      encoded = json.loads(encoded)
      #print encoded
      return encoded

def parse_file(filename):
    global enc, lines
    enc, enc_len = detect_encoding(filename)
    f = codecs.open(filename, 'r', enc)
    lines = f.read()

    # remove BOM
    lines = re.sub(u'\ufeff', ' ', lines)

    # replace the encoding decl by spaces to fool python parser
    # otherwise you get 'encoding decl in unicode string' syntax error
    # print('enc:', enc, 'enc_len', enc_len)
    if enc_len > 0:
        lines = re.sub('#.*coding\s*[:=]\s*[\w\d\-]+',  '#' + ' ' * (enc_len-1), lines)

    f.close()
    return parse_string(lines, filename)


def parse_string(string, filename=None):
    tree = ast.parse(string)
    if filename:
        tree.filename = filename

    return tree


# short function for experiments
def p(filename):
    parse_dump(filename)


def detect_encoding(path):
    fin = open(path, 'rb')
    prefix = str(fin.read(80))
    encs = re.findall('#.*coding\s*[:=]\s*([\w\d\-]+)', prefix)
    decl = re.findall('#.*coding\s*[:=]\s*[\w\d\-]+', prefix)

    if encs:
        enc1 = encs[0]
        enc_len = len(decl[0])
        try:
            info = codecs.lookup(enc1)
            # print('lookedup: ', info)
        except LookupError:
            # print('encoding not exist: ' + enc1)
            return 'latin1', enc_len
        return enc1, enc_len
    else:
        return 'latin1', -1

if __name__ == '__main__':
    pass
    # print(parse_file('./test2.py',improved = True))
    # print(is_python3)
    # myast=astChecker.MyAst()
    # myast.fileName="test2.py"
    # astContent=parse_file("test2.py")
    # print(astContent)
    # print(ast.dump(astContent,indent=4))
    # myast.visit(astContent)
    #
    # for defitem in myast.imports:
    #     print(defitem)
    # #myast.visit_FunctionDef(astContent)
    # print("========================")
    # for i in myast.defmagic:
    #     print(i)
    # print("========================")
    # for j in myast.usedmagic:
    #     print(j)
    # print("========================")
    # for a in myast.subscriptnodes:
    #     print(a)
    # print("========================")
    # for b in myast.result:
    #     print(b)




