import lib.const as C

# special cases for the accessor pattern
acc_default = [
  C.GUI.TOOL, # EventQueue
  "JMenuItem", "JMenu" # AccessibleContext
]

# configuration for the accessor pattern
acc_conf_uni = {
  "EventObject": (1, 1, 0, False), # getSource
  "InvocationEvent": (2, 0, 0, False), # to set Runnable

  "ActionEvent": (3, 1, 0, False), # getActionCommand
  "ItemEvent": (4, 2, 0, False), # get(ItemSelectable|StateChange)
  "DefaultDocumentEvent": (4, 1, 0, False), # getType
  "ListSelectionEvent": (4, 3, 0, False), # get((First|Last)Index|ValueIsAdjusting)

  "JButton": (1, 1, 1, False), # (get|set)ActionCommand

  #"JTextComponent": (4, 4, 4, True), # (get|set)(Document|Editable|CaretPosition)
  "JTextComponent": (1, 1, 0, True), # getDocument
  "JColorChooser": (1, 1, 0, True), # getSelectionModel
  #"Document": (-1, 1, 0), # getLength
}

# configuration for the accessor pattern (of Map<K,V> type)
acc_conf_map = {
  "JCompoment": (-1, 1, 1), # (get|set)InputMap
  "ActionMap": (-1, 1, 1), # get, put
}

# configuration for the observer pattern
obs_conf = {
  "ActionEvent": (1, 1, 1),
  "ItemEvent": (1, 1, 1),
  "ChangeEvent": (1, 1, 1),
  "DocumentEvent": (3, 1, 1), # (change|insert|remove)
  "ListSelectionEvent": (1, 1, 1),
}

# configuration for the singleton pattern
sng_conf = [
  C.GUI.TOOL # getDefaultToolkit
]
