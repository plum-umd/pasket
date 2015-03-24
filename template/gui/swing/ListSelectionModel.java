package javax.swing;

public interface ListSelectionModel {
  public final static int SINGLE_SELECTION = 0;
  public final static int SINGLE_INTERVAL_SELECTION = 1;
  public final static int MULTIPLE_INTERVAL_SELECTION = 2;

  public void addListSelectionListener(ListSelectionListener listener);
  public void removeListSelectionListener(ListSelectionListener listener);
}
