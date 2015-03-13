import lib.const as C

# special cases for the accessor pattern
acc_default = [
  "getHandler",
  C.ADR.ACTT, # Handler, Activity
  C.ADR.LOOP  # MessageQueue
]

# configuration for the accessor pattern
acc_conf_uni = {
  "Message": (0, 1, 1), # (get|set)Target
  "Handler": (1, 1, 0), # getLooper

  "Intent": (1, 1, 0), # getComponent
  "ComponentName": (2, 2, 0), # get(Class|Package)Name

  "InputEvent": (1, 1, 1), # (get|set)Source
  "KeyEvent": (2, 1, 0), # getKeyCode
  "MotionEvent": (2, 1, 0), # getAction(Masked)
}

# configuration for the accessor pattern (of Map<K,V> type)
acc_conf_map = {
  "Bundle": (0, 1, 1), # (get|put)*
  "Context": (0, 1, 0), # getSystemService
  # TODO: should use Window's APIs; Activity is sort of proxy
  "Activity": (0, 1, 1), # findViewById, setContentView
}

# configuration for the singleton pattern
sng_conf = [
  C.ADR.ACTT,
  C.ADR.LOOP
]
