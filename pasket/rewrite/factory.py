from functools import partial
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

class Factory(object):

  @classmethod
  def find_factory(cls):
    return lambda anno: anno.by_name(C.A.FACTORY)

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

  verbs = ["create", "make", "new"]

  @staticmethod
  def is_factory(mname):
    for v in Factory.verbs:
      if mname.startswith(v): return True
    return False

  ## [naming convention]
  ## X createX();
  ##   =>
  ## X createX() {
  ##   X obj = new X(); // for cleaner log conformity check
  ##   return obj;
  ## }
  ## [explicit annotation]
  ## @Factory Y m1();  =>  Y m1() { return new Y(); }
  ## @Factory(C) I m2();  =>  I m2() { return new C(); }
  @v.when(Method)
  def visit(self, node):
    if node.body or node.clazz.is_itf or node.typ in C.J.v: return
    mname = node.name
    factory = None
    if Factory.is_factory(mname):
      factory = node.typ
    elif util.exists(Factory.find_factory(), node.annos):
      _anno = util.find(Factory.find_factory(), node.annos)
      if hasattr(_anno, "cid"): factory = _anno.cid
      else: factory = node.typ

    if factory:
      logging.debug("filling factory: {}.{}".format(node.clazz.name, mname))
      init_e = Clazz.call_init_if_instantiable(factory, node.params)
      body = u"""
        {0} obj = {1};
        return obj;
      """.format(factory, str(init_e))
      node.body = to_statements(node, body)

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node

