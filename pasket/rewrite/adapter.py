import operator as op
from functools import partial
import logging

import lib.const as C
import lib.visit as v

from .. import add_artifacts
from .. import util
from .. import sample
from ..meta import class_lookup
from ..meta.template import Template
from ..meta.clazz import Clazz
from ..meta.method import Method
from ..meta.field import Field
from ..meta.statement import Statement, to_statements
from ..meta.expression import Expression, to_expression, gen_E_gen

class Adapter(object):

  def __init__(self, smpls):
    self._smpls = smpls
    self._smpl_clss = map(class_lookup, sample.decls(smpls).keys())

    self._clss = []
    self._aux_name = C.ADP.AUX
    self._aux = None

  @property
  def aux_name(self):
    return self._aux_name

  @property
  def aux(self):
    return self._aux

  @aux.setter
  def aux(self, v):
    self._aux = v

  @v.on("node")
  def visit(self, node):
    """
    This is the generic method to initialize the dynamic dispatcher
    """

  # find possible classes for Getter/Setter
  # assume all classes (except for interfaces) are candidates
  def find_clss_involved(self, tmpl):
    for cls in util.flatten_classes(tmpl.classes, "inners"):
      # ignore interface
      if cls.is_itf and not cls.subs:
        logging.debug("ignore interface {}".format(cls.name))
        continue
      self._clss.append(cls)

  # assume methods that participate will be neither <init> nor static
  def is_candidate_cls(self, cls):
    return util.exists(lambda c: c <= cls, self._smpl_clss)

  # assume methods that participate will be neither <init> nor static
  @staticmethod
  def is_candidate_mtd(mtd):
    return not mtd.is_init and not mtd.is_static and not mtd.params

  # retrieve candidate methods (in general)
  @staticmethod
  def get_candidate_mtds(cls):
    mtds = cls.mtds
    if cls.is_itf and cls.subs:
      mtds = util.flatten(map(op.attrgetter("mtds"), cls.subs))
    return filter(Adapter.is_candidate_mtd, mtds)

  # add a global counter
  @staticmethod
  def add_global_counter(aux, fname):
    z = to_expression(u"0")
    d = Field(clazz=aux, mods=C.PRST, typ=C.J.i, name=fname, init=z)
    aux.add_flds([d])
    return d

  # restrict call stack for the given method via a global counter
  @staticmethod
  def limit_depth(aux, mtd, depth):
    fname = mtd.name + "_depth"
    Adapter.add_global_counter(aux, fname)
    prologue = to_statements(mtd, u"""
      if ({fname} > {depth}) return;
      {fname} = {fname} + 1;
    """.format(**locals()))
    epilogue = to_statements(mtd, u"""
      {fname} = {fname} - 1;
    """.format(**locals()))
    mtd.body = prologue + mtd.body + epilogue

  # a method that calls the adaptee
  @staticmethod
  def call_adaptee(aux, clss):
    callee = u'_'.join(["rcv", aux.name])
    # NOTE: piggy-back on Accessor's global array
    rcv = u"_prvt_fld[" + getattr(aux, C.ADP.FLD) + u"]"
    params = [(C.J.i, u"mtd_id"), (aux.name, callee)]
    reflect = Method(clazz=aux, mods=C.PBST, params=params, name=u"call_adaptee")
    def switch( cls ):
      mtds = Adapter.get_candidate_mtds(cls)
      def invoke(mtd):
        cls = mtd.clazz
        # if there is no implementer for this method in interface, ignore it
        if cls.is_itf and not cls.subs: return u''
        if len(mtd.params) != 0 or mtd.typ != C.J.v: return u''
        call = u"""
          if ({0} != null && {0}.{1} != null) {{
            {0}.{1}.{2}();
          }}
        """.format(callee, rcv, mtd.name)
        adaptee_id = getattr(aux, "adaptee")
        return u"if ({adaptee_id} == {mtd.id}) {{ {call} }}".format(**locals())
      invocations = filter(None, map(invoke, mtds))
      return "\nelse ".join(invocations)
    tests = filter(None, map(switch, clss))
    prefix = u"if (" + getattr(aux, C.ADP.ADPT) + u" == mtd_id) {\n"
    reflect.body = to_statements(reflect, prefix + u"\nelse ".join(tests) + u"\n}")
    Adapter.limit_depth(aux, reflect, 2)
    aux.add_mtds([reflect])
    setattr(aux, "call_adaptee", reflect)

  ##
  ## generate an aux type
  ##
  def gen_aux_cls(self, tmpl):
    tmpl.acc_auxs.append(self.aux_name)
    aux = Clazz(name=self.aux_name, mods=[C.mod.PB], subs=self._clss)
    self.aux = aux

    # set role variables
    def set_role(role):
      setattr(aux, role, '_'.join([role, aux.name]))

    map(set_role, C.adp_roles)
    
    # add fields that stand for non-deterministic role choices
    def aux_fld(init, ty, nm):
      if hasattr(aux, nm): nm = getattr(aux, nm)
      return Field(clazz=aux, mods=[C.mod.ST], typ=ty, name=nm, init=init)
    hole = to_expression(C.T.HOLE)
    aux_int = partial(aux_fld, hole, C.J.i)

    c_to_e = lambda c: to_expression(unicode(c))

    mtds = util.flatten(map(Adapter.get_candidate_mtds, self._clss))

    ## range check
    rg_chk = Method(clazz=aux, mods=[C.mod.ST, C.mod.HN], name=u"checkRange")
    checkers = []
    gen_range = lambda ids: gen_E_gen(map(c_to_e, ids))
    get_id = op.attrgetter("id")

    # range check for an adapter index, which shouldn't be negative
    def chk_positive(role):
      rv = getattr(aux, role)
      checkers.append("assert {} >= 0;".format(rv))
    map(chk_positive, [C.ADP.FLD])

    mtd_ids = map(get_id, mtds)
    mtd_init = gen_range(mtd_ids)
    aux_int_adap = partial(aux_fld, mtd_init, C.J.i)
    adapter_roles = [C.ADP.ADPT, C.ADP.ADPE]
    adapter_flds = map(aux_int_adap, adapter_roles)
    aux.add_flds(adapter_flds + [aux_int(C.ADP.FLD)])
    Adapter.call_adaptee(aux, self._clss)

    #checkers.append(u"assert (argNum(" + getattr(aux, C.ADP.ADPT) + ")) == 0 && (argNum(" + getattr(aux, C.ADP.ADPT) + ")) == 0;")
    #checkers.append(u"assert (retType(" + getattr(aux, C.ADP.ADPT) + ")) == -1 && (retType(" + getattr(aux, C.ADP.FLD) + ")) == -1;")

    add_artifacts([aux.name])
    return aux


  @v.when(Template)
  def visit(self, node):
    self.find_clss_involved(node)
    aux = self.gen_aux_cls(node)
    node.add_classes([aux])

  @v.when(Clazz)
  def visit(self, node): pass

  @v.when(Field)
  def visit(self, node): pass

  @v.when(Method)
  def visit(self, node):
    # skip the method with explicit annotations, e.g., @Factory
    if node.annos: return
    # skip java.lang.*
    if node.clazz.pkg in ["java.lang"]: return
    # can't edit interface's methods as well as client side
    if node.clazz.is_itf or node.clazz.client: return
    cname = node.clazz.name

    # adapter candidate
    if len(node.params) == 0 and node.typ == C.J.v and not node.is_static:
      mname = u"call_adaptee"
      args = u", ".join([unicode(node.id), C.J.THIS])
      call = u"{}({});".format(u".".join([self.aux_name, mname]), args)
      node.body += to_statements(node, call)
      logging.debug("{}.{} => {}.{}".format(cname, node.name, self.aux_name, mname))

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node

