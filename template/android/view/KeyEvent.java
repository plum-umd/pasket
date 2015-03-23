package android.view;

public class KeyEvent extends InputEvent {
  public KeyEvent(int action, int code);

  public int getSource();
  public void setSource(int source);
  public final int getKeyCode();
}
