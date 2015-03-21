package android.content;

public abstract class Context {
  public final static String TELEPHONY_SERVICE = "phone";

  public Context();

  public abstract void startActivity(Intent intent);
  public abstract void startActivity(Intent intent, Bundle options);

  public abstract Object getSystemService(String name);
}
