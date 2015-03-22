import logging

import lib.const as C
import lib.visit as v

from .. import util
from ..meta.template import Template
from ..meta.clazz import Clazz
from ..meta.method import Method
from ..meta.field import Field
from ..meta.statement import Statement, to_statements
from ..meta.expression import Expression

class SemanticChecker(object):

  def __init__(self, cmd):
    self._cmd = cmd

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
    # method without any proper return statement
    if not node.is_init and node.typ != C.J.v and not node.has_return:
      v = util.default_value(self._cmd, node.typ, node.name)
      node.body += to_statements(node, u"return {};".format(v))
      logging.debug("filling return value for {}: {}".format(node.signature, v))

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node

