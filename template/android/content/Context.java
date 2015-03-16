package android.content;

public abstract class Context {
  public abstract void startActivity(Intent intent);
  public abstract void startActivity(Intent intent, Bundle options);

  public abstract Object getSystemService(String name);
}
