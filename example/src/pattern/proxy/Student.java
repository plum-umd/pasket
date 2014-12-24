package pattern.proxy;

class Student implements IStudent {

  private int _grade;

  public int getGrade() {
    return this._grade;
  }

  public void setGrade(int grade) {
    this._grade = grade;
  }

  private String _profile;

  public String getProfile() {
    System.out.println("Loading profile...");
    return this._profile;
  }

  public Student(String profile) {
    this._profile = profile;
  }

}
