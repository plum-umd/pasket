package javax.swing.colorchooser;

@ObserverPattern(ChangeEvent)
public interface ColorSelectionModel {
  public void addChangeListener(ChangeListener listener);
  public void removeChangeListener(ChangeListener listener);

  public Color getSelectedColor();
  public void setSelectedColor(Color color);
}
