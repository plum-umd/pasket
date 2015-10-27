package android.content;

public class Intent {
  //public static final String ACTION_MAIN = "android.intent.action.MAIN";

  //public Intent();
  //public Intent(String action);
  //public Intent(String action, Uri uri);
  //public Intent(Context packageContext, Class<?> cls);

  // XXX: virtual <init>
  public Intent(ComponentName cname);

  //public String getAction();
  public ComponentName getComponent();

  //public Intent setClassName(String packageName, String className);
}
