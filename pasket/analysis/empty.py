#!/usr/bin/env python

import lib.visit as v

from .. import util
from ..meta.template import Template
from ..meta.clazz import Clazz
from ..meta.method import Method
from ..meta.field import Field
from ..meta.statement import Statement
from ..meta.expression import Expression


class EmptyFinder(object):

  def __init__(self):
    self._cls_cnt = 0
    self._mtd_cnt = 0
    self._empty_cnt = 0
    self._fld_cnt = 0
    self._ffld_cnt = 0

  @property
  def cls_count(self):
    return self._cls_cnt

  @property
  def mtd_count(self):
    return self._mtd_cnt

  @property
  def empty_count(self):
    return self._empty_cnt

  @property
  def fld_count(self):
    return self._fld_cnt

  @property
  def ffld_count(self):
    return self._ffld_cnt

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
    if node.is_android or node.is_gui:
      self._cls_cnt = self._cls_cnt + 1

  def inClassOfInterest(self):
    return self._cur_cls.is_android or self._cur_cls.is_gui

  @v.when(Field)
  def visit(self, node):
    if self.inClassOfInterest():
      self._fld_cnt = self._fld_cnt + 1
      if node.is_final: self._ffld_cnt = self._ffld_cnt + 1

  @v.when(Method)
  def visit(self, node):
    if self.inClassOfInterest():
      self._mtd_cnt = self._mtd_cnt + 1
      if not node.body: self._empty_cnt = self._empty_cnt + 1

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node


"""
To import lib.*, run as follows:
  pasket $ python -m pasket.analysis.empty (demo_file | demo_path)+
"""
if __name__ == "__main__":
  from optparse import OptionParser
  usage = "usage: %prog demo_path"
  parser = OptionParser(usage=usage)

  (opt, argv) = parser.parse_args()

  if len(argv) < 1:
    parser.error("incorrect number of arguments")

  demo_files = []
  for arg in argv:
    demo_files.extend(util.get_files_from_path(arg, "java"))

  ast = util.toAST(demo_files)

  tmpl = Template(ast)

  counter = EmptyFinder()
  tmpl.accept(counter)

  print "classes: {}".format(counter.cls_count)
  print "methods: {} (empty: {})".format(counter.mtd_count, counter.empty_count)
  print "fields: {} (final: {})".format(counter.fld_count, counter.ffld_count)

