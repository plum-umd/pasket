package android.app;

@Proxy(Window)
public class Activity extends ContextThemeWrapper {
  public Activity();

  public Window getWindow();

  public void setContentView(int layoutResID);
  public void setContentView(View view);
  public void setContentView(View view, View.LayoutParams params);

  public View findViewById(int id);

  // lifecycle
  protected void onCreate(Bundle savedInstanceState);
}
