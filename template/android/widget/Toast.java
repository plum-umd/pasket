package android.widget;

public class Toast {
  public Toast(Context context);

  public static Toast makeText(Context context, CharSequence text, int duration);

  public void show();
}
