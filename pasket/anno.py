import cStringIO
import operator as op

from antlr3.tree import CommonTree as AST

from lib.typecheck import *
import lib.const as C

import util
# to avoid circular import (TODO: do we really need those annotations?)
#from meta.expression import parse_e

C.A = util.enum(OVERRIDE="Override", HARNESS="Harness", \
  EVENT="Event", REACT="React", OBS="ObserverPattern", \
  OBSS="Observers", ATTACH="Attach", DETACH="Detach", NOTI="Notified", \
  STATE="State", ERR="Error", UPDATE="Update", \
  SINGLE="Singleton", MULTI="Multiton", \
  PUT="Put", APPEND="Append", ASSEM="Assemble", \
  PROXY="Proxy", FACTORY="Factory", \
  GET="Get", SET="Set", HAS="Has", IS="Is", \
  NEW="New", OBJ="Object", \
  CMP="Compare", CMP_STR="CompareString", \
  TAG="Tag", ALL="All", CFG="CFG", MOCK="Mock")

class Anno(object):

  def __init__(self, **kwargs):
    for key in kwargs:
      setattr(self, key, kwargs[key])

  def __str__(self):
    buf = cStringIO.StringIO()
    buf.write('@' + self.name)

    attrs = [var for var in vars(self) if "name" not in var]
    if attrs:
      def var_to_str(var, print_var_too=True):
        s_attr = str(getattr(self, var)).replace('[','{').replace(']','}')
        if print_var_too: return var+"="+s_attr
        else: return s_attr

      buf.write('(')
      if len(attrs) == 1: buf.write(var_to_str(attrs[0], False))
      else: buf.write(", ".join(map(var_to_str, attrs)))
      buf.write(')')

    return buf.getvalue()

  def __repr__(self):
    return self.__str__()

  # find the designated annotation by attributes
  @takes("Anno", dict_of(str, str))
  @returns(bool)
  def by_attr(self, attrs):
    for k, v in attrs.iteritems():
      if not hasattr(self, k) or getattr(self, k) != v: return False
    return True

  # find the designated annotation by name
  @takes("Anno", str)
  @returns(bool)
  def by_name(self, name):
    return self.by_attr({"name": name})


# (ANNOTATION (NAME Id) (ELEMS (Val | (= Id Val)+))?)
@takes(AST)
@returns(Anno)
def parse_anno(node):
  _anno = Anno(name = node.getChild(0).getChild(0).getText())

  ##
  ## Java annotations
  ##
  if _anno.name == C.A.OVERRIDE: pass

  ##
  ## Observer
  ##
  # (A... (NAME ObserverPattern) (ELEMS "event" (, "event")*)?)
  elif _anno.name == C.A.OBS:
    events = []
    if node.getChildCount() > 1:
      events = util.implode_id(node.getChild(1)).split(',')
    setattr(_anno, "events", events)

  ## (A... (NAME Event) (ELEMS ("kind" | (= kind "kind") (= args exp*))))
  #elif _anno.name == C.A.EVENT:
  #  elems = node.getChild(1)
  #  if elems.getChildCount() == 2:
  #    what = elems.getChild(0).getChild(1).getText()
  #    _args = elems.getChild(1).getChildren()[1:] # exclude terminal "args"
  #    args = map(parse_e, util.parse_comma_elems(_args))
  #    setattr(_anno, "args", args)
  #  else: # "what"
  #    what = util.implode_id(elems)

  #  s_what = what.strip('"')
  #  setattr(_anno, "kind", s_what)

  # (A... (NAME Attach))
  elif _anno.name == C.A.ATTACH: pass

  # (A... (NAME Detach))
  elif _anno.name == C.A.DETACH: pass

  ## (A... (NAME Notified) (ELEMS exp*)?)
  #elif _anno.name == C.A.NOTI:
  #  if node.getChildCount() > 1:
  #    _args = node.getChild(1).getChildren()
  #    args = map(parse_e, util.parse_comma_elems(_args))
  #    setattr(_anno, "args", args)

  # (A... (NAME React))
  elif _anno.name == C.A.REACT: pass

  # (A... (NAME Observers))
  elif _anno.name == C.A.OBSS: pass

  ##
  ## State (machine)
  ##
  # (A... (NAME State) (ELEMS (Id | Anno))?)
  elif _anno.name == C.A.STATE:
    if node.getChildCount() > 1:
      _where = node.getChild(1).getChild(0)
      where = _where.getText()
      if where == C.T.ANNO:
        where = parse_anno(_where)
    else: # All methods in the class
      where = Anno(name=C.A.ALL)
    setattr(_anno, "accessed", where)

  # (A... (NAME Error))
  elif _anno.name == C.A.ERR: pass

  # (A... (NAME Update) (ELEMS Id))
  elif _anno.name == C.A.UPDATE:
    fid = util.implode_id(node.getChild(1))
    setattr(_anno, "fid", fid)

  ##
  ## Singleton/Multiton
  ##
  # (A... (NAME Singleton) (ELEMS Id)?)
  elif _anno.name == C.A.SINGLE:
    if node.getChildCount() > 1:
      cid = node.getChild(1).getChild(0).getText()
      setattr(_anno, "cid", cid)

  # (A... (NAME Multiton) (ELEMS Id*)?)
  elif _anno.name == C.A.MULTI:
    if node.getChildCount() > 1:
      _values = node.getChild(1).getChildren()
      values = map(util.implode_id, util.parse_comma_elems(_values))
      setattr(_anno, "values", values)

  ##
  ## Builder / Proxy / Factory
  ##
  # (A... (NAME (Put | Append | Proxy | Factory)) (ELEMS Id)?)
  elif _anno.name in [C.A.PUT, C.A.APPEND, C.A.PROXY, C.A.FACTORY]:
    if node.getChildCount() > 1:
      cid = node.getChild(1).getChild(0).getText()
      setattr(_anno, "cid", cid)

  # (A... (Name Assemble))
  elif _anno.name == C.A.ASSEM: pass

  ##
  ## Accessors
  ##
  # (A... (NAME Get) (ELEMS (id | (= field id) (= args exp*)))?)
  #elif _anno.name == C.A.GET:
  #  if node.getChildCount() > 1:
  #    elems = node.getChild(1)
  #    if elems.getChildCount() == 2:
  #      _fid = elems.getChild(0).getChildren()[1:] # exclude terminal "field"
  #      fid = util.implode_id(util.mk_v_node_w_children(_fid))
  #      _args = elems.getChild(1).getChildren()[1:] # exclude terminal "args"
  #      args = map(parse_e, util.parse_comma_elems(_args))
  #      setattr(_anno, "args", args)
  #    else: # Id
  #      fid = util.implode_id(elems)
  #    setattr(_anno, "fid", fid)

  # (A... (NAME (Set|Has|Is)) (ELEMS Id)?)
  elif _anno.name in [C.A.SET, C.A.HAS, C.A.IS]:
    if node.getChildCount() > 1:
      fid = util.implode_id(node.getChild(1))
      setattr(_anno, "fid", fid)

  ##
  ## Reflection
  ##
  ## (A... (NAME New) (ELEMS (Id | (= typ Id) (= args exp*))))
  #elif _anno.name == C.A.NEW:
  #  elems = node.getChild(1)
  #  if elems.getChildCount() == 2:
  #    _typ = elems.getChild(0).getChild(1)
  #    _args = elems.getChild(1).getChildren()[1:] # exclude terminal "args"
  #    args = map(parse_e, util.parse_comma_elems(_args))
  #    setattr(_anno, "args", args)
  #  else: # typ
  #    _typ = elems.getChild(0)

  #  if _typ.getText() == C.T.ANNO:
  #    typ = parse_anno(_typ)
  #  else: typ = _typ.getText()
  #  setattr(_anno, "typ", typ)

  # (A... (NAME Object) (ELEMS (= typ Id) (= idx i)))
  elif _anno.name == C.A.OBJ:
    elems = node.getChild(1)
    _typ = elems.getChild(0).getChildren()[1:] # exclude terminal "typ"
    typ = util.implode_id(util.mk_v_node_w_children(_typ))
    idx = elems.getChild(1).getChild(1).getText()
    setattr(_anno, "idx", int(idx))
    setattr(_anno, "typ", typ.split('.')[-1])

  ##
  ## Non-deterministic choices
  ##
  # (A... (NAME Tag) (ELEMS "what"))
  elif _anno.name == C.A.TAG:
    what = node.getChild(1).getChild(0).getText().strip('"')
    setattr(_anno, "tag", what)

  # (A... (NAME All))
  elif _anno.name == C.A.ALL: pass

  ## (A... (NAME (Compare | CompareString)) (ELEMS exp , exp))
  #elif _anno.name in [C.A.CMP, C.A.CMP_STR]:
  #  _exps = node.getChild(1).getChildren()
  #  exps = map(parse_e, util.parse_comma_elems(_exps))
  #  setattr(_anno, "exps", exps)

  ##
  ## Misc.
  ##
  # (A... (NAME Mock))
  elif _anno.name == C.A.MOCK: pass

  # (A... (NAME CFG) (ELEMS Id))
  elif _anno.name == C.A.CFG:
    mid = util.implode_id(node.getChild(1))
    setattr(_anno, "mid", mid)

  # (A... (NAME Harness) (ELEMS "what"))
  elif _anno.name == C.A.HARNESS:
    what = node.getChild(1).getChild(0).getText().strip('"')
    setattr(_anno, "f", what)

  else: raise Exception("unhandled @annotation", node.toStringTree())

  return _anno

