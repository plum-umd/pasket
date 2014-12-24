import copy as cp
import operator as op
from itertools import product
from functools import partial
import logging

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

class NewAccessor(object):
  # to build unique aux class names
  __cnt = 0

  aux_name = ""

  aux = Clazz()

  @staticmethod
  def get_aux():
    return NewAccessor.aux
  
  @staticmethod
  def set_aux(c):
    NewAccessor.aux = c
  
  @classmethod
  def new_aux(cls):
    cls.__cnt = cls.__cnt + 1
    return u"{}{}".format(C.ACC.AUX, cls.__cnt)

  def __init__(self, smpls):
    self._smpls = smpls
    self._cur_cls = None
    self._cur_mtd = None
    self._clss = []

  @v.on("node")
  def visit(self, node):
    """
    This is the generic method to initialize the dynamic dispatcher
    """

  # find possible classes for Getter/Setter
  # so as assume all classes
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

  # retrieve candidate methods
  @staticmethod
  def get_candidate_mtds(cls):
    mtds = cls.mtds
    if cls.is_itf and cls.subs:
      mtds = util.flatten(map(op.attrgetter("mtds"), cls.subs))
    return filter(NewAccessor.is_candidate_mtd, mtds)

  # retrieve constructors
  @staticmethod
  def get_constructors(cls):
    return filter(lambda x: x.is_init, cls.mtds)

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
    NewAccessor.add_global_counter(aux, fname)
    prologue = to_statements(mtd, u"""
      if ({fname} > {depth}) return;
      {fname} = {fname} + 1;
    """.format(**locals()))
    epilogue = to_statements(mtd, u"""
      {fname} = {fname} - 1;
    """.format(**locals()))
    mtd.body = prologue + mtd.body + epilogue

  # restrict the number of the method invocations
  @staticmethod
  def limit_number(mtd, fld, cnt, rval=u''):
    fname = fld.name
    guard = to_statements(mtd, u"""
      if ({fname} > {cnt}) return {rval};
      {fname} = {fname} + 1;
    """.format(**locals()))
    mtd.body = guard + mtd.body
  
  # common params for getter methods (and part of setter methods)
  @staticmethod
  def getter_params():
    return [ (C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (C.J.i, u"fld_id") ]

  # code for getting a field
  @staticmethod
  def getter(aux):
    params = NewAccessor.getter_params()
    getr = Method(clazz=aux, mods=C.PBST, typ=C.J.OBJ, params=params, name=u"get")
    getr.body = to_statements(getr, u"return callee._prvt_fld[fld_id];")
    aux.add_mtds([getr])
    setattr(aux, "gttr", getr)
  
  @staticmethod
  def igetter(aux):
    params = NewAccessor.getter_params()
    getr = Method(clazz=aux, mods=C.PBST, typ=C.J.i, params=params, name=u"iGet")
    getr.body = to_statements(getr, u"return callee._prvt_ifld[fld_id];")
    aux.add_mtds([getr])
    setattr(aux, "igttr", getr)
  
  @staticmethod
  def bgetter(aux):
    params = NewAccessor.getter_params()
    getr = Method(clazz=aux, mods=C.PBST, typ=C.J.z, params=params, name=u"bGet")
    getr.body = to_statements(getr, u"return callee._prvt_bfld[fld_id];")
    aux.add_mtds([getr])
    setattr(aux, "bgttr", getr)
  
  @staticmethod
  def sgetter(aux):
    params = NewAccessor.getter_params()
    getr = Method(clazz=aux, mods=C.PBST, typ=C.J.STR, params=params, name=u"sGet")
    getr.body = to_statements(getr, u"return callee._prvt_sfld[fld_id];")
    aux.add_mtds([getr])
    setattr(aux, "sgttr", getr)
  
  # code for setting a field
  @staticmethod
  def setter(aux):
    params = NewAccessor.getter_params() + [(C.J.OBJ, u"val")]
    setr = Method(clazz=aux, mods=C.PBST, params=params, name=u"set")
    setr.body = to_statements(setr, u"callee._prvt_fld[fld_id] = val;")
    aux.add_mtds([setr])
    setattr(aux, "sttr", setr)
  
  @staticmethod
  def isetter(aux):
    params = NewAccessor.getter_params() + [(C.J.i, u"val")]
    setr = Method(clazz=aux, mods=C.PBST, params=params, name=u"iSet")
    setr.body = to_statements(setr, u"callee._prvt_ifld[fld_id] = val;")
    aux.add_mtds([setr])
    setattr(aux, "isttr", setr)
  
  @staticmethod
  def bsetter(aux):
    params = NewAccessor.getter_params() + [(C.J.z, u"val")]
    setr = Method(clazz=aux, mods=C.PBST, params=params, name=u"bSet")
    setr.body = to_statements(setr, u"callee._prvt_bfld[fld_id] = val;")
    aux.add_mtds([setr])
    setattr(aux, "bsttr", setr)
  
  @staticmethod
  def ssetter(aux):
    params = NewAccessor.getter_params() + [(C.J.STR, u"val")]
    setr = Method(clazz=aux, mods=C.PBST, params=params, name=u"sSet")
    setr.body = to_statements(setr, u"callee._prvt_sfld[fld_id] = val;")
    aux.add_mtds([setr])
    setattr(aux, "ssttr", setr)
 
  @staticmethod
  def check_getter_param(aux, nums, c):
    rule = Method(clazz=aux, mods=[C.mod.ST, C.mod.HN], name=u"check"+c+u"GetterParam")
    def check_single_getter(n):
      return u"assert 0 == (argNum("+getattr(aux, "getter_"+c+"_"+str(n))+"));"
    rule.body = to_statements(rule, "\n".join(map(check_single_getter, range(nums[c][1]))))
    aux.add_mtds([rule])
  
  @staticmethod
  def check_setter_param(aux, nums, c):
    rule = Method(clazz=aux, mods=[C.mod.ST, C.mod.HN], name=u"check"+c+u"SetterParam")
    def check_single_setter(n):
      return u"assert 1 == (argNum("+getattr(aux, "setter_"+c+"_"+str(n))+"));"
    if (nums[c][2] > 0):
      rule.body = to_statements(rule, "\n".join(map(check_single_setter, range(nums[c][2]))))
      aux.add_mtds([rule])

  # getter will be invoked here
  @staticmethod
  def getter_in_one(aux, nums, fld_g, g_cnt):
    params = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee")]
    one = Method(clazz=aux, mods=C.PBST, typ=C.J.OBJ, params=params, name=u"getterInOne")
    def getter_switch_whole(cl):
      def getter_switch(role):
        aname = aux.name
        v = getattr(aux, "getter_"+cl+"_"+role)
        f = getattr(aux, "gttr").name
        argpairs = params+[(C.J.i, getattr(aux, u"gs_field_"+cl+"_"+role))]
        args = ", ".join(map(lambda (ty, nm): nm, argpairs))
        return u"if (mtd_id == {v}) return {aname}.{f}({args});".format(**locals())
      roles = map(str, range(nums[cl][1]))
      return "\nelse ".join(map(getter_switch, roles))
    one.body = to_statements(one, "\nelse ".join(map(getter_switch_whole, filter(lambda x: nums[x][1] > 0, nums.iterkeys()))))
    NewAccessor.limit_number(one, fld_g, g_cnt, C.J.N)
    aux.add_mtds([one])
    setattr(aux, "one", one)
  
  @staticmethod
  def igetter_in_one(aux, nums, fld_g, g_cnt):
    params = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee")]
    one = Method(clazz=aux, mods=C.PBST, typ=C.J.i, params=params, name=u"iGetterInOne")
    def getter_switch_whole(cl):
      def getter_switch(role):
        aname = aux.name
        v = getattr(aux, "getter_"+cl+"_"+role)
        f = getattr(aux, "igttr").name
        argpairs = params+[(C.J.i, getattr(aux, u"gs_field_"+cl+"_"+role))]
        args = ", ".join(map(lambda (ty, nm): nm, argpairs))
        return u"if (mtd_id == {v}) return {aname}.{f}({args});".format(**locals())
      roles = map(str, range(nums[cl][1]))
      return "\nelse ".join(map(getter_switch, roles))
    one.body = to_statements(one, "\nelse ".join(map(getter_switch_whole, filter(lambda x: nums[x][1] > 0, nums.iterkeys()))))
    NewAccessor.limit_number(one, fld_g, g_cnt, u"-1")
    aux.add_mtds([one])
    setattr(aux, "one", one)
  
  @staticmethod
  def bgetter_in_one(aux, nums, fld_g, g_cnt):
    params = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee")]
    one = Method(clazz=aux, mods=C.PBST, typ=C.J.z, params=params, name=u"bGetterInOne")
    def getter_switch_whole(cl):
      def getter_switch(role):
        aname = aux.name
        v = getattr(aux, "getter_"+cl+"_"+role)
        f = getattr(aux, "bgttr").name
        argpairs = params+[(C.J.i, getattr(aux, u"gs_field_"+cl+"_"+role))]
        args = ", ".join(map(lambda (ty, nm): nm, argpairs))
        return u"if (mtd_id == {v}) return {aname}.{f}({args});".format(**locals())
      roles = map(str, range(nums[cl][1]))
      return "\nelse ".join(map(getter_switch, roles))
    one.body = to_statements(one, "\nelse ".join(map(getter_switch_whole, filter(lambda x: nums[x][1] > 0, nums.iterkeys()))))
    NewAccessor.limit_number(one, fld_g, g_cnt, C.J.F)
    aux.add_mtds([one])
    setattr(aux, "one", one)
  
  @staticmethod
  def sgetter_in_one(aux, nums, fld_g, g_cnt):
    params = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee")]
    one = Method(clazz=aux, mods=C.PBST, typ=C.J.STR, params=params, name=u"sGetterInOne")
    def getter_switch_whole(cl):
      def getter_switch(role):
        aname = aux.name
        v = getattr(aux, "getter_"+cl+"_"+role)
        f = getattr(aux, "sgttr").name
        argpairs = params+[(C.J.i, getattr(aux, u"gs_field_"+cl+"_"+role))]
        args = ", ".join(map(lambda (ty, nm): nm, argpairs))
        return u"if (mtd_id == {v}) return {aname}.{f}({args});".format(**locals())
      roles = map(str, range(nums[cl][1]))
      return "\nelse ".join(map(getter_switch, roles))
    one.body = to_statements(one, "\nelse ".join(map(getter_switch_whole, filter(lambda x: nums[x][1] > 0, nums.iterkeys()))))
    NewAccessor.limit_number(one, fld_g, g_cnt, C.J.F) # TODO: default string?
    aux.add_mtds([one])
    setattr(aux, "one", one)
  
  # setter will be invoked here
  @staticmethod
  def setter_in_one(aux, nums, fld_s, s_cnt):
    params = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (C.J.OBJ, u"val")]
    one = Method(clazz=aux, mods=C.PBST, params=params, name=u"setterInOne")
    def setter_switch_whole(cl):
      def setter_switch(role):
        aname = aux.name
        v = getattr(aux, "setter_"+cl+"_"+role)
        f = getattr(aux, "sttr").name
        argpairs = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (C.J.i, getattr(aux, u"gs_field_"+cl+"_"+role)), (C.J.OBJ, u"val")]
        args = ", ".join(map(lambda (ty, nm): nm, argpairs))
        return u"if (mtd_id == {v}) {aname}.{f}({args});".format(**locals())
      roles = map(str, range(nums[cl][2]))
      return "\nelse ".join(map(setter_switch, roles))
    one.body = to_statements(one, "\nelse ".join(map(setter_switch_whole, filter(lambda x: nums[x][2] > 0, nums.iterkeys()))))
    NewAccessor.limit_number(one, fld_s, s_cnt)
    aux.add_mtds([one])
    setattr(aux, "one", one)
  
  @staticmethod
  def isetter_in_one(aux, nums, fld_s, s_cnt):
    params = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (C.J.i, u"val")]
    one = Method(clazz=aux, mods=C.PBST, params=params, name=u"iSetterInOne")
    def setter_switch_whole(cl):
      def setter_switch(role):
        aname = aux.name
        v = getattr(aux, "setter_"+cl+"_"+role)
        f = getattr(aux, "isttr").name
        argpairs = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (C.J.i, getattr(aux, u"gs_field_"+cl+"_"+role)), (C.J.OBJ, u"val")]
        args = ", ".join(map(lambda (ty, nm): nm, argpairs))
        return u"if (mtd_id == {v}) {aname}.{f}({args});".format(**locals())
      roles = map(str, range(nums[cl][1]))
      return "\nelse ".join(map(setter_switch, roles))
    one.body = to_statements(one, "\nelse ".join(map(setter_switch_whole, filter(lambda x: nums[x][2] > 0, nums.iterkeys()))))
    NewAccessor.limit_number(one, fld_s, s_cnt)
    aux.add_mtds([one])
    setattr(aux, "one", one)
  
  @staticmethod
  def bsetter_in_one(aux, nums, fld_s, s_cnt):
    params = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (C.J.z, u"val")]
    one = Method(clazz=aux, mods=C.PBST, params=params, name=u"bSetterInOne")
    def setter_switch_whole(cl):
      def setter_switch(role):
        aname = aux.name
        v = getattr(aux, "setter_"+cl+"_"+role)
        f = getattr(aux, "bsttr").name
        argpairs = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (C.J.i, getattr(aux, u"gs_field_"+cl+"_"+role)), (C.J.OBJ, u"val")]
        args = ", ".join(map(lambda (ty, nm): nm, argpairs))
        return u"if (mtd_id == {v}) {aname}.{f}({args});".format(**locals())
      roles = map(str, range(nums[cl][1]))
      return "\nelse ".join(map(setter_switch, roles))
    one.body = to_statements(one, "\nelse ".join(map(setter_switch_whole, filter(lambda x: nums[x][2] > 0, nums.iterkeys()))))
    NewAccessor.limit_number(one, fld_s, s_cnt)
    aux.add_mtds([one])
    setattr(aux, "one", one)
  
  @staticmethod
  def ssetter_in_one(aux, nums, fld_s, s_cnt):
    params = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (C.J.STR, u"val")]
    one = Method(clazz=aux, mods=C.PBST, params=params, name=u"sSetterInOne")
    def setter_switch_whole(cl):
      def setter_switch(role):
        aname = aux.name
        v = getattr(aux, "setter_"+cl+"_"+role)
        f = getattr(aux, "ssttr").name
        argpairs = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (C.J.i, getattr(aux, u"gs_field_"+cl+"_"+role)), (C.J.OBJ, u"val")]
        args = ", ".join(map(lambda (ty, nm): nm, argpairs))
        return u"if (mtd_id == {v}) {aname}.{f}({args});".format(**locals())
      roles = map(str, range(nums[cl][1]))
      return "\nelse ".join(map(setter_switch, roles))
    one.body = to_statements(one, "\nelse ".join(map(setter_switch_whole, filter(lambda x: nums[x][2] > 0, nums.iterkeys()))))
    NewAccessor.limit_number(one, fld_s, s_cnt)
    aux.add_mtds([one])
    setattr(aux, "one", one)

  # initializer will be invoked here
  @staticmethod
  def constructor_in_one(aux, nums, fld_c, c_cnt):
    params = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (C.J.OBJ, u"val"), (C.J.i, u"fld_id")]
    one = Method(clazz=aux, mods=C.PBST, params=params, name=u"constructorInOne")
    def constructor_switch_whole(cl):
      aname = aux.name
      v = getattr(aux, "cons_"+cl)
      f = getattr(aux, "sttr").name
      argpairs = NewAccessor.getter_params() + [(C.J.OBJ, u"val")]
      args = ", ".join(map(lambda (ty, nm): nm, argpairs))
      return u"if (mtd_id == {v}) {aname}.{f}({args});".format(**locals())
      #def constructor_switch(role):
        #aname = aux.name
        #v = getattr(aux, "cons_"+cl+"_"+role)
        #f = getattr(aux, "sttr").name
        #argpairs = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (C.J.i, v), (C.J.OBJ, u"val")]
        #args = ", ".join(map(lambda (ty, nm): nm, argpairs))
        #return u"if (mtd_id == {v}) {aname}.{f}({args});".format(**locals())
      #roles = map(str, range(nums[cl][1]))
      #return "\nelse ".join(map(constructor_switch, roles))
    one.body = to_statements(one, "\nelse ".join(map(constructor_switch_whole, filter(lambda n: nums[n][0]>=0, nums.iterkeys()))))
    NewAccessor.limit_number(one, fld_c, c_cnt)
    aux.add_mtds([one])
    setattr(aux, "one", one)
  
  @staticmethod
  def iconstructor_in_one(aux, nums, fld_c, c_cnt):
    params = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (C.J.i, u"val"), (C.J.i, u"fld_id")]
    one = Method(clazz=aux, mods=C.PBST, params=params, name=u"iConstructorInOne")
    def constructor_switch_whole(cl):
      aname = aux.name
      v = getattr(aux, "cons_"+cl)
      f = getattr(aux, "isttr").name
      argpairs = NewAccessor.getter_params() + [(C.J.i, u"val")]
      args = ", ".join(map(lambda (ty, nm): nm, argpairs))
      return u"if (mtd_id == {v}) {aname}.{f}({args});".format(**locals())
      #def constructor_switch(role):
        #aname = aux.name
        #v = getattr(aux, "cons_"+cl+"_"+role)
        #f = getattr(aux, "isttr").name
        #argpairs = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (C.J.i, v), (C.J.i, u"val")]
        #args = ", ".join(map(lambda (ty, nm): nm, argpairs))
        #return u"if (mtd_id == {v}) {aname}.{f}({args});".format(**locals())
      #roles = map(str, range(nums[cl][1]))
      #return "\nelse ".join(map(constructor_switch, roles))
    one.body = to_statements(one, "\nelse ".join(map(constructor_switch_whole, filter(lambda n: nums[n][0]>=0, nums.iterkeys()))))
    NewAccessor.limit_number(one, fld_c, c_cnt)
    aux.add_mtds([one])
    setattr(aux, "one", one)

  @staticmethod
  def bconstructor_in_one(aux, nums, fld_c, c_cnt):
    params = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (C.J.z, u"val"), (C.J.i, u"fld_id")]
    one = Method(clazz=aux, mods=C.PBST, params=params, name=u"bConstructorInOne")
    def constructor_switch_whole(cl):
      aname = aux.name
      v = getattr(aux, "cons_"+cl)
      f = getattr(aux, "bsttr").name
      argpairs = NewAccessor.getter_params() + [(C.J.z, u"val")]
      args = ", ".join(map(lambda (ty, nm): nm, argpairs))
      return u"if (mtd_id == {v}) {aname}.{f}({args});".format(**locals())
      #def constructor_switch(role):
        #aname = aux.name
        #v = getattr(aux, "cons_"+cl+"_"+role)
        #f = getattr(aux, "bsttr").name
        #argpairs = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (C.J.i, v), (C.J.z, u"val")]
        #args = ", ".join(map(lambda (ty, nm): nm, argpairs))
        #return u"if (mtd_id == {v}) {aname}.{f}({args});".format(**locals())
      #roles = map(str, range(nums[cl][1]))
      #return "\nelse ".join(map(constructor_switch, roles))
    one.body = to_statements(one, "\nelse ".join(map(constructor_switch_whole, filter(lambda n: nums[n][0]>=0, nums.iterkeys()))))
    NewAccessor.limit_number(one, fld_c, c_cnt)
    aux.add_mtds([one])
    setattr(aux, "one", one)

  @staticmethod
  def sconstructor_in_one(aux, nums, fld_c, c_cnt):
    params = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (C.J.STR, u"val"), (C.J.i, u"fld_id")]
    one = Method(clazz=aux, mods=C.PBST, params=params, name=u"sConstructorInOne")
    def constructor_switch_whole(cl):
      aname = aux.name
      v = getattr(aux, "cons_"+cl)
      f = getattr(aux, "ssttr").name
      argpairs = NewAccessor.getter_params() + [(C.J.STR, u"val")]
      args = ", ".join(map(lambda (ty, nm): nm, argpairs))
      return u"if (mtd_id == {v}) {aname}.{f}({args});".format(**locals())
      #def constructor_switch(role):
        #aname = aux.name
        #v = getattr(aux, "cons_"+cl+"_"+role)
        #f = getattr(aux, "ssttr").name
        #argpairs = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (C.J.i, v), (C.J.STR, u"val")]
        #args = ", ".join(map(lambda (ty, nm): nm, argpairs))
        #return u"if (mtd_id == {v}) {aname}.{f}({args});".format(**locals())
      #roles = map(str, range(nums[cl][1]))
      #return "\nelse ".join(map(constructor_switch, roles))
    one.body = to_statements(one, "\nelse ".join(map(constructor_switch_whole, filter(lambda n: nums[n][0]>=0, nums.iterkeys()))))
    NewAccessor.limit_number(one, fld_c, c_cnt)
    aux.add_mtds([one])
    setattr(aux, "one", one)
  
  @staticmethod
  def add_fld(cls, ty, nm):
    logging.debug("adding field {}.{} of type {}".format(cls.name, nm, ty))
    fld = Field(clazz=cls, typ=ty, name=nm)
    cls.add_flds([fld])
    cls.init_fld(fld)
    return fld

  # a method that calls the adaptee
  @staticmethod
  def call_adaptee(aux, clss):
    callee = u'_'.join(["rcv", aux.name])
    rcv = u"_prvt_fld["+getattr(aux, "field")+u"]"
    params = [(C.J.i, u"mtd_id"), (aux.name, callee)]
    reflect = Method(clazz=aux, mods=C.PBST, params=params, name=u"call_adaptee")
    def switch( cls ):
      mtds = NewAccessor.get_candidate_mtds(cls)
      def invoke(mtd):
        cls = mtd.clazz
        # if there is no implementer for this method in interface, ignore it
        if cls.is_itf and not cls.subs: return u''
        if len(mtd.params) != 0 or mtd.typ != C.J.v: return u''
        call = "if ({} != null) {}.{}.{}();".format(callee, callee, rcv, mtd.name)
        adaptee_id = getattr(aux, "adaptee")
        return u"if ({adaptee_id} == {mtd.id}) {{ {call} }}".format(**locals())
      invocations = filter(None, map(invoke, mtds))
      return "\nelse ".join(invocations)
    tests = filter(None, map(switch, clss))
    prefix = u"if (" + getattr(aux, "adapter") + u" == mtd_id) {\n"
    reflect.body = to_statements(reflect, prefix + u"\nelse ".join(tests) + u"\n}")
    NewAccessor.limit_depth(aux, reflect, 2)
    aux.add_mtds([reflect])
    setattr(aux, "call_adaptee", reflect)

  ##
  ## generate an aux type for getter/setter
  ##
  def gen_aux_cls(self, nums, clsses, tmpl):
    self.aux_name = NewAccessor.new_aux()
    tmpl.acc_auxs.append(self.aux_name)
    aux = Clazz(name=self.aux_name, mods=[C.mod.PB], subs=clsses)
    NewAccessor.set_aux(aux)
    constructors = []
    for c in nums:
      constructors.append("cons_"+c)
    constructor_args = []
    #for c in nums:
    #  new_args = map(lambda n: "cons_"+c+"_"+str(n), range(nums[c][0]))
    #  constructor_args.extend(new_args)
    
    # set role variables
    def get_g_roles(c, name):
      return map(lambda n: name+"_"+c+"_"+str(n), range(nums[c][1]))
    def get_s_roles(c, name):
      return map(lambda n: name+"_"+c+"_"+str(n), range(nums[c][2]))
    def gs_vars(c):
      return reduce(lambda x, y: x+y, map(partial(get_g_roles, c), ["getter", "gs_field"])) + reduce(lambda x, y: x+y, map(partial(get_s_roles, c), ["setter"]))
    all_gs_vars = reduce(lambda x, y: x+y, map(gs_vars, nums.iterkeys()))
    insts = map(lambda n: "accessor_"+n, nums.iterkeys())
    def set_role(role):
      setattr(aux, role, '_'.join([role, aux.name]))
    map(set_role, constructors)
    #map(set_role, constructor_args)
    map(set_role, all_gs_vars)
    map(set_role, insts)
    
    # add fields that stand for non-deterministic rule choices
    def aux_fld(init, ty, nm):
      if hasattr(aux, nm): nm = getattr(aux, nm)
      return Field(clazz=aux, mods=[C.mod.ST], typ=ty, name=nm, init=init)
    hole = to_expression(C.T.HOLE)
    aux_int = partial(aux_fld, hole, C.J.i)
    roles = constructors + insts + all_gs_vars # + constructor_args
    annos = map(aux_int, roles)
    aux.add_flds(annos)

    # range check
    rg_chk = Method(clazz=aux, mods=[C.mod.ST, C.mod.HN], name=u"checkRange")
    get_id = op.attrgetter("id")
    def is_accessor_candidate(cls):
      mtds = cls.mtds
      getter_mtds = filter(lambda m: len(m.params) == 0 and m.typ != C.J.v, mtds)
      cons_mtds = filter(lambda m: m.is_init, mtds)
      return getter_mtds or cons_mtds
    cls_ids = map(get_id, filter(is_accessor_candidate, clsses))
    #for c in clsses: print c.name + ": " + str(c.id)
    mtds = util.flatten(map(NewAccessor.get_candidate_mtds, clsses))
    #for m in mtds: print m.name + ": " + str(m.id)
    constructors = util.flatten(map(NewAccessor.get_constructors, clsses))
    #for cs in constructors: print cs.name + ": " + str(cs.id)
    mtd_ids = map(get_id, mtds)
    cons_ids = map(get_id, constructors)
    def aux_range(rl, c, nm, mtds, num_args, is_void):
      ids = map(get_id, filter(lambda m: len(m.params) == num_args and (m.typ == C.J.v) == is_void, mtds))
      eqs = map(lambda i: getattr(aux, rl+"_"+c+"_"+str(nm))+" == "+str(i), ids)
      return u"assert " + reduce(lambda x, y: x+" || "+y, eqs) + ";"

    def mtd_range(c):
      return reduce(lambda x,y: x+y, map(lambda m: [aux_range("getter", c, m, mtds, 0, False)], range(nums[c][1])), []) + reduce(lambda x,y: x+y, map(lambda m: [aux_range("setter", c, m, mtds, 1, True)], range(nums[c][2])), [])
    checkers = reduce(lambda x,y: x+y, map(mtd_range, nums.iterkeys()))

    def cls_range(c):
      eqs = map(lambda i: getattr(aux, "accessor_"+c)+" == "+str(i), cls_ids)
      return u"assert " + reduce(lambda x, y: x+" || "+y, eqs) + ";"
    checkers.append('\n'.join(map(cls_range, nums.iterkeys())))
    
    def cons_range(c):
      eqs = map(lambda i: getattr(aux, "cons_"+c)+" == "+str(i), cons_ids)
      return u"assert " + reduce(lambda x, y: x+" || "+y, eqs) + ";"
    checkers.append('\n'.join(map(cons_range, nums.iterkeys())))
    for c in nums.iterkeys():
      if (nums[c][0] >= 0):
        checkers.append("assert (argNum(" + getattr(aux, "cons_"+c) + ")) == " + str(nums[c][0]) + ";")
        checkers.append("assert (belongsTo(" + getattr(aux, "cons_"+c) + ")) == " + getattr(aux, "accessor_"+c) + ";")
    
    def owner_range(rl, c, ids):
      return map(lambda i: "assert subcls("+getattr(aux, "accessor_"+c)+", belongsTo("+getattr(aux, rl+"_"+c+"_"+str(i))+"));", ids)
    for c in nums.iterkeys():
      checkers.extend(owner_range("getter", c, range(nums[c][1])))
      checkers.extend(owner_range("setter", c, range(nums[c][2])))

    def bundle_getter_setter(c, gids, sids):
      return map(lambda (g, s): "assert belongsTo("+getattr(aux, "getter"+"_"+c+"_"+str(g))+") == belongsTo("+getattr(aux, "setter"+"_"+c+"_"+str(s))+");", product(gids, sids))
    for c in nums.iterkeys():
      checkers.extend(bundle_getter_setter(c, range(nums[c][1]), range(nums[c][2])))

    def getter_range(c):
      return map(lambda i: "assert (argNum("+getattr(aux, "getter_"+c+"_"+str(i))+")) == 0;", range(nums[c][1]))
    def setter_range(c):
      return map(lambda i: "assert (argNum("+getattr(aux, "setter_"+c+"_"+str(i))+")) == 1;", range(nums[c][2]))
    def gs_match(c):
      return map(lambda i: "assert subcls(argType("+getattr(aux, "setter_"+c+"_"+str(i))+", 0), retType("+getattr(aux, "getter_"+c+"_"+str(i))+"));", range(nums[c][2]))
    def gs_type_match(c):
        return map(lambda i: "assert argType("+getattr(aux, "cons_"+c)+", "+getattr(aux, "gs_field_"+c+"_"+str(i))+") == retType("+getattr(aux, "getter_"+c+"_"+str(i))+");", range(nums[c][1]))
    checkers.extend(reduce(lambda x,y: x+y, map(getter_range, nums.iterkeys())))
    checkers.extend(reduce(lambda x,y: x+y, map(setter_range, nums.iterkeys())))
    checkers.extend(reduce(lambda x,y: x+y, map(gs_match, nums.iterkeys())))
    checkers.extend(reduce(lambda x,y: x+y, map(gs_type_match, nums.iterkeys())))

    rg_chk.body = to_statements(rg_chk, '\n'.join(checkers))
    aux.add_mtds([rg_chk])
    
    for c in nums.iterkeys():
      if nums[c][1] > 0:
        NewAccessor.check_getter_param(aux, nums, c)
      if nums[c][2] > 0:
        NewAccessor.check_setter_param(aux, nums, c)

    # global counters

    # assumption: # of objects and events could be instantiated
    obj_cnt = sample.max_objs(self._smpls)
    evt_cnt = sample.max_evts(self._smpls)
    arg_cnt = sum(map(lambda (c, g, s): c, C.acc_conf.values()))
    # +1 : counting InvocationEvent
    c_cnt = (obj_cnt + evt_cnt + 1) * (arg_cnt + 1) / len(C.acc_conf.keys())

    # assumption: each getter could be invoked per event
    g_cnt = sum(map(lambda (c, g, s): g, C.acc_conf.values()))
    g_cnt = g_cnt * evt_cnt

    # assumption: setter could be invoked once, excluding constructor
    s_cnt = sum(map(lambda (c, g, s): s, C.acc_conf.values()))
    s_cnt = s_cnt * evt_cnt
    s_cnt = s_cnt + c_cnt # as constructor can call setter

    # getter pattern

    NewAccessor.getter(aux)
    NewAccessor.igetter(aux)
    NewAccessor.bgetter(aux)
    NewAccessor.sgetter(aux)

    fld_g = NewAccessor.add_global_counter(aux, u"getter_cnt")

    NewAccessor.getter_in_one(aux, nums, fld_g, g_cnt)
    NewAccessor.igetter_in_one(aux, nums, fld_g, g_cnt)
    NewAccessor.bgetter_in_one(aux, nums, fld_g, g_cnt)
    NewAccessor.sgetter_in_one(aux, nums, fld_g, g_cnt)

    # setter pattern

    NewAccessor.setter(aux)
    NewAccessor.isetter(aux)
    NewAccessor.bsetter(aux)
    NewAccessor.ssetter(aux)

    fld_s = NewAccessor.add_global_counter(aux, u"setter_cnt")

    NewAccessor.setter_in_one(aux, nums, fld_s, s_cnt)
    NewAccessor.isetter_in_one(aux, nums, fld_s, s_cnt)
    NewAccessor.bsetter_in_one(aux, nums, fld_s, s_cnt)
    NewAccessor.ssetter_in_one(aux, nums, fld_s, s_cnt)

    # constructor pattern

    fld_c = NewAccessor.add_global_counter(aux, "constructor_cnt")

    NewAccessor.constructor_in_one(aux, nums, fld_c, c_cnt)
    NewAccessor.iconstructor_in_one(aux, nums, fld_c, c_cnt)
    NewAccessor.bconstructor_in_one(aux, nums, fld_c, c_cnt)
    NewAccessor.sconstructor_in_one(aux, nums, fld_c, c_cnt)

    # adapter pattern

    adapter_roles = ["adapter", "adaptee", "field"]
    map(set_role, adapter_roles)
    aux_int = partial(aux_fld, hole, C.J.i)
    adapter_flds = map(aux_int, adapter_roles)
    aux.add_flds(adapter_flds)
    NewAccessor.call_adaptee(aux, clsses)

    add_artifacts([aux.name])
    return aux

    def adapter_range(rl, ids):
      eqs = map(lambda i: getattr(aux, rl)+" == "+str(i), ids)
      return u"assert " + reduce(lambda x, y: x+" || "+y, eqs) + ";"
    checkers = [adapter_range("adapter", mtd_ids), adapter_range("adaptee", mtd_ids), adapter_range("field", mtd_ids)]
    checkers.append(u"assert (argNum(" + getattr(aux, "adapter") + ")) == 0 && (argNum(" + getattr(aux, "adapter") + ")) == 0;")
    checkers.append(u"assert (retType(" + getattr(aux, "adapter") + ")) == -1 && (retType(" + getattr(aux, "field") + ")) == -1;")
    rg_chk.body += to_statements(rg_chk, '\n'.join(checkers))

  @v.when(Template)
  def visit(self, node):
    nums = C.acc_conf
    
    self.find_clss_involved(node)
    clss = self._clss
    node.add_classes([self.gen_aux_cls(nums, clss, node)])

  @v.when(Clazz)
  def visit(self, node):
    if (node.name == C.J.OBJ):
      def add_private_fld(n):
        NewAccessor.add_fld(node, NewAccessor.get_aux().name+u"[]", u"_prvt_fld")
        NewAccessor.add_fld(node, C.J.i+u"[]", u"_prvt_ifld")
        NewAccessor.add_fld(node, C.J.z+u"[]", u"_prvt_bfld")
        NewAccessor.add_fld(node, C.J.STR+u"[]", u"_prvt_sfld")
      map(add_private_fld, range(1))
    self._cur_cls = node

  @v.when(Field)
  def visit(self, node): pass

  @v.when(Method)
  def visit(self, node):
    self._cur_mtd = node
  
    # constructors
    if node.is_init and not node.clazz.client:
      for i in xrange(len(node.params)):
        mname = u""
        typ = node.params[i][0]
        if typ == C.J.i: mname = u"iConstructorInOne"
        elif typ == C.J.z: mname = u"bConstructorInOne"
        elif typ == C.J.STR: mname = u"sConstructorInOne"
        else: mname = u"constructorInOne"
        fid = unicode(i)
        args = ", ".join([unicode(node.id), C.J.THIS, unicode(node.params[i][1]), fid])
        node.body += to_statements(node, u"{}.{}({});".format(self.aux_name, mname, args))
      
      #aux = NewAccessor.get_aux()
      #nums = C.acc_conf
      #rg_chk = aux.mtd_by_name(u"checkRange")
      #for ty, nm in node.params:
        #NewAccessor.add_fld(aux, C.J.i, unicode(node.id) + nm)
        #role = unicode(node.id) + nm
        #hole = to_expression(C.T.HOLE)
        #fld = Field(clazz=aux, mods=[C.mod.ST], typ=C.J.i, name=role, init=hole)
        #aux.add_flds([fld])
        
        #old_body = rg_chk.body
        #def init_range(rl, c, nm, ids):
          #eqs = map(lambda i: role+" == "+str(i), range(nums[c][0]))
          #return u"assert " + reduce(lambda x, y: x+" || "+y, eqs) + ";"
        #rg_chk.body = to_statements(rg_chk, old_body + "\n" + )
      
      return
    
    if node.clazz.name in C.acc_default:
      return

    # getter candidate
    if len(node.params) == 0 and node.typ != C.J.v and not node.clazz.client:
      mname = u""
      if node.typ == C.J.i: mname = u"iGetterInOne"
      elif node.typ == C.J.z: mname = u"bGetterInOne"
      elif node.typ == C.J.STR: mname = u"sGetterInOne"
      else: mname = u"getterInOne"
      callee = u"null" if node.is_static else C.J.THIS
      node.body += to_statements(node, u"return " + self.aux_name + u"." + mname + u"(" + unicode(node.id) + u", " + callee + u");")

    # setter candidate
    if len(node.params) == 1 and node.typ == C.J.v and not node.clazz.client:
      mname = u""
      if node.params[0][0] == C.J.i: mname = u"iSetterInOne"
      elif node.params[0][0] == C.J.z: mname = u"bSetterInOne"
      elif node.params[0][0] == C.J.STR: mname = u"sSetterInOne"
      else: mname = u"setterInOne"
      callee = u"null" if node.is_static else C.J.THIS
      node.body += to_statements(node, self.aux_name + u"." + mname + u"(" + unicode(node.id) + u", " + callee + u", " + unicode(node.params[0][1]) + u");")

    # adapter candidate
    if len(node.params) == 0 and node.typ == C.J.v and not node.is_static:
      aux = NewAccessor.get_aux()
      #fname = u"_prvt_fld"
      #callee = C.J.THIS+u"."+fname+u"["+getattr(aux, "adapter")+u"]"
      node.body += to_statements(node, self.aux_name + u".call_adaptee(" + unicode(node.id) + u", " + unicode(C.J.THIS) + u");")

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node

