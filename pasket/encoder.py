import math
import cStringIO
import os
import copy as cp
from itertools import chain, ifilter, ifilterfalse
from functools import partial
import re
import operator as op
from string import Template as T
import logging

from lib.typecheck import *
import lib.const as C

import util
import sample
from meta import methods, classes, class_lookup
from meta.template import Template
from meta.clazz import Clazz, find_fld, find_mtd_by_name, find_mtd_by_sig, find_base
from meta.method import Method, sig_match
from meta.field import Field
from meta.statement import Statement
import meta.statement as st
from meta.expression import Expression, typ_of_e
import meta.expression as exp

# constants regarding sketch
C.SK = util.enum(z=u"bit", self=u"self")

# global constants that should be placed at every sketch file
_const = u''

# among class declarations in the template
# exclude subclasses so that only the base class remains
# (will make a virtual struct representing all the classes in that hierarchy)
@takes(list_of(Clazz))
@returns(list_of(Clazz))
def rm_subs(clss):
  # { cname: Clazz(cname, ...), ... }
  decls = { cls.name: cls for cls in clss }

  # remove subclasses
  for cname in decls.keys():
    if util.is_collection(cname): continue
    cls = class_lookup(cname)
    if not cls.is_class: continue
    if cls.is_aux: continue # virtual relations; don't remove sub classes
    for sub in cls.subs:
      if sub.name in decls:
        logging.debug("{} < {}".format(sub.name, cname))
        del decls[sub.name]
    for sup in util.ffilter([cls.sup]):
      if sup in decls and cname in decls:
        logging.debug("{} < {}".format(cname, sup))
        del decls[cname]

  return decls.values()


# convert the given type name into a newer one
_ty = {} # { tname : new_tname }

@takes(dict_of(unicode, unicode))
@returns(nothing)
def add_ty_map(m):
  global _ty
  for key in m: _ty[key] = m[key]


@takes(unicode)
@returns(unicode)
def trans_ty(tname):
  _tname = util.sanitize_ty(tname.strip())
  array_regex = r"([^ \[\]]+)((\[\])+)"
  m = re.match(array_regex, _tname)

  global _ty
  r_ty = _tname
  # to avoid primitive types that Sketch doesn't support
  if _tname == C.J.z: r_ty = C.SK.z
  elif _tname in [C.J.b, C.J.s, C.J.j]: r_ty = C.J.i
  # TODO: parameterize len?
  elif _tname in [C.J.c+"[]"]: r_ty = u"{}[51]".format(C.J.c)
  elif _tname in [C.J.INT]: r_ty = C.J.i
  # array bounds
  elif m:
    r_ty = trans_ty(m.group(1)) + \
        "[{}]".format(len(methods())) * len(re.findall(r"\[\]", m.group(2)))
  # use memoized type conversion
  elif _tname in _ty: r_ty = _ty[_tname]
  # convert Java collections into an appropriate struct name
  # Map<K,V> / List<T> / ... -> Map_K_V / List_T / ...
  elif util.is_collection(_tname):
    r_ty = '_'.join(util.of_collection(_tname))
    logging.debug("{} => {}".format(_tname, r_ty))
    _ty[_tname] = r_ty

  return r_ty


# check whether the given type is replaced due to class hierarchy
@takes(unicode)
@returns(bool)
def is_replaced(tname):
  return tname != trans_ty(tname)


# sanitize method name
# e.g., JComboBox(E[]) => JComboBox_JComboBox_E[] => JComboBox_JComboBox_Es
@takes(unicode)
@returns(unicode)
def sanitize_mname(mname):
  return mname.replace("[]",'s')


# convert the given method name into a new one
# considering parameterized types (e.g., collections) and inheritances
_mtds = {} # { cname_mname_... : new_mname }
@takes(unicode, unicode, list_of(unicode))
@returns(unicode)
def trans_mname(cname, mname, arg_typs=[]):
  global _mtds
  r_mtd = mname
  mid = u'_'.join([cname, mname] + arg_typs)
  # use memoized method name conversion
  if mid in _mtds:
    return _mtds[mid]
  # methods of Java collections
  elif util.is_collection(cname):
    r_mtd = u'_'.join([mname, trans_ty(cname)])
  else:
    if is_replaced(cname):
      tr_name = trans_ty(cname)
      cls = class_lookup(tr_name)
      if cls and cls.is_aux: cname = tr_name
    mtd = find_mtd_by_sig(cname, mname, arg_typs)
    if mtd: r_mtd = unicode(repr(mtd))
    else: r_mtd = '_'.join([mname, util.sanitize_ty(cname)])

  r_mtd = sanitize_mname(r_mtd)
  _mtds[mid] = r_mtd
  return r_mtd


# basic Java libraries
@takes(nothing)
@returns(unicode)
def trans_lib():
  return u''


# to avoid duplicate structs for collections
_collections = set([])

# Java collections -> C-style struct (along with basic functions)
@takes(Clazz)
@returns(unicode)
def col_to_struct(cls):
  buf = cStringIO.StringIO()
  cname = cls.name
  sname = trans_ty(cname)
  global _collections
  if sname in _collections:
    logging.debug("collection: {} (duplicated)".format(cname))
    return u''
  else:
    _collections.add(sname)
    logging.debug("collection: " + cname)

  buf.write("struct ${sname} {\n  int idx;\n")

  if C.J.MAP in cname:
    _, k, v = util.of_collection(cname)
    k = trans_ty(k)
    v = trans_ty(v)

    # Map<K,V> -> struct Map_K_V { int idx; K[S] key; V[S] val; }
    buf.write("  ${k}[S] key;\n  ${v}[S] val;\n}\n")

    # Map<K,V>.containsKey -> containsKey_Map_K_V
    buf.write("""
      bit {} (${{sname}} map, ${{k}} k) {{
        int i;
        for (i = 0; map.val[i] != null && i < S; i++) {{
          if (map.key[i] == k) return 1;
        }}
        return 0;
      }}
    """.format(trans_mname(cname, u"containsKey")))

    # Map<K,V>.get -> get_Map_K_V
    buf.write("""
      ${{v}} {} (${{sname}} map, ${{k}} k) {{
        int i;
        for (i = 0; map.val[i] != null && i < S; i++) {{
          if (map.key[i] == k) return map.val[i];
        }}
        return null;
      }}
    """.format(trans_mname(cname, u"get")))

    # Map<K,V>.put -> put_Map_K_V
    buf.write("""
      void {} (${{sname}} map, ${{k}} k, ${{v}} v) {{
        map.key[map.idx] = k;
        map.val[map.idx] = v;
        map.idx = (map.idx + 1) % S;
      }}
    """.format(trans_mname(cname, u"put")))

    # Map<K,V>.clear -> clear_Map_K_V
    if util.is_class_name(k): default_k = "null"
    else: default_k = "0"
    buf.write("""
      void {} (${{sname}} map) {{
        map.idx = 0;
        for (int i = 0; i < S; i++) {{
          map.key[i] = {};
          map.val[i] = null;
        }}
      }}
    """.format(trans_mname(cname, u"clear"), default_k))

  else:
    collection, t = util.of_collection(cname)
    t = trans_ty(t)

    if C.J.QUE in collection: buf.write("  int head;\n")
    # Collection<T> -> struct Collection_T { int idx; T[S] elts; }
    buf.write("  ${t}[S] elts;\n}\n")

    if C.J.STK in collection:
      # Stack<T>.push -> push_Stack_T
      buf.write("""
        void {} (${{sname}} stk, ${{t}} elt) {{
          stk.elts[stk.idx] = elt;
          stk.idx = (stk.idx + 1) % S;
        }}
      """.format(trans_mname(cname, u"push")))

      # Stack<T>.pop -> pop_Stack_T
      buf.write("""
        ${{t}} {} (${{sname}} stk) {{
          if (stk.idx == 0) return null;
          stk.idx = stk.idx - 1;
          ${{t}} top = stk.elts[stk.idx];
          stk.elts[stk.idx] = null;
          return top;
        }}
      """.format(trans_mname(cname, u"pop")))

    elif C.J.QUE in collection:
      # Queue<T>.add -> add_Queue_T
      buf.write("""
        void {} (${{sname}} que, ${{t}} elt) {{
          que.elts[que.idx] = elt;
          que.idx = (que.idx + 1) % S;
        }}
      """.format(trans_mname(cname, u"add")))

      # Queue<T>.remove -> remove_Queue_T
      buf.write("""
        ${{t}} {} (${{sname}} que) {{
          if (que.head == que.idx) return null;
          ${{t}} top = que.elts[que.head];
          que.elts[que.head] = null;
          que.head = (que.head + 1) % S;
          return top;
        }}
      """.format(trans_mname(cname, u"remove")))

      # Queue<T>.isEmpty -> isEmpty_Queue_T
      buf.write("""
        bit {} (${{sname}} que) {{
          return que.head == que.idx;
        }}
      """.format(trans_mname(cname, u"isEmpty")))

    elif C.J.LST in collection:
      # List<T>.add -> add_List_T
      buf.write("""
        void {} (${{sname}} lst, ${{t}} elt) {{
          lst.elts[lst.idx] = elt;
          lst.idx = (lst.idx + 1) % S;
        }}
      """.format(trans_mname(cname, u"add")))

      # List<T>.remove -> remove_List_T
      buf.write("""
        void {} (${{sname}} lst, ${{t}} elt) {{
          int i;
          for (i = 0; lst.elts[i] != null && i < S; i++) {{
            if (lst.elts[i] == elt) {{
              lst.elts[i] = null;
            }}
          }}
        }}
      """.format(trans_mname(cname, u"remove")))

  return T(buf.getvalue()).safe_substitute(locals())


_flds = {} # { cname.fname : new_fname }
_s_flds = {} # { cname.fname : accessor }

# from the given base class,
# generate a virtual struct that encompasses all the class in the hierarchy
@takes(Clazz)
@returns(Clazz)
def to_v_struct(cls):
  cls_v = Clazz(name=cls.name)

  #fld_ty = Field(clazz=cls_v, typ=C.J.i, name=u"kind")
  #cls_v.flds.append(fld_ty)

  global _ty, _flds, _s_flds
  @takes(dict_of(unicode, Field), Clazz)
  @returns(nothing)
  def per_cls(sup_flds, cls):
    aux_name = None
    # if this class is suppose to be replaced (due to pattern rewriting)
    # apply that replacement first, and then replace that aux type as well
    if not cls.is_aux and cls.name in _ty:
      aux_name = _ty[cls.name]
      logging.debug("{} => {}".format(aux_name, cls_v.name))
      # check that aux type is already involved in this family
      if aux_name not in _ty: _ty[aux_name] = cls_v.name

    # keep mappings from original subclasses to the representative
    # so that subclasses can refer to the representative
    # e.g., for C < B < A, { B : A, C : A }
    cname = util.sanitize_ty(cls.name)
    if cname != cls_v.name: # exclude the root of this family
      logging.debug("{} => {}".format(cname, cls_v.name))
      _ty[cname] = cls_v.name
      if cls.is_inner: # to handle inner class w/ outer class name
        logging.debug("{} => {}".format(repr(cls), cls_v.name))
        _ty[unicode(repr(cls))] = cls_v.name

    # if this class implements an interface which has constants,
    # then copy those constants
    for itf in cls.itfs:
      cls_i = class_lookup(itf)
      if not cls_i or not cls_i.flds: continue
      for fld in cls_i.flds:
        sup_flds[fld.name] = fld

    # also, keep mappings from original member fields to newer ones
    # so that usage of old fields can be replaced accordingly
    # e.g., for A.f1 and B.f2, { A.f1 : f1_A, B.f1 : f1_A, B.f2 : f2_B }
    for sup_fld in sup_flds.keys():
      fld = sup_flds[sup_fld]
      fname = unicode(repr(fld))
      fid = '.'.join([cname, sup_fld])
      logging.debug("{} => {}".format(fid, fname))
      if fld.is_static: _s_flds[fid] = fname
      else: _flds[fid] = fname # { ..., B.f1 : f1_A }

    cur_flds = cp.deepcopy(sup_flds) # { f1 : f1_A }
    @takes(Field)
    @returns(nothing)
    def cp_fld(fld):
      cur_flds[fld.name] = fld # { ..., f2 : f2_B }

      fname = unicode(repr(fld))
      fld_v = cp.deepcopy(fld)
      fld_v.clazz = cls_v
      fld_v.name = fname
      cls_v.flds.append(fld_v)

      def upd_flds(cname):
        fid = '.'.join([cname, fld.name])
        # if A.f1 exists and B redefines f1, then B.f1 : f1_A
        # except for enum, which can (re)define its own fields
        # e.g., SwingConstands.LEADING vs. GroupLayout.Alignment.LEADING
        if not cls.is_enum and (fid in _s_flds or fid in _flds): return
        logging.debug("{} => {}".format(fid, fname))
        if fld.is_static: _s_flds[fid] = fname
        else: _flds[fid] = fname # { ..., B.f2 : f2_B }

      upd_flds(cname)
      if aux_name: upd_flds(aux_name)

    map(cp_fld, cls.flds)

    # subclass relations of aux types are virtual, so do not visit further
    if not cls.is_aux:
      map(partial(per_cls, cur_flds), cls.subs)

  per_cls({}, cls)

  return cls_v


@takes(Field)
@returns(str)
def trans_fld(fld):
  buf = cStringIO.StringIO()
  buf.write(' '.join([trans_ty(fld.typ), fld.name]))
  if fld.is_static and fld.init and \
      not fld.init.has_call and not fld.init.has_str and not fld.is_aliasing:
    buf.write(" = " + trans_e(None, fld.init))
  buf.write(';')
  return buf.getvalue()


# Java class (along with subclasses) -> C-style struct
@takes(Clazz)
@returns(str)
def to_struct(cls):

  # make mappings from static fields to corresponding accessors
  def gen_s_flds_accessors(cls):
    s_flds = filter(op.attrgetter("is_static"), cls.flds)
    global _s_flds
    for fld in ifilterfalse(op.attrgetter("is_private"), s_flds):
      cname = fld.clazz.name
      fid = '.'.join([cname, fld.name])
      fname = unicode(repr(fld))
      logging.debug("{} => {}".format(fid, fname))
      _s_flds[fid] = fname

  cname = util.sanitize_ty(cls.name)
  global _ty
  # if this is an interface, merge this into another family of classes
  # as long as classes that implement this interface are in the same family
  if cls.is_itf:
    # interface may have static constants
    gen_s_flds_accessors(cls)
    subss = util.flatten_classes(cls.subs, "subs")
    bases = util.rm_dup(map(lambda sub: find_base(sub), subss))
    # filter out interfaces that extend other interfaces, e.g., Action
    base_clss, _ = util.partition(op.attrgetter("is_class"), bases)
    if not base_clss:
      logging.debug("no implementer of {}".format(cname))
    elif len(base_clss) > 1:
      logging.debug("ambiguous inheritance of {}: {}".format(cname, base_clss))
    else: # len(base_clss) == 1
      base = base_clss[0]
      base_name = base.name
      logging.debug("{} => {}".format(cname, base_name))
      _ty[cname] = base_name
      if cls.is_inner: # to handle inner interface w/ outer class name
        logging.debug("{} => {}".format(repr(cls), base_name))
        _ty[unicode(repr(cls))] = base_name

    return ''

  # if this is the base class having subclasses,
  # make a virtual struct first
  if cls.subs and not cls.is_aux:
    cls = to_v_struct(cls)
    cname = cls.name

  # cls can be modified above, thus generate static fields accessors here
  gen_s_flds_accessors(cls)

  # for unique class numbering, add an identity mapping
  if cname not in _ty: _ty[cname] = cname

  buf = cStringIO.StringIO()
  buf.write("struct " + cname + " {\n  int hash;\n")

  # to avoid static fields, which will be bound to a class-representing package
  _, i_flds = util.partition(op.attrgetter("is_static"), cls.flds)
  buf.write('\n'.join(map(trans_fld, i_flds)))
  if len(i_flds) > 0: buf.write('\n')
  buf.write("}\n")

  return buf.getvalue()


# convert the given field name into a newer one
# only if the field belongs to a virtual representative struct
@takes(unicode, unicode, optional(bool))
@returns(unicode)
def trans_fname(cname, fname, is_static=False):
  global _flds, _s_flds
  r_fld = fname
  fid = '.'.join([cname, fname])
  if is_static:
    if fid in _s_flds: r_fld = _s_flds[fid]
  else:
    if fid in _flds: r_fld = _flds[fid]

  return r_fld


# collect method/field declarations in the given class and its inner classes
@takes(Clazz)
@returns(list_of((Method, Field)))
def collect_decls(cls, attr):
  clss = util.flatten_classes([cls], "inners")
  declss = map(op.attrgetter(attr), clss)
  return util.flatten(declss)


# TODO: no longer used?
# translate class <init> into sketch's initializer with named parameters
@takes(unicode, list_of(unicode), list_of(unicode))
@returns(str)
def trans_init(cls_name, arg_typs, args):
  buf = cStringIO.StringIO()
  cls = class_lookup(cls_name)
  if util.is_collection(cls_name) or not cls:
    buf.write(trans_ty(cls_name) + "()")
  elif is_replaced(cls_name):
    buf.write(trans_ty(cls_name) + "(hash=nonce())")
  else:
    add_on = []
    if args:
      # NOTE: assume the order of arguments is same as that of fields
      # NOTE: for missing fields, just call default constructors
      # TODO: use template.sig_match
      kwargs = zip(cls.flds, args)
      if kwargs: assigned, _ = zip(*kwargs)
      else: assigned = []
      not_assigned = [fld for fld in cls.flds if fld not in assigned]
      if not_assigned:
        def default_init(fld):
          if util.is_class_name(fld.typ):
            return C.J.NEW + ' ' + trans_init(fld.typ, [], [])
          else: return '0'
        add_on = map(default_init, not_assigned)
    # else: # means, default constructor

    flds = ["hash"] + map(op.attrgetter("name"), cls.flds)
    vals = ["nonce()"] + args + add_on
    kwargs = map(lambda (f, v): "{}={}".format(f, v), zip(flds, vals))
    buf.write('_'.join([cls_name] + arg_typs))
    buf.write('(' + ", ".join(kwargs) + ')')

  return buf.getvalue()


# sanitize id by removing package name
# e.g., javax.swing.SwingUtilities.invokeLater -> SwingUtilities.invokeLater
@takes(unicode)
@returns(unicode)
def sanitize_id(dot_id):
  pkg, cls, mtd = util.explode_mname(dot_id)
  if cls and util.is_class_name(cls) and class_lookup(cls):
    clazz = class_lookup(cls)
    if clazz.pkg and pkg and clazz.pkg != pkg: # to avoid u'' != None
      raise Exception("wrong package", pkg, clazz.pkg)
    return '.'.join([cls, mtd])

  return dot_id


# need to check log conformity except for calls inside the platform
# i.e., client -> client, platform -> client or vice versa
@takes(Method, Method)
@returns(bool)
def check_logging(caller, callee):
  return caller.clazz.client or callee.clazz.client


@takes(optional(Method), Expression)
@returns(str)
def trans_e(mtd, e):
  curried = partial(trans_e, mtd)
  buf = cStringIO.StringIO()
  if e.kind == C.E.ANNO:
    anno = e.anno
    if anno.name == C.A.NEW: pass # TODO

    elif anno.name == C.A.OBJ:
      buf.write("retrieve_{}@log({})".format(util.sanitize_ty(anno.typ), anno.idx))

    # @Compare(exps) => {| exps[0] (< | <= | == | != | >= | >) exps[1] |}
    # @CompareString(exps) => exps[0].eqauls(exps[1])
    elif anno.name in [C.A.CMP, C.A.CMP_STR]:
      le = curried(anno.exps[0])
      re = curried(anno.exps[1])
      if anno.name == C.A.CMP:
        buf.write("{| " + le + " (< | <= | == | != | >= | >) " + re + " |}")
      else:
        buf.write("{}({},{})".format(trans_mname(C.J.STR, u"equals"), le, re))

  elif e.kind == C.E.ID:
    if hasattr(e, "ty"): buf.write(trans_ty(e.ty) + ' ')
    fld = None
    if mtd: fld = find_fld(mtd.clazz.name, e.id)
    if fld: # fname -> self.new_fname (unless the field is static)
      new_fname = trans_fname(fld.clazz.name, e.id, fld.is_static)
      if fld.is_static:
        # access to the static field inside the same class
        if fld.clazz.name == mtd.clazz.name: buf.write(e.id)
        # o.w., e.g., static constant in an interface, call the accessor
        else: buf.write(new_fname + "()")
      else: buf.write('.'.join([C.SK.self, new_fname]))
    elif e.id == C.J.THIS: buf.write(C.SK.self)
    elif util.is_str(e.id): # constant string, such as "Hello, World"
      str_init = trans_mname(C.J.STR, C.J.STR, [u"char[]", C.J.i, C.J.i])
      buf.write("{}(new Object(hash=nonce()), {}, 0, {})".format(str_init, e.id, len(e.id)))
    else: buf.write(e.id)

  elif e.kind == C.E.UOP:
    buf.write(' '.join([e.op, curried(e.e)]))

  elif e.kind == C.E.BOP:
    buf.write(' '.join([curried(e.le), e.op, curried(e.re)]))

  elif e.kind == C.E.DOT:
    # with package names, e.g., javax.swing.SwingUtilities
    if util.is_class_name(e.re.id) and class_lookup(e.re.id):
      buf.write(curried(e.re))
    elif e.re.id == C.J.THIS: # ClassName.this
      buf.write(C.SK.self)
    else:
      rcv_ty = typ_of_e(mtd, e.le)
      fld = find_fld(rcv_ty, e.re.id)
      new_fname = trans_fname(rcv_ty, e.re.id, fld.is_static)
      if fld.is_static:
        # access to the static field inside the same class
        if mtd and rcv_ty == mtd.clazz.name: buf.write(e.id)
        # o.w., e.g., static constant in an interface, call the accessor
        else: buf.write(new_fname + "()")
      else: buf.write('.'.join([curried(e.le), new_fname]))

  elif e.kind == C.E.IDX:
    buf.write(curried(e.e) + '[' + curried(e.idx) + ']')

  elif e.kind == C.E.NEW:
    if e.e.kind == C.E.CALL:
      ty = typ_of_e(mtd, e.e.f)
      cls = class_lookup(ty)
      if cls and cls.has_init:
        arg_typs = map(partial(typ_of_e, mtd), e.e.a)
        mname = trans_mname(cls.name, cls.name, arg_typs)
        obj = "alloc@log({})".format(cls.id)
        args = [obj] + map(unicode, map(curried, e.e.a))
        buf.write("{}({})".format(mname, ", ".join(args)))
      else: # collection or Object
        buf.write(C.J.NEW + ' ' + trans_ty(ty) + "()")
    else: # o.w., array initialization, e.g., new int[] { ... }
      buf.write(str(e.init))

  elif e.kind == C.E.CALL:
    arg_typs = map(partial(typ_of_e, mtd), e.a)
    logging = None
    if e.f.kind == C.E.DOT: # rcv.mid
      rcv_ty = typ_of_e(mtd, e.f.le)
      mname = e.f.re.id
      mtd_callee = find_mtd_by_sig(rcv_ty, mname, arg_typs)
      if mtd_callee and mtd_callee.is_static: rcv = None
      else: rcv = curried(e.f.le)
      mid = trans_mname(rcv_ty, mname, arg_typs)
      if mtd_callee and not util.is_collection(mtd_callee.clazz.name):
        logging = str(check_logging(mtd, mtd_callee)).lower()
    else: # mid
      mname = e.f.id
      # pre-defined meta information
      if mname in C.typ_arrays:
        mid = mname
        rcv = None
      elif mname == C.J.SUP and mtd.is_init: # super(...) inside <init>
        sup = class_lookup(class_lookup(mtd.name).sup)
        mid = trans_mname(sup.name, sup.name, arg_typs)
        rcv = C.SK.self
      else: # member methods
        mtd_callee = find_mtd_by_sig(mtd.clazz.name, mname, arg_typs)
        if mtd_callee and mtd_callee.is_static: rcv = None
        else: rcv = C.SK.self
        mid = trans_mname(mtd.clazz.name, mname, arg_typs)
        if mtd_callee and not util.is_collection(mtd_callee.clazz.name):
          logging = str(check_logging(mtd, mtd_callee)).lower()

    args = util.rm_none([rcv] + map(curried, e.a) + [logging])
    buf.write(mid + '(' + ", ".join(args) + ')')

  elif e.kind == C.E.CAST:
    # since a family of classes is merged, simply ignore the casting
    buf.write(curried(e.e))

  else: buf.write(str(e))
  return buf.getvalue()


@takes(Method, Statement)
@returns(str)
def trans_s(mtd, s):
  curried_e = partial(trans_e, mtd)
  curried_s = partial(trans_s, mtd)
  buf = cStringIO.StringIO()

  if s.kind == C.S.IF:
    e = curried_e(s.e)
    t = '\n'.join(map(curried_s, s.t))
    f = '\n'.join(map(curried_s, s.f))
    buf.write("if (" + e + ") {\n" + t + "\n}")
    if f: buf.write("\nelse {\n" + f + "\n}")

  elif s.kind == C.S.WHILE:
    e = curried_e(s.e)
    b = '\n'.join(map(curried_s, s.b))
    buf.write("while (" + e + ") {\n" + b + "\n}")

  elif s.kind == C.S.REPEAT:
    e = curried_e(s.e)
    b = '\n'.join(map(curried_s, s.b))
    if e == "??": buf.write("minrepeat {\n" + b + "\n}")
    else: buf.write("repeat (" + e + ") {\n" + b + "\n}")

  elif s.kind == C.S.FOR:
    # assume "for" is used for List<T> and LinkedList<T> only
    col = mtd.vars[s.init.id]
    if not util.is_collection(col) or \
        util.of_collection(col)[0] not in [C.J.LST, C.J.LNK]:
      raise Exception("not iterable type", col)

    # if this is about observers, let sketch choose iteration direction
    is_obs = hasattr(class_lookup(util.of_collection(col)[1]), "obs")
    s_init = curried_e(s.init)

    if is_obs: init = "{{| 0 | {}.idx - 1 |}}".format(s_init)
    else: init = '0'
    buf.write("  int idx = {};".format(init))

    s_i_typ = trans_ty(s.i.ty)
    buf.write("""
      while (0 <= idx && idx < S && {s_init}.elts[idx] != null) {{
        {s_i_typ} {s.i.id} = {s_init}.elts[idx];
    """.format(**locals()))

    buf.write('\n'.join(map(curried_s, s.b)))

    if is_obs: upd = "{| idx (+ | -) 1 |}"
    else: upd = "idx + 1"
    buf.write("""
        idx = {};
      }}
    """.format(upd))

  elif s.kind == C.S.TRY:
    # NOTE: no idea how to handle catch blocks
    # at this point, just walk through try/finally blocks
    buf.write('\n'.join(map(curried_s, s.b + s.fs)))

  else: buf.write(s.__str__(curried_e))
  return buf.getvalue()


@takes(tuple_of(unicode))
@returns(unicode)
def log_param( (ty, nm) ):
  ty = trans_ty(ty)
  if util.is_class_name(ty):
    if nm == C.J.N: return u''
    else: return nm + ".hash"
  elif ty in [C.SK.z] + C.primitives: return nm
  else: return u''


# Java member method -> C-style function
_mids = set([])  # to maintain which methods are logged
_inits = set([]) # to maintain which <init> are translated
@takes(list_of(sample.Sample), Method)
@returns(str)
def to_func(smpls, mtd):
  buf = cStringIO.StringIO()
  if C.mod.GN in mtd.mods: buf.write(C.mod.GN + ' ')
  elif C.mod.HN in mtd.mods: buf.write(C.mod.HN + ' ')
  cname = mtd.clazz.name
  mname = mtd.name
  arg_typs = mtd.param_typs
  buf.write(trans_ty(mtd.typ) + ' ' + trans_mname(cname, mname, arg_typs) + '(')

  @takes(tuple_of(unicode))
  @returns(unicode)
  def trans_param( (ty, nm) ):
    return ' '.join([trans_ty(ty), nm])

  # for instance methods, add "this" pointer into parameters
  if mtd.is_static:
    params = mtd.params[:]
  else:
    self_ty = trans_ty(mtd.clazz.name)
    params = [ (self_ty, C.SK.self) ] + mtd.params[:]

  # add "logging" flag into parameters
  # to check log conformity only if invocations cross the boundary
  if not mtd.is_init and not mtd.is_clinit:
    params.append( (C.SK.z, u"logging") )

  if len(params) > 0:
    buf.write(", ".join(map(trans_param, params)))
  buf.write(") {\n")

  # once function signature is dumped out, remove "logging" flag
  if not mtd.is_init and not mtd.is_clinit:
    params.pop()

  clss = util.flatten_classes([mtd.clazz], "subs")
  logged = (not mtd.is_init) and sample.mtd_appears(smpls, clss, mtd.name)
  mid = unicode(repr(mtd))
  m_ent = mid + "_ent()"
  m_ext = mid + "_ext()"
  if logged:
    global _mids
    _mids.add(mid)

  if logged: # logging method entry (>)
    log_params = util.ffilter([m_ent] + map(log_param, params))
    buf.write("""
      int[P] params = {{ {} }};
      if (logging) check_log@log(params);
    """.format(", ".join(log_params)))

  is_void = C.J.v == mtd.typ
  if mtd.body:
    if is_void: bodies = mtd.body
    else: bodies = mtd.body[:-1] # exclude the last 'return' statement
    buf.write('\n'.join(map(partial(trans_s, mtd), bodies)))

  if logged: # logging method exit (<)
    ret = u''
    if mtd.body and not is_void:
      if mtd.is_init: ret_v = st.gen_E_id(C.SK.self)
      else: ret_v = mtd.body[-1].e
      ret_u = unicode(trans_e(mtd, ret_v))
      ret_ty = trans_ty(mtd.typ)
      ret = log_param( (ret_ty, ret_u) )
    log_params = util.ffilter([m_ext, ret])
    buf.write("""
      params = {{ {} }};
      if (logging) check_log@log(params);
    """.format(", ".join(log_params)))

  if mtd.body and not is_void:
    buf.write('\n' + trans_s(mtd, mtd.body[-1]))

  if mtd.is_init:
    evt_srcs = map(util.sanitize_ty, sample.evt_sources(smpls))
    cname = unicode(repr(mtd.clazz))
    if cname in evt_srcs:
      global _inits
      _inits.add(cname)
    buf.write("\nreturn {};".format(C.SK.self))

  buf.write("\n}\n")
  return buf.getvalue()


# generate type.sk
@takes(str, list_of(Clazz))
@returns(nothing)
def gen_type_sk(sk_dir, bases):
  buf = cStringIO.StringIO()
  buf.write("package type;\n")
  buf.write(_const)

  buf.write(trans_lib())
  buf.write('\n')

  cols, decls = util.partition(lambda c: util.is_collection(c.name), bases)
  decls = filter(lambda c: not util.is_array(c.name), decls)
  itfs, clss = util.partition(op.attrgetter("is_itf"), decls)
  logging.debug("# interface(s): {}".format(len(itfs)))
  logging.debug("# class(es): {}".format(len(clss)))
  # convert interfaces first, then usual classes
  buf.write('\n'.join(util.ffilter(map(to_struct, itfs))))
  buf.write('\n'.join(util.ffilter(map(to_struct, clss))))

  # convert collections at last
  logging.debug("# collection(s): {}".format(len(cols)))
  buf.write('\n'.join(map(col_to_struct, cols)))

  # argument number of methods
  arg_num = map(lambda mtd: len(mtd.params), methods())
  buf.write("""
    #define _{0} {{ {1} }}
    int {0}(int id) {{
      return _{0}[id];
    }}
  """.format(C.typ.argNum, ", ".join(map(str, arg_num))))

  # argument types of methods
  def get_args_typ(mtd):
    def get_arg_typ(param): return str(class_lookup(param[0]).id)
    return '{' + ", ".join(map(get_arg_typ, mtd.params)) + '}'
  args_typ = map(get_args_typ, methods())
  buf.write("""
    #define _{0} {{ {1} }}
    int {0}(int id, int idx) {{
      return _{0}[id][idx];
    }}
  """.format(C.typ.argType, ", ".join(args_typ)))

  # return type of methods
  def get_ret_typ(mtd):
    cls = class_lookup(mtd.typ)
    if cls: return cls.id
    else: return -1
  ret_typ = map(get_ret_typ, methods())
  buf.write("""
    #define _{0} {{ {1} }}
    int {0}(int id) {{
      return _{0}[id];
    }}
  """.format(C.typ.retType, ", ".join(map(str, ret_typ))))

  # belonging class of methods
  belongs = map(lambda mtd: mtd.clazz.id, methods())
  buf.write("""
    #define _{0} {{ {1} }}
    int {0}(int id) {{
      return _{0}[id];
    }}
  """.format(C.typ.belongsTo, ", ".join(map(str, belongs))))

  subcls = \
      map(lambda cls_i: '{' + ", ".join( \
          map(lambda cls_j: str(cls_i <= cls_j).lower(), classes()) \
      ) + '}', classes())
  buf.write("""
    #define _{0} {{ {1} }}
    bit {0}(int i, int j) {{
      return _{0}[i][j];
    }}
  """.format(C.typ.subcls, ", ".join(subcls)))

  ## sub type relations
  #subcls = []
  #for cls_i in classes():
  #  row = []
  #  for cls_j in classes():
  #    row.append(int(cls_i <= cls_j))
  #  subcls.append(row)

  ## sub type relations in yale format 
  #_, IA, JA = util.yale_format(subcls)
  #li, lj = len(IA), len(JA)
  #si = ", ".join(map(str, IA))
  #sj = ", ".join(map(str, JA))
  #buf.write("""
  #  #define _iA {{ {si} }}
  #  #define _jA {{ {sj} }}
  #  int iA(int i) {{
  #    return _iA[i];
  #  }}
  #  int jA(int j) {{
  #    return _jA[j];
  #  }}
  #  bit subcls(int i, int j) {{
  #    int col_i = iA(i);
  #    int col_j = iA(i+1);
  #    for (int col = col_i; col < col_j; col++) {{
  #      if (j == jA(col)) return true;
  #    }}
  #    return false;
  #  }}
  #""".format(**locals()))

  with open(os.path.join(sk_dir, "type.sk"), 'w') as f:
    f.write(buf.getvalue())
    logging.info("encoding " + f.name)
  buf.close()


# generate cls.sk
@takes(str, list_of(sample.Sample), Clazz)
@returns(optional(unicode))
def gen_cls_sk(sk_dir, smpls, cls):
  mtds = collect_decls(cls, "mtds")
  flds = collect_decls(cls, "flds")
  s_flds = filter(op.attrgetter("is_static"), flds)
  if cls.is_class:
    if not mtds and not s_flds: return None
  else: # cls.is_itf or cls.is_enum
    if not s_flds: return None

  cname = util.sanitize_ty(cls.name)

  buf = cStringIO.StringIO()
  buf.write("package {};\n".format(cname))
  buf.write(_const)

  # static fields
  buf.write('\n'.join(map(trans_fld, s_flds)))
  if len(s_flds) > 0: buf.write('\n')

  # migrating static fields' initialization to <clinit>
  for fld in ifilter(op.attrgetter("init"), s_flds):
    if not fld.init.has_call and not fld.init.has_str and not fld.is_aliasing: continue
    # retrieve (or declare) <clinit>
    clinit = fld.clazz.get_or_declare_clinit()
    if clinit not in mtds: mtds.append(clinit)
    # add assignment
    assign = st.gen_S_assign(exp.gen_E_id(fld.name), fld.init)
    clinit.body.append(assign)

  # accessors for static fields
  for fld in ifilterfalse(op.attrgetter("is_private"), s_flds):
    fname = fld.name
    accessor = trans_fname(fld.clazz.name, fname, True)
    buf.write("""
      {0} {1}() {{ return {2}; }}
    """.format(trans_ty(fld.typ), accessor, fname))

  # methods
  if not cls.is_itf: # interface won't have method bodies
    buf.write('\n'.join(map(partial(to_func, smpls), mtds)))

  cls_sk = cname + ".sk"
  with open(os.path.join(sk_dir, cls_sk), 'w') as f:
    f.write(buf.getvalue())
    logging.info("encoding " + f.name)
    return cls_sk


# max # of objects in samples
max_objs = 0

# generate sample_x.sk
@takes(str, sample.Sample, Template, Method)
@returns(nothing)
def gen_smpl_sk(sk_path, smpl, tmpl, main):
  buf = cStringIO.StringIO()
  buf.write("harness void {} () {{\n".format(smpl.name))

  # insert call-return sequences
  buf.write("""
    clear_log@log();
    int[P] log = { 0 };
  """)
  global _mids
  objs = {} # { @Obj...aaa : 1, @Obj...bbb : 2, ... }
  obj_cnt = 0
  for io in smpl.IOs:
    # ignore <init>
    if io.is_init: continue
    try: # ignore methods that are not declared in the template
      mtd = find_mtd_by_name(io.cls, io.mtd)
      mid = repr(mtd)
      if mid not in _mids: continue
    except AttributeError: continue

    if isinstance(io, sample.CallEnt):
      mid = mid + "_ent()"
    else: # sample.CallExt
      mid = mid + "_ext()"

    vals = []
    for val in io.vals:
      kind = sample.kind(val)
      if kind is [str, unicode]: pass # ignore strings in the samples

      if type(kind) is type: val = str(val)
      if val not in objs: # this object (or primitive value) never occurs
        obj_cnt = obj_cnt + 1
        objs[val] = obj_cnt
      vals.append(str(objs[val]))

    buf.write("""
      log = (int[P]){{ {} }};
      write_log@log(log);
    """.format(", ".join([mid] + vals)))

  buf.write("""
    int len_log = get_log_cnt@log();
    reset_log_cnt@log();
  """)
  global max_objs
  max_objs = max(max_objs, obj_cnt)

  # invoke class initializers
  for cls in util.flatten_classes(tmpl.classes, "inners"):
    clinit = cls.mtd_by_sig(C.J.CLINIT)
    if not clinit: continue
    buf.write("  {}();\n".format(trans_mname(cls.name, clinit.name)))

  # execute template's *main*
  cname = main.clazz.name
  mname = main.name
  arg_typs = main.param_typs
  params = main.params + [ (C.J.z, u"logging") ]
  args = ", ".join(sig_match(params, []))
  buf.write("\n  {}({});\n".format(trans_mname(cname, mname, arg_typs), args))

  buf.write("assert len_log == get_log_cnt@log();")
  buf.write("\n}\n")
  with open(sk_path, 'w') as f:
    f.write(buf.getvalue())
    logging.info("encoding " + f.name)
  buf.close()


# generate log.sk
@takes(str, Template)
@returns(nothing)
def gen_log_sk(sk_dir, tmpl):
  buf = cStringIO.StringIO()
  buf.write("package log;\n")
  buf.write(_const)
  global max_objs
  buf.write("int O = {}; // # of objects\n".format(max_objs + 1))

  buf.write("""
    int log_cnt = 0;
    int[P][N] ev;
    int[O] obj;

    // to enforce the length of logs
    int get_log_cnt() {
      return log_cnt;
    }

    // after writing logs, reset the cursor in order to check logs in order
    void reset_log_cnt() {
      log_cnt = 0;
    }

    // to clean up the logs totally
    void clear_log() {
      reset_log_cnt();
      ev = {};
      obj = {};
    }

    // to write the log from samples
    void write_log (int[P] params) {
      ev[log_cnt++] = params;
    }

    // to check whether control-flow conforms to the samples
    @Native("{ std::cout << \\\"log::check_log::\\\" << params[0] << std::endl; }")
    void check_log (int[P] params) {
      assert params[0] == ev[log_cnt][0]; // check mid
      for (int i = 1; i < P; i++) {
        if (ev[log_cnt][i] != 0) {
          if (obj[ev[log_cnt][i]] == 0) { // not set yet
            obj[ev[log_cnt][i]] = params[i];
          }
          else { // o.w. check obj eq.
            assert obj[ev[log_cnt][i]] == params[i];
          }
        }
      }
      log_cnt++; // advance
    }

    // distinct hash values for runtime objects
    int obj_cnt = 0;
    int nonce () {
      return obj_cnt++;
    }
  """)

  global _inits
  reg_codes = []
  for ty in _inits:
    cls = class_lookup(ty)
    if not cls: continue

    buf.write("""
      int obj_{0}_cnt = 0;
      {1}[O] obj_{0};

      // to register runtime instances of {0}
      void register_{0} ({1} {2}) {{
        if (obj_{0}_cnt < O) {{
          obj_{0}[obj_{0}_cnt++] = {2};
        }}
      }}

      // to access to a certain instance of {0}
      {1} retrieve_{0} (int idx) {{
        if (0 <= idx && idx < obj_{0}_cnt) {{
          return obj_{0}[idx];
        }}
        else {{
          return null;
        }}
      }}
    """.format(ty, trans_ty(ty), ty.lower()))

    reg_code = "if (ty == {0}) register_{1}@log({2});".format(cls.id, repr(cls), C.SK.self)
    reg_codes.append(reg_code)

  # factory of Object
  buf.write("""
    // factory of Object
    Object alloc(int ty) {{
      Object {0} = new Object(hash=nonce());
      {1}
      return {0};
    }}
  """.format(C.SK.self, "\nelse ".join(reg_codes)))

  global _ty;
  _clss = []
  for ty in _ty.keys():
    if util.is_collection(ty): continue
    if util.is_array(ty): continue
    cls = class_lookup(ty)
    if not cls: continue # to avoid None definition
    # inner class may appear twice: w/ and w/o outer class name
    if cls not in _clss: _clss.append(cls)

  buf.write("\n// distinct class IDs\n")
  for cls in _clss:
    buf.write("int {cls!r} () {{ return {cls.id}; }}\n".format(**locals()))

  buf.write("\n// distinct method IDs\n")
  for cls in tmpl.classes:
    mtds = collect_decls(cls, "mtds")
    if not mtds: continue

    for mtd in mtds:
      mname = sanitize_mname(unicode(repr(mtd)))
      buf.write("""
        int {mname}_ent () {{ return  {mtd.id}; }}
        int {mname}_ext () {{ return -{mtd.id}; }}
      """.format(**locals()))

  with open(os.path.join(sk_dir, "log.sk"), 'w') as f:
    f.write(buf.getvalue())
    logging.info("encoding " + f.name)
  buf.close()


# reset global variables
@takes(nothing)
@returns(nothing)
def reset():
  global _ty, _mtds, _flds, _s_flds
  global _collections, _mids, _inits
  global max_objs
  _ty = {}
  _mtds = {}
  _flds = {}
  _s_flds = {}
  _collections = set([])
  _mids = set([])
  _inits = set([])
  max_objs = 0


# translate the high-level templates into low-level sketches
# using information at the samples
@takes(list_of(sample.Sample), Template, str)
@returns(nothing)
def to_sk(smpls, tmpl, sk_dir):
  # clean up result directory
  if os.path.isdir(sk_dir): util.clean_dir(sk_dir)
  else: os.makedirs(sk_dir)

  # reset global variables so that we can run this encoding phase per demo
  reset()

  # update global constants
  def logged(mtd):
    if mtd.is_init: return False
    clss = util.flatten_classes([mtd.clazz], "subs")
    return sample.mtd_appears(smpls, clss, mtd.name)
  mtds = filter(logged, methods())
  if mtds:
    n_params = 2 + max(map(len, map(op.attrgetter("params"), mtds)))
  else: # no meaningful logs in the sample?
    n_params = 2
  n_evts = sample.max_evts(smpls)
  n_ios = sample.max_IOs(smpls)

  global _const
  _const = u"""
    int P = {}; // length of parameters (0: (>|<)mid, 1: receiver, 2...)
    int S = {}; // length of arrays for Java collections
    int N = {}; // length of logs
  """.format(n_params, max(5, n_evts + 1), n_ios)

  # type.sk
  tmpl.consist()
  # merge all classes and interfaces, except for primitive types
  clss, _ = util.partition(lambda c: util.is_class_name(c.name), classes())
  bases = rm_subs(clss)
  gen_type_sk(sk_dir, bases)

  # cls.sk
  cls_sks = []
  for cls in tmpl.classes:
    cls_sk = gen_cls_sk(sk_dir, smpls, cls)
    if cls_sk: cls_sks.append(cls_sk)

  # sample_x.sk
  smpl_sks = []
  for smpl in smpls:
    smpl_sk = "sample_" + smpl.name + ".sk"
    smpl_sks.append(smpl_sk)
    sk_path = os.path.join(sk_dir, smpl_sk)
    gen_smpl_sk(sk_path, smpl, tmpl, tmpl.harness(smpl.name))

  # log.sk
  gen_log_sk(sk_dir, tmpl)

  # sample.sk that imports all the other sketch files
  buf = cStringIO.StringIO()
  # --bnd-cbits: the number of bits for integer holes
  bits = max(5, int(math.ceil(math.log(len(methods()), 2))))
  buf.write("pragma options \"--bnd-cbits {}\";\n".format(bits))
  # --bnd-unroll-amnt: the unroll amount for loops
  unroll_amnt = n_params
  buf.write("pragma options \"--bnd-unroll-amnt {}\";\n".format(unroll_amnt))
  # --bnd-inline-amnt: bounds inlining to n levels of recursion
  # setting it 1 means there is no recursion in tutorials
  buf.write("pragma options \"--bnd-inline-amnt 1\";\n")
  buf.write("pragma options \"--bnd-bound-mode CALLSITE\";\n")
  sks = ["log.sk", "type.sk"] + cls_sks + smpl_sks
  for sk in sks:
    buf.write("include \"{}\";\n".format(sk))
  with open(os.path.join(sk_dir, "sample.sk"), 'w') as f:
    f.write(buf.getvalue())
    logging.info("encoding " + f.name)
  buf.close()

