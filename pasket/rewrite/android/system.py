from lib.typecheck import *
import lib.const as C
import lib.visit as v

from ...meta.template import Template
from ...meta.clazz import Clazz
from ...meta.method import Method
from ...meta.field import Field
from ...meta.statement import Statement, to_statements
from ...meta.expression import Expression

sys_conf = {
  C.ADR.TPM: ("TELEPHONY_SERVICE", "getDefault"),
}

class System(object):

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
    cname = node.clazz.name
    mname = node.name

    ## SystemServer.main
    if cname == C.ADR.SYS and mname == "main":
      body = u"""
        {0} manager = {0}.getInstance();
      """.format(C.ADR.SSM)
      # start system-level services
      for srv in sys_conf:
        name, getter = sys_conf[srv]
        body += u"""
          {srv} __srv_{srv} = {srv}.{getter}();
          manager.registerService(Context.{name}, __srv_{srv});
        """.format(**locals())
      node.body = to_statements(node, body)

    # Context.getSystemService
    if cname == C.ADR.CTX and mname == "getSystemService":
      _, nm = node.params[0]
      body = u"""
        {0} manager = {0}.getInstance();
        return manager.getService({1});
      """.format(C.ADR.SSM, nm)
      node.body = to_statements(node, body)

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node

