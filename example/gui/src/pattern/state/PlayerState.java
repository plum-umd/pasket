package pattern.state;

// Abstract class cannot be instantiated
abstract class PlayerState implements IPlayerState {

  private void errorMsg(String mname) {
    String tag = this.getClass().getName();
    System.out.println("invalid: " + tag + "." + mname + "()");
  }

  // If the subclass does not override this method,
  // it'll move to Error state when this method is invoked.
  // That is, this operation is not allowed for that class.
  public void prepare(Player player) {
    errorMsg("prepare");
    player.setError();
  }

  public void release(Player player) {
    errorMsg("release");
    player.setError();
  }

  public void reset(Player player) {
    errorMsg("reset");
    player.setError();
  }

  public void start(Player player) {
    errorMsg("start");
    player.setError();
  }

  public void pause(Player player) {
    errorMsg("pause");
    player.setError();
  }

  public void stop(Player player) {
    errorMsg("stop");
    player.setError();
  }

}
