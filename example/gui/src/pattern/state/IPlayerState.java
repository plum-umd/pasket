package pattern.state;

interface IPlayerState {
  void prepare(Player player);
  void release(Player player);
  void reset(Player player);

  void start(Player player);
  void pause(Player player);
  void stop(Player player);
}
