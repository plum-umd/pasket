import logging

import lib.visit as v
import lib.const as C

from .. import util
from ..meta.template import Template
from ..meta.clazz import Clazz
from ..meta.method import Method
from ..meta.field import Field
from ..meta.statement import Statement
from ..meta.expression import Expression

class Collection(object):

  @v.on("node")
  def visit(self, node):
    """
    This is the generic method to initialize the dynamic dispatcher
    """

  @v.when(Template)
  def visit(self, node): pass

  @v.when(Clazz)
  def visit(self, node): pass

  @v.when(Field)
  def visit(self, node): pass

  @v.when(Method)
  def visit(self, node): pass

  @v.when(Statement)
  def visit(self, node): return [node]

  __impl = { \
    C.J.MAP: C.J.TMAP, \
    C.J.LST: C.J.LNK, \
    C.J.LNK: C.J.LNK, \
    C.J.STK: C.J.STK, \
    C.J.QUE: C.J.DEQ }

  # replace interfaces with implementing classes
  # e.g., List<T> x = new List<T>(); => new ArrayList<T>();
  # this should *not* be recursive, e.g., Map<K, List<V>> => TreeMap<K, List<V>>
  @staticmethod
  def repl_itf(tname):
    if not util.is_collection(tname): return tname
    ids = util.of_collection(tname)
    collection = Collection.__impl[ids[0]]
    generics = ids[1:] # don't be recursive, like map(repl_itf, ids[1:])
    return u"{}<{}>".format(collection, ','.join(generics))

  @v.when(Expression)
  def visit(self, node):
    if node.kind == C.E.NEW:
      if node.e.kind == C.E.CALL:
        mid = unicode(node.e.f)
        if util.is_class_name(mid):
          node.e.f.id = Collection.repl_itf(mid)

    return node

