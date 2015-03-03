#!/usr/bin/env python

import sys
import os
import re
import cStringIO

dd = "dexdump"

# Ljava/lang/Object; -> java.lang.Object
def of_java_ty(tname):
  if tname[0] == 'L' and tname[-1] == ';':
    return tname[1:-1].replace('/','.')
  else: return tname


# java.lang.Object -> Object
def exclude_pkg(cname):
  return cname.split('.')[-1]


def main():
  c = os.popen(' '.join(["which", dd]))
  which = c.readline()
  c.close()
  if not which: raise Exception("can't find %s" % dd)

  cls_re = re.compile("Class descriptor.*: '(L.*;)'")
  sup_re = re.compile("Superclass.*: '(L.*;)'")
  itf = "Interfaces"
  itm_re = re.compile("#\d+.*: '(L.*;)'")

  is_itfs = False
  itfs = []
  ignore_cls = False
  buf = cStringIO.StringIO()
  d = os.popen("%s %s" % (dd, sys.argv[1]))
  while True:
    line = d.readline()
    if len(line) == 0: break # EOF
    line = line.strip()

    if is_itfs:
      m = itm_re.search(line)
      if m:
        itm = of_java_ty(m.group(1)).replace('$','.')
        itfs.append(exclude_pkg(itm))
      else:
        if not ignore_cls and itfs:
          buf.write("implements %s " % (", ".join(itfs)))
        is_itfs = False
        itfs = []
        if not ignore_cls:
          print >>buf, "{\n}\n"
    elif itf in line: is_itfs = True

    elif cls_re.search(line):
      m = cls_re.search(line)
      cls = of_java_ty(m.group(1))
      cname = exclude_pkg(cls)
      ignore_cls = "R" == cname or cname.startswith("R$")
      if not ignore_cls: buf.write("class %s " % cname)

    elif sup_re.search(line):
      m = sup_re.search(line)
      sup = of_java_ty(m.group(1))
      if not ignore_cls and not "Object" in sup:
        buf.write("extends %s " % exclude_pkg(sup))

  print buf.getvalue()
  buf.close()
  d.close()

if __name__ == "__main__":
  if len(sys.argv) <= 1:
    print "usage: %s <apk>" % sys.argv[0]
    sys.exit(1)
  else: sys.exit(main())

