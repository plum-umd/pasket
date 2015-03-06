package android.os;

public class Handler {
  public interface CallBack {
    public boolean handleMessage(Message msg);
  }

  public Handler();
  public Handler(Looper looper);

  public final Looper getLooper();

  public void handleMessage(Message msg);
  public void dispatchMessage(Message msg);
  public final boolean sendMessage(Message msg);

  public final boolean post(Runnable r);
}
