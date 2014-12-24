class Player {

  @Set @State
  int state;

  @Error
  void setError();

  void prepare();
  void release();
  void reset();

  void start();
  void pause();
  void stop();

}
