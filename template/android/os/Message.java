package android.os;

public final class Message {
  public Message();

  public int what;

  public void setTarget(Handler target);
  public Handler getTarget();
}
