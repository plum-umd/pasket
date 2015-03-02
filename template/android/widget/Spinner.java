package android.widget;

public class Spinner extends AbsSpinner {
  public Spinner(Context context, int mode);

  public static final int MODE_DIALOG = 0;
  public static final int MODE_DROPDOWN = 1;

  public void setPrompt(CharSequence prompt);
  public CharSequence getPrompt();
}
