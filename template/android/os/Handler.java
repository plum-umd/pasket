package android.os;

public class Handler {
  public interface CallBack {
    public boolean handleMessage(Message msg);
  }

  public Handler();

  public void handleMessage(Message msg);
  public void dispatchMessage(Message msg);
}
