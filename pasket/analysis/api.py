#!/usr/bin/env python

import logging
import os
import sys

import lib.const as C
import lib.visit as v

from .. import util
from ..meta import class_lookup
from ..meta.template import Template
from ..meta.clazz import Clazz
from ..meta.method import Method
from ..meta.field import Field
from ..meta.statement import Statement
from ..meta.expression import Expression, typ_of_e

class APICollector(object):

  def __init__(self):
    self._apis = set([]) # { (cname, mname, param_typs) ... }
    self._cur_mtd = None

  @property
  def APIs(self):
    for api_t in self._apis:
      api = list(api_t)
      cname, mname, arg_typs = api[0], api[1], api[2:]
      yield cname, mname, arg_typs

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

    def wrap_typ_of_e(exp):
      try: return typ_of_e(self._cur_mtd, exp)
      except AttributeError:
        s_e = unicode(exp)
        if '.' in s_e:
          s_e_dots = s_e.split('.')
          if util.is_class_name(s_e_dots[0]): return s_e
          elif util.is_class_name(s_e_dots[-1]): return s_e_dots[-1]
        logging.debug("can't interpret " + s_e)
        return u"?"

    if node.kind == C.E.CALL:
      arg_typs = map(wrap_typ_of_e, node.a)
      if node.f.kind == C.E.DOT: # rcv.mid
        rcv_ty = wrap_typ_of_e(node.f.le)
        mname = node.f.re.id
        self._apis.add(tuple([rcv_ty, mname] + arg_typs))
      else: # mid
        mname = node.f.id
        if util.is_class_name(mname): cname = mname
        else: cname = self._cur_mtd.clazz.name
        self._apis.add(tuple([cname, mname] + arg_typs))

    return node


"""
To import lib.*, run as follows:
  pasket $ python -m spec.analysis.api [-t tmpl_path] (demo_file | demo_path)+
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
  spec_dir = os.path.join(pwd, "..")
  root_dir = os.path.join(spec_dir, "..")
  sys.path.append(root_dir)

  ## logging configuration
  logging.config.fileConfig(os.path.join(spec_dir, "logging.conf"))
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

  collector = APICollector()
  tmpl.accept(collector)

  for cname, mname, arg_typs in collector.APIs:
    print "{}.{}({})".format(cname, mname, ", ".join(arg_typs))

