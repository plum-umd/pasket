import logging

import lib.const as C
import lib.visit as v

from .. import util
from ..meta.template import Template
from ..meta.clazz import Clazz
from ..meta.method import Method
from ..meta.field import Field
from ..meta.statement import Statement
from ..meta.expression import Expression, gen_E_c

class SemanticChecker(object):

  def __init__(self): pass

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
  def visit(self, node):
    if node.clazz.is_aux: return
    if node.clazz.is_itf: return
    # abstract method cannot have a body
    if node.is_abstract and node.body:
      logging.debug("clean up abstract method: {}".format(node.signature))
      node.body = []

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node):
    # if a hole is still there, replace it with any number
    if node.kind == C.E.HOLE: return gen_E_c(u"0")

    return node

