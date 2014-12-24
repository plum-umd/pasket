@Singleton
class Manager {

  static final int water = 0;
  static final int power = 1;

  @Multiton
  Map<Integer, Resource> resource;

}
