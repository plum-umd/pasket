package pattern.state;

class Player {

  private IPlayerState initState;
  private IPlayerState prepState;
  private IPlayerState startState;
  private IPlayerState pausedState;
  private IPlayerState stopState;
  private IPlayerState endState; 
  private IPlayerState errState;

  private IPlayerState _state;

  public Player () {
    initState = new Initialized();
    prepState = new Prepared();
    startState = new Started();
    pausedState = new Paused();
    stopState = new Stopped();
    endState = new End();
    errState = new Error();

    this._state = initState;
  }

  public void prepare() {
    this._state.prepare(this);
  }

  public void release() {
    this._state.release(this);
  }

  public void reset() {
    this._state.reset(this);
  }

  public void start() {
    this._state.start(this);
  }

  public void pause() {
    this._state.pause(this);
  }

  public void stop() {
    this._state.stop(this);
  }

  void setState(IPlayerState state) {
    String before = this._state.getClass().getName();
    String after = state.getClass().getName();
    System.out.println("Player: " + before + " -> " + after);
    this._state = state;
  }

  void setError() {
    this._state = errState;
  }

  class Initialized extends PlayerState {
    public void prepare(Player player) {
      player.setState(prepState);
    }
    public void release(Player player) {
      player.setState(endState);
    }
    public void reset(Player player) {
      player.setState(initState);
    }
  }

  class Prepared extends PlayerState {
    public void release(Player player) {
      player.setState(endState);
    }
    public void reset(Player player) {
      player.setState(initState);
    }
    public void start(Player player) {
      player.setState(startState);
    }
  }

  class Started extends PlayerState {
    public void release(Player player) {
      player.setState(endState);
    }
    public void reset(Player player) {
      player.setState(initState);
    }
    public void pause(Player player) {
      player.setState(pausedState);
    }
    public void stop(Player player) {
      player.setState(stopState);
    }
  }

  class Paused extends PlayerState {
    public void release(Player player) {
      player.setState(endState);
    }
    public void reset(Player player) {
      player.setState(initState);
    }
    public void start(Player player) {
      player.setState(startState);
    }
    public void stop(Player player) {
      player.setState(stopState);
    }
  }

  class Stopped extends PlayerState {
    public void prepare(Player player) {
      player.setState(prepState);
    }
    public void release(Player player) {
      player.setState(endState);
    }
    public void reset(Player player) {
      player.setState(initState);
    }
  }

  class End extends PlayerState { }
  class Error extends PlayerState { }

}
