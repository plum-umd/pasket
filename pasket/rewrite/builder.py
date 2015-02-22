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

class Builder(object):

  @classmethod
  def find_builder(cls):
    names = [C.A.PUT, C.A.APPEND]
    return lambda anno: util.exists(lambda name: anno.by_name(name), names)

  @classmethod
  def find_assembler(cls):
    return lambda anno: anno.by_name(C.A.ASSEM)

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

  @staticmethod
  def __is_part(verbs, mname):
    return util.exists(lambda v: mname.startswith(v), verbs)

  b_verbs = ["add", "append", "put"]

  @staticmethod
  def is_builder(mname):
    return Builder.__is_part(Builder.b_verbs, mname)

  a_verbs = ["assemble", "build"]

  @staticmethod
  def is_assembler(mname):
    return Builder.__is_part(Builder.a_verbs, mname)

  @v.when(Method)
  def visit(self, node):
    if node.body or node.clazz.is_itf: return
    mname = node.name

    ## [naming convention]
    ## X addY(Y y);
    ##   =>
    ## X addY(Y y) {
    ##   this.ys.add(y);
    ##   return this;
    ## }
    ## [explicit annotation]
    ## @Append X m1(Y y);  =>  X m1(Y y) { ... }
    if Builder.is_builder(mname) or \
        util.exists(Builder.find_builder(), node.annos):

      # TODO: intro fields (or a field of list type) to hold parts
      # TODO: then assign (or append) the given part

      # if it will be used in a chain, return *this*
      if node.typ == node.clazz.name:
        logging.debug("builder chain: {}.{}".format(node.clazz.name, mname))
        ret_this = to_statements(node, u"return this;")
        node.body = node.body + ret_this

    elif Builder.is_assembler(mname) or \
        util.exists(Builder.find_assembler(), node.annos):
      pass # TODO

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node

