package javax.swing;

@ObserverPattern(ActionEvent)
//public class JComboBox extends JComponent implements ActionListener, ItemSelectable {
public class JComboBox extends JComponent {
  public JComboBox();

  public void dispatchEvent(AWTEvent event); // TODO: should use Component's

  //public void actionPerformed(ActionEvent e);
  public void addActionListener(ActionListener l);
  public void removeActionListener(ActionListener l);

  public void addItemListener(ItemListener l);
  public void removeItemListener(ItemListener l);

  //public Object getSelectedItem();

  public int getSelectedIndex();
  public void setSelectedIndex(int anIndex);

}
