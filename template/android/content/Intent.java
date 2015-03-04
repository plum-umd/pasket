package android.content;

public class Intent {
  public Intent();
  public Intent(String action);
  public Intent(String action, Uri uri);
  // TODO: bounded type parameter
  //public Intent(Context packageContext, Class<?> cls);
  public Intent(Context packageContext, Class cls);
}
