package android.view;

public abstract class InputEvent {
  public static final int SOURCE_UNKNOWN = 0;

  // XXX: virtual <init>, in lieu of CREATOR factory
  InputEvent(int source);

  public abstract int getSource();
  public abstract void setSource(int source);
}
