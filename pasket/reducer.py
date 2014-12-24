import copy as cp
from itertools import ifilter
from functools import partial
import operator as op
from string import Template as T
import logging

from lib.typecheck import *
import lib.const as C

from . import get_artifacts
import util
import sample
import anno
from meta import class_lookup
from meta.template import Template
from meta.clazz import Clazz
from meta.method import Method
from meta.field import Field
import meta.statement as st

# base class for exceptions in this module
class ReduceError(Exception): pass


__mark = "mark"


@takes(Clazz)
@returns(nothing)
def mark(cls):
  setattr(cls, __mark, True)


@takes(Clazz)
@returns(bool)
def is_marked(cls):
  return hasattr(cls, __mark)


@takes(Clazz)
@returns(nothing)
def unmark(cls):
  delattr(cls, __mark)


# delete classes in the template which do not appear in the samples
# classes whose subclasses are used should be kept for class hierarchy
@takes(list_of(sample.Sample), Template)
@returns(nothing)
def remove_cls(smpls, tmpl):
  cnames = sample.decls(smpls).keys() + tmpl.events.keys() + get_artifacts()

  def marker(cname):
    cls = class_lookup(cname)
    if not cls: return
    if is_marked(cls): return
    mark(cls)

    if cls.sup: marker(cls.sup)
    for itf in cls.itfs: marker(itf)
    for fld in cls.flds: marker(fld.typ)
    for mtd in cls.mtds:
      marker(mtd.typ)
      for ty, _ in mtd.params: marker(ty)

  # primitive types
  marker(C.J.OBJ)
  # interfaces with constants
  clss = util.flatten_classes(tmpl.classes, "inners")
  for itf in ifilter(op.attrgetter("is_itf"), clss):
    if itf.flds: mark(itf)

  map(marker, cnames)
  marked = filter(lambda cls: is_marked(cls), tmpl.classes)
  diff = list(set(tmpl.classes) - set(marked))
  if diff:
    logging.debug("unnecessary class(es): {}: {}".format(len(diff), diff))
  tmpl.classes = marked
  map(lambda cls: unmark(cls), tmpl.classes)


# add a simple getter method: fld_typ getFname() { return fld; }
@takes(Clazz, Field, unicode)
@returns(nothing)
def add_getter(cls, fld, mname):
  mtd_g = Method(clazz=cls, mods=fld.mods, typ=fld.typ, name=mname)
  fname = fld.name
  body = T("return ${fname};").safe_substitute(locals())
  mtd_g.body = st.to_statements(mtd_g, body)
  cls.mtds.append(mtd_g)
  # to replace annotation @Get(e) in expressions
  # or to encode static fields into sketch
  setattr(fld, "getter", mtd_g)


# reduce annotations at a field level
@takes(list_of(sample.Sample), Template, Clazz, Field)
@returns(nothing)
def reduce_anno_fld(smpls, tmpl, cls, fld):
  if not fld.annos: return
  cname = cls.name
  fname = fld.name
  Fname = util.cap_1st_only(fname)
  for _anno in fld.annos:

    ##
    ## @State(@Tag(...) | @All) int _state
    ##
    if _anno.name == C.A.STATE:
      setattr(cls, "state", fld)

      # find all the methods involved in this state variable
      where = _anno.accessed
      if where.name == C.A.ALL:
        mtds = cls.mtds[:] # quick copy, since mtds will be modified below
      elif where.name == C.A.TAG:
        find_tag = partial(anno.by_attr, {"tag": where.tag})
        mtds = cls.mtds_w_anno(find_tag)
      else: mtds = cls.mtd_by_name(where)

      # exclude setter to avoid a recursive call
      if hasattr(fld, "setter"): mtds.remove(fld.setter)
      # exclude error, if exists, to avoid redundant state update
      find_err = partial(anno.by_name, C.A.ERR)
      errs = cls.mtds_w_anno(find_err)
      if errs:
        if len(errs) > 1: raise ReduceError("ambiguous error state")
        err = errs[0]
        mtds.remove(err)

      # then add a statement to update this state variable into those methods
      for mtd in mtds:

        # TODO: currently, @Set should be reduced before @State
        if hasattr(fld, "setter"): # use setter if exists
          f_setter = fld.setter.name
          upd = "${f_setter}(??);"
        else: upd = "${fname} = ??;"

        if errs and err:
          e_name = err.name
          trans = "if (??) { " + upd + " } else { ${e_name}(); }"
        else: trans = upd

        body_tmpl = "repeat(??) { if (${fname} == ??) { " + trans + " } }"
        body = T(body_tmpl).safe_substitute(locals())
        mtd.body = st.to_statements(mtd, body) + mtd.body

      # introduce getter to replace @State in expressions later
      name = "get" + Fname
      mtd_g = Method(clazz=cls, typ=fld.typ, name=name)
      body = T("return ${fname};").safe_substitute(locals())
      mtd_g.body = st.to_statements(mtd, body)
      cls.mtds.append(mtd_g)
      setattr(fld, "getter", mtd_g)

    ##
    ## @Multiton({typ_v, ...})? Map<key,value> fname
    ##
    elif _anno.name == C.A.MULTI:
      # assume fld.typ is Map<key,value>
      key, value = util.extract_generics(fld.typ)
      if hasattr(_anno, "values"): values = _anno.values
      elif C.J.MAP in fld.typ: values = [value]

      # add a getter
      mname = sample.find_getter(smpls, values, Fname)
      params = [ (key, u"key") ]
      mtd_g = Method(clazz=cls, typ=value, name=mname, params=params)
      cls.mtds.append(mtd_g)

      # usage 1: Map<String,Object> systemService
      if len(values) > 1: pass
        # TODO: collect key-value mappings occurred at the samples
        # TODO: then add code to initialize those mappings into the constructor
      # usage 2: Map<int,View> viewById
      else: # i.e. values = [value]
        body = T("""
boolean chk = ${fname}.containsKey(key);
if (chk != true) {
  ${fname}.put(key, new ${value}(key));
}
return ${fname}.get(key);
""").safe_substitute(locals())
      mtd_g.body = st.to_statements(mtd_g, body)
      setattr(fld, "getter", mtd_g)

      # initialize this field
      cname = cls.name
      init = cls.mtd_by_sig(cname)
      if not init: init = cls.add_default_init()
      fld_typ = fld.typ
      body = T("${fname} = new ${fld_typ}();").safe_substitute(locals())
      init.body.extend(st.to_statements(init, body))

    ##
    ## @Get typ fname
    ## @Is typ fname
    ##
    elif _anno.name in [C.A.GET, C.A.IS]:
      # special case: Map<String, Object> _elements;
      if C.J.MAP in fld.typ: pass
        # TODO: collect get$T$ occurrences, where $T$ is any types
        # TODO: then add all those getters which look like below:
        # TODO: $T$ get$T$(String key) { return _elements.get(k); }

    ##
    ## @Has typ fname
    ##
    elif _anno.name == C.A.HAS:
      # add a checker, along with a boolean field, say "_setFname"
      name = "_set" + Fname
      fld_h = Field(clazz=cls, typ=C.J.z, name=name)
      cls.flds.append(fld_h)

      mname = sample.find_getter(smpls, [C.J.z], Fname, "has")
      mtd_h = Method(clazz=cls, typ=C.J.z, name=mname)
      body = T("return ${name};").safe_substitute(locals())
      mtd_h.body = st.to_statements(mtd_h, body)

      # find the setter and add a statement: _setFname := true
      if hasattr(fld, "setter"):
        mtd_s = fld.setter
        body = T("${name} = true;").safe_substitute(locals())
        mtd_s.body.extend(st.to_statements(mtd_s, body))

    ##
    ## @Put(typ_b) typ fname
    ##
    elif _anno.name == C.A.PUT:
      # special case: Map<String, Object> _elements;
      if C.J.MAP in fld.typ: pass
        # TODO: collect put$T$ occurrences, where $T$ is any types
        # TODO: then add all those putters which look like below:
        # TODO: void put$T$(String k, $T$ v) { _elements.put(k, v); }
      else: pass

    ##
    ## @Append typ fname
    ##


# reduce annotations at a method level
@takes(list_of(sample.Sample), Template, Clazz, Method)
@returns(nothing)
def reduce_anno_mtd(smpls, tmpl, cls, mtd):
  if not mtd.annos: return
  mname = mtd.name
  for _anno in mtd.annos:

    ##
    ## @Error void mname()
    ##
    if _anno.name == C.A.ERR:
      if not hasattr(cls, "state"): raise ReduceError("no state variable")
      setattr(cls.state, "error", mtd)
      state = cls.state.name
      body = T("${state} = ??;").safe_substitute(locals())
      mtd.body = st.to_statements(mtd, body) + mtd.body

    ##
    ## @Assemble typ mname(...)
    ##

    ##
    ## @CFG(other_mname) typ mname(...)
    ##
    elif _anno.name == C.A.CFG:
      # find the designated method
      _, cls_c_name, mtd_c_name = util.explode_mname(_anno.mid)
      if cls_c_name: mtd_c = class_lookup(cls_c_name).mtd_by_name(mtd_c_name)
      else: mtd_c = cls.mtd_by_name(mtd_c_name)
      # and then copy its body
      if mtd_c: mtd.body = mtd_c[0].body


# reduce annotations at an expression level
# NOTE: returns either an expression or a list of statements
@takes(Template, Clazz, Method, st.Expression, optional(st.Expression))
@returns((st.Expression, list_of(st.Statement)))
def reduce_anno_e(tmpl, cls, mtd, e, pe=None):
  curried = partial(reduce_anno_e, tmpl, cls, mtd)
  if e.kind == C.E.ANNO:
    _anno = e.anno

    ##
    ## Getters
    ##
    if _anno.name in [C.A.STATE, C.A.GET]:
      args = []
      if _anno.name == C.A.STATE:
        # @State(this) -> this.getter()
        if _anno.accessed == C.J.THIS:
          mtd_g = cls.state.getter
          f = st.gen_E_id(mtd_g.name)
        # @State(var) -> var.getter()
        else:
          var = _anno.accessed
          tname = mtd.vars[var]
          mtd_g = class_lookup(tname).state.getter
          f = st.gen_E_dot(st.gen_E_id(var), st.gen_E_id(mtd_g.name))
      # @Get(var.fname, args?) -> var.getFname(args?)
      elif _anno.name == C.A.GET:
        var, fname = _anno.fid.split('.')
        tname = mtd.vars[var]
        mtd_g = class_lookup(tname).fld_by_name(fname).getter
        f = st.gen_E_dot(st.gen_E_id(var), st.gen_E_id(mtd_g.name))
        if hasattr(_anno, "args"): args = _anno.args
      return st.gen_E_call(f, args)

    ##
    ## Setter
    ##
    # @Update(var) -> var.setter(??)
    elif _anno.name == C.A.UPDATE:
      var, fname = _anno.fid.split('.')
      tname = mtd.vars[var]
      mtd_s = class_lookup(tname).fld_by_name(fname).setter
      f = st.gen_E_dot(st.gen_E_id(var), st.gen_E_id(mtd_s.name))
      return st.gen_E_call(f, [st.gen_E_hole()])

    ##
    ## Generator
    ##
    elif _anno.name in [C.A.ALL, C.A.TAG]:
      if _anno.name == C.A.ALL: tag_g = u"gen_all"
      else: tag_g = u"gen_" + _anno.tag # assume tag name is unique
      # (var.)? @anno
      if not pe: cls_g = cls
      else: cls_g = class_lookup(mtd.vars[unicode(pe.le)])

      if hasattr(cls_g, tag_g): mtd_g = getattr(cls_g, tag_g)
      else: # introduce generator
        if _anno.name == C.A.ALL: mtds = cls_g.mtds
        else: # C.A.TAG
          find_tag = partial(anno.by_attr, {"tag": _anno.tag})
          mtds = cls_g.mtds_w_anno(find_tag)
        mtd_g = Method(clazz=cls_g, mods=[C.mod.GN], name=tag_g)
        body = "int t = ??;\n"
        for i, mtd in enumerate(mtds):
          mid = mtd.name
          case = T("if (t == ${i}) { ${mid}(); }\n").safe_substitute(locals())
          body = body + case

        body = body + "assert t <= {};".format(len(mtds))
        mtd_g.body = st.to_statements(mtd_g, body)

        cls_g.mtds.append(mtd_g)
        setattr(cls_g, tag_g, mtd_g)

      # @Tag("tag") | @All -> gen_tag | gen_all
      return st.gen_E_id(mtd_g.name)

    ##
    ## Reflection
    ##
    # @New should be handled differently
    # e.g., for "ClassName".@New({ args })
    # Sketch: new ClassName(args);
    # Java: (ClassName)(Class.forName("ClassName").newInstance(args));
    elif _anno.name == C.A.NEW: pass

    ##
    ## Comparator
    ##
    # @Compare will be encoded into a regex generator in Sketch
    # and then will be replaced with a proper operator in Java
    elif _anno.name in [C.A.CMP, C.A.CMP_STR]: pass

    ##
    ## Observers
    ##
    # event sending
    elif _anno.name == C.A.EVENT: pass # TODO

    # a list that maintains the registered observers
    elif _anno.name == C.A.OBSS:
      if not hasattr(cls, "obs"):
        cls_o_name, _ = find_observer_at_cls(tmpl, cls)
        add_obs(cls, cls_o_name)
      return st.gen_E_id(cls.obs.name)

    # invoke the @Notified method
    elif _anno.name == C.A.NOTI:
      mtd_noti = find_noti(tmpl, cls)
      rcv = _anno.args[0]
      call_noti = st.gen_E_dot(rcv, st.gen_E_id(mtd_noti.name))
      return st.gen_E_call(call_noti, _anno.args[1:])

  elif e.kind in [C.E.BOP, C.E.DOT]:
    e.le = curried(e.le, e)
    e.re = curried(e.re, e)

  elif e.kind == C.E.NEW:
    e.e = curried(e.e)

  elif e.kind == C.E.CALL:
    e.f = curried(e.f)
    map(curried, e.a)

  return e


# statements cannot have annotations
# bypass statement structures and continue to expressions
@takes(Template, Clazz, Method, st.Statement)
@returns(list_of(st.Statement))
def reduce_anno_s(tmpl, cls, mtd, s):
  curried_e = partial(reduce_anno_e, tmpl, cls, mtd)
  curried_s = partial(reduce_anno_s, tmpl, cls, mtd)

  if s.kind in [C.S.EXP, C.S.ASSERT, C.S.RETURN]:
    red_e = curried_e(s.e)
    if type(red_e) is list: return red_e
    else: s.e = red_e

  elif s.kind == C.S.ASSIGN:
    s.le = curried_e(s.le)
    s.re = curried_e(s.re)

  elif s.kind == C.S.IF:
    s.e = curried_e(s.e)
    s.t = util.flatten(map(curried_s, s.t))
    s.f = util.flatten(map(curried_s, s.f))

  elif s.kind in [C.S.WHILE, C.S.REPEAT]:
    s.e = curried_e(s.e)
    s.b = util.flatten(map(curried_s, s.b))

  elif s.kind == C.S.FOR:
    s.i = curried_e(s.i)
    s.init = curried_e(s.init)
    s.b = util.flatten(map(curried_s, s.b))

  return [s]


# reduce annotations in the template
# according to the samples and annotation reduction rules
@takes(list_of(sample.Sample), Template)
@returns(nothing)
def reduce_anno(smpls, tmpl):
  for cls in util.flatten_classes(tmpl.classes, "inners"):
    for fld in cls.flds:
      reduce_anno_fld(smpls, tmpl, cls, fld)
    for mtd in cls.mtds:
      reduce_anno_mtd(smpls, tmpl, cls, mtd)
      red_s = map(partial(reduce_anno_s, tmpl, cls, mtd), mtd.body)
      mtd.body = util.flatten(red_s)

