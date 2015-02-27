Using Swing Components
======================

http://docs.oracle.com/javase/tutorial/uiswing/examples/components/index.html


format:

    * DemoName
    * very brief explanation (or similarity)
    * candidacy
    * current status using pasket
        - if not ready, explain reasons and solutions (if any)


BorderDemo
----------

not using any event-relevant interfaces


ButtonDemo
----------

new JButton -> JButton.addActionListener(ButtonDemo d)
(button click) -> ActionEvent e -> ButtonDemo.actionPerformed(e)

@ObsPtn(ActionEvent) class AbstractButton
@ObsPtn(ActionEvent) interface ActionListener

working


ButtonHtmlDemo
--------------

same as ButtonDemo.

working


CheckBoxDemo
------------

new JCheckBox -> JCheckBox.addItemListener(CheckBoxDemo cbd)
(box check/uncheck) -> ItemEvent e -> CheckBoxDemo.itemStateChanged(e)

@ObsPtn(ItemEvent) interface ItemSelectable
@ObsPtn(ItemEvent) interface ItemListener

working


ColorChooserDemo
----------------

new JColorChooser -> JColorChooser.getSelectionModel().addChangeListener(ColorChooserDemo ccd)
(color changed) -> ChangeEvent e -> ColorChooserDemo.stateChanged(e)

@ObsPtn(ChangeEvent) interface ColorSelectionModel
@ObsPtn(ChangeEvent) interface ChangeListener

working


ColorChooserDemo2
-----------------

new JButton and new JColorChooser -> JButton.addActionListener(JButton jb) ->  JColorChooser.getSelectionModel().addChangeListener(ColorChooserDemo ccd) ->
JButton for JColorChooser created -> JButton.addActionListener(JColorChooser cc)

(crayon click) -> ActioinEvent e -> CrayonPanel.actionPerformed() -> (dispatch a ChangeEvent e) -> ColorChooserDemo.stateChanged(e)

(button click) -> new JPanel including new JColorChooser and new JButton -> JColorChooser.getSelectionModel().addChangeListerner(JPanel) -> JButton.addActionListener(JPanel) (color changed) -> JPanel.stateChanged() -> (button click) -> JPanel.actionPerformed() -> (dispatch a ChangeEvent e) -> ColorChooserDemo.stateChanged(e)

Note: very complex example, two design patterns are involved. The update methods do important things that cannot be omitted: create new observer/observable, create and dispatch events...

@ObsPtn(ChangeEvent) class ColorSelectionModel
@ObsPtn(ChangeEvent) class ChangeListener
@ObsPtn(ActionEvent) class AbstractButton
@ObsPtn(ActionEvent) class ActionListener



ComboBoxDemo
------------

new JComboBox -> JComboBox.addActionListener(ComboBoxDemo cbd)
(item selected) -> ActionEvent e -> ComboBoxDemo.actionPerformed(e)

@ObsPtn(ActionEvent) class JComboBox
@ObsPtn(ActionEvent) interface ActionListener



ComboBoxDemo2
-------------

same as ComboBoxDemo

new JComboBox -> JComboBox.addActionListener(ComboBoxDemo2 cbd)
(item selected) -> ActionEvent e -> ComboBoxDemo.actionPerformed(e)

@ObsPtn(ActionEvent) class JComboBox
@ObsPtn(ActionEvent) interface ActionListener



Converter
---------

ConverterRangeModel

The conversion panel listens to three components: the JFormattedTextField (PropertyChangeEvent), the slider's ConverterRangeModel (ChangeEvent), the ComboBox (ActionEvent).

@ObsPtn(ChangeEvent) class BoundedRangeModel
@ObsPtn(ChangeEvent) class ChangeListener
@ObsPtn(ActionEvent) class AbstractButton
@ObsPtn(ActionEvent) class ActionListener
@ObsPtn(PropertyChangeEvent) class JFormattedTextField (Container?)
@ObsPtn(PropertyChangeEvent) class PropertyChangeListener

The FollowerRangeModel plays two roles: the observer and the observable. It listens to the original ConverterRangeModel, and fire state changed events to its registers. So again, the behavior of the update method matters.



CustomComboBoxDemo
------------------

The JComboBox is supposed to be the observable, but there's no observer registered.

@ObsPtn class JComboBox ?



CustomIconDemo
--------------

same as ButtonDemo.

working


DialogDemo
----------

(button click) -> ActionEvent e -> ActionListener.actionPerformed(e)

@ObsPtn class JButton
@ObsPtn class ActionListener



DynamicTreeDemo
---------------

(button click) -> ActionEvent e -> ActionListener.actionPerformed(e)

@ObsPtn class DynamicTreeDemo
@ObsPtn class ActionListener



FileChooserDemo
---------------

new JButton *2 -> JButton.addActionListener(FileChooserDemo fcd)
(button click) -> ActionEvent e -> fcd.actionPerformed(e) -> JFileChooser.showDialog() -> ...

@ObsPtn class JButton
@ObsPtn class ActionListener

The JFileChooser may implicitly involve another design pattern (react to mouse click, etc.) ?


FileChooserDemo2
----------------

new JButton -> JButton.addActionListener(FileChooserDemo2 fc)
(button click) -> ActionEvent e -> fc.actionPerformed(e) -> new ImagePreview(fc) -> fc.addPropertyChangeListener(ImagePreview ip) -> ... -> JFileChooser.showDialog() -> ...

@ObsPtn class JButton
@ObsPtn class ActionListener
@ObsPtn class JFileChooser
@ObsPtn class PropertyChangeListener



FormattedTextFieldDemo
----------------------

The FormattedTextFieldDemo listens to three JFormattedTextField instances, but only listens to the "value" change: Container.addPropertyChangeListener(String propertyName, PropertyChangeListener listener)

@ObsPtn(PropertyChangeEvent) class JFormattedTextField (Container?)
@ObsPtn(PropertyChangeEvent) class PropertyChangeListener

The observable needs to provide multiple attach methods. When the observer provides a particular property name, the observable needs to remember it and only notify appropriate events.



FormatterFactoryDemo
--------------------

@ObsPtn(PropertyChangeEvent) class JFormattedTextField (Container?)
@ObsPtn(PropertyChangeEvent) class PropertyChangeListener

Similar to the FormattedTextFieldDemo, but the formatter for each TextField is generated by a DefaultFormatterFactory instance, which uses the factory pattern.



FrameDemo
---------

not using any event-relevant interfaces
(events may be handled within the JFrame class)


FrameDemo2
----------

FrameDemo2 listens to six JRadioButton's and one JButton. 

(button click) -> ActionEvent e -> fd2.actionPerformed(e) -> new JFrame() -> ...

JFrame may use the observer pattern?



Framework
---------

Each menu item is listened by a dedicated listener.

@ObsPtn class JMenuItem
@ObsPtn class ActionListener



GenealogyExample
----------------

Standard Button-Action pattern.

@ObsPtn(ActionEvent) class JRadioButton
@ObsPtn(ActionEvent) class ActionListener

The GenealogyModel is a observable that can be listened by TreeModelListener's. But there's no listener for the tree model.



GlassPaneDemo
-------------

new JCheckBox() -> MyGlassPane.addItemListener() ->
(JCheckBox click) -> (MyGlassPane visible) -> (react to mouse event) 
listener = new MouseInputAdapter() -> MyGlassPane.addMouseListner(listener) & addMouseMotionListener(listener) ->
(mouse event) -> (fire the appropriate handle method of the listener)

@ObsPtn class JCheckBox
@ObsPtn class ItemListener
@ObsPtn class JComponent
@ObsPtn class MouseInputAdapter

There are multiple attach methods for the MouseEvent: addMouseListener, addMouseMotionListener, addMouseWheelListener. And correspondingly, there are three listener lists. In this example, the listener registers to two of them.



HtmlDemo
--------

Standard Button-Action pattern.

@ObsPtn(ActionEvent) class AbstractButton
@ObsPtn(ActionEvent) interface ActionListener



IconDemo
--------

No explicit observer pattern.



InternalFrameDemo
-----------------

Standard Button-Action pattern.

@ObsPtn(ActionEvent) class JMenuItem
@ObsPtn(ActionEvent) interface ActionListener



JWSFileChooserDemo
------------------

new JButton *2 -> JButton.addActionListener(JWSFileChooserDemo jws)
(button click) -> ActionEvent e -> jws.actionPerformed(e) -> FileOpen/SaveService.showDialog() -> ...

@ObsPtn class JButton
@ObsPtn class ActionListener



LabelDemo
---------

No explicit observer pattern.



LayeredPaneDemo
---------------

The LayeredPaneDemo listens to a JCheckBox, a JComboBox, as well as the MouseMotionEvents.

@ObsPtn class JCheckBox
@ObsPtn class JComboBox
@ObsPtn class Component
@ObsPtn class ActionListener



LayeredPaneDemo2
----------------

The LayeredPaneDemo listens to a JCheckBox, a JComboBox, as well as the MouseMotionEvents.

@ObsPtn class JCheckBox
@ObsPtn class JComboBox
@ObsPtn class Component
@ObsPtn class ActionListener



ListDemo
--------

ListDemo listens to ListSelectionEvent. HireListener and FireListener are two inner classes. HireListener registers to both DocumentEvents and ActionEvents, FireListener registers to only ActionEvents.

new JTextField -> JTextComponent.getDocument() -> Document.addDocumentListener()
new JList -> JList.getSelectionModel() -> ListSelectionModel.addListSelectionListener()
(insert/delete text) -> ActionEvent e -> AbstractUndoableEdit() -> AbstractDocument$DefaultDocumentEvent e' -> HireListener.insertUpdate(e')
(hire button click) -> ActionEvent e -> HireListener.actionPerformed(e)
(list selection) -> ListSelectionEvent e -> ListDemo.valueChanged(e)
(fire button click) -> ActionEvent e -> FireListener.actionPerformed(e)

@ObsPtn(ActionEvent) class JTextField
@ObsPtn(ActionEvent) class AbstractButton
@ObsPtn(ListSelectionEvent) interface ListSelectionListener
@ObsPtn(ListSelectionEvent) interface ListSelectionModel
@ObsPtn(DocumentEvent) interface Document
@ObsPtn(DocumentEvent) interface DocumentListener

How to handle inner class?



ListDialogRunner
----------------

JButton.addActionListener(ListDialogRunner) -> (button click) -> ListDialogRunner.actionPerformed(e) -> ListDialog.showDialog() -> JButton.addActionListener(ListDialog) -> (button click) -> ...

@ObsPtn class JButton
@ObsPtn class ActionListener

The Action listener in the ListDialogRunner is an anonymous class. How to handle anonymous classes?



MenuDemo
--------

MenuDemo implements both ActionListener and ItemListener.

@ObsPtn class JMenuItem
@ObsPtn class ActionListener
@ObsPtn class JCheckBoxMenuItem
@ObsPtn class ItemListener



MenuGlueDemo
------------

No explicit observer pattern.



MenuLayoutDemo
--------------

No explicit observer pattern.



MenuLookDemo
------------

No explicit observer pattern.



MenuSelectionManagerDemo
------------------------

Similar to MenuDemo, but the Timer fires an action event every second to its anonymous listener.

@ObsPtn class Timer
@ObsPtn class JMenuItem
@ObsPtn class ActionListener
@ObsPtn class JCheckBoxMenuItem
@ObsPtn class ItemListener

The Timer looks like an interesting observable...



PasswordDemo
------------

@ObsPtn class JPasswordField
@ObsPtn class JButton
@ObsPtn class ActionListener



PopupMenuDemo
-------------

In addition to the MenuDemo, a popup menu extends MouseAdapter and listens to MouseEvent in the TextArea.

@ObsPtn class JMenuItem
@ObsPtn class ActionListener
@ObsPtn class JCheckBoxMenuItem
@ObsPtn class ItemListener
@ObsPtn class TextArea
@ObsPtn class MouseAdapter



ProgressBarDemo
---------------

(button click) -> ActionPerformed() -> new Task() -> Task.addPropertyChangeListener() -> Task.execute() -> (property change) -> propertyChange()

@ObsPtn class JButton
@ObsPtn class ActionListener
@ObsPtn class Task
@ObsPtn class PropertyChangeListener

Task is an inner class.



ProgressBarDemo2
----------------

Similar to ProgressBarDemo.



ProgressMonitorDemo
-------------------

Similar to ProgressBarDemo.



RadioButtonDemo
---------------

same as ButtonDemo

new JRadioButton -> JRadioButton.addActionListener(RadioButtonDemo d)
(button click) -> ActionEvent e -> RadioButtonDemo.actionPerformed(e)

@ObsPtn(ActionEvent) class JRadioButton
@ObsPtn(ActionEvent) interface ActionListener



RootLayeredPaneDemo
-------------------

new JLayeredPane -> JLayeredPane.addMouseMotionListener(RootLayeredPaneDemo d)
new JCheckBox -> JCheckBox.addActionListener(d)
new JComboBox -> JComboBox.addActionListener(d)

(mouse movement) -> MouseEvent e -> Root...Demo.mouseMoved(e)
(box un/check) -> ActionEvent e -> Root...Demo.actionPerformed(e)
(item selected) -> ActionEvent e -> Root...Demo.actionPerformed(e)

@ObsPtn(MouseEvent) interface MouseMotionListener
@ObsPtn(MouseEvent) class Component
@ObsPtn(ActionEvent) interface ActionListener
@ObsPtn(ActionEvent) class AbstractButton
@ObsPtn(ActionEvent) class JComboBox



ScrollDemo
----------

Same as CheckboxDemo

new JToggleButton -> JToggleButton.addItemListener(ScrollDemo d)
(button toggle) -> ItemEvent e -> ScrollDemo.itemStateChanged(e)

@ObsPtn(ItemEvent) class AbstractButton
@ObsPtn(ItemEvent) interface ItemListener



ScrollDemo2
-----------

new DrawingPane -> JPanel.addMouseListener(ScrollDemo2 d)
(left/right mouse click) -> MouseEvent e -> ScrollDemo2.mouseReleased(e)

@ObsPtn(MouseEvent) class Component
@ObsPtn(MouseEvent) interface MouseListener



SharedModelDemo
---------------

Subsumed under ListDemo

new JList -> JList.getSelectionModel() -> ListSelectionModel.addListSelectionListener(new SharedListSelectionHandler())
(list selection) -> ListSelectionEvent e -> SharedListSelectionHandler.valueChanged(e)

@ObsPtn(ListSelectionEvent) interface ListSelectionListener
@ObsPtn(ListSelectionEvent) interface ListSelectionModel



SimpleTableDemo
---------------

not using any event-relevant interfaces



SimpleTableSelectionDemo
------------------------

same as SharedModelDemo (i.e., subsumed under ListDemo)
except for that it registers an anonymous ListSelectionListener

new JTable -> JTable.getSelectionModel() -> ListSelectionModel.addListSelectionListener(anonymous class)
(list selection) -> ListSelectionEvent e -> ...Demo$1.valueChanged(e)

@ObsPtn(ListSelectionEvent) interface ListSelectionListener
@ObsPtn(ListSelectionEvent) interface ListSelectionModel



SliderDemo
----------

similar to MenuSelectionManagerDemo, timer is used to update animation frames
addWindowListener() seems dead code

new JSlider -> JSlider.addChangeListener(SliderDemo d)
(slide shift) -> ChangeEvent e -> SliderDemo.stateChanged(e)

@ObsPtn(ChangeEvent) interface ChangeListener
@ObsPtn(ChangeEvent) class JSlider

@ObsPtn(ActionEvent) interface ActionListener
@ObsPtn(ActionEvent) class Timer



SliderDemo2
-----------

same as SliderDemo, except for the vertical, relative slider



SpinnerDemo
-----------

None of methods in client-side code are involved in event dispatching.
Nonetheless, we can see interesting event flows:

1) instantiating JSlider
-> javax.swing.text.InternationalFormatter$IncrementAction (hidden class)
-> javax.swing.AbstractAction("increment"/"decrement")
-> ... (several super() calls)
-> javax.swing.JSpinner$ModelListener(spinner, null)

2) clicking up/down spinner button
-> javax.swing.text.InternationalFormatter$IncrementAction
-> javax.swing.AbstractAction("increment"/"decrement")
-> ...
-> javax.swing.text.AbstractDocument$DefaultDocumentEvent
-> javax.swing.undo.CompoundEdit
-> javax.swing.undo.AbstractUndoableEdit


SpinnerDemo2
------------

same as SpinnerDemo



SpinnerDemo3
------------

new JSpinner -> JSpinner.addChangeListener(SpinnerDemo3 d)

(clicking up/down spinner button) -> ChangeEvent e -> SpinnerDemo3.stateChanged(e)

@ObsPtn(ChangeEvent) interface ChangeListener
@ObsPtn(ChangeEvent) class JSpinner



SpinnerDemo4
------------

similar to SpinnerDemo3

new JSpinner -> JSpinner.addChangeListener(SpinnerDemo4$GrayEditor ge)

(clicking up/down spinner button) -> ChangeEvent e -> SpinnerDemo4$GrayEditer.stateChanged(e)

@ObsPtn(ChangeEvent) interface ChangeListener
@ObsPtn(ChangeEvent) class JSpinner



SplitPaneDemo
-------------

different from ListDemo, where ListSelectionModel.add...Listener is used

new JList -> JList.addListSelectionListener(SplitPaneDemo d)

(list selection) -> ListSelectionEvent e -> SplitPaneDemo.valueChanged(e)

@ObsPtn(ListSelectionEvent) interface ListSelectionListener
@ObsPtn(ListSelectionEvent) class JList



SplitPaneDemo2
--------------

use SplitPaneDemo as a client, but its pattern usage is same



SplitPaneDividerDemo
--------------------

Standard Button-Action pattern

@ObsPtn(ActionEvent) class AbstractButton
@ObsPtn(ActionEvent) interface ActionListener

working


TabbedPaneDemo
--------------

Similar to SpinnerDemo, none of methods in client-side code are involved.

(tab selection) -> ActionEvent -> WindowEvent -> then handled by framework



TabComponentsDemo
-----------------

Standard Button-Action pattern (anonymous classes)

JCheckBoxMenuItem < AbstractButton
JMenuItem < AbstractButton

@ObsPtn(ActionEvent) class AbstractButton
@ObsPtn(ActionEvent) interface ActionListener



TableDemo
---------

JTable has AbstractTableModel (or subclasses),
and some of methods in that model will be invoked by the framework.
Unlike any other pattern usages, such model is given via constructor, e.g.,

    new JTable(new MyTableModel());

According to the API document, at least three methods should be overridden:

    public int getRowCount();
    public int getColumnCount();
    public Object getValueAt(int row, int column);

Not sure this is always the case, but, according to the log trace of this demo,
getColumnCount() is invoked when creating the table first time;
getRowCount() is invoked every time table-related events happen; and
getValueAt() is also invoked every time table is rendered.

Prior to getValueAt(), AbstractTableModel.getColumnClass(int c)
is invoked so as to determine renderer/editor for each cell.
If a user tried to edit a certain cell (by double-clicking),
AbstractTableModel.isCellEditable(int row, int col) is invoked.
After editing, AbstractTableModel.setValueAt(Object value, int row, int col)
is invoked.

(double click) -> MouseEvent e
-> MyTableModel.getRowCount(), .isCellEditable(), .getColumnClass(), .getValueAt()

(edit done) -> ChangeEvent e
-> MyTableModel.setValueAt()
  -> fireTableCellUpdated() -> TableModelEvent e (-> TableModelListener if any)



TableDialogEditDemo
-------------------

On top of TableDemo, this demo uses custom renderer and editor as well.
We can regard these as registering listeners for rendering/editing events.

    JTable table = new JTable(new MyTableModel());
    table.setDefaultRenderer(Color.class, new ColorRenderer(true));
    table.setDefaultEditor(Color.class, new ColorEditor());

ColorEditor < AbstractCellEditor
ColorRenderer < TableCellRenderer

(double click a Color cell) -> MouseEvent e -> ActionEvent e
-> ColorEditor.actionPerformed(e') // which opens ColorChooser
  -> (pick whatever color) -> ChangeEvent e -> ColorEditor.getCellEditorValue() -> MyTableModel.setValueAt()
  -> fireEditingStopped() // renderer reappear
    -> MyTableModel.getRowCount(), .isCellEditable(), .getColumnClass(), .getValueAt()
      -> ColorRenderer.getTableCellRendererComponent(...)



TableFTFEditDemo
----------------

Similar to TableDialogEditDemo; but the custom editor in this demo extends
a different base class: DefaultCellEditor (a subclass of AbstractCellEditor)

    JTable table = new JTable(new MyTableModel());
    table.setDefaultEditor(Integer.class, new IntegerEditor());

IntegerEditor < DefaultCellEditor (< AbstractCellEditor)

(editing - keystroke) -> KeyEvent e
-> DefaultCellEditor.getTableCellEditorComponent() -> .setValue()

(edit done) -> ActionEvent e
-> IntegerEditor$1.actionPerformed()
  -> JFormattedTextField.postActionEvent() -> ActionEvent e
  -> IntegerEditor.stopCellEditing() -> super() -> ChangeEvent e
    -> IntegerEditor.getCellEditorValue() -> MyTableModel.setValueAt() -> TableModelEvent e



TableFilterDemo
---------------

Partially subsumed by ListDemo or TextAreaDemo:

new JTextField -> .getDocument().addDocumentListener()

(key stroke) -> KeyEvent e
-> AbstractDocumentEvent$DefaultDocumentEvent e'
-> TAbleFilterDemo$2.insertUpdate(e') -> ... -> TableRowSorter.setRowFilter()
  -> MyTableModel.getColumnCount(), .getValueAt()
  -> DefaultRowSorter$Row()



TablePrintDemo
--------------

Standard Button-Action pattern.



TableSelectionDemo
------------------

Partially subsumed by RadioButtonDemo and ListDemo;
using JRadioButton to examine different combinations of table selection modes

State machine patterns are involved.
Based on the selection mode (which is set by the above radio buttons),
list selection events will be passed to different listeners

    JTable table = new JTable(new MyTableModel());
    table.getSelectionModel().addListSelectionListener(new RowListener());
    table.getColumnModel().getSelectionModel().addListSelectionListener(new ColumnListener());

(button click) -> ActionEvent e -> TableSelectionDemo.actionPerformed(e)

(list selection) -> ListSelectionEvent e ->
TableSelectionDemo$(RowListener|ColumnListener).valueChanged(e)



TableSortDemo
-------------

Almost identical to TableDemo, except for that it sets auto row sorter:

  JTable table = new JTable(new MyTableModel());
  table.setAutoCreateRowSorter(true);

(click table header) -> MouseEvent e -> RowSorter$SortKey(...)
-> RowSorterEvent e (then, sorted and re-rendered)



TableToolTipsDemo
-----------------

Similar to TableDemo, except that it shows tool tip texts when mouse moved

According to the API document, JTable overrides JComponent's getToolTipText()
in order to invoke its renderer's tool tip text.
In this demo, JTable's model implements that method.

(mouse hovered on certain cells or column header) -> MouseEvent e
-> MyTableModel$1.getToolTipText(e)



TextAreaDemo
------------

The TextAreaDemo implements DocumentListener, which provides three update methods: changedUpdate(), insertUpdate(), and removeUpdate(). The observerable is a TextArea.

@ObsPtn(DocumentEvent) interface Document
@ObsPtn(DocumentEvent) interface DocumentListener

As three update methods are involved, we may need to split the observer pattern into three sub patterns: @ObsPtn(DocumentChanged), @ObsPtn(DocumentInsert), and @ObsPtn(DocumentRemove).

javax.swing.event.DocumentEvent$EventType("INSERT")
javax.swing.event.DocumentEvent$EventType("REMOVE")
javax.swing.event.DocumentEvent$EventType("CHANGE")



TextComponentDemo
-----------------

Three observer patterns involved:

@ObsPtn(DocumentEvent, UndoableEditEvent) interface Document
@ObsPtn(DocumentEvent) interface DocumentListener
@ObsPtn(UndoableEditEvent) interface UndoableEditListener
@ObsPtn(CaretEvent) class JTextPane
@ObsPtn(CaretEvent) interface CaretListener

The observers are inner class instances: MyUndoableListener, CaretListenerLabel, MyDocumentListener.


TextDemo
--------

new JTextField -> JTextField.addActionListener(TextDemo td)
(text entered) -> ActionEvent e -> TextDemo.actionPerformed(e)

@ObsPtn(ActionEvent) class JTextField
@ObsPtn(ActionEvent) interface ActionListener


TextFieldDemo
-------------

Similar to TextAreaDemo.


TextInputDemo
-------------

The TextInputDemo is an ActionListener that listens to every JButton and every JTextField. It is also a FocusListener that listens to every JTextField. As a FocusListener, two update methods are implemented: focusGained() and focusLost().

@ObsPtn(DocumentEvent) class DocumentEventListener
@ObsPtn(FocusEvent) class FocusEventListener
@ObsPtn(DocumentEvent, FocusEvent) interface JTextField
@ObsPtn(DocumentEvent) interface JButton

Also need to split @ObsPtn(FocusEvent) to sub-patterns.


TextSampleDemo
--------------

The TextSampleDemo listens to JTextField, JPasswordField, JFormattedTextField, JButton, so the observable class should be their common super class: JComponent.

@ObsPtn(ActionEvent) class JComponent
@ObsPtn(ActionEvent) interface ActionListener


ToolBarDemo
-----------

new JButton -> JButton.addActionListener(ToolBarDemo tbd)
(button click) -> ActionEvent e -> ToolBarDemo.actionPerformed(e)

@ObsPtn(ActionEvent) class JButton
@ObsPtn(ActionEvent) interface ActionListener

working


ToolBarDemo2
------------

Similar to ToolBarDemo, but has one more JButton.

working



TopLevelDemo
------------

No explicit observer pattern.


TreeDemo
--------

new JTree -> JTree.addTreeSelectionListener(TreeDemo td)
(tree value selected) -> TreeSelectionEvent e -> TreeDemo.valueChanged(e)

@ObsPtn(TreeSelectionEvent) class JTree
@ObsPtn(TreeSelectionEvent) interface TreeSelectionListener


TreeIconDemo
------------

Similar to TreeDemo.


TreeIconDemo2
-------------

Similar to TreeDemo.


TumbleItem
----------

An applet program. The animation is controlled by the timer which repeatedly send the ActionEvent.

@ObsPtn(ActionEvent) class Timer
@ObsPtn(ActionEvent) interface ActionListener


