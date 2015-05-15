package javax.swing;

@ObserverPattern(ActionEvent)
public class AbstractButton extends JComponent implements SwingConstants, ItemSelectable {
  public AbstractButton();

  public void addActionListener(ActionListener l);
  public void removeActionListener(ActionListener l);
  public void fireActionPerformed(ActionEvent event);
  // TODO: new role: @Retrieve
  //public ActionListener[] getActionListeners();

  public void addItemListener(ItemListener l);
  public void removeItemListener(ItemListener l);
  public void fireItemStateChanged(ItemEvent event);

  public void setVerticalTextPosition(int textPosition);
  public void setHorizontalTextPosition(int textPosition);

  //public void setMnemonic(char mnemonic); // TODO: handling overloading
  public void setMnemonic(int mnemonic);

  public String getActionCommand();
  public void setActionCommand(String actionCommand);

  public void setSelected(boolean b);
}
