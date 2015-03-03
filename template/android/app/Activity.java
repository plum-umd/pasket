package android.app;

public class Activity extends ContextThemeWrapper {

  public void setContentView(View view);
  public void setContentView(int layoutResID);

  public View findViewById(int id);

  protected void onCreate(Bundle savedInstanceState);
}
