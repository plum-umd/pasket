package javax.swing;

public class JSplitPane extends JComponent {
  public static final int HORIZONTAL_SPLIT = 1;

  public JSplitPane(int newOrientation);

  public void resetToPreferredSizes() {
    int _neworientation = 0; // TODO: how to synthesize this sort of "reset"?
  }

  public void setContinuousLayout(boolean newContinuousLayout);
  public void setOneTouchExpandable(boolean newValue);
  //public void setResizeWeight(double value);
}
