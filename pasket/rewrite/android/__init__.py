import lib.const as C

# special cases for the accessor pattern
acc_default = [
  "getHandler",
  C.ADR.ACTT, # Handler, Activity
  C.ADR.LOOP  # MessageQueue
]

# configuration for the accessor pattern
acc_conf_uni = {
  C.ADR.MSG: (1, 1, 1), # (get|set)Target
  C.ADR.HDL: (1, 1, 0), # getLooper

  C.ADR.INTT: (1, 1, 0), # getComponent
  C.ADR.CMP: (2, 2, 0), # get(Class|Package)Name

  "InputEvent": (1, 1, 1), # (get|set)Source
  "MotionEvent": (2, 1, 0), # getAction(Masked)
  #"KeyEvent": (2, 1, 0), # getKeyCode
}

# configuration for the accessor pattern (of Map<K,V> type)
acc_conf_map = {
  #C.ADR.BDL: (0, 1, 1), # (get|put)*
  C.ADR.CTX: (0, 1, 0), # getSystemService
  C.ADR.WMG: (0, 1, 1), # addView, findViewById
}

# configuration for the observer pattern
obs_conf = {
  "MotionEvent": (1, 1, 0), # no $detach
}

# configuration for the singleton pattern
sng_conf = [
  C.ADR.ACTT,
  C.ADR.LOOP,
  C.ADR.WMG
]
