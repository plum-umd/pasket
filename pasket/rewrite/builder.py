import lib.visit as v

from .. import sample
from ..meta.template import Template
from ..meta.clazz import Clazz
from ..meta.method import Method
from ..meta.field import Field
from ..meta.statement import Statement
from ..meta.expression import Expression

class Builder(object):
  def __init__(self, smpls):
    self._smpls = smpls

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

  @v.when(Expression)
  def visit(self, node): return node

