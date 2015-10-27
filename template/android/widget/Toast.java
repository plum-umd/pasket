package android.widget;

public class Toast {
  public Toast(Context context);

  public final static int LENGTH_LONG = 1;
  public final static int LENGTH_SHORT = 0;

  public static Toast makeText(Context context, CharSequence text, int duration);

  public void show();
}
