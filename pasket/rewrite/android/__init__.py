import lib.const as C

# special cases for the accessor pattern
acc_default = [
  "getHandler",
  C.ADR.ACTT, # Handler, Activity
  C.ADR.LOOP  # MessageQueue
]

# configuration for the accessor pattern
acc_conf_uni = {
  "Message": (1, 1, 1), # (get|set)Target
  "Handler": (1, 1, 0), # getLooper

  "Intent": (1, 1, 0), # getComponent
  "ComponentName": (2, 2, 0), # get(Class|Package)Name

  "InputEvent": (1, 1, 1), # (get|set)Source
  "MotionEvent": (2, 1, 0), # getAction(Masked)
  #"KeyEvent": (2, 1, 0), # getKeyCode
}

# configuration for the accessor pattern (of Map<K,V> type)
acc_conf_map = {
  "Bundle": (0, 1, 1), # (get|put)*
  "Context": (0, 1, 0), # getSystemService
}

# configuration for the observer pattern
obs_conf = {
  "MotionEvent": (1, 1, 0), # no $detach
}

# configuration for the singleton pattern
sng_conf = [
  C.ADR.ACTT,
  C.ADR.LOOP
]
