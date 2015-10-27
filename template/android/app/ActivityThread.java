package android.app;

//@Singleton
public final class ActivityThread {

  public static ActivityThread currentActivityThread();

  final Handler getHandler();

  private class H extends Handler {
    public static final int LAUNCH_ACTIVITY          = 100;
    public static final int PAUSE_ACTIVITY           = 101;
    public static final int PAUSE_ACTIVITY_FINISHING = 102;
    public static final int STOP_ACTIVITY_SHOW       = 103;
    public static final int STOP_ACTIVITY_HIDE       = 104;

    public static final int RESUME_ACTIVITY          = 107;

    public static final int DESTRIY_ACTIVITY         = 109;

    public void handleMessage(Message msg);
  }

  // TODO: should be able to maintain multiple Activity's
  //public final Activity getActivity(IBinder token);
  public final Activity getActivity();

  //public static void main(String[] args);
}
