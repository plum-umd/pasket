import lib.const as C

# special cases for the accessor pattern
acc_default = [
  C.GUI.TOOL, # EventQueue
  "JColorChooser", # ColorSelectionModel
  "JTextComponent", # Document
  "JMenuItem", "JMenu" # AccessibleContext
]

# configuration for the accessor pattern
acc_conf_uni = {
  "EventObject": (1, 1, 0), # getSource
  "InvocationEvent": (2, 0, 0), # to set Runnable

  "ActionEvent": (3, 1, 0), # getActionCommand
  "ItemEvent": (4, 2, 0), # get(ItemSelectable|StateChange)
  "DefaultDocumentEvent": (4, 1, 0), # getType
  "ListSelectionEvent": (4, 3, 0), # get((First|Last)Index|ValueIsAdjusting)

  "JButton": (2, 1, 1), # (get|set)ActionCommand
}

# configuration for the accessor pattern (of Map<K,V> type)
acc_conf_map = {
  "JCompoment": (0, 1, 1), # (get|set)InputMap
  "ActionMap": (0, 1, 1), # get, put
}

# configuration for the observer pattern:
# number of handle/attach/detach methods
obs_conf = {
  "ActionEvent": (1, 1, 1),
  "ItemEvent": (1, 1, 1),
  "ChangeEvent": (1, 1, 1),
  "DocumentEvent": (3, 1, 1), # (change|insert|remove)
  "ListSelectionEvent": (0, 1, 1),
}

# configuration for the singleton pattern
sng_conf = [
  C.GUI.TOOL # getDefaultToolkit
]

# number of instances and number of args
adp_conf = {
  "InvocationEvent": (1, 0),
  "DefaultListModel": (3, 1)
  #"JList": (1, 1)
}
