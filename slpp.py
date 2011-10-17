import re

class SLPP:

    def __init__(self):
        self.text = ''
        self.ch = ''
        self.at = 0
        self.len = 0
        self.depth = 0
        self.space = re.compile('\s', re.M)
        self.alnum = re.compile('\w', re.M)

    def decode(self, text):
        if not text or type(text) is not str:
            return
        reg = re.compile('---.*$', re.M)
        text = reg.sub('', text, 0)
        self.text = text
        self.at, self.ch, self.depth = 0, '', 0
        self.len = len(text)
        self.next_chr()
        result = self.value()
        return result

    def encode(self, obj):
        if not obj:
            return
        self.depth = 0
        return self.__encode(obj)

    def __encode(self, obj):
        s = ''
        tab = '\t'
        newline = '\n'
        tp = type(obj).__name__
        if tp == 'str':
            s += '"'+obj+'"'
        elif tp == 'int' or tp == 'float' or tp == 'long' or tp == 'complex':
            s += str(obj)
        elif tp == 'bool':
            s += str(obj).lower()
        elif tp == 'list' or tp == 'tuple':
            s += "{" + newline
            self.depth += 1
            for el in obj:
                s += tab * self.depth + self.__encode(el) + ',' + newline
            self.depth -= 1
            s += tab * self.depth + "}"
        elif tp == 'dict':
            s += "{" + newline
            self.depth += 1
            for key in obj:
                #TODO: lua cannot into number keys. Add check.
                if type(key).__name__ == 'int':
                    s += tab * self.depth + self.__encode(obj[key]) + ',' + newline
                else:
                    s += tab * self.depth + key + ' = ' + self.__encode(obj[key]) + ',' + newline
            self.depth -= 1
            s += tab * self.depth + "}"
        return s


    def white(self):
        while self.ch:
            if self.space.match(self.ch):
                self.next_chr()
            else:
                break

    def next_chr(self):
        if self.at >= self.len:
            self.ch = None
            return None
        self.ch = self.text[self.at]
        self.at += 1
        return True

    def value(self):
        self.white()
        if not self.ch:
            return
        if self.ch == '{':
            return self.object()
        if self.ch == '"':
            return self.string()
        if self.ch.isdigit() or self.ch == '-':
            return self.number()
        return self.word()

    def string(self):
        s = ''
        if self.ch == '"':
            while self.next_chr():
                if self.ch == '"':
                    self.next_chr()
                    return str(s)
                else:
                    s += self.ch
        print "Unexpected end of string while parsing Lua string"

    def object(self):
        o = {}
        k = ''
        idx = 0
        self.depth += 1
        self.next_chr()
        self.white()
        if self.ch and self.ch == '}':
            self.depth -= 1
            self.next_chr()
            return o #Exit here
        else:
            while self.ch:
                self.white()
                if self.ch == '{':
                    o[idx] = self.object()
                    idx += 1
                    continue
                elif self.ch == '}':
                    self.depth -= 1
                    self.next_chr()
                    if k: o[idx] = k
                    if len([ key for key in o if type(key).__name__ == 'str' ]) == 0:
                        ar = []
                        for key in o: ar.insert(key, o[key])
                        o = ar
                    return o #or here
                else:
                    if self.ch == '"':
                        k = self.string()
                    else:
                        k = self.value()
                    self.white()
                    if self.ch == '=':
                        self.next_chr()
                        self.white()
                        o[k] = self.value()
                        idx += 1
                        k = ''
                    elif self.ch == ',':
                        self.next_chr()
                        self.white()
                        o[idx] = k
                        idx += 1
                        k = ''
        print "Unexpected end of table while parsing Lua string."#Bad exit here

    def word(self):
        s = ''
        if self.ch != '\n':
          s = self.ch
        while self.next_chr():
            if self.alnum.match(self.ch):
                s += self.ch
            else:
                if re.match('^true$', s, re.I):
                    return True
                elif re.match('^false$', s, re.I):
                    return False
                return str(s)

    def number(self):
        n = ''
        flt = False
        if self.ch == '-':
            n = '-'
            self.next_chr()
            if not self.ch or not self.ch.isdigit():
                print "Malformed number %s(no digits after initial minus)" % self.ch
                return 0
            self.next_chr()
        while self.ch and self.ch.isdigit():
            n += self.ch
            self.next_chr()
        if self.ch and self.ch == '.':
            n += self.ch
            flt = True
            self.next_chr()
            if not self.ch or not self.ch.isdigit():
                print "Malformed number %s (no digits after decimal point)" % self.ch
                return n+'0'
            else:
                n += self.ch
            while self.ch and self.ch.isdigit():
                n += self.ch
                self.next_chr()
        if flt:
            return float(n)
        return int(n)
