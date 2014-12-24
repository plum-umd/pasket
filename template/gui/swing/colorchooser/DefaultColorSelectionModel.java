package javax.swing.colorchooser;

public class DefaultColorSelectionModel implements ColorSelectionModel {

  public void addChangeListener(ChangeListener listener);
  //protected void fireStateChanged();
  public void fireStateChanged(ChangeEvent e); // TODO: expedient
  //public ChangeListener[] getChangeListeners();
  public void removeChangeListener(ChangeListener listener);

  public Color getSelectedColor();
  public void setSelectedColor(Color color);
}
