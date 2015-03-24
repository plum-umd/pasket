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

  def __init__(self, smpls, adp_conf):
    self._smpls = smpls
    self._smpl_clss = sample.decls(smpls).keys()
    self._adp_conf = adp_conf

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
  @staticmethod
  def is_candidate_mtd(mtd):
    return not mtd.is_init and not mtd.is_static

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

  # add a List<T> field
  @staticmethod
  def add_list(aux, clss):
    typ = u"{}<{}>".format(C.J.LST, C.J.OBJ)
    lst = Field(clazz=aux, typ=typ, name=C.ADP.adaptee)
    aux.add_flds([lst])
    setattr(aux, "list", lst)
    tmp = '_'.join([C.ADP.tmp, aux.name])
    for cls in clss:
      if cls.is_itf: continue
      for mtd in cls.inits:
        body = u"""
          {0} {1} = ({0})this;
          {1}.{2} = new {3}();
        """.format(aux.name, tmp, C.ADP.adaptee, typ)
        mtd.body.extend(to_statements(mtd, body))

  # a method that calls the adaptee
  @staticmethod
  def call_adaptee(aux, clss, adpt_cls, conf):
    callee = u'_'.join(["rcv", aux.name])
    # NOTE: piggy-back on Accessor's global array
    params = [(C.J.i, u"mtd_id"), (aux.name, callee)]
    reflect = Method(clazz=aux, mods=C.PBST, params=params, name=u"call_adaptee_"+adpt_cls)
    def body_on_role(role):
      adapter_id = getattr(aux, C.ADP.ADPT+"_"+role)
      def switch( cls ):
        mtds = Adapter.get_candidate_mtds(cls)
        typ = u"{}<{}>".format(C.J.LST, C.J.OBJ)
        def invoke(mtd):
          cls = mtd.clazz
          rcv = C.ADP.adaptee if cls.name == typ else u"_prvt_fld[" + getattr(aux, C.ADP.FLD+"_"+role) + u"]"
          # if there is no implementer for this method in interface, ignore it
          if cls.is_itf and not cls.subs: return u''
          if len(mtd.params) != 0 or mtd.typ != C.J.v: return u''
          call = u"if ({0} != null) {0}.{1}.{2}();".format(callee, rcv, mtd.name)
          adaptee_id = getattr(aux, C.ADP.ADPE+"_"+role)
          return u"if ({adaptee_id} == {mtd.id}) {{ {call} }}".format(**locals())
        invocations = filter(None, map(invoke, mtds))
        return "\nelse ".join(invocations)
      tests = filter(None, map(switch, clss))
      prefix = u"if (" + adapter_id + u" == mtd_id) {\n"
      return prefix + u"\nelse ".join(tests) + u"\n}"
    body = u"\nelse ".join(map(lambda x: body_on_role(u'_'.join([adpt_cls, str(x)])), range(conf[adpt_cls][0])))
    reflect.body = to_statements(reflect, body)
    Adapter.limit_depth(aux, reflect, 2)
    aux.add_mtds([reflect])
    setattr(aux, "call_adaptee_"+adpt_cls, reflect)

  ##
  ## generate an aux type
  ##
  def gen_aux_cls(self, tmpl, conf, smpl_clss):
    tmpl.acc_auxs.append(self.aux_name)
    aux = Clazz(name=self.aux_name, mods=[C.mod.PB], subs=self._clss)
    self.aux = aux

    instances = []
    for c in conf.iterkeys():
      n = conf[c][0]
      map(lambda i: instances.append(c + "_" + str(i)), range(n))

    # add an adaptee field into candidate classes
    self.add_list(aux, self._clss)

    # set role variables
    def set_role(role, ins):
      setattr(aux, '_'.join([role, ins]), '_'.join([role, ins, aux.name]))
    
    for role in C.adp_roles:
      map(partial(set_role, role), instances)
    
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
    map(chk_positive, map(lambda r: u'_'.join([C.ADP.FLD, r]), instances))

    mtd_ids = map(get_id, mtds)
    mtd_init = gen_range(mtd_ids)
    aux_int_adap = partial(aux_fld, mtd_init, C.J.i)
    adapter_roles = [C.ADP.ADPT, C.ADP.ADPE]

    def contains(cls, c):
      t = class_lookup(c)
      return cls <= t if t else False

    for c in conf.iterkeys():
      for x in range(conf[c][0]):
        adapter_flds = map(aux_int_adap, map(lambda r: u'_'.join([r, c, unicode(x)]), adapter_roles))
        aux.add_flds(adapter_flds + [aux_int(u'_'.join([C.ADP.FLD, c, unicode(x)]))])
      if util.exists(partial(contains, class_lookup(c)), smpl_clss) or c == "InvocationEvent": 
        Adapter.call_adaptee(aux, self._clss, c, conf)

    #checkers.append(u"assert (argNum(" + getattr(aux, C.ADP.ADPT) + ")) == 0 && (argNum(" + getattr(aux, C.ADP.ADPT) + ")) == 0;")
    #checkers.append(u"assert (retType(" + getattr(aux, C.ADP.ADPT) + ")) == -1 && (retType(" + getattr(aux, C.ADP.FLD) + ")) == -1;")

    add_artifacts([aux.name])
    return aux


  @v.when(Template)
  def visit(self, node):
    self.find_clss_involved(node)
    aux = self.gen_aux_cls(node, self._adp_conf, self._smpl_clss)
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

    cls = node.clazz
    def get_cat():
      for c in self._adp_conf.iterkeys():
        if cls <= class_lookup(c):
          return c
      return "InvocationEvent"
    cat = get_cat()

    # adapter candidate
    mname = "call_adaptee_"+cat
    if len(node.params) == self._adp_conf[cat][1] and not node.is_init and not node.is_static:
      args = u", ".join([unicode(node.id), C.J.THIS])
      call = u"{}({});".format(u".".join([self.aux_name, mname]), args)
      node.body += to_statements(node, call)
      logging.debug("{}.{} => {}.{}".format(cname, node.name, self.aux_name, mname))    

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node

