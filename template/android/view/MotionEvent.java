package android.view;

public class MotionEvent extends InputEvent {
  public static final int ACTION_DOWN = 0;
  public static final int ACTION_UP = 1;

  public static final int ACTION_MASK = 255; // 0xff

  // XXX: virtual <init>, in lieu of CREATOR factory
  MotionEvent(int source, int action);

  public final int getActionMasked();
}
