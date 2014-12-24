import lib.const as C
import lib.visit as v

from .. import add_artifacts
from .. import util
from .. import sample
from ..meta.template import Template
from ..meta.clazz import Clazz
from ..meta.method import Method
from ..meta.field import Field
from ..meta.statement import Statement, to_statements
from ..meta.expression import Expression, to_expression

class State(object):
  def __init__(self, smpls):
    self._smpls = smpls

  @v.on("node")
  def visit(self, node):
    """
    This is the generic method to initialize the dynamic dispatcher
    """

  def aux_cls_for_observer(self):
    newcls = Clazz(mods=[C.mod.PB], name=u"AuxState")
    def aux_int(nm):
      return Field(clazz=newcls, mods=[C.mod.ST], typ=C.J.i, name=nm, init=to_expression(u"??"))
    def aux_string(nm):
      return Field(clazz=newcls, mods=[C.mod.ST], typ=C.J.STR, name=nm, init=to_expression(u"??"))
    annos = map(aux_int, ["state","context","change_state","request","set_state"])
    rule1_int = map(aux_int, ["rule1_C","rule1_D","rule1_handle","rule1_request","rule1_curr_state"])
    rule2_int = map(aux_int, ["rule2_C","rule2_D","rule2_curr_state","rule2_M2"])
    rule3_int = map(aux_int, ["rule3_C","rule3_handle","rule3_request","rule3_handle_request","rule3_M3"])
    rule2_string = map(aux_string, ["rule2_obj1","rule2_obj2"])
    rule3_string = map(aux_string, ["rule3_obj"])
    state_param = map(aux_int, ["state_1","state_2","state_3"])
    context_param = map(aux_int, ["context_1","context_2","context_3","context_4"])
    change_state_param = [aux_int("change_state_1"), aux_string("change_state_2"), aux_string("change_state_3")]
    request_param = map(aux_int, ["request_1","request_2"])
    set_state_param = [aux_int("set_state_1"), aux_string("set_state_2")]
    newcls.add_flds(annos + rule1_int + rule2_int + rule3_int + rule2_string + rule3_string + state_param + context_param + change_state_param + request_param + set_state_param)
    
    # range check
    range_checker = Method(clazz=newcls, mods=[C.mod.PB, C.mod.ST], typ=C.J.v, name=u"checkRange")
    cls_len = len(Clazz.clss())
    mtd_len = len(Method.mtds())
    fld_len = len(Field.flds())
    def aux_range(nm, rg):
      return "assert 0 <= " + nm + "; assert " + nm + " < " + str(rg) + ";"

    add_artifacts([u"AuxState"])
    return newcls
    
  @v.when(Template)
  def visit(self, node): pass

  @v.when(Clazz)
  def visit(self, node): pass

  @v.when(Field)
  def visit(self, node): pass

  @v.when(Method)
  def visit(self, node): pass
    #if sample.mtd_appears(self._smpls, [node.clazz], node.name):
    #  node.body = to_statements(node, unicode("AuxState.allInOne(" + str(node.id) + ");"));

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node

