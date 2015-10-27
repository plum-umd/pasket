package android.view;

//@Singleton
final class WindowManagerGlobal implements WindowManager {

  public static WindowManagerGlobal getInstance();

  public void addView(View view, ViewGroup.LayoutParams params);

  // XXX: to make them look like an adapter
  public void addView(View view, int index, ViewGroup.LayoutParams params);
  public void addView(View view);

  // XXX: to be an instance of Map-typed accessor
  void addView(int id, View view);
  View findViewById(int id);

}
