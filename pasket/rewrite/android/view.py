import logging

import lib.const as C
import lib.visit as v

from ...meta.template import Template
from ...meta.clazz import Clazz
from ...meta.method import Method
from ...meta.field import Field
from ...meta.statement import Statement, to_statements
from ...meta.expression import Expression, to_expression

class View(object):

  def __init__(self): pass

  @v.on("node")
  def visit(self, node):
    """
    This is the generic method to initialize the dynamic dispatcher
    """

  @v.when(Template)
  def visit(self, node): pass

  @staticmethod
  def add_fld(cls, ty, nm, init=None):
    logging.debug("adding field {}.{} of type {}".format(cls.name, nm, ty))
    fld = Field(clazz=cls, typ=ty, name=nm, init=init)
    cls.add_flds([fld])
    cls.init_fld(fld)
    return fld

  @v.when(Clazz)
  def visit(self, node):
    cname = node.name
    # a field for View id
    if cname == C.ADR.VIEW:
      no_id = to_expression(u"View.NO_ID")
      fld = View.add_fld(node, C.J.i, u"_vid", no_id)
      setattr(node, "vid", fld)

    # (for recursive hierarchy buildup)
    ## a field of List type to hold children View's
    #elif cname in [C.ADR.VG, C.ADR.WIN]:
    #  fld = View.add_fld(node, u"List<{}>".format(C.ADR.VIEW), u"mChildren")
    #  setattr(node, "children", fld)

  @v.when(Field)
  def visit(self, node): pass

  @v.when(Method)
  def visit(self, node):
    cname = node.clazz.name
    mname = node.name

    ##
    ## speicial initialization for classes in the View hierarchy
    ##
    if node.is_init:
      if cname == C.ADR.VIEW:
        body = u"""
          setEnabled(true);
        """
        node.body = to_statements(node, body)

      elif cname == "CompoundButton":
        body = u"""
          setChecked(true);
        """
        node.body = to_statements(node, body)

    ##
    ## View id setup
    ##
    if cname == C.ADR.VIEW:
      if mname in ["setId", "getId"]:
        fld = getattr(node.clazz, "vid")
        fname = fld.name
        if mname.startswith("set"):
          _, v = node.params[0]
          body = u"this.{fname} = {v};".format(**locals())
        else: # get
          body = u"return this.{fname};".format(**locals())
        node.body = to_statements(node, body)

    #self._recursive_hierarchy(node)
    self._flat_views(node)


  def _flat_views(self, node):
    cname = node.clazz.name
    mname = node.name

    ##
    ## View registerations
    ##
    if cname in [C.ADR.VG, C.ADR.WIN]:
      # ViewGroup.addView or (set|add)ContentView
      if mname == "addView" or mname.endswith("ContentView"):
        ty, _ = node.params[0]
        args = [ nm for (_, nm) in node.params ]
        if ty == C.ADR.VIEW:
          body = u"""
            {0} wm = {0}.getInstance();
            wm.addView({1});
          """.format(C.ADR.WMG, ", ".join(args))
          node.body = to_statements(node, body)

    elif cname == C.ADR.WMG and mname == "addView":
      ty, v = node.params[0]
      if ty == C.ADR.VIEW:
        body = u"addView({v}.getId(), {v});".format(**locals())
        node.body = to_statements(node, body)

    ##
    ## View lookup
    ##
    if mname.startswith("find"+C.ADR.VIEW) and cname != C.ADR.WMG:
      _, _id = node.params[0]
      body = u"""
        {0} wm = {0}.getInstance();
        return wm.findViewById({1});
      """.format(C.ADR.WMG, _id)
      node.body = to_statements(node, body)


  def _recursive_hierarchy(self, node):
    cname = node.clazz.name
    mname = node.name

    ##
    ## View hierarchy buildup
    ##

    if cname in [C.ADR.VG, C.ADR.WIN]:
      fld = getattr(node.clazz, "children")
      fname = fld.name
      # ViewGroup.addView or (set|add)ContentView
      if mname == "addView" or mname.endswith("ContentView"):
        ty, v = node.params[0]
        if ty == C.ADR.VIEW:
          body = u"{fname}.add({v});".format(**locals())
          node.body = to_statements(node, body)

    ##
    ## View lookup
    ##

    if mname.startswith("find"+C.ADR.VIEW):
      _, _id = node.params[0]

      if cname == C.ADR.VIEW:
        ##
        ## public *final* View View.findViewById(int id)
        ##
        if mname.endswith("ById"):
          body = u"""
            if ({_id} < 0) return null;
            return this.findViewTraversal({_id});
          """.format(**locals())
          node.body = to_statements(node, body)

        ##
        ## *protected* View View.findViewTraversal(int id)
        ##
        else: # overridable traversal
          body = u"""
            int me = this.getId();
            if ({_id} == me) return this;
            else return null;
          """.format(**locals())
          node.body = to_statements(node, body)

      elif cname in [C.ADR.VG, C.ADR.WIN]:
        ##
        ## protected View ViewGroup.findViewTraversal(int id)
        ## public View Window.findViewById(int id)
        ##
        fld = getattr(node.clazz, "children")
        fname = fld.name
        traversal = u"""
          // if this is a leaf, no more children are there
          if ({fname} == null) return null;
          if ({fname}.isEmpty()) return null;

          for (View v : {fname}) {{
            View vv;
            try {{
              vv = ((ViewGroup)v).findViewTraversal({_id});
            }} catch (ClassCastException e) {{
              View vv = v.findViewById({_id});
            }}
            if (vv != null) return vv;
          }}
          return null;
        """.format(**locals())

        if cname == C.ADR.VG:
          check_myself = u"""
            int me = this.getId();
            if ({_id} == me) return this;
          """.format(**locals())
          traversal = check_myself + traversal

        node.body = to_statements(node, traversal)


  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node
 
