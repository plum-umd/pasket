import logging

from lib.typecheck import *
import lib.const as C

from .. import util

from accessor import Accessor
from new_accessor import NewAccessor
from builder import Builder
from factory import Factory
from proxy import Proxy
from singleton import Singleton
from state import State

# configuration for the accessor pattern
C.acc_conf = { \
  "EventObject": (1, 1, 0), # getSource
  "InvocationEvent": (2, 0, 0), # to set Runnable

  "ActionEvent": (3, 1, 0), # getActionCommand
  "ItemEvent": (4, 2, 0), # getItemSelectable/getStateChange

  "JButton": (2, 1, 1), # (get|set)ActionCommand
}

# special cases for the accessor pattern
C.acc_default = [ \
    C.GUI.TOOL,
    "JColorChooser", # ColorSelectionModel
    "JTextComponent", # Document
    "JMenuItem", "JMenu" # AccessibleContext
]

@takes(str, list_of("Sample"), "Template", list_of(str))
@returns(nothing)
def visit(cmd, smpls, tmpl, patterns):
  p2v = {}

  p2v[C.P.BLD] = Builder(smpls)

  p2v[C.P.FAC] = Factory(smpls)

  if cmd == "android": pass
  elif cmd == "gui":
    from gui.observer import Observer
    p2v[C.P.OBS] = Observer(smpls)
  else:
    from observer import Observer
    p2v[C.P.OBS] = Observer(smpls)

  p2v[C.P.PRX] = Proxy(smpls)

  p2v[C.P.SNG] = Singleton(smpls)

  p2v[C.P.STA] = State(smpls)

  keys = p2v.keys()
  if not patterns: # then try all the patterns
    patterns = keys

  # filter out unknown pattern names
  patterns = util.intersection(patterns, keys)
  # sort so that visitors can be visited in the order of generation
  patterns.sort()

  accessr = "accessor"
  p2v[accessr] = Accessor(smpls)
  patterns.insert(0, accessr) # run Accessor first by default

  new_accessr = "new_accessor"
  p2v[new_accessr] = NewAccessor(smpls)
  patterns.insert(1, new_accessr) # run NewAccessor first by default

  for p in patterns:
    logging.info("rewriting {} pattern".format(p))
    tmpl.accept(p2v[p])

