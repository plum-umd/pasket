#!/usr/bin/env python

from itertools import combinations

import logging
import os
import sys

from lib.typecheck import *
import lib.const as C
import lib.visit as v

from ... import util
from ...meta import class_lookup
from ...meta.template import Template
from ...meta.clazz import Clazz
from ...meta.method import Method
from ...meta.field import Field
from ...meta.statement import Statement, to_statements
from ...meta.expression import Expression, gen_E_hole

class R(object):

  def __init__(self):
    self._raw_Rs = set([])
    self._Rs = {} # { layout: [ id1, id2, ... ], ... }

    self._cur_cls = None
    self._cur_mtd = None

  @property
  def Rs(self):
    return self._Rs

  def build_R(self):
    # remove prefix, e.g., R.layout < R.layout.activity1
    _rs = set([])
    for r in self._raw_Rs:
      others = self._raw_Rs - set([r])
      if util.exists(lambda rr: rr.startswith(r), list(others)): continue
      else: _rs.add(r)

    # [R.layout.act1, R.id.x, R.id.y]
    # => { 'layout': ['act1'], 'id': ['x', 'y'] }
    for r in _rs:
      # ['R', 'layout', 'act1']
      elts = r.split('.')[1:] # skip the first element---"R"
      n_e = len(elts)
      cursor = self._Rs
      for (i, elt) in enumerate(elts):
        if elt not in cursor:
          if i < n_e-2:
            cursor[elt] = {}
          elif i < n_e-1: # 2nd-to-last level
            # { 'layout': [] }
            cursor[elt] = []
          else: # means, this is the leaf
            # { 'layout': ['act1'] }
            cursor.append(elt)
            continue
        cursor = cursor[elt]

  @v.on("node")
  def visit(self, node):
    """
    This is the generic method to initialize the dynamic dispatcher
    """

  @v.when(Template)
  def visit(self, node): pass

  @v.when(Clazz)
  def visit(self, node):
    self._cur_cls = node

  @v.when(Field)
  def visit(self, node): pass

  @v.when(Method)
  def visit(self, node):
    self._cur_mtd = node

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node):
    if not self._cur_cls.client: return node

    if node.kind == C.E.DOT:
      _id = unicode(node)
      if _id.startswith("R.") and _id not in self._raw_Rs:
        logging.debug(_id)
        self._raw_Rs.add(_id)

    return node


# generate R class
# which will have all R.* appearances in the given template
@takes(Template)
@returns(nothing)
def generate_R(tmpl):
  collector = R()
  tmpl.accept(collector)
  collector.build_R()

  cls_R = Clazz(name=u"R", mods=C.PBST)
  holes = []

  def dfs(cursor):
    if type(cursor) is dict:
      for elt in cursor:
        # the trick here is that the field's type is R itself
        # so that R can be used as receiver type again
        fld_elt = Field(clazz=cls_R, mods=C.PBST, name=unicode(elt), typ=cls_R.name)
        cls_R.add_flds([fld_elt])
        dfs(cursor[elt])

    elif type(cursor) is list: # 2nd-to-last level
      def leaf_hole(elt):
        hole = gen_E_hole()
        fld_elt = Field(clazz=cls_R, mods=C.PBST, name=unicode(elt), typ=C.J.i, init=hole)
        holes.append(elt)
        return fld_elt
      cls_R.add_flds(map(leaf_hole, cursor))

  dfs(collector.Rs)

  rg_chk = Method(clazz=cls_R, mods=[C.mod.ST, C.mod.HN], name=u"checkRange")
  checkers = []

  for f1, f2 in combinations(holes, 2):
    checkers.append(u"assert {} != {};".format(f1, f2))

  rg_chk.body += to_statements(rg_chk, u'\n'.join(checkers))
  cls_R.add_mtds([rg_chk])

  tmpl.add_classes([cls_R])


"""
To import lib.*, run as follows:
  pasket $ python -m pasket.rewrite.android.R [-t tmpl_path] (demo_file | demo_path)+
"""
if __name__ == "__main__":
  from optparse import OptionParser
  usage = "usage: %prog [-t tmpl_path] demo_path"
  parser = OptionParser(usage=usage)
  parser.add_option("-t", "--template", # same as run.py at the top level
    action="append", dest="tmpl", default=[],
    help="template folder")

  (opt, argv) = parser.parse_args()

  if len(argv) < 1:
    parser.error("incorrect number of arguments")

  pwd = os.path.dirname(__file__)
  src_dir = os.path.join(pwd, "..", "..")
  root_dir = os.path.join(src_dir, "..")
  sys.path.append(root_dir)

  ## logging configuration
  logging.config.fileConfig(os.path.join(src_dir, "logging.conf"))
  logging.getLogger().setLevel(logging.DEBUG)

  tmpl_files = []
  for tmpl_path in opt.tmpl:
    tmpl_files.extend(util.get_files_from_path(tmpl_path, "java"))

  demo_files = []
  for arg in argv:
    demo_files.extend(util.get_files_from_path(arg, "java"))

  ast = util.toAST(tmpl_files + demo_files)

  tmpl = Template(ast)

  ## mark client-side classes
  for client in demo_files:
    base = os.path.basename(client)
    cname = os.path.splitext(base)[0]
    cls = class_lookup(cname)
    cls.client = True

  collector = R()
  tmpl.accept(collector)
  collector.build_R()

  import pprint
  pp = pprint.PrettyPrinter(indent=2)
  pp.pprint(collector.Rs)

