class Main {

  @Harness("sample1")
  public static void main1() {
    Manager m1 = @Singleton(Manager);
    Manager m2 = @Singleton(Manager);
    assert m1 == m2;
    Resource r1 = @Get(field = m1.resource, args = {Manager.water});
    Resource r2 = @Get(field = m1.resource, args = {Manager.power});
    Resource r3 = @Get(field = m1.resource, args = {Manager.water});
    assert r1 == r3;
  }
}
